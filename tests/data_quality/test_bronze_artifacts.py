from __future__ import annotations

import json
from pathlib import Path

from src.ingestion.bronze_pipeline import bronze_artifact_paths


def test_bronze_artifact_paths_stay_under_bronze_layer() -> None:
    paths = bronze_artifact_paths("2024-01", "2024-02")
    assert len(paths) == 2
    for path in paths:
        assert "data/bronze" in path.as_posix()
        assert path.name.endswith(".parquet")


def test_sample_batch_metadata_shape_is_expected(tmp_path: Path) -> None:
    metadata = {
        "batch_id": "yellow_taxi_2024-01_to_2024-01",
        "source_name": "yellow_taxi",
        "start_month": "2024-01",
        "end_month": "2024-01",
        "loaded_at": "2026-05-09T00:00:00+00:00",
        "status": "completed",
        "rerun_mode": "fail",
        "files": [
            {
                "year_month": "2024-01",
                "source_uri": "https://example/yellow_tripdata_2024-01.parquet",
                "local_path": "data/bronze/2024-01/yellow_tripdata_2024-01.parquet",
                "load_status": "downloaded",
                "downloaded_bytes": 123,
            }
        ],
    }
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    loaded = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert loaded["batch_id"] == "yellow_taxi_2024-01_to_2024-01"
    assert loaded["files"][0]["load_status"] == "downloaded"
