"""Enables `python -m csv_summary`."""

from __future__ import annotations

import sys

from csv_summary.cli import main

if __name__ == "__main__":
    sys.exit(main())
