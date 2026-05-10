from __future__ import annotations

import json

import pandas as pd

from src.common.lakehouse_manifests import read_manifest
from src.ml.evaluate_forecast import evaluate_forecast
from src.ml.write_ml_outputs import write_ml_outputs


def test_evaluate_forecast_calculates_mae_rmse_and_mape_when_applicable() -> None:
    prediction_frame = pd.DataFrame(
        {
            "forecast_date": ["2024-01-10", "2024-01-11"],
            "pickup_zone_id": [100, 100],
            "predicted_demand": [10.0, 14.0],
            "observed_demand": [12.0, 15.0],
            "model_name": ["baseline", "baseline"],
            "run_id": ["run-1", "run-1"],
        }
    )

    metrics = evaluate_forecast(prediction_frame=prediction_frame, split_strategy="time_holdout", holdout_days=2)

    assert "mae" in metrics
    assert "rmse" in metrics
    assert metrics["mape_if_applicable"] is not None


def test_write_ml_outputs_persists_predictions_and_metrics(tmp_path) -> None:
    data_root = tmp_path / "data"
    training_slice = pd.DataFrame(
        {
            "service_date": ["2024-01-01"],
            "pickup_zone_id": [100],
            "observed_demand": [12.0],
            "day_of_week": [0],
            "day_of_month": [1],
            "month": [1],
            "is_weekend": [0],
            "feature_window_id": ["2024-01_to_2024-01"],
        }
    )
    predictions = pd.DataFrame(
        {
            "forecast_date": ["2024-01-10"],
            "pickup_zone_id": [100],
            "predicted_demand": [10.5],
            "observed_demand": [12.0],
            "model_name": ["baseline"],
            "run_id": ["run-1"],
        }
    )
    metrics = {
        "run_id": "run-1",
        "model_name": "baseline",
        "evaluation_window": "2024-01-10_to_2024-01-10",
        "split_strategy": "time_holdout",
        "holdout_days": 1,
        "prediction_rows": 1,
        "mae": 1.5,
        "rmse": 1.5,
        "mape_if_applicable": 12.5,
    }

    artifact_paths = write_ml_outputs(
        training_slice=training_slice,
        predictions=predictions,
        metrics=metrics,
        start_month="2024-01",
        end_month="2024-01",
        data_root=data_root,
    )

    assert artifact_paths.training_slice_path.exists()
    assert artifact_paths.predictions_path.exists()
    assert artifact_paths.metrics_path.exists()
    assert artifact_paths.manifest_path.exists()
    persisted_metrics = json.loads(artifact_paths.metrics_path.read_text(encoding="utf-8"))
    persisted_manifest = read_manifest("ml", "2024-01", "2024-01", data_root=data_root)
    assert persisted_metrics["mae"] == 1.5
    assert persisted_metrics["rmse"] == 1.5
    assert persisted_manifest is not None
    assert persisted_manifest.latest_path == "ml/2024-01_to_2024-01/runs/run-1"
    assert persisted_manifest.latest_run_id == "run-1"
