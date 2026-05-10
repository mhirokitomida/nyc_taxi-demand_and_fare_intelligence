from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.common.lakehouse_manifests import (
    ensure_rerun_allowed,
    resolve_latest_layer_path,
    run_output_path,
    sanitize_run_id,
    write_manifest,
)


def test_sanitize_run_id_replaces_unsafe_path_characters() -> None:
    assert sanitize_run_id("manual__2026-05-09T10:20:30+00:00") == "manual__2026-05-09T10_20_30_00_00"


def test_manifest_points_to_latest_versioned_run_path(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    latest_path = run_output_path("gold", "2024-01", "2024-01", "manual:run/1", data_root=data_root)
    latest_path.mkdir(parents=True, exist_ok=True)

    manifest_path = write_manifest(
        layer="gold",
        start_month="2024-01",
        end_month="2024-01",
        latest_run_id="manual:run/1",
        latest_path=latest_path,
        status="completed",
        row_count=10,
        source_paths=["/tmp/source"],
        data_root=data_root,
    )

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["latest_run_id"] == "manual_run_1"
    assert payload["latest_path"] == "gold/2024-01_to_2024-01/runs/manual_run_1"
    assert resolve_latest_layer_path("gold", "2024-01", "2024-01", data_root=data_root) == latest_path


def test_rerun_mode_fail_blocks_when_completed_manifest_exists(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    latest_path = run_output_path("silver", "2024-01", "2024-01", "run-1", data_root=data_root)
    latest_path.mkdir(parents=True, exist_ok=True)
    write_manifest(
        layer="silver",
        start_month="2024-01",
        end_month="2024-01",
        latest_run_id="run-1",
        latest_path=latest_path,
        status="completed",
        data_root=data_root,
    )

    with pytest.raises(FileExistsError):
        ensure_rerun_allowed("silver", "2024-01", "2024-01", "fail", data_root=data_root)
