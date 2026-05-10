from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.common.lakehouse_manifests import resolve_latest_layer_path
from src.common.logging_utils import get_logger
from src.processing.build_gold_daily_zone import build_gold_daily_zone, validate_silver_input_schema
from src.processing.read_bronze import create_spark_session
from src.processing.write_gold import write_gold


logger = get_logger(__name__)


@dataclass(frozen=True)
class GoldPipelineResult:
    output_path: Path
    manifest_path: Path
    run_id: str | None
    row_count: int


def run_silver_to_gold(
    start_month: str,
    end_month: str,
    spark_master: str | None = None,
    rerun_mode: str = "fail",
    run_id: str | None = None,
    data_root: Path | None = None,
) -> GoldPipelineResult:
    spark = create_spark_session("silver-to-gold", master=spark_master)
    try:
        input_path = resolve_latest_layer_path(
            layer="silver",
            start_month=start_month,
            end_month=end_month,
            data_root=data_root,
        )
        logger.info("Reading silver input from %s", input_path)
        silver_df = spark.read.parquet(str(input_path))
        validate_silver_input_schema(silver_df)
        gold_df = build_gold_daily_zone(silver_df)
        row_count = gold_df.count()
        if row_count == 0:
            raise ValueError("Gold pipeline produced zero aggregated rows")
        output_path, manifest_path = write_gold(
            dataframe=gold_df,
            start_month=start_month,
            end_month=end_month,
            run_id=run_id,
            rerun_mode=rerun_mode,
            row_count=row_count,
            source_paths=[str(input_path)],
            data_root=data_root,
        )
        logger.info("Gold pipeline completed with %s rows", row_count)
        return GoldPipelineResult(output_path=output_path, manifest_path=manifest_path, run_id=run_id, row_count=row_count)
    finally:
        spark.stop()
