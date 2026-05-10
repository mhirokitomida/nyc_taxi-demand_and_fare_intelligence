from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.common.lakehouse_manifests import ensure_rerun_allowed, run_output_path, write_manifest
from src.common.logging_utils import get_logger
from src.common.paths import get_data_paths


logger = get_logger(__name__)


@dataclass(frozen=True)
class MLOutputPaths:
    output_dir: Path
    manifest_path: Path
    training_slice_path: Path
    predictions_path: Path
    metrics_path: Path
    metadata_path: Path


def ml_output_dir(start_month: str, end_month: str, data_root: Path | None = None) -> Path:
    root = data_root or get_data_paths().root
    return root / "ml" / f"{start_month}_to_{end_month}"


def write_ml_outputs(
    training_slice: pd.DataFrame,
    predictions: pd.DataFrame,
    metrics: dict[str, float | int | str | None],
    start_month: str,
    end_month: str,
    run_id: str | None = None,
    rerun_mode: str = "fail",
    source_paths: list[str] | None = None,
    data_root: Path | None = None,
) -> MLOutputPaths:
    ensure_rerun_allowed(
        layer="ml",
        start_month=start_month,
        end_month=end_month,
        rerun_mode=rerun_mode,
        data_root=data_root,
    )
    output_dir = run_output_path(
        layer="ml",
        start_month=start_month,
        end_month=end_month,
        run_id=run_id or str(metrics["run_id"]),
        data_root=data_root,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    training_slice_path = output_dir / "training_slice.parquet"
    predictions_path = output_dir / "forecast_predictions.parquet"
    metrics_path = output_dir / "evaluation_metrics.json"
    metadata_path = output_dir / "run_metadata.json"

    logger.info("Writing ML artifacts to %s", output_dir)
    training_slice.to_parquet(training_slice_path, index=False)
    predictions.to_parquet(predictions_path, index=False)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(UTC).isoformat(),
                "start_month": start_month,
                "end_month": end_month,
                "run_id": run_id or metrics["run_id"],
                "model_name": metrics["model_name"],
                "training_rows": int(len(training_slice)),
                "prediction_rows": int(len(predictions)),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    manifest_path = write_manifest(
        layer="ml",
        start_month=start_month,
        end_month=end_month,
        latest_run_id=run_id or str(metrics["run_id"]),
        latest_path=output_dir,
        status="completed",
        row_count=int(len(predictions)),
        source_paths=source_paths,
        data_root=data_root,
    )

    return MLOutputPaths(
        output_dir=output_dir,
        manifest_path=manifest_path,
        training_slice_path=training_slice_path,
        predictions_path=predictions_path,
        metrics_path=metrics_path,
        metadata_path=metadata_path,
    )
