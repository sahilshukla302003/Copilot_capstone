"""Unit tests for csv_summary.stats."""

from datetime import date

from csv_summary.models import ColumnType
from csv_summary.stats import compute_stats


def test_numeric_column_stats(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("age\n10\n20\nNA\n", encoding="utf-8")

    row_count, stats = compute_stats(csv_file, {"age": ColumnType.NUMERIC})

    assert row_count == 3
    assert stats["age"].min_value == 10
    assert stats["age"].max_value == 20
    assert stats["age"].mean_value == 15.0
    assert stats["age"].null_count == 1


def test_date_column_stats(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("joined\n2024-01-01\n2024-03-01\nnull\n", encoding="utf-8")

    _, stats = compute_stats(csv_file, {"joined": ColumnType.DATE})

    assert stats["joined"].earliest_date == date(2024, 1, 1)
    assert stats["joined"].latest_date == date(2024, 3, 1)
    assert stats["joined"].null_count == 1


def test_text_column_stats(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name\nAlice\nBob\nAlice\nNA\n", encoding="utf-8")

    _, stats = compute_stats(csv_file, {"name": ColumnType.TEXT})

    assert stats["name"].unique_count == 2
    assert stats["name"].null_count == 1
