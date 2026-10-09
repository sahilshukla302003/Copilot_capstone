"""Shared data models for the CSV summary pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class ColumnType(Enum):
    """Inferred type of a CSV column."""

    NUMERIC = "numeric"
    TEXT = "text"
    DATE = "date"


# Tokens treated as null/missing, matched case-insensitively after stripping whitespace.
NULL_TOKENS = frozenset({"", "na", "n/a", "null", "nan"})


def is_null_token(raw_value: str | None) -> bool:
    """Return True if raw_value should be treated as null/missing."""
    if raw_value is None:
        return True
    return raw_value.strip().lower() in NULL_TOKENS


class CsvFileNotFoundError(Exception):
    """Raised when the requested CSV file does not exist."""


@dataclass
class ColumnStats:
    """Computed statistics for a single column, shaped by its ColumnType."""

    column_type: ColumnType
    null_count: int = 0

    # Numeric-only fields
    min_value: float | None = None
    max_value: float | None = None
    mean_value: float | None = None

    # Date-only fields
    earliest_date: date | None = None
    latest_date: date | None = None

    # Text-only fields
    unique_count: int | None = None
