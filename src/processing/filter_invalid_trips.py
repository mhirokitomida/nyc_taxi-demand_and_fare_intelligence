from __future__ import annotations

from collections.abc import Mapping

from src.common.data_checks import find_negative_values


def invalid_trip_range_fields(record: Mapping[str, float | int | None]) -> list[str]:
    return find_negative_values(
        record,
        ["trip_distance", "fare_amount", "total_amount", "trip_duration_minutes"],
    )


def filter_invalid_trips(dataframe):
    from pyspark.sql import functions as F

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
        & (F.col("fare_amount") >= 0)
        & (F.col("trip_distance") >= 0)
        & (F.col("total_amount") >= 0)
        & (duration_minutes >= 0)
    )
