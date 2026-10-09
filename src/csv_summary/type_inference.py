"""Pass 1: infer each column's type by streaming the file once."""

from __future__ import annotations

import os
from datetime import datetime

from csv_summary.models import ColumnType, is_null_token
from csv_summary.reader import open_rows

_TYPE_MATCH_THRESHOLD = 0.9


def _is_numeric(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


def _is_iso_date(value: str) -> bool:
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
    except ValueError:
        return False
    return True


def infer_types(path: str | os.PathLike[str]) -> dict[str, ColumnType]:
    """Return the inferred ColumnType for every column in the CSV at path."""
    numeric_counts: dict[str, int] = {}
    date_counts: dict[str, int] = {}
    non_null_counts: dict[str, int] = {}
    columns: list[str] = []

    for row in open_rows(path):
        for column, raw_value in row.items():
            if column is None:
                continue
            if column not in non_null_counts:
                columns.append(column)
                numeric_counts[column] = 0
                date_counts[column] = 0
                non_null_counts[column] = 0

            if is_null_token(raw_value):
                continue

            value = raw_value.strip() if raw_value is not None else ""
            non_null_counts[column] += 1
            if _is_numeric(value):
                numeric_counts[column] += 1
            if _is_iso_date(value):
                date_counts[column] += 1

    result: dict[str, ColumnType] = {}
    for column in columns:
        total_non_null = non_null_counts[column]
        if total_non_null == 0:
            result[column] = ColumnType.TEXT
            continue

        numeric_ratio = numeric_counts[column] / total_non_null
        date_ratio = date_counts[column] / total_non_null

        if numeric_ratio >= _TYPE_MATCH_THRESHOLD:
            result[column] = ColumnType.NUMERIC
        elif date_ratio >= _TYPE_MATCH_THRESHOLD:
            result[column] = ColumnType.DATE
        else:
            result[column] = ColumnType.TEXT

    return result
