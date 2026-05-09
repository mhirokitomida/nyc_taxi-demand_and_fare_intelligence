from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.ml.run_ml_pipeline import run_ml_pipeline


REAL_GOLD_PATH = Path("data/gold/2024-01_to_2024-01")


@pytest.mark.skipif(not REAL_GOLD_PATH.exists(), reason="Real gold artifacts are required for ML pipeline integration test")
def test_ml_pipeline_runs_against_real_gold_and_writes_outputs() -> None:
    result = run_ml_pipeline(start_month="2024-01", end_month="2024-01")

    assert result.artifact_paths.output_dir.exists()
    assert result.artifact_paths.training_slice_path.exists()
    assert result.artifact_paths.predictions_path.exists()
    assert result.artifact_paths.metrics_path.exists()
    assert result.metrics["mae"] is not None
    assert result.metrics["rmse"] is not None
    assert "mape_if_applicable" in result.metrics

    predictions = pd.read_parquet(result.artifact_paths.predictions_path)
    persisted_metrics = json.loads(result.artifact_paths.metrics_path.read_text(encoding="utf-8"))

    assert not predictions.empty
    assert {"predicted_demand", "observed_demand", "pickup_zone_id", "forecast_date"}.issubset(predictions.columns)
    assert persisted_metrics["mae"] == result.metrics["mae"]
