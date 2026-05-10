from __future__ import annotations

import json
from pathlib import Path

import pyarrow.dataset as ds
import pyarrow.parquet as pq
import pytest

from src.common.lakehouse_manifests import read_manifest, resolve_latest_layer_path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
BRONZE_METADATA = DATA_ROOT / "bronze" / "_batch_metadata" / "yellow_taxi_2024-01_to_2024-01.json"


def _bronze_row_count() -> int:
    if not BRONZE_METADATA.exists():
        pytest.skip("Local bronze batch metadata is not available for row count sanity validation")

    metadata = json.loads(BRONZE_METADATA.read_text(encoding="utf-8"))
    total_rows = 0
    for item in metadata["files"]:
        file_path = Path(item["local_path"])
        normalized = item["local_path"].replace("\\", "/")
        if normalized.startswith("/opt/airflow/data/"):
            file_path = DATA_ROOT / Path(normalized.removeprefix("/opt/airflow/data/"))
        if not file_path.is_absolute():
            file_path = PROJECT_ROOT / file_path
        if not file_path.exists():
            pytest.skip(f"Bronze source file is missing for row count sanity validation: {file_path}")
        total_rows += pq.ParquetFile(file_path).metadata.num_rows
    return int(total_rows)


def _latest_layer_row_count(layer: str) -> tuple[int, int | None]:
    manifest = read_manifest(layer, "2024-01", "2024-01", data_root=DATA_ROOT)
    if manifest is None:
        pytest.skip(f"Local {layer} manifest is not available for row count sanity validation")
    latest_path = resolve_latest_layer_path(layer, "2024-01", "2024-01", data_root=DATA_ROOT)
    return int(ds.dataset(latest_path, format="parquet").count_rows()), manifest.row_count


def test_row_count_sanity_across_bronze_silver_and_gold() -> None:
    bronze_rows = _bronze_row_count()
    silver_rows, silver_manifest_rows = _latest_layer_row_count("silver")
    gold_rows, gold_manifest_rows = _latest_layer_row_count("gold")

    assert bronze_rows > 0
    assert silver_rows > 0
    assert gold_rows > 0
    assert bronze_rows >= silver_rows >= gold_rows
    if silver_manifest_rows is not None:
        assert silver_manifest_rows == silver_rows
    if gold_manifest_rows is not None:
        assert gold_manifest_rows == gold_rows
