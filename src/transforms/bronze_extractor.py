from pyspark.sql import DataFrame


def write_bronze(df: DataFrame, output_path: str, entity_name: str) -> None:
    (
        df.write
        .format("avro")
        .mode("overwrite")
        .save(f"{output_path}/{entity_name}")
    )
