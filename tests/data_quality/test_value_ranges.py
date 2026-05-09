from __future__ import annotations

from src.processing.filter_invalid_trips import invalid_trip_range_fields


def test_invalid_range_fields_identifies_negative_values() -> None:
    invalid_fields = invalid_trip_range_fields(
        {
            "trip_distance": -1.0,
            "fare_amount": 10.0,
            "total_amount": -2.0,
            "trip_duration_minutes": 5.0,
        }
    )
    assert invalid_fields == ["trip_distance", "total_amount"]


def test_invalid_range_fields_allows_non_negative_values() -> None:
    invalid_fields = invalid_trip_range_fields(
        {
            "trip_distance": 1.0,
            "fare_amount": 10.0,
            "total_amount": 12.0,
            "trip_duration_minutes": 5.0,
        }
    )
    assert invalid_fields == []
