from __future__ import annotations

from datetime import datetime

from src.processing.filter_invalid_trips import (
    invalid_trip_range_fields,
    requested_pickup_window,
    service_date_is_within_requested_window,
)


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


def test_requested_pickup_window_builds_inclusive_exclusive_month_bounds() -> None:
    start, end_exclusive = requested_pickup_window(start_month="2024-01", end_month="2024-01")
    assert start == datetime(2024, 1, 1)
    assert end_exclusive == datetime(2024, 2, 1)


def test_service_date_window_allows_only_requested_month() -> None:
    assert service_date_is_within_requested_window(datetime(2024, 1, 1), "2024-01", "2024-01")
    assert service_date_is_within_requested_window(datetime(2024, 1, 31, 23, 59), "2024-01", "2024-01")
    assert not service_date_is_within_requested_window(datetime(2023, 12, 31, 23, 59), "2024-01", "2024-01")
    assert not service_date_is_within_requested_window(datetime(2024, 2, 1), "2024-01", "2024-01")
