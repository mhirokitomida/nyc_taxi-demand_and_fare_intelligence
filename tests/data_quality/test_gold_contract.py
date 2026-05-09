from __future__ import annotations

from datetime import date

import pyarrow as pa
import pytest

from src.processing.validate_gold_contract import validate_gold_table


def test_validate_gold_table_accepts_expected_contract() -> None:
    table = pa.table(
        {
            "service_date": [date(2024, 1, 1)],
            "pickup_zone_id": [100],
            "trip_count": [12],
            "total_fare": [240.0],
            "avg_fare": [20.0],
            "total_distance": [55.0],
            "avg_distance": [4.58],
            "avg_duration_minutes": [14.2],
        }
    )

    validate_gold_table(table)


def test_validate_gold_table_rejects_missing_required_columns() -> None:
    table = pa.table(
        {
            "service_date": [date(2024, 1, 1)],
            "pickup_zone_id": [100],
            "trip_count": [12],
        }
    )

    with pytest.raises(ValueError, match="missing required columns"):
        validate_gold_table(table)
