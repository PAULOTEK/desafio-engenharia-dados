from pyspark.sql import DataFrame
from pyspark.sql.functions import sum as _sum, avg, count, desc


def build_gold(silver_df: DataFrame) -> DataFrame:
    return (
        silver_df.groupBy("fund_code", "fund_name", "position_date", "asset_code", "asset_name", "issuer_name", "asset_type")
        .agg(
            _sum("quantity").alias("total_quantity"),
            _sum("financial_value_calc").alias("total_financial_value"),
            avg("market_price").alias("avg_market_price"),
            count("asset_code").alias("records_count")
        )
    )
