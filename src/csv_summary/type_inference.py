"""Pass 1: infer each column's type by streaming the file once (FR-04)."""

from __future__ import annotations

import math
import re
from datetime import date, datetime

from csv_summary.models import ColumnType, MalformedRow, is_null_token
from csv_summary.reader import stream_rows

_TYPE_MATCH_THRESHOLD = 0.9

# Require the YYYY-MM-DD extended format, optionally followed by a time
# component, so compact/basic ISO 8601 forms (e.g. "20230115") are rejected.
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ].*)?$")


def _is_numeric(value: str) -> bool:
    """Return True if value parses as a finite int or float."""
    try:
        parsed = float(value)
    except ValueError:
        return False
    return math.isfinite(parsed)


def _is_iso_date(value: str) -> bool:
    """Return True if value parses as an ISO 8601 date or datetime."""
    if not _ISO_DATE_RE.match(value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        pass
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def infer_types(path: str) -> dict[str, ColumnType]:
    """Return the inferred ColumnType for every column in the CSV at path."""
    header, rows = stream_rows(path)
    numeric_counts = dict.fromkeys(header, 0)
    date_counts = dict.fromkeys(header, 0)
    non_null_counts = dict.fromkeys(header, 0)

    try:
        for row in rows:
            if isinstance(row, MalformedRow):
                continue
            for column, raw_value in zip(header, row.fields):
                if is_null_token(raw_value):
                    continue
                non_null_counts[column] += 1
                if _is_iso_date(raw_value):
                    date_counts[column] += 1
                elif _is_numeric(raw_value):
                    numeric_counts[column] += 1
    finally:
        rows.close()

    result: dict[str, ColumnType] = {}
    for column in header:
        total = non_null_counts[column]
        if total == 0:
            result[column] = ColumnType.TEXT
            continue
        if date_counts[column] / total >= _TYPE_MATCH_THRESHOLD:
            result[column] = ColumnType.DATE
        elif numeric_counts[column] / total >= _TYPE_MATCH_THRESHOLD:
            result[column] = ColumnType.NUMERIC
        else:
            result[column] = ColumnType.TEXT
    return result
