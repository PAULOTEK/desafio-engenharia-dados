from pyspark.sql import SparkSession


def build_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config(
            "spark.jars.packages",
            "io.delta:delta-spark_2.12:3.2.0,"
            "org.postgresql:postgresql:42.7.3,"
            "org.apache.spark:spark-avro_2.12:3.5.1",
        )
        .getOrCreate()
    )
