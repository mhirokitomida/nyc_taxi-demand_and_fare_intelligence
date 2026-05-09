from __future__ import annotations

from src.processing.derive_trip_features import REQUIRED_SILVER_COLUMNS


def test_silver_schema_contains_expected_fields() -> None:
    expected = {
        "pickup_datetime",
        "dropoff_datetime",
        "service_date",
        "pickup_hour",
        "day_of_week",
        "pickup_zone_id",
        "dropoff_zone_id",
        "trip_distance",
        "fare_amount",
        "total_amount",
        "trip_duration_minutes",
        "passenger_count",
        "payment_type",
    }
    assert expected.issubset(set(REQUIRED_SILVER_COLUMNS))
