import argparse
import sys

from src.transforms.silver_transformer import transform_silver
from src.utils.logging_config import get_logger
from src.utils.spark import build_spark

logger = get_logger(__name__)

BRONZE_TABLES = ["position", "fund", "asset", "issuer", "market_price"]


def _read_bronze(spark, bronze_path: str, entity: str):
    path = f"{bronze_path}/{entity}"
    try:
        return spark.read.format("avro").load(path)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to read bronze entity '{entity}' from {path}. "
            f"Ensure the bronze job ran successfully. Original error: {exc}"
        ) from exc


def run(args: argparse.Namespace) -> None:
    spark = build_spark("silver-job")
    try:
        dfs = {t: _read_bronze(spark, args.bronze_path, t) for t in BRONZE_TABLES}

        silver_df = transform_silver(
            dfs["position"], dfs["fund"], dfs["asset"], dfs["issuer"], dfs["market_price"]
        )

        logger.info("Writing silver layer to %s", args.silver_path)
        silver_df.write.format("delta").mode("overwrite").save(args.silver_path)
        logger.info("Silver layer written successfully")
    finally:
        spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the silver layer (Delta) from the bronze layer.")
    parser.add_argument("--bronze-path", required=True)
    parser.add_argument("--silver-path", required=True)
    args = parser.parse_args()

    try:
        run(args)
    except Exception:
        logger.exception("Silver job failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
