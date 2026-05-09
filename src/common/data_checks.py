from __future__ import annotations

from collections.abc import Iterable, Mapping


def require_columns(columns: Iterable[str], required: Iterable[str]) -> list[str]:
    present = set(columns)
    return [column for column in required if column not in present]


def find_negative_values(record: Mapping[str, float | int], fields: Iterable[str]) -> list[str]:
    invalid_fields: list[str] = []
    for field in fields:
        value = record.get(field)
        if value is None:
            continue
        if value < 0:
            invalid_fields.append(field)
    return invalid_fields
