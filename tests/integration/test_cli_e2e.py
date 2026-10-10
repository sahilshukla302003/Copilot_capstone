"""Smoke test invoking `python -m csv_summary` as a subprocess.

Detailed scenario coverage lives in test_end_to_end_happy_path.py,
test_malformed_rows.py, and test_error_handling.py.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

RunCli = Callable[..., "subprocess.CompletedProcess[str]"]


def test_valid_csv_prints_summary_and_exits_0(run_cli: RunCli, fixtures_dir: Path) -> None:
    result = run_cli(str(fixtures_dir / "valid_basic.csv"))

    assert result.returncode == 0
    assert "Total rows: 6" in result.stdout
    assert "Column: name (text)" in result.stdout
    assert "Column: id (numeric)" in result.stdout
    assert "Column: signup_date (date)" in result.stdout

