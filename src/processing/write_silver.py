from __future__ import annotations

from pathlib import Path

from src.common.lakehouse_manifests import ensure_rerun_allowed, run_output_path, write_manifest
from src.common.logging_utils import get_logger
from src.common.paths import get_data_paths


logger = get_logger(__name__)


def silver_output_path(start_month: str, end_month: str, data_root: Path | None = None) -> Path:
    root = data_root or get_data_paths().root
    return root / "silver" / f"{start_month}_to_{end_month}"


def write_silver(
    dataframe,
    start_month: str,
    end_month: str,
    run_id: str | None,
    rerun_mode: str = "fail",
    row_count: int | None = None,
    source_paths: list[str] | None = None,
    data_root: Path | None = None,
) -> tuple[Path, Path]:
    ensure_rerun_allowed(
        layer="silver",
        start_month=start_month,
        end_month=end_month,
        rerun_mode=rerun_mode,
        data_root=data_root,
    )
    target = run_output_path(
        layer="silver",
        start_month=start_month,
        end_month=end_month,
        run_id=run_id,
        data_root=data_root,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Writing silver output to %s", target)
    dataframe.write.mode("errorifexists").parquet(str(target))
    manifest_path = write_manifest(
        layer="silver",
        start_month=start_month,
        end_month=end_month,
        latest_run_id=run_id or target.name,
        latest_path=target,
        status="completed",
        row_count=row_count,
        source_paths=source_paths,
        data_root=data_root,
    )
    return target, manifest_path
