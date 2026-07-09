import pytest
from pyspark.sql import SparkSession

from src.transforms.silver_transformer import transform_silver


def _spark():
    return SparkSession.builder.master("local[1]").appName("test-silver").getOrCreate()


def _base_frames(spark):
    position = spark.createDataFrame(
        [(1, 1, "2026-07-02", 1000.0, 10.75, 10750.0, 12.5)],
        ["fund_id", "asset_id", "position_date", "quantity", "market_price", "financial_value", "nav_percentage"],
    )
    fund = spark.createDataFrame(
        [(1, " fund001 ", " Fundo Alpha ", " Ações ")],
        ["fund_id", "fund_code", "fund_name", "fund_type"],
    )
    asset = spark.createDataFrame(
        [(1, " atv001 ", " Ação XYZ ", " Ação ", 1)],
        ["asset_id", "asset_code", "asset_name", "asset_type", "issuer_id"],
    )
    issuer = spark.createDataFrame(
        [(1, " Empresa XYZ S.A. ", "12.345.678/0001-90", " Financeiro ")],
        ["issuer_id", "issuer_name", "issuer_document", "sector"],
    )
    market_price = spark.createDataFrame(
        [(1, "2026-07-02", 10.75, "B3")],
        ["asset_id", "reference_date", "price", "source"],
    )
    return position, fund, asset, issuer, market_price


def test_transform_silver_standardizes_and_keeps_flat_columns():
    spark = _spark()
    try:
        position, fund, asset, issuer, market_price = _base_frames(spark)
        result = transform_silver(position, fund, asset, issuer, market_price)
        row = result.collect()[0]

        # Standardization: code uppercased/trimmed, names trimmed, document digits only.
        assert row["fund_code"] == "FUND001"
        assert row["fund_name"] == "Fundo Alpha"
        assert row["issuer_document"] == "12345678000190"

        # Derived values present and consistent with source.
        assert row["financial_value_calc"] == 10750.0
        assert row["nav_percentage_calc"] == 12.5
    finally:
        spark.stop()


def test_transform_silver_raises_on_missing_columns():
    spark = _spark()
    try:
        position, fund, asset, issuer, market_price = _base_frames(spark)
        bad_fund = fund.drop("fund_name")
        with pytest.raises(ValueError, match="fund"):
            transform_silver(position, bad_fund, asset, issuer, market_price)
    finally:
        spark.stop()
