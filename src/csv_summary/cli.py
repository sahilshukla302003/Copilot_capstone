"""CLI entrypoint for the CSV Summary Report Generator."""

from __future__ import annotations

import argparse
import sys

from csv_summary import reader, report, stats, type_inference
from csv_summary.models import CsvFileNotFoundError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv_summary",
        description="Read a CSV file and print a summary report.",
    )
    parser.add_argument("csv_path", help="Path to the CSV file to summarize.")
    return parser


def main(argv: list[str]) -> int:
    """Run the CLI. Returns the process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if not reader.has_data_rows(args.csv_path):
            print("No data rows found")
            return 0
    except CsvFileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except PermissionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    column_types = type_inference.infer_types(args.csv_path)
    row_count, column_stats = stats.compute_stats(args.csv_path, column_types)
    print(report.render(row_count, column_stats), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
