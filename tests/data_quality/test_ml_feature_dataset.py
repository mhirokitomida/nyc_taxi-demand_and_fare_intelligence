from __future__ import annotations

import pandas as pd

from src.ml.build_training_slice import REQUIRED_TRAINING_COLUMNS, build_training_slice_from_frame


def test_build_training_slice_from_gold_frame_creates_expected_ml_columns() -> None:
    gold_frame = pd.DataFrame(
        {
            "service_date": ["2024-01-01", "2024-01-02"],
            "pickup_zone_id": [100, 101],
            "trip_count": [12, 18],
            "total_fare": [100.0, 120.0],
        }
    )

    training_slice = build_training_slice_from_frame(gold_frame=gold_frame, feature_window_id="2024-01_to_2024-01")

    assert list(training_slice.columns) == REQUIRED_TRAINING_COLUMNS
    assert training_slice["observed_demand"].tolist() == [12.0, 18.0]
    assert training_slice["pickup_zone_id"].tolist() == [100, 101]
    assert training_slice["feature_window_id"].nunique() == 1
    assert (training_slice["observed_demand"] >= 0).all()
