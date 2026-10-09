"""Streaming CSV row reader."""

from __future__ import annotations

import csv
import os
from collections.abc import Iterator
from pathlib import Path

from csv_summary.models import CsvFileNotFoundError


def _validate_readable(path: str | os.PathLike[str]) -> Path:
    file_path = Path(path)
    if not file_path.exists():
        raise CsvFileNotFoundError(f"file not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"permission denied: {file_path}")
    return file_path


def open_rows(path: str | os.PathLike[str]) -> Iterator[dict[str, str | None]]:
    """Yield each data row of the CSV at path as a dict keyed by header name.

    A fresh generator is returned on every call, so the file can be streamed
    multiple times (once per pipeline pass) without buffering it in memory.
    Ragged rows (extra or missing fields relative to the header) are tolerated:
    DictReader puts overflow values under the None key and missing fields as None.
    """
    file_path = _validate_readable(path)

    def _generator() -> Iterator[dict[str, str | None]]:
        with file_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            yield from reader

    return _generator()


def has_data_rows(path: str | os.PathLike[str]) -> bool:
    """Return True if the CSV at path has at least one data row beyond the header."""
    for _ in open_rows(path):
        return True
    return False
