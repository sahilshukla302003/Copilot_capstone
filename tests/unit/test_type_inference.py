"""Unit tests for csv_summary.type_inference."""

from csv_summary.models import ColumnType
from csv_summary.type_inference import infer_types


def test_infers_numeric_column(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("age\n1\n2\n3\n", encoding="utf-8")

    assert infer_types(csv_file)["age"] is ColumnType.NUMERIC


def test_infers_date_column(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("joined\n2024-01-01\n2024-02-01\n", encoding="utf-8")

    assert infer_types(csv_file)["joined"] is ColumnType.DATE


def test_infers_text_column(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name\nAlice\nBob\n", encoding="utf-8")

    assert infer_types(csv_file)["name"] is ColumnType.TEXT


def test_mixed_column_below_threshold_is_text(tmp_path):
    csv_file = tmp_path / "data.csv"
    # Only 1 of 3 non-null values is numeric (<90%) -> classified TEXT.
    csv_file.write_text("mixed\n1\nhello\nworld\n", encoding="utf-8")

    assert infer_types(csv_file)["mixed"] is ColumnType.TEXT


def test_all_null_column_defaults_to_text(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("empty\nNA\nnull\n\n", encoding="utf-8")

    assert infer_types(csv_file)["empty"] is ColumnType.TEXT
