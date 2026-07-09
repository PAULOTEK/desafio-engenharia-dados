import argparse
from src.utils.spark import build_spark
from src.transforms.bronze_extractor import write_bronze


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--jdbc-url", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    spark = build_spark("bronze-job")

    tables = ["fund", "issuer", "asset", "position", "operation", "market_price"]

    for table in tables:
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

    spark.stop()


if __name__ == "__main__":
    main()
