"""End-to-end orchestration: bronze -> silver -> gold -> flat CSV export.

Each stage is executed in-process and any failure is logged with context and
propagated (non-zero exit code) instead of being silently ignored, so a broken
stage aborts the pipeline rather than leaving partial/stale downstream data.
"""
import argparse
import sys
from types import SimpleNamespace

from src.jobs import bronze_job, export_job, gold_job, silver_job
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def run(args: argparse.Namespace) -> None:
    logger.info("Starting pipeline")

    logger.info("[1/4] Bronze extraction")
    bronze_job.run(SimpleNamespace(
        output=f"{args.data_dir}/bronze",
        jdbc_url=args.jdbc_url,
        user=args.user,
        password=args.password,
    ))

    logger.info("[2/4] Silver transformation")
    silver_job.run(SimpleNamespace(
        bronze_path=f"{args.data_dir}/bronze",
        silver_path=f"{args.data_dir}/silver",
    ))

    logger.info("[3/4] Gold aggregation")
    gold_job.run(SimpleNamespace(
        silver_path=f"{args.data_dir}/silver",
        gold_path=f"{args.data_dir}/gold",
    ))

    logger.info("[4/4] Flat CSV export")
    final_path = export_job.run(SimpleNamespace(
        silver_path=f"{args.data_dir}/silver",
        output_dir=args.output_dir,
        filename=args.filename,
    ))

    logger.info("Pipeline finished successfully. Flat file: %s", final_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full bronze/silver/gold/export pipeline.")
    parser.add_argument("--jdbc-url", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--data-dir", default="./data")
    parser.add_argument("--output-dir", required=True, help="Local directory for the consolidated CSV file.")
    parser.add_argument("--filename", default="consolidated_positions.csv")
    args = parser.parse_args()

    try:
        run(args)
    except Exception:
        logger.exception("Pipeline aborted due to a stage failure")
        sys.exit(1)


if __name__ == "__main__":
    main()
