from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.common.logging_utils import get_logger
from src.common.paths import get_data_paths
from src.ingestion.source_catalog import SourceFile


logger = get_logger(__name__)


@dataclass(frozen=True)
class DownloadResult:
    source_uri: str
    local_path: Path
    year_month: str
    load_status: str
    downloaded_bytes: int


class RemoteArtifactUnavailableError(FileNotFoundError):
    """Raised when an expected public artifact cannot be reached."""


def verify_remote_exists(source_uri: str) -> None:
    request = Request(source_uri, method="HEAD")
    try:
        with urlopen(request, timeout=15) as response:
            if response.status >= 400:
                raise RemoteArtifactUnavailableError(
                    f"Remote artifact returned HTTP {response.status}: {source_uri}"
                )
    except HTTPError as exc:
        raise RemoteArtifactUnavailableError(
            f"Remote artifact returned HTTP {exc.code}: {source_uri}"
        ) from exc
    except URLError as exc:
        raise RemoteArtifactUnavailableError(
            f"Remote artifact could not be reached: {source_uri}"
        ) from exc


def download_source_file(source: SourceFile, replace_existing: bool = False) -> DownloadResult:
    paths = get_data_paths()
    relative_path = Path(source.local_relative_path)
    if relative_path.parts[0] == "bronze":
        relative_path = Path(*relative_path.parts[1:])
    target_path = paths.bronze / relative_path

    if target_path.exists() and not replace_existing:
        raise FileExistsError(
            f"Target file already exists for {source.year_month}: {target_path}"
        )

    verify_remote_exists(source.source_uri)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists() and replace_existing:
        target_path.unlink()

    request = Request(source.source_uri, method="GET")
    try:
        with urlopen(request, timeout=60) as response, target_path.open("wb") as file_obj:
            shutil.copyfileobj(response, file_obj)
    except URLError as exc:
        raise RemoteArtifactUnavailableError(
            f"Download failed for remote artifact: {source.source_uri}"
        ) from exc

    downloaded_bytes = target_path.stat().st_size
    logger.info("Downloaded bronze file %s to %s", source.source_uri, target_path)
    return DownloadResult(
        source_uri=source.source_uri,
        local_path=target_path,
        year_month=source.year_month,
        load_status="downloaded",
        downloaded_bytes=downloaded_bytes,
    )
