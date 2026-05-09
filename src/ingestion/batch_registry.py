from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.common.paths import get_data_paths
from src.ingestion.downloader import DownloadResult
from src.ingestion.period_config import IngestionPeriod


@dataclass(frozen=True)
class BatchFileMetadata:
    year_month: str
    source_uri: str
    local_path: str
    load_status: str
    downloaded_bytes: int


@dataclass(frozen=True)
class BatchMetadata:
    batch_id: str
    source_name: str
    start_month: str
    end_month: str
    loaded_at: str
    status: str
    rerun_mode: str
    files: list[BatchFileMetadata]


def metadata_path_for_period(period: IngestionPeriod) -> Path:
    return get_data_paths().bronze / "_batch_metadata" / f"{period.batch_id}.json"


def build_batch_metadata(
    period: IngestionPeriod,
    download_results: list[DownloadResult],
    status: str,
    rerun_mode: str,
) -> BatchMetadata:
    return BatchMetadata(
        batch_id=period.batch_id,
        source_name="yellow_taxi",
        start_month=period.start_month,
        end_month=period.end_month,
        loaded_at=datetime.now(timezone.utc).isoformat(),
        status=status,
        rerun_mode=rerun_mode,
        files=[
            BatchFileMetadata(
                year_month=result.year_month,
                source_uri=result.source_uri,
                local_path=str(result.local_path),
                load_status=result.load_status,
                downloaded_bytes=result.downloaded_bytes,
            )
            for result in download_results
        ],
    )


def write_batch_metadata(metadata: BatchMetadata) -> Path:
    path = metadata_path_for_period(
        IngestionPeriod(start_month=metadata.start_month, end_month=metadata.end_month)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(metadata), indent=2), encoding="utf-8")
    return path
