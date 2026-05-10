from __future__ import annotations

from types import SimpleNamespace

import pytest

from dags._dag_params import (
    DEFAULT_DOWNLOAD_BACKOFF_MULTIPLIER,
    DEFAULT_DOWNLOAD_INITIAL_WAIT_SECONDS,
    DEFAULT_DOWNLOAD_MAX_ATTEMPTS,
    DEFAULT_DOWNLOAD_MAX_WAIT_SECONDS,
    load_dag_run_parameters,
)
from src.ingestion.period_config import IngestionPeriod
from src.ingestion.source_catalog import build_yellow_taxi_source, resolve_period_sources


def test_period_config_rejects_invalid_month_order() -> None:
    with pytest.raises(ValueError):
        IngestionPeriod(start_month="2024-03", end_month="2024-02")


def test_period_config_accepts_long_historical_range() -> None:
    period = IngestionPeriod(start_month="2009-01", end_month="2026-02")

    assert period.month_count == 206
    months = period.iter_months()
    assert months[0] == "2009-01"
    assert months[-1] == "2026-02"
    assert len(months) == 206


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


def test_dag_run_parameters_keep_download_retry_defaults_for_legacy_triggers() -> None:
    context = {
        "dag_run": SimpleNamespace(
            conf={
                "start_month": "2024-01",
                "end_month": "2024-01",
                "rerun_mode": "replace",
                "target_layers": ["bronze"],
            },
            run_id="manual__legacy_trigger",
        )
    }

    params = load_dag_run_parameters(context)

    assert params.download_max_attempts == DEFAULT_DOWNLOAD_MAX_ATTEMPTS
    assert params.download_initial_wait_seconds == DEFAULT_DOWNLOAD_INITIAL_WAIT_SECONDS
    assert params.download_backoff_multiplier == DEFAULT_DOWNLOAD_BACKOFF_MULTIPLIER
    assert params.download_max_wait_seconds == DEFAULT_DOWNLOAD_MAX_WAIT_SECONDS


def test_dag_run_parameters_accept_download_retry_overrides() -> None:
    context = {
        "dag_run": SimpleNamespace(
            conf={
                "start_month": "2024-01",
                "end_month": "2024-01",
                "download_max_attempts": 7,
                "download_initial_wait_seconds": 3,
                "download_backoff_multiplier": 1.5,
                "download_max_wait_seconds": 30,
            },
            run_id="manual__override_trigger",
        )
    }

    params = load_dag_run_parameters(context)

    assert params.download_max_attempts == 7
    assert params.download_initial_wait_seconds == 3.0
    assert params.download_backoff_multiplier == 1.5
    assert params.download_max_wait_seconds == 30.0
