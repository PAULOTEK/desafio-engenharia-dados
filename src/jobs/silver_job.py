import argparse
from pyspark.sql import SparkSession
from src.utils.spark import build_spark
from src.transforms.silver_transformer import transform_silver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bronze-path", required=True)
    parser.add_argument("--silver-path", required=True)
    args = parser.parse_args()

    spark = build_spark("silver-job")

    position_df = spark.read.format("avro").load(f"{args.bronze_path}/position")
    fund_df = spark.read.format("avro").load(f"{args.bronze_path}/fund")
    asset_df = spark.read.format("avro").load(f"{args.bronze_path}/asset")
    issuer_df = spark.read.format("avro").load(f"{args.bronze_path}/issuer")
    market_price_df = spark.read.format("avro").load(f"{args.bronze_path}/market_price")

    silver_df = transform_silver(position_df, fund_df, asset_df, issuer_df, market_price_df)

    (
        silver_df.write
        .format("delta")
        .mode("overwrite")
        .save(args.silver_path)
    )

    spark.stop()


if __name__ == "__main__":
    main()
