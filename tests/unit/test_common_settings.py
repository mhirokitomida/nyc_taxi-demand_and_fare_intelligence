from __future__ import annotations

from pathlib import Path

from src.common.data_checks import find_negative_values, require_columns
from src.common.paths import get_data_paths
from src.common.settings import get_settings


def test_get_settings_reads_environment_overrides(monkeypatch) -> None:
    monkeypatch.setenv("DATA_ROOT", "custom-data")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("AIRFLOW__WEBSERVER__BASE_URL", "http://localhost:18080")
    monkeypatch.setenv("STREAMLIT_SERVER_PORT", "9999")
    monkeypatch.setenv("SPARK_MASTER_URL", "local[2]")

    settings = get_settings()

    assert settings.project_root.name == "nyc_taxi demand_and_fare_intelligence"
    assert settings.data_root == settings.project_root / "custom-data"
    assert settings.log_level == "DEBUG"
    assert settings.airflow_base_url == "http://localhost:18080"
    assert settings.streamlit_port == 9999
    assert settings.spark_master_url == "local[2]"


def test_get_data_paths_builds_expected_layer_paths(monkeypatch) -> None:
    monkeypatch.setenv("DATA_ROOT", "lake-data")

    paths = get_data_paths()

    assert paths.root == paths.root.parent / "lake-data"
    assert paths.bronze == paths.root / "bronze"
    assert paths.silver == paths.root / "silver"
    assert paths.gold == paths.root / "gold"
    assert paths.ml == paths.root / "ml"


def test_require_columns_and_find_negative_values_cover_common_validation_cases() -> None:
    missing = require_columns(columns=["a", "b"], required=["a", "c"])
    negatives = find_negative_values(
        {"fare_amount": -1.0, "trip_distance": 2.5, "trip_duration_minutes": -3.0},
        ["fare_amount", "trip_distance", "trip_duration_minutes"],
    )

    assert missing == ["c"]
    assert negatives == ["fare_amount", "trip_duration_minutes"]
