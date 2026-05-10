from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from src.common.paths import get_data_paths


RERUN_MODES = {"fail", "replace"}
SAFE_RUN_ID_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class LayerManifest:
    layer: str
    period_id: str
    latest_run_id: str
    latest_path: str
    created_at: str
    status: str
    row_count: int | None = None
    source_paths: list[str] | None = None


def period_id_for(start_month: str, end_month: str) -> str:
    return f"{start_month}_to_{end_month}"


def layer_period_dir(layer: str, start_month: str, end_month: str, data_root: Path | None = None) -> Path:
    root = data_root or get_data_paths().root
    return root / layer / period_id_for(start_month=start_month, end_month=end_month)


def manifest_path_for(layer: str, start_month: str, end_month: str, data_root: Path | None = None) -> Path:
    return layer_period_dir(layer=layer, start_month=start_month, end_month=end_month, data_root=data_root) / "_manifest.json"


def sanitize_run_id(run_id: str | None) -> str:
    if run_id is None or not str(run_id).strip():
        run_id = datetime.now(UTC).strftime("manual__%Y%m%dT%H%M%S")
    safe = SAFE_RUN_ID_PATTERN.sub("_", str(run_id).strip())
    return safe.strip("._-") or datetime.now(UTC).strftime("run_%Y%m%dT%H%M%S")


def read_manifest(layer: str, start_month: str, end_month: str, data_root: Path | None = None) -> LayerManifest | None:
    path = manifest_path_for(layer=layer, start_month=start_month, end_month=end_month, data_root=data_root)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    required_fields = {"layer", "period_id", "latest_run_id", "latest_path", "created_at", "status"}
    if not required_fields.issubset(payload):
        return None
    return LayerManifest(**payload)


def latest_manifest_path(layer: str, start_month: str, end_month: str, data_root: Path | None = None) -> Path | None:
    manifest = read_manifest(layer=layer, start_month=start_month, end_month=end_month, data_root=data_root)
    if manifest is None:
        return None
    root = data_root or get_data_paths().root
    stored_path = manifest.latest_path.replace("\\", "/")
    if stored_path.startswith("/opt/airflow/data/"):
        return root / Path(stored_path.removeprefix("/opt/airflow/data/"))

    candidate = Path(manifest.latest_path)
    if candidate.exists():
        return candidate
    if candidate.is_absolute():
        return candidate
    return root / candidate


def run_output_path(
    layer: str,
    start_month: str,
    end_month: str,
    run_id: str | None,
    data_root: Path | None = None,
) -> Path:
    period_dir = layer_period_dir(layer=layer, start_month=start_month, end_month=end_month, data_root=data_root)
    return period_dir / "runs" / sanitize_run_id(run_id)


def resolve_latest_layer_path(layer: str, start_month: str, end_month: str, data_root: Path | None = None) -> Path:
    manifest_latest = latest_manifest_path(layer=layer, start_month=start_month, end_month=end_month, data_root=data_root)
    if manifest_latest is not None:
        if not manifest_latest.exists():
            raise FileNotFoundError(f"Manifest latest_path does not exist for {layer}: {manifest_latest}")
        return manifest_latest

    period_dir = layer_period_dir(layer=layer, start_month=start_month, end_month=end_month, data_root=data_root)
    if not period_dir.exists():
        raise FileNotFoundError(f"{layer.title()} period path does not exist: {period_dir}")
    return period_dir


def ensure_rerun_allowed(layer: str, start_month: str, end_month: str, rerun_mode: str, data_root: Path | None = None) -> None:
    if rerun_mode not in RERUN_MODES:
        raise ValueError(f"Unsupported rerun_mode: {rerun_mode!r}")

    manifest = read_manifest(layer=layer, start_month=start_month, end_month=end_month, data_root=data_root)
    if rerun_mode == "fail" and manifest is not None and manifest.status == "completed":
        raise FileExistsError(
            f"{layer.title()} manifest already exists for {manifest.period_id}. Use rerun_mode='replace' to create a new run."
        )


def write_manifest(
    layer: str,
    start_month: str,
    end_month: str,
    latest_run_id: str,
    latest_path: Path,
    status: str,
    row_count: int | None = None,
    source_paths: list[str] | None = None,
    data_root: Path | None = None,
) -> Path:
    root = data_root or get_data_paths().root
    try:
        stored_latest_path = latest_path.relative_to(root).as_posix()
    except ValueError:
        stored_latest_path = str(latest_path)

    manifest = LayerManifest(
        layer=layer,
        period_id=period_id_for(start_month=start_month, end_month=end_month),
        latest_run_id=sanitize_run_id(latest_run_id),
        latest_path=stored_latest_path,
        created_at=datetime.now(UTC).isoformat(),
        status=status,
        row_count=row_count,
        source_paths=source_paths,
    )
    manifest_path = manifest_path_for(layer=layer, start_month=start_month, end_month=end_month, data_root=data_root)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")
    return manifest_path
