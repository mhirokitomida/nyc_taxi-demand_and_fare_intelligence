from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.common.logging_utils import get_logger
from src.common.read_gold_artifacts import read_gold_table


logger = get_logger(__name__)

REQUIRED_GOLD_INPUT_COLUMNS = [
    "service_date",
    "pickup_zone_id",
    "trip_count",
]

REQUIRED_TRAINING_COLUMNS = [
    "service_date",
    "pickup_zone_id",
    "observed_demand",
    "day_of_week",
    "day_of_month",
    "month",
    "is_weekend",
    "feature_window_id",
]


def build_training_slice_from_frame(gold_frame: pd.DataFrame, feature_window_id: str) -> pd.DataFrame:
    missing = [column for column in REQUIRED_GOLD_INPUT_COLUMNS if column not in gold_frame.columns]
    if missing:
        raise ValueError(f"Gold frame is missing required ML input columns: {missing}")

    training_slice = gold_frame.copy()
    training_slice["service_date"] = pd.to_datetime(training_slice["service_date"])
    training_slice["pickup_zone_id"] = training_slice["pickup_zone_id"].astype(int)
    training_slice["observed_demand"] = training_slice["trip_count"].astype(float)
    training_slice["day_of_week"] = training_slice["service_date"].dt.dayofweek
    training_slice["day_of_month"] = training_slice["service_date"].dt.day
    training_slice["month"] = training_slice["service_date"].dt.month
    training_slice["is_weekend"] = training_slice["day_of_week"].isin([5, 6]).astype(int)
    training_slice["feature_window_id"] = feature_window_id

    training_slice = training_slice.sort_values(["service_date", "pickup_zone_id"]).reset_index(drop=True)
    return training_slice[REQUIRED_TRAINING_COLUMNS]


def build_training_slice(start_month: str, end_month: str, data_root: Path | None = None) -> pd.DataFrame:
    feature_window_id = f"{start_month}_to_{end_month}"
    logger.info("Building ML training slice from gold window %s", feature_window_id)
    gold_table = read_gold_table(start_month=start_month, end_month=end_month, data_root=data_root)
    gold_frame = gold_table.to_pandas()
    return build_training_slice_from_frame(gold_frame=gold_frame, feature_window_id=feature_window_id)
