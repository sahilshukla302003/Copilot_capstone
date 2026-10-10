"""Deterministic, streaming generator for the NFR-01 memory-benchmark CSV fixture.

Usage:
    python tests/fixtures/generate_large_csv.py [--rows N | --size-mb N] [--output PATH]

Generates a CSV with a header containing one numeric column, one high-cardinality
unique-text column, and one date column, writing rows one at a time so the
generator itself never exceeds O(1) memory regardless of target size.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from collections.abc import Iterator

HEADER = ["id", "unique_text", "amount", "event_date"]

_BYTES_PER_ROW_ESTIMATE = 48  # rough average row size in bytes, used for --size-mb


def _rows(row_count: int) -> Iterator[str]:
    """Yield CSV data rows (without trailing newline) one at a time."""
    start_date = datetime.date(2020, 1, 1)
    for i in range(row_count):
        event_date = start_date + datetime.timedelta(days=i % 3650)
        amount = round((i % 10000) + (i % 7) / 10, 2)
        yield f"{i},unique-value-{i:012d},{amount},{event_date.isoformat()}"


def generate(output_path: str, *, row_count: int) -> None:
    """Stream row_count data rows of the benchmark CSV to output_path."""
    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(",".join(HEADER) + "\n")
        for row in _rows(row_count):
            handle.write(row + "\n")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="tests/fixtures/large_benchmark.csv")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--rows", type=int, default=None, help="Exact number of data rows.")
    group.add_argument(
        "--size-mb", type=int, default=100, help="Approximate target file size in MB."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: generate the benchmark CSV per --rows or --size-mb."""
    args = _parse_args(argv)
    row_count = args.rows
    if row_count is None:
        row_count = (args.size_mb * 1024 * 1024) // _BYTES_PER_ROW_ESTIMATE
    generate(args.output, row_count=row_count)
    print(f"Wrote {row_count} data rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
