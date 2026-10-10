"""Unit tests for csv_summary.cli."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from csv_summary import cli

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_main_valid_file_exits_0_with_report(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.main([str(FIXTURES / "valid_basic.csv")])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Total rows: 6" in captured.out


def test_main_header_only_exits_0_with_no_data_rows_message(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.main([str(FIXTURES / "header_only.csv")])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "No data rows found"


def test_main_nonexistent_path_exits_1_with_file_not_found_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing.csv"

    exit_code = cli.main([str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert f"Error: file not found: '{missing}'" in captured.err


def test_main_directory_path_exits_1_with_directory_message(capsys: pytest.CaptureFixture[str]) -> None:
    directory = FIXTURES / "a_directory"

    exit_code = cli.main([str(directory)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert f"Error: '{directory}' is a directory, not a file" in captured.err


def test_main_not_utf8_file_exits_1_with_decode_message(capsys: pytest.CaptureFixture[str]) -> None:
    path = FIXTURES / "not_utf8.csv"

    exit_code = cli.main([str(path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert f"Error: '{path}' is not valid UTF-8 text" in captured.err


@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX-only permission semantics")
def test_main_permission_denied_exits_1_with_permission_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    restricted = tmp_path / "restricted.csv"
    restricted.write_text("a,b\n1,2\n", encoding="utf-8")
    restricted.chmod(0)
    try:
        exit_code = cli.main([str(restricted)])
        captured = capsys.readouterr()
        assert exit_code == 1
        assert f"Error: permission denied reading '{restricted}'" in captured.err
    finally:
        restricted.chmod(0o644)


def test_main_unexpected_error_exits_1_with_generic_message(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def _boom(path: str) -> bool:
        raise RuntimeError("boom")

    monkeypatch.setattr(cli.reader, "has_data_rows", _boom)

    exit_code = cli.main([str(FIXTURES / "valid_basic.csv")])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: an unexpected error occurred: boom" in captured.err


def test_main_missing_argument_exits_2() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main([])

    assert exc_info.value.code == 2
