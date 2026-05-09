from __future__ import annotations

from dataclasses import dataclass
from datetime import date


def _parse_year_month(value: str) -> tuple[int, int]:
    parts = value.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid year-month value: {value!r}")
    year = int(parts[0])
    month = int(parts[1])
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month in year-month value: {value!r}")
    return year, month


def _month_index(year: int, month: int) -> int:
    return year * 12 + month


@dataclass(frozen=True)
class IngestionPeriod:
    start_month: str
    end_month: str

    def __post_init__(self) -> None:
        start_year, start_num = _parse_year_month(self.start_month)
        end_year, end_num = _parse_year_month(self.end_month)

        if _month_index(start_year, start_num) > _month_index(end_year, end_num):
            raise ValueError("start_month must be earlier than or equal to end_month")

        month_span = (_month_index(end_year, end_num) - _month_index(start_year, start_num)) + 1
        if month_span < 1:
            raise ValueError("Ingestion period must include at least one month")
        if month_span > 12:
            raise ValueError("Ingestion period must not exceed 12 months for the MVP")

    @property
    def month_count(self) -> int:
        start_year, start_num = _parse_year_month(self.start_month)
        end_year, end_num = _parse_year_month(self.end_month)
        return (_month_index(end_year, end_num) - _month_index(start_year, start_num)) + 1

    @property
    def batch_id(self) -> str:
        return f"yellow_taxi_{self.start_month}_to_{self.end_month}"

    def iter_months(self) -> list[str]:
        start_year, start_num = _parse_year_month(self.start_month)
        end_year, end_num = _parse_year_month(self.end_month)
        values: list[str] = []
        year = start_year
        month = start_num
        while _month_index(year, month) <= _month_index(end_year, end_num):
            values.append(f"{year:04d}-{month:02d}")
            month += 1
            if month == 13:
                month = 1
                year += 1
        return values


def default_validation_period() -> IngestionPeriod:
    today = date.today()
    month = max(1, today.month - 1)
    return IngestionPeriod(
        start_month=f"{today.year:04d}-{month:02d}",
        end_month=f"{today.year:04d}-{month:02d}",
    )
