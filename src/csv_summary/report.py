"""Render the final plain-text summary report (FR-03, FR-05-FR-07, FR-12)."""

from __future__ import annotations

from datetime import datetime

from csv_summary.models import (
    ColumnStats,
    DateColumnStats,
    NumericColumnStats,
    TextColumnStats,
)


def _format_number(value: float) -> str:
    """Render value without a trailing .0 when whole, else in fixed-point form."""
    if value == int(value):
        return str(int(value))
    text = f"{value:.4f}".rstrip("0")
    return text if not text.endswith(".") else f"{text}0"


def _format_datetime(value: datetime, has_time_component: bool) -> str:
    """Render value as YYYY-MM-DD, or full ISO timestamp if it carries time info."""
    if has_time_component:
        return value.isoformat(timespec="seconds")
    return value.date().isoformat()


def _render_numeric(stats: NumericColumnStats) -> list[str]:
    """Render the min/max/mean/null-count lines for a numeric column."""
    min_text = _format_number(stats.min_value) if stats.min_value is not None else "N/A"
    max_text = _format_number(stats.max_value) if stats.max_value is not None else "N/A"
    mean_text = _format_number(stats.mean_value) if stats.mean_value is not None else "N/A"
    return [
        f"  min: {min_text}",
        f"  max: {max_text}",
        f"  mean: {mean_text}",
        f"  nulls: {stats.null_count}",
    ]


def _render_text(stats: TextColumnStats) -> list[str]:
    """Render the unique-count/null-count lines for a text column."""
    return [
        f"  unique values: {stats.unique_count}",
        f"  nulls: {stats.null_count}",
    ]


def _render_date(stats: DateColumnStats) -> list[str]:
    """Render the earliest/latest/null-count lines for a date column."""
    earliest = (
        _format_datetime(stats.earliest, stats.has_time_component)
        if stats.earliest is not None
        else "N/A"
    )
    latest = (
        _format_datetime(stats.latest, stats.has_time_component)
        if stats.latest is not None
        else "N/A"
    )
    return [
        f"  earliest: {earliest}",
        f"  latest: {latest}",
        f"  nulls: {stats.null_count}",
    ]


def render(row_count: int, column_stats: dict[str, ColumnStats]) -> str:
    """Build the human-readable, plain-text summary report (never JSON, FR-12)."""
    lines: list[str] = [f"Total rows: {row_count}", ""]

    for column, stats in column_stats.items():
        if isinstance(stats, NumericColumnStats):
            lines.append(f"Column: {column} (numeric)")
            lines.extend(_render_numeric(stats))
        elif isinstance(stats, DateColumnStats):
            lines.append(f"Column: {column} (date)")
            lines.extend(_render_date(stats))
        else:
            lines.append(f"Column: {column} (text)")
            lines.extend(_render_text(stats))
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"
