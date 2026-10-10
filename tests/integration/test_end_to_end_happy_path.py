"""Integration test: end-to-end happy path and FR-04-FR-07 type/stat coverage."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

RunCli = Callable[..., "subprocess.CompletedProcess[str]"]


def test_valid_basic_csv_reports_expected_types_and_stats(run_cli: RunCli, fixtures_dir: Path) -> None:
    result = run_cli(str(fixtures_dir / "valid_basic.csv"))

    assert result.returncode == 0
    assert "Total rows: 6" in result.stdout
    assert "Column: id (numeric)" in result.stdout
    assert "Column: name (text)" in result.stdout
    assert "Column: signup_date (date)" in result.stdout
    assert "Column: score (numeric)" in result.stdout
    # id: 1..6 -> min 1, max 6, mean 3.5
    assert "min: 1" in result.stdout
    assert "max: 6" in result.stdout
    assert "mean: 3.5" in result.stdout
    # name: 6 unique, 0 nulls
    assert "unique values: 6" in result.stdout
    # signup_date: earliest/latest
    assert "earliest: 2023-01-15" in result.stdout
    assert "latest: 2023-06-01" in result.stdout


def test_mixed_nulls_csv_reports_correct_null_counts(run_cli: RunCli, fixtures_dir: Path) -> None:
    result = run_cli(str(fixtures_dir / "mixed_nulls.csv"))

    assert result.returncode == 0
    assert "Total rows: 6" in result.stdout
    assert "Column: id (numeric)" in result.stdout
    assert "Column: name (text)" in result.stdout
    assert "Column: signup_date (date)" in result.stdout
    assert "Column: score (numeric)" in result.stdout
    # name column has null tokens: "", "N/A", "None" -> 3 nulls
    # score column has null tokens: "NA", "" -> 2 nulls
    # signup_date column has null tokens: "", "NULL" -> 2 nulls
    # id column has no null tokens -> 0 nulls
    assert "nulls: 0" in result.stdout
    assert "nulls: 3" in result.stdout
    assert "nulls: 2" in result.stdout
    assert result.stdout.count("nulls: 2") == 2
    assert result.stdout.count("nulls:") == 4
