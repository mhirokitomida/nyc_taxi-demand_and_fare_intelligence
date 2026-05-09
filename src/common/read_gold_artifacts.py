from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.common.paths import get_data_paths
from src.processing.write_gold import gold_output_path


def get_gold_dataset_path(start_month: str, end_month: str, data_root: Path | None = None) -> Path:
    return gold_output_path(start_month=start_month, end_month=end_month, data_root=data_root)


def list_gold_artifact_files(start_month: str, end_month: str, data_root: Path | None = None) -> list[Path]:
    dataset_path = get_gold_dataset_path(start_month=start_month, end_month=end_month, data_root=data_root)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Gold dataset path does not exist: {dataset_path}")
    files = sorted(dataset_path.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet artifacts were found in gold dataset path: {dataset_path}")
    return files


def read_gold_table(start_month: str, end_month: str, data_root: Path | None = None) -> pa.Table:
    dataset_path = get_gold_dataset_path(start_month=start_month, end_month=end_month, data_root=data_root)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Gold dataset path does not exist: {dataset_path}")
    return pq.read_table(dataset_path)


def read_gold_records(start_month: str, end_month: str, data_root: Path | None = None) -> list[dict]:
    return read_gold_table(start_month=start_month, end_month=end_month, data_root=data_root).to_pylist()


def default_gold_records() -> list[dict]:
    root = get_data_paths().root
    return read_gold_records(start_month="2024-01", end_month="2024-01", data_root=root)
