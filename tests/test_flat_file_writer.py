import csv
import os

import pytest
from pyspark.sql import SparkSession

from src.transforms.flat_file_writer import FLAT_FILE_COLUMNS, write_flat_file


def _spark():
    return SparkSession.builder.master("local[1]").appName("test-flat").getOrCreate()


def _sample_df(spark):
    data = [
        ("FUND001", "Fundo Alpha", "2026-07-02", "ATV001", "Ação XYZ", "Empresa XYZ", "Ação", 1000.0, 10.75, 10750.0, 12.5),
        ("FUND002", "Fundo Beta", "2026-07-02", "ATV003", "Cota FII", "Grupo Delta", "FII", 200.0, 98.2, 19640.0, 18.0),
    ]
    return spark.createDataFrame(data, FLAT_FILE_COLUMNS)


def test_write_flat_file_produces_single_csv(tmp_path):
    spark = _spark()
    try:
        df = _sample_df(spark)
        out_dir = str(tmp_path / "export")
        final_path = write_flat_file(df, out_dir, "consolidated.csv")

        assert os.path.isfile(final_path)
        # Only the final file should remain (staging dir removed).
        assert os.listdir(out_dir) == ["consolidated.csv"]

        with open(final_path, newline="") as fh:
            rows = list(csv.reader(fh))
        assert rows[0] == FLAT_FILE_COLUMNS
        assert len(rows) == 3  # header + 2 data rows
    finally:
        spark.stop()


def test_write_flat_file_appends_csv_extension(tmp_path):
    spark = _spark()
    try:
        df = _sample_df(spark)
        out_dir = str(tmp_path / "export2")
        final_path = write_flat_file(df, out_dir, "myfile")
        assert final_path.endswith("myfile.csv")
    finally:
        spark.stop()


def test_write_flat_file_raises_on_missing_columns(tmp_path):
    spark = _spark()
    try:
        df = _sample_df(spark).drop("issuer_name")
        with pytest.raises(ValueError, match="issuer_name"):
            write_flat_file(df, str(tmp_path / "export3"))
    finally:
        spark.stop()
