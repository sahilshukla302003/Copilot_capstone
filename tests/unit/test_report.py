"""Unit tests for csv_summary.report."""

from datetime import date

from csv_summary.models import ColumnStats, ColumnType
from csv_summary.report import render


def test_render_includes_row_count_and_column_stats():
    stats = {
        "age": ColumnStats(column_type=ColumnType.NUMERIC, min_value=1.0, max_value=5.0, mean_value=3.0, null_count=0),
        "name": ColumnStats(column_type=ColumnType.TEXT, unique_count=2, null_count=1),
        "joined": ColumnStats(
            column_type=ColumnType.DATE,
            earliest_date=date(2024, 1, 1),
            latest_date=date(2024, 2, 1),
            null_count=0,
        ),
    }

    report_text = render(row_count=5, stats=stats)

    assert "Total rows: 5" in report_text
    assert "min: 1.0" in report_text
    assert "unique values: 2" in report_text
    assert "earliest: 2024-01-01" in report_text
