"""Pass 2: compute per-column statistics by streaming the file once more."""

from __future__ import annotations

import os
from datetime import datetime

from csv_summary.models import ColumnStats, ColumnType, is_null_token
from csv_summary.reader import open_rows


class _NumericAccumulator:
    def __init__(self) -> None:
        self.min_value: float | None = None
        self.max_value: float | None = None
        self.sum_value: float = 0.0
        self.count: int = 0
        self.null_count: int = 0

    def add(self, raw_value: str | None) -> None:
        if is_null_token(raw_value):
            self.null_count += 1
            return
        try:
            value = float(raw_value.strip())  # type: ignore[union-attr]
        except (ValueError, AttributeError):
            self.null_count += 1
            return
        self.count += 1
        self.sum_value += value
        self.min_value = value if self.min_value is None else min(self.min_value, value)
        self.max_value = value if self.max_value is None else max(self.max_value, value)

    def to_stats(self) -> ColumnStats:
        mean_value = round(self.sum_value / self.count, 2) if self.count else None
        return ColumnStats(
            column_type=ColumnType.NUMERIC,
            null_count=self.null_count,
            min_value=self.min_value,
            max_value=self.max_value,
            mean_value=mean_value,
        )


class _DateAccumulator:
    def __init__(self) -> None:
        self.earliest = None
        self.latest = None
        self.null_count: int = 0

    def add(self, raw_value: str | None) -> None:
        if is_null_token(raw_value):
            self.null_count += 1
            return
        try:
            parsed = datetime.strptime(raw_value.strip(), "%Y-%m-%d").date()  # type: ignore[union-attr]
        except (ValueError, AttributeError):
            self.null_count += 1
            return
        self.earliest = parsed if self.earliest is None else min(self.earliest, parsed)
        self.latest = parsed if self.latest is None else max(self.latest, parsed)

    def to_stats(self) -> ColumnStats:
        return ColumnStats(
            column_type=ColumnType.DATE,
            null_count=self.null_count,
            earliest_date=self.earliest,
            latest_date=self.latest,
        )


class _TextAccumulator:
    def __init__(self) -> None:
        self.unique_values: set[str] = set()
        self.null_count: int = 0

    def add(self, raw_value: str | None) -> None:
        if is_null_token(raw_value):
            self.null_count += 1
            return
        self.unique_values.add(raw_value.strip())  # type: ignore[union-attr]

    def to_stats(self) -> ColumnStats:
        return ColumnStats(
            column_type=ColumnType.TEXT,
            null_count=self.null_count,
            unique_count=len(self.unique_values),
        )


_Accumulator = _NumericAccumulator | _DateAccumulator | _TextAccumulator


def _new_accumulator(column_type: ColumnType) -> _Accumulator:
    if column_type is ColumnType.NUMERIC:
        return _NumericAccumulator()
    if column_type is ColumnType.DATE:
        return _DateAccumulator()
    return _TextAccumulator()


def compute_stats(
    path: str | os.PathLike[str], column_types: dict[str, ColumnType]
) -> tuple[int, dict[str, ColumnStats]]:
    """Stream the CSV at path once, returning (row_count, per-column ColumnStats)."""
    accumulators: dict[str, _Accumulator] = {
        column: _new_accumulator(column_type) for column, column_type in column_types.items()
    }

    row_count = 0
    for row in open_rows(path):
        row_count += 1
        for column, accumulator in accumulators.items():
            accumulator.add(row.get(column))

    stats = {column: accumulator.to_stats() for column, accumulator in accumulators.items()}
    return row_count, stats
