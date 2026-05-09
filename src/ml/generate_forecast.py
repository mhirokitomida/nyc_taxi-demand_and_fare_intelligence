from __future__ import annotations

from uuid import uuid4

import pandas as pd

from src.ml.train_baseline_model import FEATURE_COLUMNS, MODEL_NAME


def generate_forecast_frame(model, evaluation_frame: pd.DataFrame, run_id: str | None = None) -> pd.DataFrame:
    if evaluation_frame.empty:
        raise ValueError("Evaluation frame must not be empty")

    resolved_run_id = run_id or uuid4().hex
    predictions = model.predict(evaluation_frame[FEATURE_COLUMNS])
    prediction_frame = pd.DataFrame(
        {
            "forecast_date": pd.to_datetime(evaluation_frame["service_date"]).dt.date,
            "pickup_zone_id": evaluation_frame["pickup_zone_id"].astype(int),
            "predicted_demand": pd.Series(predictions).clip(lower=0.0),
            "observed_demand": evaluation_frame["observed_demand"].astype(float),
            "model_name": MODEL_NAME,
            "run_id": resolved_run_id,
        }
    )
    return prediction_frame
