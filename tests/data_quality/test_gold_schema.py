from __future__ import annotations

from src.processing.build_gold_daily_zone import REQUIRED_GOLD_COLUMNS


def test_gold_schema_contains_expected_fields() -> None:
    expected = {
        "service_date",
        "pickup_zone_id",
        "trip_count",
        "total_fare",
        "avg_fare",
        "total_distance",
        "avg_distance",
        "avg_duration_minutes",
    }
    assert expected == set(REQUIRED_GOLD_COLUMNS)
