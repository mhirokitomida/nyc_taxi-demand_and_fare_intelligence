from __future__ import annotations

import importlib.util
import os
import shutil
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from src.processing.bronze_to_silver import run_bronze_to_silver
from src.processing.silver_to_gold import run_silver_to_gold


PYSPARK_AVAILABLE = importlib.util.find_spec("pyspark") is not None
JAVA_AVAILABLE = bool(os.environ.get("JAVA_HOME")) or shutil.which("java") is not None


@pytest.mark.skipif(not PYSPARK_AVAILABLE, reason="pyspark is not available in this environment")
@pytest.mark.skipif(not JAVA_AVAILABLE, reason="Java is not available for local PySpark integration test")
def test_bronze_to_silver_to_gold_outputs_are_created(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data_root = tmp_path / "data"
    bronze_dir = data_root / "bronze" / "2024-01"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = bronze_dir / "yellow_tripdata_2024-01.parquet"

    table = pa.table(
        {
            "VendorID": [1, 2],
            "tpep_pickup_datetime": [datetime(2024, 1, 1, 0, 0, 0), datetime(2024, 1, 1, 1, 0, 0)],
            "tpep_dropoff_datetime": [datetime(2024, 1, 1, 0, 10, 0), datetime(2024, 1, 1, 1, 20, 0)],
            "passenger_count": [1.0, 2.0],
            "trip_distance": [1.5, 3.0],
            "PULocationID": [100, 100],
            "DOLocationID": [200, 201],
            "payment_type": [1, 2],
            "fare_amount": [10.0, 20.0],
            "total_amount": [13.0, 24.0],
        }
    )
    pq.write_table(table, parquet_path)

    monkeypatch.setenv("DATA_ROOT", str(data_root))

    silver_result = run_bronze_to_silver(
        start_month="2024-01",
        end_month="2024-01",
        spark_master="local[1]",
        data_root=data_root,
    )
    gold_result = run_silver_to_gold(
        start_month="2024-01",
        end_month="2024-01",
        spark_master="local[1]",
        data_root=data_root,
    )

    assert silver_result.row_count > 0
    assert gold_result.row_count > 0
    assert silver_result.output_path.exists()
    assert gold_result.output_path.exists()
