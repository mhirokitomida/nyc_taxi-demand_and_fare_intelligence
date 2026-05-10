from __future__ import annotations

import socket
import shutil
from dataclasses import dataclass
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.common.logging_utils import get_logger
from src.common.paths import get_data_paths
from src.ingestion.source_catalog import SourceFile


logger = get_logger(__name__)

DEFAULT_USER_AGENT = "nyc-taxi-demand-intelligence/1.0"
DEFAULT_DOWNLOAD_MAX_ATTEMPTS = 5
DEFAULT_DOWNLOAD_INITIAL_WAIT_SECONDS = 5.0
DEFAULT_DOWNLOAD_BACKOFF_MULTIPLIER = 2.0
DEFAULT_DOWNLOAD_MAX_WAIT_SECONDS = 60.0
RETRYABLE_HTTP_STATUS_CODES = {403, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class DownloadResult:
    source_uri: str
    local_path: Path
    year_month: str
    load_status: str
    downloaded_bytes: int


class RemoteArtifactUnavailableError(FileNotFoundError):
    """Raised when an expected public artifact cannot be reached."""


@dataclass(frozen=True)
class DownloadRetryConfig:
    max_attempts: int = DEFAULT_DOWNLOAD_MAX_ATTEMPTS
    initial_wait_seconds: float = DEFAULT_DOWNLOAD_INITIAL_WAIT_SECONDS
    backoff_multiplier: float = DEFAULT_DOWNLOAD_BACKOFF_MULTIPLIER
    max_wait_seconds: float = DEFAULT_DOWNLOAD_MAX_WAIT_SECONDS

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("download_max_attempts must be at least 1")
        if self.initial_wait_seconds < 0:
            raise ValueError("download_initial_wait_seconds must be non-negative")
        if self.backoff_multiplier < 1:
            raise ValueError("download_backoff_multiplier must be at least 1")
        if self.max_wait_seconds < 0:
            raise ValueError("download_max_wait_seconds must be non-negative")


def _build_request(source_uri: str) -> Request:
    return Request(
        source_uri,
        method="GET",
        headers={"User-Agent": DEFAULT_USER_AGENT},
    )


def _is_retryable_error(exc: Exception) -> bool:
    if isinstance(exc, HTTPError):
        return exc.code in RETRYABLE_HTTP_STATUS_CODES
    if isinstance(exc, TimeoutError | socket.timeout | ConnectionError):
        return True
    if isinstance(exc, URLError):
        reason = exc.reason
        if isinstance(reason, TimeoutError | socket.timeout | ConnectionError | OSError):
            return True
        if isinstance(reason, str):
            lowered = reason.lower()
            return any(
                marker in lowered
                for marker in ("timeout", "timed out", "temporary", "reset", "unreachable", "refused")
            )
    return False


def _calculate_retry_wait_seconds(attempt_number: int, config: DownloadRetryConfig) -> float:
    if attempt_number <= 1:
        return 0.0
    wait_seconds = config.initial_wait_seconds * (config.backoff_multiplier ** (attempt_number - 2))
    return min(wait_seconds, config.max_wait_seconds)


def _run_with_retries(
    *,
    source_uri: str,
    year_month: str,
    action_name: str,
    config: DownloadRetryConfig,
    operation,
):
    last_error: Exception | None = None
    for attempt_number in range(1, config.max_attempts + 1):
        logger.info(
            "%s remote artifact for %s (%s) attempt %s/%s",
            action_name,
            year_month,
            source_uri,
            attempt_number,
            config.max_attempts,
        )
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if not _is_retryable_error(exc) or attempt_number == config.max_attempts:
                logger.error(
                    "%s failed for %s (%s) on attempt %s/%s: %s",
                    action_name,
                    year_month,
                    source_uri,
                    attempt_number,
                    config.max_attempts,
                    exc,
                )
                if attempt_number == config.max_attempts:
                    logger.error(
                        "Exhausted all %s attempts for %s (%s)",
                        config.max_attempts,
                        year_month,
                        source_uri,
                    )
                raise

            wait_seconds = _calculate_retry_wait_seconds(attempt_number + 1, config)
            logger.warning(
                "%s failed for %s (%s) on attempt %s/%s: %s. Waiting %ss before retry.",
                action_name,
                year_month,
                source_uri,
                attempt_number,
                config.max_attempts,
                exc,
                wait_seconds,
            )
            sleep(wait_seconds)

    if last_error is not None:
        raise last_error
    raise RuntimeError(f"{action_name} failed before any attempt for {source_uri}")


def verify_remote_exists(
    source_uri: str,
    retry_config: DownloadRetryConfig | None = None,
    year_month: str = "unknown",
) -> None:
    config = retry_config or DownloadRetryConfig()

    def _verify() -> None:
        request = _build_request(source_uri)
        with urlopen(request, timeout=15) as response:
            if response.status >= 400:
                raise HTTPError(
                    source_uri,
                    response.status,
                    f"Remote artifact returned HTTP {response.status}",
                    hdrs=response.headers,
                    fp=None,
                )
            response.read(1)

    try:
        _run_with_retries(
            source_uri=source_uri,
            year_month=year_month,
            action_name="Verifying",
            config=config,
            operation=_verify,
        )
    except (HTTPError, URLError, TimeoutError, socket.timeout, ConnectionError) as exc:
        raise RemoteArtifactUnavailableError(
            f"Remote artifact could not be reached: {source_uri}"
        ) from exc


def download_source_file(
    source: SourceFile,
    replace_existing: bool = False,
    retry_config: DownloadRetryConfig | None = None,
) -> DownloadResult:
    paths = get_data_paths()
    relative_path = Path(source.local_relative_path)
    if relative_path.parts[0] == "bronze":
        relative_path = Path(*relative_path.parts[1:])
    target_path = paths.bronze / relative_path
    temp_path = target_path.with_name(f"{target_path.name}.tmp")
    config = retry_config or DownloadRetryConfig()

    if target_path.exists() and not replace_existing:
        raise FileExistsError(
            f"Target file already exists for {source.year_month}: {target_path}"
        )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if temp_path.exists():
        temp_path.unlink()

    def _download() -> None:
        if temp_path.exists():
            temp_path.unlink()
        request = _build_request(source.source_uri)
        with urlopen(request, timeout=60) as response, temp_path.open("wb") as file_obj:
            if response.status >= 400:
                raise HTTPError(
                    source.source_uri,
                    response.status,
                    f"Remote artifact returned HTTP {response.status}",
                    hdrs=response.headers,
                    fp=None,
                )
            shutil.copyfileobj(response, file_obj)

    try:
        _run_with_retries(
            source_uri=source.source_uri,
            year_month=source.year_month,
            action_name="Downloading",
            config=config,
            operation=_download,
        )
        temp_path.replace(target_path)
    except (HTTPError, URLError, TimeoutError, socket.timeout, ConnectionError) as exc:
        if temp_path.exists():
            temp_path.unlink()
        raise RemoteArtifactUnavailableError(
            f"Download failed for remote artifact: {source.source_uri}"
        ) from exc
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise

    downloaded_bytes = target_path.stat().st_size
    logger.info("Downloaded bronze file %s to %s", source.source_uri, target_path)
    return DownloadResult(
        source_uri=source.source_uri,
        local_path=target_path,
        year_month=source.year_month,
        load_status="downloaded",
        downloaded_bytes=downloaded_bytes,
    )
