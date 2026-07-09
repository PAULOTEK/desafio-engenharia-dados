from pyspark.sql import SparkSession
from src.transforms.gold_builder import build_gold


def test_build_gold_aggregates_values():
    spark = SparkSession.builder.master("local[1]").appName("test").getOrCreate()

    data = [
        ("F1", "Fundo 1", "2026-07-01", "A1", "Ativo 1", "Emissor 1", "Renda Fixa", 10.0, 100.0),
        ("F1", "Fundo 1", "2026-07-01", "A1", "Ativo 1", "Emissor 1", "Renda Fixa", 5.0, 50.0),
    ]
    cols = ["fund_code", "fund_name", "position_date", "asset_code", "asset_name", "issuer_name", "asset_type", "quantity", "financial_value_calc"]
    df = spark.createDataFrame(data, cols)

    result = build_gold(df)
    row = result.collect()[0]

    assert row["total_quantity"] == 15.0
    assert row["total_financial_value"] == 150.0

    spark.stop()