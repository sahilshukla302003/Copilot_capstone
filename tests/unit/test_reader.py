"""Unit tests for csv_summary.reader."""

import pytest

from csv_summary.models import CsvFileNotFoundError
from csv_summary.reader import has_data_rows, open_rows


def test_open_rows_yields_rows(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    rows = list(open_rows(csv_file))

    assert rows == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]


def test_open_rows_missing_file_raises(tmp_path):
    missing = tmp_path / "missing.csv"

    with pytest.raises(CsvFileNotFoundError):
        list(open_rows(missing))


def test_has_data_rows_false_for_header_only(tmp_path):
    csv_file = tmp_path / "header_only.csv"
    csv_file.write_text("a,b\n", encoding="utf-8")

    assert has_data_rows(csv_file) is False


def test_open_rows_tolerates_ragged_rows(tmp_path):
    csv_file = tmp_path / "ragged.csv"
    csv_file.write_text("a,b\n1\n1,2,3\n", encoding="utf-8")

    rows = list(open_rows(csv_file))

    assert rows[0]["a"] == "1"
    assert rows[0]["b"] is None
    assert rows[1]["a"] == "1"
    assert rows[1]["b"] == "2"
