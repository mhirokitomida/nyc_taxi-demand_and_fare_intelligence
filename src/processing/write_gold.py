from __future__ import annotations

from pathlib import Path

from src.common.logging_utils import get_logger
from src.common.paths import get_data_paths


logger = get_logger(__name__)


def gold_output_path(start_month: str, end_month: str, data_root: Path | None = None) -> Path:
    root = data_root or get_data_paths().root
    return root / "gold" / f"{start_month}_to_{end_month}"


def write_gold(dataframe, start_month: str, end_month: str, mode: str = "overwrite", data_root: Path | None = None) -> Path:
    target = gold_output_path(start_month=start_month, end_month=end_month, data_root=data_root)
    logger.info("Writing gold output to %s", target)
    dataframe.write.mode(mode).parquet(str(target))
    return target
