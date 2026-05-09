from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.common.settings import get_settings


@dataclass(frozen=True)
class DataPaths:
    root: Path
    bronze: Path
    silver: Path
    gold: Path
    ml: Path


def get_data_paths() -> DataPaths:
    settings = get_settings()
    root = settings.data_root
    return DataPaths(
        root=root,
        bronze=root / "bronze",
        silver=root / "silver",
        gold=root / "gold",
        ml=root / "ml",
    )
