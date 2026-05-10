from __future__ import annotations

from pathlib import Path

import pytest

from src.common.lakehouse_manifests import read_manifest, resolve_latest_layer_path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
PERIOD_ID = "2024-01_to_2024-01"
BRONZE_FILE = DATA_ROOT / "bronze" / "2024-01" / "yellow_tripdata_2024-01.parquet"
BRONZE_METADATA = DATA_ROOT / "bronze" / "_batch_metadata" / "yellow_taxi_2024-01_to_2024-01.json"


def _require_real_local_artifacts() -> None:
    if not BRONZE_FILE.exists():
        pytest.skip("Local bronze artifact is not available for layer presence validation")
    if not BRONZE_METADATA.exists():
        pytest.skip("Local bronze batch metadata is not available for layer presence validation")


def test_bronze_layer_presence_for_local_validation_window() -> None:
    _require_real_local_artifacts()

    assert BRONZE_FILE.exists()
    assert BRONZE_METADATA.exists()


@pytest.mark.parametrize("layer", ["silver", "gold", "ml"])
def test_manifest_and_latest_path_exist_for_versioned_layers(layer: str) -> None:
    _require_real_local_artifacts()

    manifest = read_manifest(layer, "2024-01", "2024-01", data_root=DATA_ROOT)
    if manifest is None:
        pytest.skip(f"Local {layer} manifest is not available for layer presence validation")

    latest_path = resolve_latest_layer_path(layer, "2024-01", "2024-01", data_root=DATA_ROOT)
    assert manifest.period_id == PERIOD_ID
    assert latest_path.exists()
    assert latest_path.is_dir()
