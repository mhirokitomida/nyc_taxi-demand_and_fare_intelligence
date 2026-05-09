from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.common.logging_utils import get_logger
from src.processing.derive_trip_features import derive_trip_features
from src.processing.filter_invalid_trips import filter_invalid_trips
from src.processing.read_bronze import create_spark_session, read_bronze_dataframe
from src.processing.validate_bronze_schema import validate_bronze_schema
from src.processing.write_silver import write_silver


logger = get_logger(__name__)


@dataclass(frozen=True)
class SilverPipelineResult:
    output_path: Path
    row_count: int


def run_bronze_to_silver(
    start_month: str,
    end_month: str,
    spark_master: str | None = None,
    data_root: Path | None = None,
) -> SilverPipelineResult:
    spark = create_spark_session("bronze-to-silver", master=spark_master)
    try:
        bronze_df = read_bronze_dataframe(
            spark=spark,
            start_month=start_month,
            end_month=end_month,
            data_root=data_root,
        )
        validate_bronze_schema(bronze_df)
        filtered_df = filter_invalid_trips(bronze_df)
        silver_df = derive_trip_features(filtered_df)
        row_count = silver_df.count()
        if row_count == 0:
            raise ValueError("Silver pipeline produced zero rows after validation and filtering")
        output_path = write_silver(
            dataframe=silver_df,
            start_month=start_month,
            end_month=end_month,
            data_root=data_root,
        )
        logger.info("Silver pipeline completed with %s rows", row_count)
        return SilverPipelineResult(output_path=output_path, row_count=row_count)
    finally:
        spark.stop()
