"""Unit tests for csv_summary.models."""

from __future__ import annotations

from csv_summary.models import (
    ColumnType,
    CsvFileNotFoundError,
    DateColumnStats,
    MalformedRow,
    NumericColumnStats,
    RawRow,
    TextColumnStats,
    is_null_token,
)


def test_column_type_has_three_members() -> None:
    assert {member.value for member in ColumnType} == {"numeric", "text", "date"}


def test_is_null_token_empty_string_returns_true() -> None:
    assert is_null_token("") is True


def test_is_null_token_na_mixed_case_returns_true() -> None:
    assert is_null_token("Na") is True
    assert is_null_token("NA") is True
    assert is_null_token("na") is True


def test_is_null_token_n_slash_a_returns_true() -> None:
    assert is_null_token("N/A") is True
    assert is_null_token("n/a") is True


def test_is_null_token_null_returns_true() -> None:
    assert is_null_token("NULL") is True
    assert is_null_token("null") is True


def test_is_null_token_none_returns_true() -> None:
    assert is_null_token("None") is True
    assert is_null_token("NONE") is True


def test_is_null_token_non_null_value_returns_false() -> None:
    assert is_null_token("Alice") is False
    assert is_null_token("123") is False
    assert is_null_token("2023-01-01") is False


def test_raw_row_construction_and_field_access() -> None:
    row = RawRow(row_number=1, fields=["1", "Alice", "2023-01-15"])
    assert row.row_number == 1
    assert row.fields == ["1", "Alice", "2023-01-15"]


def test_malformed_row_construction_and_field_access() -> None:
    row = MalformedRow(row_number=2, fields=["1", "Bob"], expected_field_count=3)
    assert row.row_number == 2
    assert row.fields == ["1", "Bob"]
    assert row.expected_field_count == 3


def test_csv_file_not_found_error_carries_original_path() -> None:
    error = CsvFileNotFoundError("missing.csv")
    assert error.path == "missing.csv"
    assert "missing.csv" in str(error)


def test_numeric_column_stats_defaults() -> None:
    stats = NumericColumnStats()
    assert stats.null_count == 0
    assert stats.min_value is None
    assert stats.max_value is None
    assert stats.mean_value is None


def test_text_column_stats_defaults() -> None:
    stats = TextColumnStats()
    assert stats.null_count == 0
    assert stats.unique_count == 0


def test_date_column_stats_defaults() -> None:
    stats = DateColumnStats()
    assert stats.null_count == 0
    assert stats.earliest is None
    assert stats.latest is None
    assert stats.has_time_component is False
