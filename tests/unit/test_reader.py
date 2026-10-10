"""Unit tests for csv_summary.reader."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from csv_summary.models import CsvFileNotFoundError, MalformedRow, RawRow
from csv_summary.reader import has_data_rows, stream_rows

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_has_data_rows_false_for_header_only() -> None:
    assert has_data_rows(str(FIXTURES / "header_only.csv")) is False


def test_has_data_rows_true_for_valid_basic() -> None:
    assert has_data_rows(str(FIXTURES / "valid_basic.csv")) is True


def test_missing_file_raises_csv_file_not_found_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    with pytest.raises(CsvFileNotFoundError):
        stream_rows(str(missing))


def test_directory_path_raises_is_a_directory_error() -> None:
    with pytest.raises(IsADirectoryError):
        stream_rows(str(FIXTURES / "a_directory"))


@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX-only permission semantics")
def test_permission_denied_raises_permission_error(tmp_path: Path) -> None:
    restricted = tmp_path / "restricted.csv"
    restricted.write_text("a,b\n1,2\n", encoding="utf-8")
    restricted.chmod(0)
    try:
        with pytest.raises(PermissionError):
            stream_rows(str(restricted))
    finally:
        restricted.chmod(0o644)


def test_not_utf8_file_raises_unicode_decode_error() -> None:
    with pytest.raises(UnicodeDecodeError):
        stream_rows(str(FIXTURES / "not_utf8.csv"))


def test_malformed_rows_yielded_with_correct_row_numbers() -> None:
    header, rows = stream_rows(str(FIXTURES / "malformed_rows.csv"))
    rows = list(rows)

    assert isinstance(rows[0], RawRow)
    assert isinstance(rows[1], MalformedRow)
    assert rows[1].row_number == 2
    assert isinstance(rows[2], RawRow)
    assert isinstance(rows[3], MalformedRow)
    assert rows[3].row_number == 4
    assert isinstance(rows[4], RawRow)


def test_stream_rows_accepts_injected_file_object() -> None:
    buffer = io.StringIO("a,b\n1,2\n3,4\n")
    header, rows = stream_rows("unused.csv", file_obj=buffer)
    rows = list(rows)

    assert header == ["a", "b"]
    assert rows == [RawRow(1, ["1", "2"]), RawRow(2, ["3", "4"])]
