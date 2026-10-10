"""Integration test: full error-handling taxonomy end-to-end (architecture § 7)."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

RunCli = Callable[..., "subprocess.CompletedProcess[str]"]


def test_nonexistent_path_exits_1_with_file_not_found_message(
    tmp_path: Path, run_cli: RunCli
) -> None:
    missing = tmp_path / "does_not_exist.csv"

    result = run_cli(str(missing))

    assert result.returncode == 1
    assert f"Error: file not found: '{missing}'" in result.stderr


def test_directory_path_exits_1_with_directory_message(run_cli: RunCli, fixtures_dir: Path) -> None:
    directory = fixtures_dir / "a_directory"

    result = run_cli(str(directory))

    assert result.returncode == 1
    assert f"Error: '{directory}' is a directory, not a file" in result.stderr


def test_not_utf8_file_exits_1_with_decode_message(run_cli: RunCli, fixtures_dir: Path) -> None:
    path = fixtures_dir / "not_utf8.csv"

    result = run_cli(str(path))

    assert result.returncode == 1
    assert f"Error: '{path}' is not valid UTF-8 text" in result.stderr


@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX-only permission semantics")
def test_permission_denied_exits_1_with_permission_message(
    tmp_path: Path, run_cli: RunCli
) -> None:
    restricted = tmp_path / "restricted.csv"
    restricted.write_text("a,b\n1,2\n", encoding="utf-8")
    restricted.chmod(0)
    try:
        result = run_cli(str(restricted))
        assert result.returncode == 1
        assert f"Error: permission denied reading '{restricted}'" in result.stderr
    finally:
        restricted.chmod(0o644)


def test_header_only_file_exits_0_with_no_data_rows_message(
    run_cli: RunCli, fixtures_dir: Path
) -> None:
    result = run_cli(str(fixtures_dir / "header_only.csv"))

    assert result.returncode == 0
    assert "No data rows found" in result.stdout
