from __future__ import annotations

from src.ingestion.batch_registry import build_batch_metadata
from src.ingestion.downloader import DownloadResult
from src.ingestion.period_config import IngestionPeriod, default_validation_period
from src.ingestion.source_catalog import build_yellow_taxi_source, resolve_period_sources


def test_resolve_period_sources_builds_expected_public_yellow_taxi_artifacts() -> None:
    period = IngestionPeriod(start_month="2024-01", end_month="2024-03")

    sources = resolve_period_sources(period)

    assert [source.year_month for source in sources] == ["2024-01", "2024-02", "2024-03"]
    assert all(source.dataset == "yellow_taxi" for source in sources)
    assert all(source.source_uri.endswith(f"yellow_tripdata_{source.year_month}.parquet") for source in sources)


def test_build_yellow_taxi_source_uses_expected_relative_bronze_path() -> None:
    source = build_yellow_taxi_source("2024-01")

    assert source.filename == "yellow_tripdata_2024-01.parquet"
    assert source.local_relative_path == "bronze/2024-01/yellow_tripdata_2024-01.parquet"
    assert source.source_uri == "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"


def test_build_batch_metadata_keeps_period_and_download_status_traceable(tmp_path) -> None:
    period = IngestionPeriod(start_month="2024-01", end_month="2024-01")
    download_results = [
        DownloadResult(
            source_uri="https://example/yellow_tripdata_2024-01.parquet",
            local_path=tmp_path / "yellow_tripdata_2024-01.parquet",
            year_month="2024-01",
            load_status="downloaded",
            downloaded_bytes=123,
        )
    ]

    metadata = build_batch_metadata(
        period=period,
        download_results=download_results,
        status="completed",
        rerun_mode="replace",
    )

    assert metadata.batch_id == "yellow_taxi_2024-01_to_2024-01"
    assert metadata.rerun_mode == "replace"
    assert metadata.files[0].year_month == "2024-01"
    assert metadata.files[0].load_status == "downloaded"


def test_default_validation_period_returns_single_month_window() -> None:
    period = default_validation_period()

    assert period.start_month == period.end_month
    assert period.month_count == 1
