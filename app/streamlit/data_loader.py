from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.common.lakehouse_manifests import latest_manifest_path, read_manifest, resolve_latest_layer_path
from src.common.paths import get_data_paths


@dataclass(frozen=True)
class DashboardPeriod:
    label: str
    start_month: str
    end_month: str


@dataclass(frozen=True)
class MLArtifactStatus:
    state: str
    message: str


@dataclass(frozen=True)
class DashboardArtifacts:
    period: DashboardPeriod
    gold_frame: pd.DataFrame
    ml_predictions: pd.DataFrame | None
    ml_metrics: dict | None
    ml_status: MLArtifactStatus


def _parse_period_label(label: str) -> DashboardPeriod:
    start_month, end_month = label.split("_to_")
    return DashboardPeriod(label=label, start_month=start_month, end_month=end_month)


def list_gold_periods(data_root: Path | None = None) -> list[DashboardPeriod]:
    root = (data_root or get_data_paths().root) / "gold"
    periods = [entry.name for entry in root.iterdir() if entry.is_dir() and "_to_" in entry.name] if root.exists() else []
    return [_parse_period_label(label) for label in sorted(periods)]


def list_ml_periods(data_root: Path | None = None) -> list[str]:
    root = (data_root or get_data_paths().root) / "ml"
    return sorted(entry.name for entry in root.iterdir() if entry.is_dir() and "_to_" in entry.name) if root.exists() else []


def resolve_dashboard_period(requested_period: str | None = None, data_root: Path | None = None) -> DashboardPeriod:
    periods = list_gold_periods(data_root=data_root)
    if not periods:
        raise FileNotFoundError("No gold periods are available for the dashboard")
    if requested_period is None:
        return periods[-1]
    for period in periods:
        if period.label == requested_period:
            return period
    raise FileNotFoundError(f"Requested gold period was not found: {requested_period}")


def load_gold_frame(period: DashboardPeriod, data_root: Path | None = None) -> pd.DataFrame:
    dataset_path = resolve_latest_layer_path(
        layer="gold",
        start_month=period.start_month,
        end_month=period.end_month,
        data_root=data_root,
    )
    return pd.read_parquet(dataset_path)


def load_ml_artifacts(period: DashboardPeriod, data_root: Path | None = None) -> tuple[pd.DataFrame | None, dict | None, MLArtifactStatus]:
    root = data_root or get_data_paths().root
    requested_ml_dir = root / "ml" / period.label
    available_ml_periods = list_ml_periods(data_root=root)

    if not requested_ml_dir.exists():
        if available_ml_periods:
            return None, None, MLArtifactStatus(
                state="stale",
                message=f"No ML artifacts were found for {period.label}. Available ML periods: {', '.join(available_ml_periods)}",
            )
        return None, None, MLArtifactStatus(
            state="missing",
            message=f"No ML artifacts were found for {period.label}. Run the ML pipeline to enable predictive views.",
        )

    manifest = read_manifest(layer="ml", start_month=period.start_month, end_month=period.end_month, data_root=root)
    artifact_dir = (
        latest_manifest_path(layer="ml", start_month=period.start_month, end_month=period.end_month, data_root=root)
        if manifest is not None
        else requested_ml_dir
    )
    if artifact_dir is None:
        artifact_dir = requested_ml_dir

    predictions_path = artifact_dir / "forecast_predictions.parquet"
    metrics_path = artifact_dir / "evaluation_metrics.json"
    if not predictions_path.exists() or not metrics_path.exists():
        return None, None, MLArtifactStatus(
            state="incomplete",
            message=f"ML artifacts for {period.label} are incomplete. Expected forecast_predictions.parquet and evaluation_metrics.json.",
        )

    predictions = pd.read_parquet(predictions_path)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    metrics_run_id = metrics.get("run_id")
    prediction_run_ids = set(predictions["run_id"].astype(str).unique()) if "run_id" in predictions.columns else set()
    if metrics_run_id and prediction_run_ids and metrics_run_id not in prediction_run_ids:
        return predictions, metrics, MLArtifactStatus(
            state="stale",
            message=f"ML artifacts for {period.label} have inconsistent run ids between predictions and metrics.",
        )

    return predictions, metrics, MLArtifactStatus(
        state="ready",
        message=f"ML artifacts for {period.label} are ready for dashboard consumption.",
    )


def load_dashboard_artifacts(requested_period: str | None = None, data_root: Path | None = None) -> DashboardArtifacts:
    period = resolve_dashboard_period(requested_period=requested_period, data_root=data_root)
    gold_frame = load_gold_frame(period=period, data_root=data_root)
    ml_predictions, ml_metrics, ml_status = load_ml_artifacts(period=period, data_root=data_root)
    return DashboardArtifacts(
        period=period,
        gold_frame=gold_frame,
        ml_predictions=ml_predictions,
        ml_metrics=ml_metrics,
        ml_status=ml_status,
    )
