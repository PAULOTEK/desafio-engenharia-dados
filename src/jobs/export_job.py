import argparse
import sys

from src.transforms.flat_file_writer import write_flat_file
from src.utils.logging_config import get_logger
from src.utils.spark import build_spark

logger = get_logger(__name__)


def run(args: argparse.Namespace) -> str:
    spark = build_spark("export-job")
    try:
        try:
            silver_df = spark.read.format("delta").load(args.silver_path)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to read silver layer from {args.silver_path}. "
                f"Ensure the silver job ran successfully. Original error: {exc}"
            ) from exc

        final_path = write_flat_file(silver_df, args.output_dir, args.filename)
        logger.info("Flat file export completed: %s", final_path)
        return final_path
    finally:
        spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the consolidated single flat CSV file to a user-defined directory."
    )
    parser.add_argument("--silver-path", required=True)
    parser.add_argument("--output-dir", required=True, help="Local directory where the CSV file is written.")
    parser.add_argument("--filename", default="consolidated_positions.csv")
    args = parser.parse_args()

    try:
        run(args)
    except Exception:
        logger.exception("Export job failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
