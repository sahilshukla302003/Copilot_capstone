"""Pass 2: compute per-column statistics by streaming the file once more (FR-05-FR-07, FR-11)."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, time

from csv_summary.models import (
    ColumnStats,
    ColumnType,
    DateColumnStats,
    MalformedRow,
    NumericColumnStats,
    TextColumnStats,
    is_null_token,
)
from csv_summary.reader import stream_rows


@dataclass
class _NumericAccumulator:
    """Constant-memory running min/max/mean/null-count for a numeric column."""

    null_count: int = 0
    count: int = 0
    total: float = 0.0
    min_value: float | None = None
    max_value: float | None = None


@dataclass
class _TextAccumulator:
    """Running exact unique-value set and null-count for a text column."""

    null_count: int = 0
    seen: set[str] = field(default_factory=set)


@dataclass
class _DateAccumulator:
    """Running earliest/latest/null-count for a date column."""

    null_count: int = 0
    earliest: datetime | None = None
    latest: datetime | None = None
    has_time_component: bool = False


_Accumulator = _NumericAccumulator | _TextAccumulator | _DateAccumulator


def _new_accumulator(column_type: ColumnType) -> _Accumulator:
    """Create a fresh, empty accumulator matching column_type."""
    if column_type is ColumnType.NUMERIC:
        return _NumericAccumulator()
    if column_type is ColumnType.DATE:
        return _DateAccumulator()
    return _TextAccumulator()


def _parse_date(value: str) -> tuple[datetime, bool]:
    """Parse value as a date or datetime; return (value, has_time_component)."""
    try:
        return datetime.combine(date.fromisoformat(value), time.min), False
    except ValueError:
        return datetime.fromisoformat(value), True


def _update_numeric(acc: _NumericAccumulator, raw_value: str) -> None:
    """Fold raw_value into a numeric accumulator, treating unparsable text as null."""
    if is_null_token(raw_value):
        acc.null_count += 1
        return
    try:
        value = float(raw_value)
    except ValueError:
        acc.null_count += 1
        return
    if not math.isfinite(value):
        acc.null_count += 1
        return
    acc.count += 1
    acc.total += value
    acc.min_value = value if acc.min_value is None else min(acc.min_value, value)
    acc.max_value = value if acc.max_value is None else max(acc.max_value, value)


def _update_text(acc: _TextAccumulator, raw_value: str) -> None:
    """Fold raw_value into a text accumulator."""
    if is_null_token(raw_value):
        acc.null_count += 1
        return
    acc.seen.add(raw_value)


def _update_date(acc: _DateAccumulator, raw_value: str) -> None:
    """Fold raw_value into a date accumulator, treating unparsable text as null."""
    if is_null_token(raw_value):
        acc.null_count += 1
        return
    try:
        parsed, has_time = _parse_date(raw_value)
    except ValueError:
        acc.null_count += 1
        return
    acc.has_time_component = acc.has_time_component or has_time
    acc.earliest = parsed if acc.earliest is None else min(acc.earliest, parsed)
    acc.latest = parsed if acc.latest is None else max(acc.latest, parsed)


def _update(acc: _Accumulator, raw_value: str) -> None:
    """Dispatch raw_value to the accumulator matching its runtime type."""
    if isinstance(acc, _NumericAccumulator):
        _update_numeric(acc, raw_value)
    elif isinstance(acc, _DateAccumulator):
        _update_date(acc, raw_value)
    else:
        _update_text(acc, raw_value)


def _finalize(acc: _Accumulator) -> ColumnStats:
    """Convert an internal accumulator into its public ColumnStats variant."""
    if isinstance(acc, _NumericAccumulator):
        mean = acc.total / acc.count if acc.count else None
        return NumericColumnStats(acc.null_count, acc.min_value, acc.max_value, mean)
    if isinstance(acc, _DateAccumulator):
        return DateColumnStats(acc.null_count, acc.earliest, acc.latest, acc.has_time_component)
    return TextColumnStats(acc.null_count, len(acc.seen))


def compute_stats(
    path: str, column_types: dict[str, ColumnType]
) -> tuple[int, dict[str, ColumnStats]]:
    """Stream the CSV at path once, returning (row_count, per-column ColumnStats).

    Malformed rows are counted toward row_count, trigger a stderr warning naming
    the 1-indexed data-row number, and are excluded from per-column statistics (FR-11).
    """
    header, rows = stream_rows(path)
    accumulators = {column: _new_accumulator(column_types[column]) for column in header}

    row_count = 0
    try:
        for row in rows:
            row_count += 1
            if isinstance(row, MalformedRow):
                print(
                    f"Warning: row {row.row_number} has {len(row.fields)} field(s), "
                    f"expected {row.expected_field_count}; excluded from statistics",
                    file=sys.stderr,
                )
                continue
            for column, raw_value in zip(header, row.fields):
                _update(accumulators[column], raw_value)
    finally:
        rows.close()

    result = {column: _finalize(acc) for column, acc in accumulators.items()}
    return row_count, result
