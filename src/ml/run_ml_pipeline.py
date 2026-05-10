from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.common.lakehouse_manifests import resolve_latest_layer_path
from src.common.logging_utils import get_logger
from src.ml.build_training_slice import build_training_slice
from src.ml.evaluate_forecast import evaluate_forecast
from src.ml.generate_forecast import generate_forecast_frame
from src.ml.train_baseline_model import split_training_slice, train_baseline_model
from src.ml.write_ml_outputs import MLOutputPaths, write_ml_outputs


logger = get_logger(__name__)


@dataclass(frozen=True)
class MLRunResult:
    artifact_paths: MLOutputPaths
    metrics: dict[str, float | int | str | None]


def run_ml_pipeline(
    start_month: str,
    end_month: str,
    data_root: Path | None = None,
    holdout_days: int | None = None,
    rerun_mode: str = "fail",
    run_id: str | None = None,
) -> MLRunResult:
    training_slice = build_training_slice(start_month=start_month, end_month=end_month, data_root=data_root)
    split_result = split_training_slice(training_slice=training_slice, holdout_days=holdout_days)

    logger.info(
        "Running ML pipeline with split_strategy=%s holdout_days=%s",
        split_result.split_strategy,
        split_result.holdout_days,
    )

    model = train_baseline_model(split_result.train_frame)
    predictions = generate_forecast_frame(model=model, evaluation_frame=split_result.evaluation_frame, run_id=run_id)
    metrics = evaluate_forecast(
        prediction_frame=predictions,
        split_strategy=split_result.split_strategy,
        holdout_days=split_result.holdout_days,
    )
    artifact_paths = write_ml_outputs(
        training_slice=training_slice,
        predictions=predictions,
        metrics=metrics,
        start_month=start_month,
        end_month=end_month,
        run_id=run_id,
        rerun_mode=rerun_mode,
        source_paths=[
            str(
                resolve_latest_layer_path(
                    layer="gold",
                    start_month=start_month,
                    end_month=end_month,
                    data_root=data_root,
                )
            )
        ],
        data_root=data_root,
    )
    return MLRunResult(artifact_paths=artifact_paths, metrics=metrics)
