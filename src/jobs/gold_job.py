import argparse
from src.utils.spark import build_spark
from src.transforms.gold_builder import build_gold


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--silver-path", required=True)
    parser.add_argument("--gold-path", required=True)
    args = parser.parse_args()

    spark = build_spark("gold-job")
    silver_df = spark.read.format("delta").load(args.silver_path)
    gold_df = build_gold(silver_df)

    (
        gold_df.write
        .format("delta")
        .mode("overwrite")
        .save(args.gold_path)
    )

    spark.stop()


if __name__ == "__main__":
    main()
