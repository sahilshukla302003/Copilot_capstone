"""Unit tests for csv_summary.report."""

from __future__ import annotations

from datetime import datetime

from csv_summary.models import DateColumnStats, NumericColumnStats, TextColumnStats
from csv_summary.report import render


def test_whole_numeric_value_rendered_without_trailing_zero() -> None:
    stats = {"score": NumericColumnStats(null_count=0, min_value=1.0, max_value=5.0, mean_value=3.0)}

    report_text = render(row_count=2, column_stats=stats)

    assert "min: 1" in report_text
    assert "max: 5" in report_text
    assert "mean: 3" in report_text


def test_fractional_mean_rendered_in_fixed_point_form() -> None:
    stats = {"score": NumericColumnStats(null_count=0, min_value=1.0, max_value=5.0, mean_value=3.3333)}

    report_text = render(row_count=3, column_stats=stats)

    assert "mean: 3.3333" in report_text


def test_date_only_column_rendered_as_yyyy_mm_dd() -> None:
    stats = {
        "joined": DateColumnStats(
            null_count=0,
            earliest=datetime(2024, 1, 1),
            latest=datetime(2024, 2, 1),
            has_time_component=False,
        )
    }

    report_text = render(row_count=2, column_stats=stats)

    assert "earliest: 2024-01-01" in report_text
    assert "latest: 2024-02-01" in report_text


def test_mixed_date_datetime_column_rendered_with_full_timestamp() -> None:
    stats = {
        "joined": DateColumnStats(
            null_count=0,
            earliest=datetime(2024, 1, 1),
            latest=datetime(2024, 2, 1, 10, 30, 0),
            has_time_component=True,
        )
    }

    report_text = render(row_count=2, column_stats=stats)

    assert "earliest: 2024-01-01T00:00:00" in report_text
    assert "latest: 2024-02-01T10:30:00" in report_text


def test_output_has_one_section_per_column_and_total_row_count() -> None:
    stats = {
        "score": NumericColumnStats(null_count=0, min_value=1.0, max_value=5.0, mean_value=3.0),
        "name": TextColumnStats(null_count=1, unique_count=2),
    }

    report_text = render(row_count=5, column_stats=stats)

    assert "Total rows: 5" in report_text
    assert "Column: score (numeric)" in report_text
    assert "Column: name (text)" in report_text


def test_output_is_plain_text_not_json() -> None:
    stats = {"name": TextColumnStats(null_count=0, unique_count=1)}

    report_text = render(row_count=1, column_stats=stats)

    assert "{" not in report_text
    assert "[" not in report_text
