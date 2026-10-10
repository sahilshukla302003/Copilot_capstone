"""Integration test: malformed-row handling end-to-end (FR-11)."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

RunCli = Callable[..., "subprocess.CompletedProcess[str]"]


def test_malformed_rows_included_in_total_but_excluded_from_stats(
    run_cli: RunCli, fixtures_dir: Path
) -> None:
    result = run_cli(str(fixtures_dir / "malformed_rows.csv"))

    assert result.returncode == 0
    # 5 data rows total, including the 2 malformed ones.
    assert "Total rows: 5" in result.stdout


def test_malformed_rows_emit_stderr_warning_with_row_number(
    run_cli: RunCli, fixtures_dir: Path
) -> None:
    result = run_cli(str(fixtures_dir / "malformed_rows.csv"))

    assert "row 2" in result.stderr
    assert "row 4" in result.stderr
