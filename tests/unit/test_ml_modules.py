from __future__ import annotations

import pandas as pd
import pytest

from src.ml.evaluate_forecast import calculate_mape_if_applicable, evaluate_forecast
from src.ml.generate_forecast import generate_forecast_frame
from src.ml.train_baseline_model import FEATURE_COLUMNS, split_training_slice


def _training_slice(service_dates: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "service_date": pd.to_datetime(service_dates),
            "pickup_zone_id": [100] * len(service_dates),
            "observed_demand": [10.0 + index for index, _ in enumerate(service_dates)],
            "day_of_week": [0] * len(service_dates),
            "day_of_month": list(range(1, len(service_dates) + 1)),
            "month": [1] * len(service_dates),
            "is_weekend": [0] * len(service_dates),
            "feature_window_id": ["2024-01_to_2024-01"] * len(service_dates),
        }
    )


def test_split_training_slice_uses_same_day_fallback_for_single_date() -> None:
    training_slice = _training_slice(["2024-01-01", "2024-01-01"])

    result = split_training_slice(training_slice)

    assert result.split_strategy == "same_day_fallback"
    assert result.holdout_days == 0
    assert len(result.train_frame) == len(training_slice)
    assert len(result.evaluation_frame) == len(training_slice)


def test_split_training_slice_uses_time_holdout_for_multiple_dates() -> None:
    training_slice = _training_slice(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"])

    result = split_training_slice(training_slice, holdout_days=1)

    assert result.split_strategy == "time_holdout"
    assert result.holdout_days == 1
    assert result.train_frame["service_date"].max() < result.evaluation_frame["service_date"].min()


def test_generate_forecast_frame_clips_negative_predictions_and_keeps_run_id() -> None:
    class StubModel:
        def predict(self, frame):
            assert list(frame.columns) == FEATURE_COLUMNS
            return [-5.0, 3.5]

    evaluation_frame = _training_slice(["2024-01-10", "2024-01-11"])
    forecast = generate_forecast_frame(StubModel(), evaluation_frame, run_id="manual__ml")

    assert forecast["predicted_demand"].tolist() == [0.0, 3.5]
    assert forecast["run_id"].tolist() == ["manual__ml", "manual__ml"]


def test_evaluate_forecast_rejects_empty_frame_and_handles_non_positive_mape() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        evaluate_forecast(pd.DataFrame(), split_strategy="time_holdout", holdout_days=1)

    observed = pd.Series([10.0, 0.0])
    predicted = pd.Series([8.0, 1.0])
    assert calculate_mape_if_applicable(observed, predicted) is None
