from __future__ import annotations

from datetime import datetime

import pytest

from src.processing.build_gold_daily_zone import missing_silver_input_columns
from src.processing.filter_invalid_trips import (
    invalid_trip_range_fields,
    requested_pickup_window,
    service_date_is_within_requested_window,
)


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
