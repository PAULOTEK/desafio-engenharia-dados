import glob
import os
import shutil

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

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

# Numeric columns formatted to 2 decimal places (no thousands separator) for clean output.
NUMERIC_COLUMNS = ["quantity", "market_price", "financial_value", "nav_percentage"]

# Deterministic, readable row ordering.
SORT_COLUMNS = ["fund_code", "asset_code", "position_date"]


def _format_for_output(df: DataFrame) -> DataFrame:
    formatted = df.select(*FLAT_FILE_COLUMNS)
    for c in NUMERIC_COLUMNS:
        formatted = formatted.withColumn(c, col(c).cast("decimal(20,2)").cast("string"))
    return formatted.orderBy(*SORT_COLUMNS)


def _write_aligned_view(rows: list, path: str) -> None:
    """Write a human-readable, column-aligned table (fixed-width) for easy reading."""
    widths = [
        max(len(FLAT_FILE_COLUMNS[i]), max((len(r[i]) for r in rows), default=0))
        for i in range(len(FLAT_FILE_COLUMNS))
    ]

    def fmt(values):
        return " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(values))

    lines = [fmt(FLAT_FILE_COLUMNS), "-+-".join("-" * w for w in widths)]
    lines += [fmt(r) for r in rows]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_flat_file(df: DataFrame, output_dir: str, filename: str = "consolidated_positions.csv") -> str:
    """Write ``df`` as a single flat CSV file into ``output_dir``.

    Numeric columns are formatted to 2 decimals and rows are sorted for a clean,
    stable output. A column-aligned, human-readable ``.txt`` companion is written
    alongside the CSV for easy visual inspection.

    Spark writes CSV as a directory of part files; this coalesces the DataFrame to
    a single partition and renames the resulting part file to ``filename`` so the
    caller gets one deterministic flat file. Returns the absolute path of the CSV.
    Raises if the expected part file is not produced instead of silently returning
    a bad path.
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

    formatted = _format_for_output(df)

    logger.info("Writing consolidated flat file to staging dir %s", staging_dir)
    (
        formatted
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

    aligned_path = f"{os.path.splitext(final_path)[0]}.txt"
    _write_aligned_view([list(r) for r in formatted.collect()], aligned_path)

    logger.info("Consolidated flat file written to %s (aligned view: %s)", final_path, aligned_path)
    return final_path
