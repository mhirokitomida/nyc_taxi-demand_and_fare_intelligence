from __future__ import annotations

from src.common.data_checks import require_columns


REQUIRED_GOLD_COLUMNS = [
    "service_date",
    "pickup_zone_id",
    "trip_count",
    "total_fare",
    "avg_fare",
    "total_distance",
    "avg_distance",
    "avg_duration_minutes",
]

REQUIRED_SILVER_INPUT_COLUMNS = [
    "service_date",
    "pickup_zone_id",
    "trip_distance",
    "fare_amount",
    "trip_duration_minutes",
]


def missing_silver_input_columns(columns: list[str]) -> list[str]:
    return require_columns(columns, REQUIRED_SILVER_INPUT_COLUMNS)


def validate_silver_input_schema(dataframe) -> None:
    missing = missing_silver_input_columns(list(dataframe.columns))
    if missing:
        raise ValueError(f"Silver schema is missing required columns for gold aggregation: {missing}")


def build_gold_daily_zone(dataframe):
    from pyspark.sql import functions as F

    return dataframe.groupBy("service_date", "pickup_zone_id").agg(
        F.count("*").alias("trip_count"),
        F.sum("fare_amount").alias("total_fare"),
        F.avg("fare_amount").alias("avg_fare"),
        F.sum("trip_distance").alias("total_distance"),
        F.avg("trip_distance").alias("avg_distance"),
        F.avg("trip_duration_minutes").alias("avg_duration_minutes"),
    )
