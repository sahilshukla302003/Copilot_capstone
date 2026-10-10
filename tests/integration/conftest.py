"""Shared fixtures for integration tests: CLI subprocess runner and repo paths."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures"

RunCli = Callable[..., "subprocess.CompletedProcess[str]"]


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the shared tests/fixtures directory."""
    return FIXTURES


@pytest.fixture
def run_cli() -> RunCli:
    """Return a callable that runs `python -m csv_summary` as a subprocess."""

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

    return _run_cli
