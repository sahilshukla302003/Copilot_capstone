"""Shared data models, exceptions, and null-token predicate.

This module performs no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ColumnType(Enum):
    """Inferred type of a CSV column."""

    NUMERIC = "numeric"
    TEXT = "text"
    DATE = "date"


# Tokens treated as null/missing per FR-04a, matched case-insensitively.
NULL_TOKENS = frozenset({"", "na", "n/a", "null", "none"})


def is_null_token(raw_value: str) -> bool:
    """Return True if raw_value should be treated as null/missing per FR-04a."""
    return raw_value.strip().lower() in NULL_TOKENS


class CsvFileNotFoundError(Exception):
    """Raised when the requested CSV file does not exist on disk."""

    def __init__(self, path: str) -> None:
        super().__init__(f"CSV file not found: '{path}'")
        self.path = path


@dataclass(frozen=True)
class RawRow:
    """A well-formed data row whose field count matches the header."""

    row_number: int
    fields: list[str]


@dataclass(frozen=True)
class MalformedRow:
    """A data row whose field count differs from the header's field count."""

    row_number: int
    fields: list[str]
    expected_field_count: int


@dataclass
class NumericColumnStats:
    """Aggregated statistics for a column inferred as numeric (FR-05)."""

    null_count: int = 0
    min_value: float | None = None
    max_value: float | None = None
    mean_value: float | None = None


@dataclass
class TextColumnStats:
    """Aggregated statistics for a column inferred as text (FR-06)."""

    null_count: int = 0
    unique_count: int = 0


@dataclass
class DateColumnStats:
    """Aggregated statistics for a column inferred as date (FR-07)."""

    null_count: int = 0
    earliest: datetime | None = None
    latest: datetime | None = None
    has_time_component: bool = False


ColumnStats = NumericColumnStats | TextColumnStats | DateColumnStats
