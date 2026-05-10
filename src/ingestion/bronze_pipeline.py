from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.common.logging_utils import get_logger
from src.common.paths import get_data_paths
from src.ingestion.batch_registry import BatchMetadata, build_batch_metadata, metadata_path_for_period, write_batch_metadata
from src.ingestion.downloader import DownloadResult, DownloadRetryConfig, download_source_file
from src.ingestion.period_config import IngestionPeriod
from src.ingestion.source_catalog import resolve_period_sources


logger = get_logger(__name__)

RERUN_MODES = {"fail", "replace"}


@dataclass(frozen=True)
class BronzePipelineResult:
    metadata_path: Path
    metadata: BatchMetadata
    downloaded_files: list[DownloadResult]


def _assert_valid_rerun_mode(rerun_mode: str) -> None:
    if rerun_mode not in RERUN_MODES:
        raise ValueError(f"Unsupported rerun_mode: {rerun_mode!r}")


def _prepare_for_rerun(period: IngestionPeriod, rerun_mode: str) -> None:
    metadata_path = metadata_path_for_period(period)
    if metadata_path.exists():
        if rerun_mode == "fail":
            raise FileExistsError(
                f"Batch metadata already exists for {period.batch_id}. Use rerun_mode='replace' to rerun."
            )
        metadata_path.unlink()


def run_bronze_ingestion(
    start_month: str,
    end_month: str,
    rerun_mode: str = "fail",
    download_max_attempts: int = 5,
    download_initial_wait_seconds: float = 5.0,
    download_backoff_multiplier: float = 2.0,
    download_max_wait_seconds: float = 60.0,
) -> BronzePipelineResult:
    _assert_valid_rerun_mode(rerun_mode)
    period = IngestionPeriod(start_month=start_month, end_month=end_month)
    _prepare_for_rerun(period, rerun_mode)
    retry_config = DownloadRetryConfig(
        max_attempts=download_max_attempts,
        initial_wait_seconds=download_initial_wait_seconds,
        backoff_multiplier=download_backoff_multiplier,
        max_wait_seconds=download_max_wait_seconds,
    )

    logger.info(
        "Starting bronze ingestion for %s to %s with rerun_mode=%s and retry_config=%s",
        period.start_month,
        period.end_month,
        rerun_mode,
        retry_config,
    )

    download_results: list[DownloadResult] = []
    sources = resolve_period_sources(period)
    replace_existing = rerun_mode == "replace"

    for source in sources:
        logger.info("Downloading yellow taxi artifact for %s", source.year_month)
        result = download_source_file(
            source,
            replace_existing=replace_existing,
            retry_config=retry_config,
        )
        download_results.append(result)

    metadata = build_batch_metadata(
        period=period,
        download_results=download_results,
        status="completed",
        rerun_mode=rerun_mode,
    )
    metadata_path = write_batch_metadata(metadata)

    logger.info(
        "Bronze ingestion completed for batch %s with %s files",
        metadata.batch_id,
        len(download_results),
    )
    return BronzePipelineResult(
        metadata_path=metadata_path,
        metadata=metadata,
        downloaded_files=download_results,
    )


def bronze_artifact_paths(start_month: str, end_month: str) -> list[Path]:
    period = IngestionPeriod(start_month=start_month, end_month=end_month)
    data_paths = get_data_paths()
    paths: list[Path] = []
    for source in resolve_period_sources(period):
        relative_path = Path(source.local_relative_path)
        if relative_path.parts[0] == "bronze":
            relative_path = Path(*relative_path.parts[1:])
        paths.append(data_paths.bronze / relative_path)
    return paths
