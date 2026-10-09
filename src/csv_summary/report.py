"""Render the final plain-text summary report."""

from __future__ import annotations

from csv_summary.models import ColumnStats, ColumnType


def render(row_count: int, stats: dict[str, ColumnStats]) -> str:
    """Build the human-readable summary report string."""
    lines: list[str] = [f"Total rows: {row_count}", ""]

    for column, column_stats in stats.items():
        lines.append(f"Column: {column} ({column_stats.column_type.value})")
        if column_stats.column_type is ColumnType.NUMERIC:
            lines.append(f"  min: {column_stats.min_value}")
            lines.append(f"  max: {column_stats.max_value}")
            lines.append(f"  mean: {column_stats.mean_value}")
            lines.append(f"  nulls: {column_stats.null_count}")
        elif column_stats.column_type is ColumnType.DATE:
            lines.append(f"  earliest: {column_stats.earliest_date}")
            lines.append(f"  latest: {column_stats.latest_date}")
            lines.append(f"  nulls: {column_stats.null_count}")
        else:
            lines.append(f"  unique values: {column_stats.unique_count}")
            lines.append(f"  nulls: {column_stats.null_count}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
