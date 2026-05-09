from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from src.common.data_checks import find_negative_values


def invalid_trip_range_fields(record: Mapping[str, float | int | None]) -> list[str]:
    return find_negative_values(
        record,
        ["trip_distance", "fare_amount", "total_amount", "trip_duration_minutes"],
    )


def requested_pickup_window(start_month: str, end_month: str) -> tuple[datetime, datetime]:
    start = datetime.strptime(start_month, "%Y-%m")
    end = datetime.strptime(end_month, "%Y-%m")
    if end < start:
        raise ValueError("end_month must be greater than or equal to start_month")

    if end.month == 12:
        end_exclusive = datetime(end.year + 1, 1, 1)
    else:
        end_exclusive = datetime(end.year, end.month + 1, 1)
    return start, end_exclusive


def service_date_is_within_requested_window(
    value: datetime,
    start_month: str,
    end_month: str,
) -> bool:
    start, end_exclusive = requested_pickup_window(start_month=start_month, end_month=end_month)
    return start <= value < end_exclusive


def filter_invalid_trips(dataframe, start_month: str, end_month: str):
    from pyspark.sql import functions as F

    start, end_exclusive = requested_pickup_window(start_month=start_month, end_month=end_month)
    duration_minutes = (
        F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")
    ) / F.lit(60.0)

    return dataframe.filter(
        F.col("tpep_pickup_datetime").isNotNull()
        & F.col("tpep_dropoff_datetime").isNotNull()
        & F.col("PULocationID").isNotNull()
        & F.col("DOLocationID").isNotNull()
        & F.col("fare_amount").isNotNull()
        & F.col("trip_distance").isNotNull()
        & F.col("total_amount").isNotNull()
        & (F.col("tpep_pickup_datetime") >= F.lit(start))
        & (F.col("tpep_pickup_datetime") < F.lit(end_exclusive))
        & (F.col("fare_amount") >= 0)
        & (F.col("trip_distance") >= 0)
        & (F.col("total_amount") >= 0)
        & (duration_minutes >= 0)
    )
