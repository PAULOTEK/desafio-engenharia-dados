import csv
import datetime
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
        # Staging dir removed; CSV plus the aligned .txt companion remain.
        assert sorted(os.listdir(out_dir)) == ["consolidated.csv", "consolidated.txt"]

        with open(final_path, newline="") as fh:
            rows = list(csv.reader(fh))
        assert rows[0] == FLAT_FILE_COLUMNS
        assert len(rows) == 3  # header + 2 data rows

        # Numeric columns are formatted to exactly 2 decimals (no thousands separator).
        record = dict(zip(rows[0], rows[1]))
        assert record["quantity"] == "1000.00"
        assert record["market_price"] == "10.75"
        assert record["financial_value"] == "10750.00"
        assert record["nav_percentage"] == "12.50"

        # Aligned view is readable and column-separated.
        with open(os.path.join(out_dir, "consolidated.txt"), encoding="utf-8") as fh:
            aligned = fh.read()
        assert "fund_code" in aligned and " | " in aligned
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


def test_write_flat_file_handles_date_typed_columns(tmp_path):
    spark = _spark()
    try:
        # Real silver data has position_date as a date (not a string); the aligned
        # view must handle non-string values without raising.
        data = [
            ("FUND001", "Fundo Alpha", datetime.date(2026, 7, 2), "ATV001", "Ação XYZ", "Empresa XYZ", "Ação", 1000.0, 10.75, 10750.0, 12.5),
        ]
        df = spark.createDataFrame(data, FLAT_FILE_COLUMNS)
        out_dir = str(tmp_path / "export_date")
        write_flat_file(df, out_dir, "consolidated.csv")

        assert sorted(os.listdir(out_dir)) == ["consolidated.csv", "consolidated.txt"]
        with open(os.path.join(out_dir, "consolidated.txt"), encoding="utf-8") as fh:
            assert "2026-07-02" in fh.read()
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
