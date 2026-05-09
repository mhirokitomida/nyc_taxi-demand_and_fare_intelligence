from __future__ import annotations

import math
from collections.abc import Iterable

import pyarrow as pa

from src.common.data_checks import require_columns
from src.processing.build_gold_daily_zone import REQUIRED_GOLD_COLUMNS


CRITICAL_GOLD_COLUMNS = ["service_date", "pickup_zone_id", "trip_count"]
NON_NEGATIVE_GOLD_COLUMNS = [
    "trip_count",
    "total_fare",
    "avg_fare",
    "total_distance",
    "avg_distance",
    "avg_duration_minutes",
]


def missing_gold_columns(columns: Iterable[str]) -> list[str]:
    return require_columns(columns, REQUIRED_GOLD_COLUMNS)


def validate_gold_table(table: pa.Table) -> None:
    missing = missing_gold_columns(table.column_names)
    if missing:
        raise ValueError(f"Gold dataset is missing required columns: {missing}")

    if table.num_rows <= 0:
        raise ValueError("Gold dataset must contain at least one row")

    for column_name in CRITICAL_GOLD_COLUMNS:
        column = table.column(column_name)
        if column.null_count > 0:
            raise ValueError(f"Gold dataset contains nulls in critical column: {column_name}")

    for column_name in NON_NEGATIVE_GOLD_COLUMNS:
        values = table.column(column_name).to_pylist()
        for value in values:
            if value is None:
                raise ValueError(f"Gold dataset contains nulls in non-negative metric column: {column_name}")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"Gold dataset contains non-finite values in metric column: {column_name}")
            if value < 0:
                raise ValueError(f"Gold dataset contains negative values in metric column: {column_name}")


def validate_gold_records(records: list[dict]) -> None:
    validate_gold_table(pa.Table.from_pylist(records))
