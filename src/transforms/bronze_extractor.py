from pyspark.sql import DataFrame

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def write_bronze(df: DataFrame, output_path: str, entity_name: str) -> None:
    if not entity_name:
        raise ValueError("entity_name must be a non-empty string")
    if not output_path:
        raise ValueError("output_path must be a non-empty string")

    target = f"{output_path}/{entity_name}"
    try:
        df.write.format("avro").mode("overwrite").save(target)
    except Exception as exc:
        raise RuntimeError(f"Failed to write bronze entity '{entity_name}' to {target}: {exc}") from exc
