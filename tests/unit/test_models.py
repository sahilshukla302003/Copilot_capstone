"""Unit tests for csv_summary.models."""

from csv_summary.models import ColumnStats, ColumnType, is_null_token


def test_column_type_has_three_members() -> None:
    assert {member.value for member in ColumnType} == {"numeric", "text", "date"}


def test_column_stats_constructs_per_type() -> None:
    numeric = ColumnStats(column_type=ColumnType.NUMERIC, min_value=1.0, max_value=2.0, mean_value=1.5)
    text = ColumnStats(column_type=ColumnType.TEXT, unique_count=3)
    assert numeric.column_type is ColumnType.NUMERIC
    assert text.unique_count == 3


def test_is_null_token_recognizes_all_documented_tokens() -> None:
    for token in ["", "  ", "NA", "n/a", "Null", "NaN", "nan"]:
        assert is_null_token(token) is True


def test_is_null_token_rejects_non_null_value() -> None:
    assert is_null_token("42") is False
    assert is_null_token(None) is True
