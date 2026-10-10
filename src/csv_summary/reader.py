"""Streaming CSV row reader: path/encoding validation and malformed-row detection."""

from __future__ import annotations

import csv
import os
from collections.abc import Iterator
from typing import TextIO

from csv_summary.models import CsvFileNotFoundError, MalformedRow, RawRow


def _open_text(path: str) -> TextIO:
    """Open path for reading as UTF-8 (or UTF-8-with-BOM).

    Raises CsvFileNotFoundError for a missing path and IsADirectoryError for a
    directory path, normalizing Windows' PermissionError-on-directory behavior
    to match POSIX's IsADirectoryError.
    """
    if os.path.isdir(path):
        raise IsADirectoryError(f"Is a directory: '{path}'")
    try:
        return open(path, encoding="utf-8-sig", newline="")
    except FileNotFoundError as exc:
        raise CsvFileNotFoundError(path) from exc


def stream_rows(
    path: str, *, file_obj: TextIO | None = None
) -> tuple[list[str], Iterator[RawRow | MalformedRow]]:
    """Return (header, row_iterator) for the CSV at path.

    Opens path (or uses the provided file_obj, e.g. an io.StringIO, for tests),
    reads the header once, and returns a generator yielding each subsequent data
    row as a RawRow (field count matches header) or MalformedRow (it doesn't),
    without ever materializing the full file in memory.
    """
    handle = file_obj if file_obj is not None else _open_text(path)
    csv_reader = csv.reader(handle)
    try:
        header = next(csv_reader)
    except StopIteration:
        header = []

    def _rows() -> Iterator[RawRow | MalformedRow]:
        try:
            for row_number, fields in enumerate(csv_reader, start=1):
                if len(fields) != len(header):
                    yield MalformedRow(row_number, fields, len(header))
                else:
                    yield RawRow(row_number, fields)
        finally:
            if file_obj is None:
                handle.close()

    return header, _rows()


def has_data_rows(path: str) -> bool:
    """Return True if the CSV at path has at least one data row beyond the header."""
    _, rows = stream_rows(path)
    try:
        next(rows)
    except StopIteration:
        return False
    else:
        return True
    finally:
        rows.close()
