from __future__ import annotations

from dataclasses import dataclass

from src.ingestion.period_config import IngestionPeriod


BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DATASET_NAME = "yellow_taxi"


@dataclass(frozen=True)
class SourceFile:
    dataset: str
    year_month: str
    filename: str
    source_uri: str
    local_relative_path: str


def build_yellow_taxi_source(year_month: str) -> SourceFile:
    filename = f"yellow_tripdata_{year_month}.parquet"
    return SourceFile(
        dataset=DATASET_NAME,
        year_month=year_month,
        filename=filename,
        source_uri=f"{BASE_URL}/{filename}",
        local_relative_path=f"bronze/{year_month}/{filename}",
    )


def resolve_period_sources(period: IngestionPeriod) -> list[SourceFile]:
    return [build_yellow_taxi_source(year_month) for year_month in period.iter_months()]
