from __future__ import annotations

from src.common.data_checks import require_columns


REQUIRED_BRONZE_COLUMNS = [
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "total_amount",
]


def missing_bronze_columns(columns: list[str]) -> list[str]:
    return require_columns(columns, REQUIRED_BRONZE_COLUMNS)


def validate_bronze_schema(dataframe) -> None:
    missing = missing_bronze_columns(list(dataframe.columns))
    if missing:
        raise ValueError(f"Bronze schema is missing required columns: {missing}")
