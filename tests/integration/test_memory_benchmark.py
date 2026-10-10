"""Integration test: NFR-01 100MB / 512MB peak-RSS memory benchmark."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import psutil
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures"
BENCHMARK_CSV = FIXTURES / "large_benchmark.csv"
PEAK_RSS_BUDGET_KB = 512 * 1024  # 512MB, expressed in KB
_POLL_INTERVAL_SECONDS = 0.05


def _generate_benchmark_csv(size_mb: int = 100) -> None:
    sys.path.insert(0, str(FIXTURES))
    try:
        import generate_large_csv

        generate_large_csv.main(["--size-mb", str(size_mb), "--output", str(BENCHMARK_CSV)])
    finally:
        sys.path.remove(str(FIXTURES))


def _track_peak_rss_kb(pid: int, peak: list[int], stop: threading.Event) -> None:
    """Poll the process's RSS until stop is set, recording the maximum seen."""
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    while not stop.is_set():
        try:
            rss_kb = process.memory_info().rss // 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break
        peak[0] = max(peak[0], rss_kb)
        time.sleep(_POLL_INTERVAL_SECONDS)


@pytest.mark.slow
def test_100mb_csv_stays_within_512mb_peak_rss() -> None:
    if not BENCHMARK_CSV.exists():
        _generate_benchmark_csv(size_mb=100)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")

    peak_rss_kb = [0]
    stop = threading.Event()
    proc = subprocess.Popen(
        [sys.executable, "-m", "csv_summary", str(BENCHMARK_CSV)],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    watcher = threading.Thread(target=_track_peak_rss_kb, args=(proc.pid, peak_rss_kb, stop))
    watcher.start()
    stdout, _stderr = proc.communicate()
    stop.set()
    watcher.join()

    assert proc.returncode == 0
    assert peak_rss_kb[0] <= PEAK_RSS_BUDGET_KB
    assert "Column: unique_text (text)" in stdout
