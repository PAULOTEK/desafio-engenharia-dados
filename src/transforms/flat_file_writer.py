import glob
import os
import shutil

from pyspark.sql import DataFrame

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Columns of the single consolidated flat file, as described in the challenge.
FLAT_FILE_COLUMNS = [
    "fund_code",
    "fund_name",
    "position_date",
    "asset_code",
    "asset_name",
    "issuer_name",
    "asset_type",
    "quantity",
    "market_price",
    "financial_value",
    "nav_percentage",
]


def write_flat_file(df: DataFrame, output_dir: str, filename: str = "consolidated_positions.csv") -> str:
    """Write ``df`` as a single flat CSV file into ``output_dir``.

    Spark writes CSV as a directory of part files; this coalesces the
    DataFrame to a single partition and renames the resulting part file to
    ``filename`` so the caller gets one deterministic flat file.

    Returns the absolute path of the written file. Raises if the expected
    part file is not produced instead of silently returning a bad path.
    """
    missing = [c for c in FLAT_FILE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Cannot write flat file: input DataFrame is missing required columns {missing}. "
            f"Available columns: {df.columns}"
        )

    if not filename.lower().endswith(".csv"):
        filename = f"{filename}.csv"

    os.makedirs(output_dir, exist_ok=True)
    staging_dir = os.path.join(output_dir, "_flat_file_staging")

    logger.info("Writing consolidated flat file to staging dir %s", staging_dir)
    (
        df.select(*FLAT_FILE_COLUMNS)
        .coalesce(1)
        .write.format("csv")
        .option("header", "true")
        .mode("overwrite")
        .save(staging_dir)
    )

    part_files = glob.glob(os.path.join(staging_dir, "part-*.csv"))
    if not part_files:
        raise RuntimeError(
            f"Spark did not produce a CSV part file in {staging_dir}; flat file was not written."
        )

    final_path = os.path.join(output_dir, filename)
    shutil.move(part_files[0], final_path)
    shutil.rmtree(staging_dir, ignore_errors=True)

    logger.info("Consolidated flat file written to %s", final_path)
    return final_path
