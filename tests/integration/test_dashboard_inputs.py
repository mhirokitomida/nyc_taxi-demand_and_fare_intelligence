from __future__ import annotations

import pandas as pd

from app.streamlit.data_loader import load_dashboard_artifacts, load_ml_artifacts, resolve_dashboard_period


def test_dashboard_loader_reads_real_gold_and_ml_artifacts() -> None:
    artifacts = load_dashboard_artifacts(requested_period="2024-01_to_2024-01")

    assert not artifacts.gold_frame.empty
    assert {"service_date", "pickup_zone_id", "trip_count"}.issubset(artifacts.gold_frame.columns)
    assert artifacts.ml_status.state == "ready"
    assert artifacts.ml_predictions is not None
    assert artifacts.ml_metrics is not None
    assert {"predicted_demand", "observed_demand"}.issubset(artifacts.ml_predictions.columns)


def test_dashboard_loader_reports_missing_ml_artifacts_when_absent(tmp_path) -> None:
    data_root = tmp_path / "data"
    gold_dir = data_root / "gold" / "2024-01_to_2024-01"
    gold_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "service_date": ["2024-01-01"],
            "pickup_zone_id": [100],
            "trip_count": [12],
            "total_fare": [100.0],
            "avg_fare": [8.3],
            "total_distance": [50.0],
            "avg_distance": [4.2],
            "avg_duration_minutes": [15.0],
        }
    ).to_parquet(gold_dir / "part-00000.parquet", index=False)

    period = resolve_dashboard_period(requested_period="2024-01_to_2024-01", data_root=data_root)
    predictions, metrics, status = load_ml_artifacts(period=period, data_root=data_root)

    assert predictions is None
    assert metrics is None
    assert status.state == "missing"
