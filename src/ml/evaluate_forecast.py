from __future__ import annotations

from math import sqrt

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_mape_if_applicable(observed: pd.Series, predicted: pd.Series) -> float | None:
    if (observed <= 0).any():
        return None
    absolute_percentage_errors = ((observed - predicted).abs() / observed).mean()
    return float(absolute_percentage_errors * 100.0)


def evaluate_forecast(
    prediction_frame: pd.DataFrame,
    split_strategy: str,
    holdout_days: int,
) -> dict[str, float | int | str | None]:
    if prediction_frame.empty:
        raise ValueError("Prediction frame must not be empty")

    observed = prediction_frame["observed_demand"].astype(float)
    predicted = prediction_frame["predicted_demand"].astype(float)

    return {
        "run_id": str(prediction_frame["run_id"].iloc[0]),
        "model_name": str(prediction_frame["model_name"].iloc[0]),
        "evaluation_window": (
            f"{prediction_frame['forecast_date'].min()}_to_{prediction_frame['forecast_date'].max()}"
        ),
        "split_strategy": split_strategy,
        "holdout_days": holdout_days,
        "prediction_rows": int(len(prediction_frame)),
        "mae": float(mean_absolute_error(observed, predicted)),
        "rmse": float(sqrt(mean_squared_error(observed, predicted))),
        "mape_if_applicable": calculate_mape_if_applicable(observed, predicted),
    }
