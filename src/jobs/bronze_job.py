import argparse
import sys

from src.transforms.bronze_extractor import write_bronze
from src.utils.logging_config import get_logger
from src.utils.spark import build_spark

logger = get_logger(__name__)

TABLES = ["fund", "issuer", "asset", "position", "operation", "market_price"]


def run(args: argparse.Namespace) -> None:
    spark = build_spark("bronze-job")
    try:
        failures = {}
        for table in TABLES:
            try:
                logger.info("Extracting table '%s' from source database", table)
                df = (
                    spark.read.format("jdbc")
                    .option("url", args.jdbc_url)
                    .option("dbtable", table)
                    .option("user", args.user)
                    .option("password", args.password)
                    .option("driver", "org.postgresql.Driver")
                    .load()
                )
                write_bronze(df, args.output, table)
                logger.info("Table '%s' written to bronze layer", table)
            except Exception:
                # Capture the failure with table context instead of losing it,
                # but keep going so one bad table does not hide the others.
                logger.exception("Failed to extract/write table '%s'", table)
                failures[table] = sys.exc_info()[1]

        if failures:
            raise RuntimeError(
                "Bronze extraction failed for tables: "
                + ", ".join(f"{t} ({err})" for t, err in failures.items())
            )
    finally:
        spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract source tables into the bronze layer (Avro).")
    parser.add_argument("--output", required=True)
    parser.add_argument("--jdbc-url", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    try:
        run(args)
    except Exception:
        logger.exception("Bronze job failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
