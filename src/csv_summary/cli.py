"""CLI entry point for the CSV Summary Report Generator (FR-01, FR-08, FR-09)."""

from __future__ import annotations

import argparse
import sys

from csv_summary import reader, report, stats, type_inference
from csv_summary.models import CsvFileNotFoundError


def _build_parser() -> argparse.ArgumentParser:
    """Build the single-positional-argument CLI parser."""
    parser = argparse.ArgumentParser(
        prog="csv_summary",
        description="Read a CSV file and print a plain-text summary report.",
    )
    parser.add_argument("csv_path", help="Path to the CSV file to summarize.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI pipeline and return the process exit code.

    Wraps the entire pipeline in the single top-level try/except boundary
    from architecture § 7 so no raw traceback can ever reach the user.
    """
    args = _build_parser().parse_args(argv)
    path = args.csv_path

    try:
        if not reader.has_data_rows(path):
            print("No data rows found")
            return 0
        column_types = type_inference.infer_types(path)
        row_count, column_stats = stats.compute_stats(path, column_types)
        print(report.render(row_count, column_stats), end="")
        return 0
    except CsvFileNotFoundError as exc:
        print(f"Error: file not found: '{exc.path}'", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Error: permission denied reading '{path}'", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"Error: '{path}' is a directory, not a file", file=sys.stderr)
        return 1
    except UnicodeDecodeError as exc:
        print(
            f"Error: '{path}' is not valid UTF-8 text "
            f"(decode failed at byte offset {exc.start})",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(f"Error: an unexpected error occurred: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
