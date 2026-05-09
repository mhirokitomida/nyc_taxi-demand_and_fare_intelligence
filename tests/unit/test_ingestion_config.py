from __future__ import annotations

import pytest

from src.ingestion.period_config import IngestionPeriod
from src.ingestion.source_catalog import build_yellow_taxi_source, resolve_period_sources


def test_period_config_rejects_invalid_month_order() -> None:
    with pytest.raises(ValueError):
        IngestionPeriod(start_month="2024-03", end_month="2024-02")


def test_period_config_rejects_more_than_twelve_months() -> None:
    with pytest.raises(ValueError):
        IngestionPeriod(start_month="2023-01", end_month="2024-02")


def test_period_config_iterates_bounded_months() -> None:
    period = IngestionPeriod(start_month="2024-01", end_month="2024-03")
    assert period.month_count == 3
    assert period.iter_months() == ["2024-01", "2024-02", "2024-03"]


def test_source_catalog_builds_expected_yellow_taxi_url() -> None:
    source = build_yellow_taxi_source("2024-01")
    assert source.filename == "yellow_tripdata_2024-01.parquet"
    assert source.source_uri.endswith("/yellow_tripdata_2024-01.parquet")
    assert source.local_relative_path == "bronze/2024-01/yellow_tripdata_2024-01.parquet"


def test_source_catalog_resolves_all_months_in_period() -> None:
    period = IngestionPeriod(start_month="2024-01", end_month="2024-02")
    sources = resolve_period_sources(period)
    assert [source.year_month for source in sources] == ["2024-01", "2024-02"]
