"""Enables `python -m csv_summary`."""

import sys

from csv_summary.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
