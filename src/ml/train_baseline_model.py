from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.common.logging_utils import get_logger


logger = get_logger(__name__)

MODEL_NAME = "linear_regression_zone_day_baseline"
FEATURE_COLUMNS = [
    "pickup_zone_id",
    "day_of_week",
    "day_of_month",
    "month",
    "is_weekend",
]


@dataclass(frozen=True)
class SplitResult:
    train_frame: pd.DataFrame
    evaluation_frame: pd.DataFrame
    holdout_days: int
    split_strategy: str


def split_training_slice(training_slice: pd.DataFrame, holdout_days: int | None = None) -> SplitResult:
    unique_dates = sorted(training_slice["service_date"].dt.normalize().unique())
    if len(unique_dates) == 1:
        logger.warning("Using same-day fallback for ML evaluation because only one service date is available")
        return SplitResult(
            train_frame=training_slice.copy(),
            evaluation_frame=training_slice.copy(),
            holdout_days=0,
            split_strategy="same_day_fallback",
        )

    inferred_holdout_days = min(7, max(1, len(unique_dates) // 4))
    effective_holdout_days = holdout_days or inferred_holdout_days
    effective_holdout_days = min(effective_holdout_days, len(unique_dates) - 1)
    holdout_dates = set(unique_dates[-effective_holdout_days:])

    train_frame = training_slice[~training_slice["service_date"].dt.normalize().isin(holdout_dates)].copy()
    evaluation_frame = training_slice[training_slice["service_date"].dt.normalize().isin(holdout_dates)].copy()

    return SplitResult(
        train_frame=train_frame.reset_index(drop=True),
        evaluation_frame=evaluation_frame.reset_index(drop=True),
        holdout_days=effective_holdout_days,
        split_strategy="time_holdout",
    )


def build_baseline_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                ["pickup_zone_id", "day_of_week", "is_weekend"],
            ),
            ("numeric", "passthrough", ["day_of_month", "month"]),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LinearRegression()),
        ]
    )


def train_baseline_model(train_frame: pd.DataFrame) -> Pipeline:
    if train_frame.empty:
        raise ValueError("Training frame must not be empty")

    logger.info("Training ML baseline on %s rows", len(train_frame))
    model = build_baseline_pipeline()
    model.fit(train_frame[FEATURE_COLUMNS], train_frame["observed_demand"])
    return model
