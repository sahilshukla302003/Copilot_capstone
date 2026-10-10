"""Unit tests for csv_summary.stats."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from csv_summary.models import ColumnType
from csv_summary.stats import compute_stats

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_numeric_column_min_max_mean_null_count(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("age\n10\n20\nNA\n", encoding="utf-8")

    row_count, stats = compute_stats(str(csv_file), {"age": ColumnType.NUMERIC})

    assert row_count == 3
    assert stats["age"].min_value == 10
    assert stats["age"].max_value == 20
    assert stats["age"].mean_value == 15.0
    assert stats["age"].null_count == 1


def test_date_column_earliest_latest_null_count(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("joined\n2024-01-01\n2024-03-01\nnull\n", encoding="utf-8")

    _, stats = compute_stats(str(csv_file), {"joined": ColumnType.DATE})

    assert stats["joined"].earliest == datetime(2024, 1, 1)
    assert stats["joined"].latest == datetime(2024, 3, 1)
    assert stats["joined"].null_count == 1


def test_date_column_mixed_date_only_and_datetime_tracks_time_component(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("joined\n2024-01-01\n2024-03-01T08:15:00\n", encoding="utf-8")

    _, stats = compute_stats(str(csv_file), {"joined": ColumnType.DATE})

    assert stats["joined"].has_time_component is True
    assert stats["joined"].earliest == datetime(2024, 1, 1)
    assert stats["joined"].latest == datetime(2024, 3, 1, 8, 15, 0)


def test_text_column_unique_count_and_null_count(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name\nAlice\nBob\nAlice\nNA\n", encoding="utf-8")

    _, stats = compute_stats(str(csv_file), {"name": ColumnType.TEXT})

    assert stats["name"].unique_count == 2
    assert stats["name"].null_count == 1


def test_unparsable_numeric_cell_treated_as_null(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("age\n10\nnot-a-number\n20\n", encoding="utf-8")

    _, stats = compute_stats(str(csv_file), {"age": ColumnType.NUMERIC})

    assert stats["age"].null_count == 1
    assert stats["age"].min_value == 10
    assert stats["age"].max_value == 20


def test_nan_and_infinity_tokens_treated_as_null_not_crashing(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("age\n10\nnan\ninf\n-infinity\n20\n", encoding="utf-8")

    _, stats = compute_stats(str(csv_file), {"age": ColumnType.NUMERIC})

    assert stats["age"].null_count == 3
    assert stats["age"].min_value == 10
    assert stats["age"].max_value == 20
    assert stats["age"].mean_value == 15.0


def test_malformed_rows_counted_in_row_count_but_excluded_from_stats_with_warning(
    capsys: pytest.CaptureFixture[str],
) -> None:
    column_types = {
        "id": ColumnType.NUMERIC,
        "name": ColumnType.TEXT,
        "signup_date": ColumnType.DATE,
        "score": ColumnType.NUMERIC,
    }

    row_count, stats = compute_stats(str(FIXTURES / "malformed_rows.csv"), column_types)

    assert row_count == 5
    assert stats["id"].null_count == 0
    captured = capsys.readouterr()
    assert "row 2" in captured.err
    assert "row 4" in captured.err
