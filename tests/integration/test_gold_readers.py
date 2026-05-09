from __future__ import annotations

from pathlib import Path

import pytest

from src.common.read_gold_artifacts import list_gold_artifact_files, read_gold_records, read_gold_table
from src.processing.analytics_views import build_daily_demand_series, build_zone_summary, extract_gold_kpis
from src.processing.validate_gold_contract import validate_gold_table


REAL_GOLD_PATH = Path("data/gold/2024-01_to_2024-01")


@pytest.mark.skipif(not REAL_GOLD_PATH.exists(), reason="Local gold artifacts are required for analytical reader integration test")
def test_gold_readers_and_kpis_work_against_real_gold_artifacts() -> None:
    files = list_gold_artifact_files(start_month="2024-01", end_month="2024-01")
    table = read_gold_table(start_month="2024-01", end_month="2024-01")
    records = read_gold_records(start_month="2024-01", end_month="2024-01")

    validate_gold_table(table)

    kpis = extract_gold_kpis(records)
    daily_series = build_daily_demand_series(records)
    zone_summary = build_zone_summary(records, limit=5)

    assert files
    assert table.num_rows > 0
    assert records
    assert kpis["total_rides"] > 0
    assert kpis["total_demand"] > 0
    assert kpis["total_fare"] > 0
    assert kpis["total_distance"] > 0
    assert kpis["avg_duration_minutes"] > 0
    assert daily_series
    assert zone_summary
    assert "trip_count" in daily_series[0]
    assert "pickup_zone_id" in zone_summary[0]
