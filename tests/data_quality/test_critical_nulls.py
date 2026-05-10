from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.common.lakehouse_manifests import resolve_latest_layer_path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"

SILVER_CRITICAL_COLUMNS = [
    "pickup_datetime",
    "dropoff_datetime",
    "service_date",
    "pickup_zone_id",
    "dropoff_zone_id",
    "trip_distance",
    "fare_amount",
    "total_amount",
    "trip_duration_minutes",
]

GOLD_CRITICAL_COLUMNS = [
    "service_date",
    "pickup_zone_id",
    "trip_count",
    "total_fare",
    "avg_fare",
    "total_distance",
    "avg_distance",
    "avg_duration_minutes",
]


def _load_layer_frame(layer: str) -> pd.DataFrame:
    try:
        path = resolve_latest_layer_path(layer, "2024-01", "2024-01", data_root=DATA_ROOT)
    except FileNotFoundError:
        pytest.skip(f"Local {layer} latest artifact is not available for critical null validation")
    return pd.read_parquet(path)


def test_silver_latest_artifact_has_no_critical_nulls() -> None:
    frame = _load_layer_frame("silver")

    null_counts = frame[SILVER_CRITICAL_COLUMNS].isnull().sum()
    assert int(null_counts.sum()) == 0


def test_gold_latest_artifact_has_no_critical_nulls() -> None:
    frame = _load_layer_frame("gold")

    null_counts = frame[GOLD_CRITICAL_COLUMNS].isnull().sum()
    assert int(null_counts.sum()) == 0
