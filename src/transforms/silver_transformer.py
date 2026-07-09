from pyspark.sql import DataFrame
from pyspark.sql.functions import col, upper, trim, regexp_replace, row_number, desc, when, lit
from pyspark.sql.window import Window

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def _require_columns(df: DataFrame, columns: list, df_name: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(
            f"DataFrame '{df_name}' is missing required columns {missing}. Available: {df.columns}"
        )


def transform_silver(position_df: DataFrame, fund_df: DataFrame, asset_df: DataFrame, issuer_df: DataFrame, market_price_df: DataFrame) -> DataFrame:
    _require_columns(position_df, ["fund_id", "asset_id", "position_date", "quantity", "market_price", "financial_value", "nav_percentage"], "position")
    _require_columns(fund_df, ["fund_id", "fund_code", "fund_name", "fund_type"], "fund")
    _require_columns(asset_df, ["asset_id", "asset_code", "asset_name", "asset_type", "issuer_id"], "asset")
    _require_columns(issuer_df, ["issuer_id", "issuer_name", "issuer_document", "sector"], "issuer")
    _require_columns(market_price_df, ["asset_id", "reference_date", "price"], "market_price")

    fund_df = fund_df.select(
        col("fund_id"),
        upper(trim(col("fund_code"))).alias("fund_code"),
        trim(col("fund_name")).alias("fund_name"),
        trim(col("fund_type")).alias("fund_type")
    )

    asset_df = asset_df.select(
        col("asset_id"),
        upper(trim(col("asset_code"))).alias("asset_code"),
        trim(col("asset_name")).alias("asset_name"),
        trim(col("asset_type")).alias("asset_type"),
        col("issuer_id")
    )

    issuer_df = issuer_df.select(
        col("issuer_id"),
        trim(col("issuer_name")).alias("issuer_name"),
        regexp_replace(col("issuer_document"), r"\D", "").alias("issuer_document"),
        trim(col("sector")).alias("sector")
    )

    # Keep a single "current" price per asset (most recent reference_date, highest
    # price as tie-break) so joining on asset_id does not fan out each position
    # across every historical price date.
    latest_price_window = Window.partitionBy("asset_id").orderBy(desc("reference_date"), desc("price"))
    market_price_df = (
        market_price_df
        .withColumn("rn", row_number().over(latest_price_window))
        .filter(col("rn") == 1)
        .select("asset_id", col("price").alias("latest_market_price"), "reference_date")
    )

    joined = (
        position_df
        .join(fund_df, "fund_id", "left")
        .join(asset_df, "asset_id", "left")
        .join(issuer_df, "issuer_id", "left")
        .join(market_price_df, ["asset_id"], "left")
    )

    result = joined.withColumn(
        "financial_value_calc",
        when(col("financial_value").isNotNull(), col("financial_value")).otherwise(col("quantity") * col("market_price"))
    ).withColumn(
        "nav_percentage_calc",
        when(col("nav_percentage").isNotNull(), col("nav_percentage")).otherwise(lit(0.0))
    )

    return result
