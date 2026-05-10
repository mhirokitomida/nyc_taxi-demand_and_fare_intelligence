from __future__ import annotations

import importlib.util
import os
import shutil
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from src.processing.build_gold_daily_zone import missing_silver_input_columns
from src.processing.filter_invalid_trips import (
    invalid_trip_range_fields,
    requested_pickup_window,
    service_date_is_within_requested_window,
)
from src.processing.read_bronze import BRONZE_NORMALIZED_TYPES, create_spark_session, read_bronze_dataframe


PYSPARK_AVAILABLE = importlib.util.find_spec("pyspark") is not None
JAVA_AVAILABLE = bool(os.environ.get("JAVA_HOME")) or shutil.which("java") is not None


def test_requested_pickup_window_is_start_inclusive_and_next_month_exclusive() -> None:
    start, end_exclusive = requested_pickup_window(start_month="2024-01", end_month="2024-01")

    assert start == datetime(2024, 1, 1, 0, 0, 0)
    assert end_exclusive == datetime(2024, 2, 1, 0, 0, 0)


def test_requested_pickup_window_rejects_end_before_start() -> None:
    with pytest.raises(ValueError, match="end_month must be greater than or equal to start_month"):
        requested_pickup_window(start_month="2024-02", end_month="2024-01")


def test_service_date_within_requested_window_filters_outside_period() -> None:
    assert service_date_is_within_requested_window(datetime(2024, 1, 1, 0, 0, 0), "2024-01", "2024-01")
    assert service_date_is_within_requested_window(datetime(2024, 1, 31, 23, 59, 59), "2024-01", "2024-01")
    assert not service_date_is_within_requested_window(datetime(2023, 12, 31, 23, 59, 59), "2024-01", "2024-01")
    assert not service_date_is_within_requested_window(datetime(2024, 2, 1, 0, 0, 0), "2024-01", "2024-01")


def test_invalid_trip_range_fields_reports_negative_metrics_only() -> None:
    invalid_fields = invalid_trip_range_fields(
        {
            "trip_distance": -1.0,
            "fare_amount": 12.0,
            "total_amount": -2.5,
            "trip_duration_minutes": 5.0,
        }
    )

    assert invalid_fields == ["trip_distance", "total_amount"]


def test_missing_silver_input_columns_reports_gold_dependencies() -> None:
    missing = missing_silver_input_columns(["service_date", "pickup_zone_id"])

    assert missing == ["trip_distance", "fare_amount", "trip_duration_minutes"]


@pytest.mark.skipif(not PYSPARK_AVAILABLE, reason="pyspark is not available in this environment")
@pytest.mark.skipif(not JAVA_AVAILABLE, reason="Java is not available for local PySpark processing test")
def test_read_bronze_dataframe_normalizes_mixed_monthly_physical_schemas(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    january_dir = data_root / "bronze" / "2024-01"
    february_dir = data_root / "bronze" / "2024-02"
    january_dir.mkdir(parents=True, exist_ok=True)
    february_dir.mkdir(parents=True, exist_ok=True)

    pq.write_table(
        pa.table(
            {
                "VendorID": pa.array([1], type=pa.int32()),
                "tpep_pickup_datetime": pa.array([datetime(2024, 1, 1, 0, 0, 0)], type=pa.timestamp("us")),
                "tpep_dropoff_datetime": pa.array([datetime(2024, 1, 1, 0, 10, 0)], type=pa.timestamp("us")),
                "passenger_count": pa.array([1.0], type=pa.float64()),
                "trip_distance": pa.array([1.5], type=pa.float64()),
                "PULocationID": pa.array([100], type=pa.int32()),
                "DOLocationID": pa.array([200], type=pa.int32()),
                "payment_type": pa.array([1], type=pa.int32()),
                "fare_amount": pa.array([10.0], type=pa.float64()),
                "total_amount": pa.array([13.0], type=pa.float64()),
            }
        ),
        january_dir / "yellow_tripdata_2024-01.parquet",
    )
    pq.write_table(
        pa.table(
            {
                "VendorID": pa.array([2], type=pa.int64()),
                "tpep_pickup_datetime": pa.array([datetime(2024, 2, 1, 0, 0, 0)], type=pa.timestamp("us")),
                "tpep_dropoff_datetime": pa.array([datetime(2024, 2, 1, 0, 20, 0)], type=pa.timestamp("us")),
                "passenger_count": pa.array([2.0], type=pa.float64()),
                "trip_distance": pa.array([2.5], type=pa.float64()),
                "PULocationID": pa.array([101], type=pa.int64()),
                "DOLocationID": pa.array([201], type=pa.int64()),
                "payment_type": pa.array([2], type=pa.int32()),
                "fare_amount": pa.array([20.0], type=pa.float64()),
                "total_amount": pa.array([24.0], type=pa.float64()),
                "airport_fee": pa.array([1.25], type=pa.float64()),
            }
        ),
        february_dir / "yellow_tripdata_2024-02.parquet",
    )

    spark = create_spark_session("bronze-schema-normalization-test", master="local[1]")
    try:
        dataframe = read_bronze_dataframe(
            spark=spark,
            start_month="2024-01",
            end_month="2024-02",
            data_root=data_root,
        )

        schema_types = {field.name: field.dataType.simpleString() for field in dataframe.schema.fields}
        assert dataframe.count() == 2
        assert schema_types["PULocationID"] == "bigint"
        assert schema_types["DOLocationID"] == "bigint"
        assert schema_types["airport_fee"] == "double"
        assert schema_types["VendorID"] == "bigint"
        assert set(BRONZE_NORMALIZED_TYPES).issubset(schema_types)

        january_row = dataframe.filter("VendorID = 1").select("airport_fee").collect()[0]
        february_row = dataframe.filter("VendorID = 2").select("airport_fee").collect()[0]
        assert january_row["airport_fee"] is None
        assert february_row["airport_fee"] == pytest.approx(1.25)
    finally:
        spark.stop()
