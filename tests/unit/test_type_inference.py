"""Unit tests for csv_summary.type_inference."""

from __future__ import annotations

from pathlib import Path

from csv_summary.models import ColumnType
from csv_summary.type_inference import infer_types

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_infers_numeric_column(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("age\n1\n2\n3\n", encoding="utf-8")

    assert infer_types(str(csv_file))["age"] is ColumnType.NUMERIC


def test_infers_date_column_mixed_date_only_and_datetime(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("joined\n2024-01-01\n2024-02-01T10:30:00\n", encoding="utf-8")

    assert infer_types(str(csv_file))["joined"] is ColumnType.DATE


def test_infers_text_column_below_both_thresholds(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name\nAlice\nBob\n", encoding="utf-8")

    assert infer_types(str(csv_file))["name"] is ColumnType.TEXT


def test_mixed_column_below_threshold_is_text(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    # Only 1 of 3 non-null values is numeric (<90%) -> classified TEXT.
    csv_file.write_text("mixed\n1\nhello\nworld\n", encoding="utf-8")

    assert infer_types(str(csv_file))["mixed"] is ColumnType.TEXT


def test_all_null_column_defaults_to_text_without_raising(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("empty\nNA\nnull\n\n", encoding="utf-8")

    assert infer_types(str(csv_file))["empty"] is ColumnType.TEXT


def test_infer_types_using_valid_basic_fixture() -> None:
    result = infer_types(str(FIXTURES / "valid_basic.csv"))

    assert result["id"] is ColumnType.NUMERIC
    assert result["name"] is ColumnType.TEXT
    assert result["signup_date"] is ColumnType.DATE
    assert result["score"] is ColumnType.NUMERIC


def test_infer_types_using_mixed_nulls_fixture() -> None:
    result = infer_types(str(FIXTURES / "mixed_nulls.csv"))

    assert result["signup_date"] is ColumnType.DATE
    assert result["score"] is ColumnType.NUMERIC


def test_nan_and_infinity_tokens_are_not_classified_as_numeric(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("val\nnan\ninf\n-infinity\nNaN\n", encoding="utf-8")

    assert infer_types(str(csv_file))["val"] is ColumnType.TEXT


def test_compact_iso_date_digits_are_not_classified_as_date(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("code\n20230115\n20230220\n20230301\n", encoding="utf-8")

    assert infer_types(str(csv_file))["code"] is ColumnType.NUMERIC

