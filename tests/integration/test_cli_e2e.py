"""End-to-end integration tests invoking `python -m csv_summary` as a subprocess."""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "csv_summary", *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def test_valid_csv_prints_summary_and_exits_0():
    result = _run_cli(str(FIXTURES / "valid.csv"))

    assert result.returncode == 0
    assert "Total rows: 4" in result.stdout
    assert "Column: name (text)" in result.stdout
    assert "Column: age (numeric)" in result.stdout
    assert "Column: joined_date (date)" in result.stdout


def test_missing_file_exits_1_with_stderr_message():
    result = _run_cli(str(FIXTURES / "does_not_exist.csv"))

    assert result.returncode == 1
    assert "Error:" in result.stderr


def test_header_only_file_exits_0_with_message():
    result = _run_cli(str(FIXTURES / "header_only.csv"))

    assert result.returncode == 0
    assert "No data rows found" in result.stdout


def test_mixed_nulls_reports_null_counts():
    result = _run_cli(str(FIXTURES / "mixed_nulls.csv"))

    assert result.returncode == 0
    assert "Total rows: 5" in result.stdout
    assert "nulls:" in result.stdout
