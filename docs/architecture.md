# Architecture: CSV Summary Report Generator

## 1. Component Overview

### System Overview
A single-purpose Python CLI (`python -m csv_summary <path>`) that streams a CSV file in two bounded passes — one to infer each column's type, one to compute its statistics — and prints a plain-text summary report to stdout. No data is ever loaded fully into memory, keeping peak memory well under the 512 MB ceiling for 100 MB inputs.

### Component Diagram
```
┌────────────┐     ┌───────────────┐     ┌────────────────────┐     ┌──────────────┐     ┌─────────────┐
│    cli.py  │────►│  reader.py    │────►│ type_inference.py  │────►│  stats.py    │────►│  report.py  │
│ (entrypoint│     │ (streaming    │     │ (decides column    │     │ (per-column  │     │ (formats    │
│  + errors) │     │  CSV rows)    │     │  type per pass 1)  │     │  accumulators│     │  stdout     │
└────────────┘     └───────────────┘     └────────────────────┘     │  pass 2)     │     │  text)      │
                                                                      └──────────────┘     └─────────────┘
```
`models.py` (not pictured) underlies every component above, supplying the shared `ColumnType`/`ColumnStats` types and null-token rules.

### Component Descriptions
| Component | Responsibility | Interfaces |
|-----------|---------------|------------|
| `cli.py` | Parses argv, validates the file path exists, drives the two-pass pipeline, maps exceptions to exit codes (0/1), prints to stdout/stderr. | Input: `sys.argv`. Output: process exit code + stdout/stderr text. |
| `reader.py` | Opens the CSV file and yields rows as an iterator using the stdlib `csv` module; never materializes the whole file in memory; raises a typed `FileNotFoundError`-derived exception if the path is missing. | Input: file path. Output: generator of `dict[str, str]` rows (via `csv.DictReader`). |
| `type_inference.py` | Pass 1 — for each column, tallies how many non-null values parse as numeric / date / neither; decides the column's final type (`numeric`, `date`, `text`) using the 90% threshold rule from requirements. | Input: row generator. Output: `dict[str, ColumnType]`. |
| `stats.py` | Pass 2 — given the decided column types, streams the file again and maintains O(1)-memory-per-column accumulators (min/max/running mean for numeric, min/max date for date, a `set()` of seen values + count for text) plus null counts. | Input: row generator + `dict[str, ColumnType]`. Output: `dict[str, ColumnStats]`. |
| `report.py` | Formats the row count and per-column `ColumnStats` into a human-readable plain-text report. | Input: row count + `dict[str, ColumnStats]`. Output: `str` (printed by `cli.py`). |
| `__main__.py` | Enables `python -m csv_summary` by delegating to `cli.main()`. | Input: none. Output: none (process entry). |
| `models.py` | Shared data contracts used by every other component: `ColumnType` enum, `ColumnStats` dataclass, the `NULL_TOKENS` set with `is_null_token()`, and the `CsvFileNotFoundError` exception type. | Input: none (pure data definitions). Output: types imported by `reader.py`, `type_inference.py`, `stats.py`, `report.py`, `cli.py`. |

---

## 2. Data Flow

1. `__main__.py` calls `cli.main(sys.argv[1:])`.
2. `cli.py` validates exactly one argument was given and that the path exists; on missing-file it prints `Error: file not found: <path>` to stderr and exits 1 (FR-08).
3. `cli.py` opens the file once via `reader.open_rows(path)` to check whether any data rows exist. If the CSV has a header but zero data rows, `cli.py` prints `No data rows found` and exits 0 (FR-09) without running either analysis pass.
4. **Pass 1 (type inference)**: `reader.open_rows(path)` is re-opened as a fresh generator; `type_inference.infer_types(rows)` streams through it once, tallying per-column parse-success counts, and returns the decided `ColumnType` per column (FR-03).
5. **Pass 2 (statistics)**: `reader.open_rows(path)` is re-opened as a fresh generator again; `stats.compute_stats(rows, column_types)` streams through it once, updating the appropriate accumulator per column per row (FR-04–FR-07).
6. `report.render(row_count, column_stats)` builds the final plain-text report string.
7. `cli.py` prints the report to stdout and exits 0.
8. Any unexpected parse error on a single malformed row is caught per-row and the value is treated as null for that column (NFR-02) — never crashes the whole run.

Two sequential streaming passes over the same file keep memory bounded (NFR-01): at no point does the program hold more than one row plus small fixed-size per-column accumulators in memory.

---

## 3. Technology Choices
| Technology | Purpose | Justification |
|------------|---------|----------------|
| Python 3.11+ | Runtime | Project requirement (constraint from requirements doc). |
| `csv` (stdlib, `DictReader`) | CSV parsing | Streams rows lazily; avoids pulling the whole file into memory; no extra dependency. |
| `datetime` (stdlib) | Date parsing/validation for date columns | Handles ISO 8601 `YYYY-MM-DD` parsing/validation without extra dependencies. |
| `argparse` (stdlib) | CLI argument parsing | Standard, dependency-free, clear error messages for a single positional argument. |
| `dataclasses` / `enum` (stdlib) | Shared data models (`ColumnType`, `ColumnStats`) in `models.py` | Avoids a hand-rolled class hierarchy; gives free `__repr__`/equality for tests. |
| No `pandas` / third-party deps | — | Requirements doc (decision #4) explicitly chose stdlib-only to make the 512 MB/100 MB memory ceiling straightforward to guarantee and keep the dependency footprint at zero. |

---

## 4. External Dependencies
| Dependency | Type | Purpose | Failure Mode |
|------------|------|---------|--------------|
| Local filesystem CSV file | File | Sole data input to the tool | Missing file → caught in `cli.py`, printed to stderr, exit code 1 (FR-08). Unreadable/permission-denied file → same handling path **only on the initial check** (see ⚠️ DEVIATION note in `output/reports/doc-sync-report.md`); a file that becomes unreadable mid-run during pass 1/2 currently propagates uncaught. |
| None (no network, no DB, no external APIs) | — | — | — |

---

## 5. Security Considerations
- **Input validation**: the file path argument is validated to exist and be a regular file before any parsing begins; no path is executed, evaluated, or passed to a shell — `open()` is called directly with no shell interpolation, eliminating command/path injection risk.
- **Data sanitization**: CSV cell values are only ever used as data (parsed into numbers/dates or counted as text) — never evaluated, formatted into shell commands, or used to construct file paths, removing CSV/formula-injection execution risk (`csv.DictReader` returns plain strings, not formulas).
- **Resource exhaustion**: the two-pass streaming design bounds memory to O(number of columns), independent of file size, directly satisfying NFR-01 and preventing a maliciously large file from causing an OOM-based denial of service.
- **Secrets management**: not applicable — the tool has no credentials, tokens, or network calls.
- **Error messages**: error output reflects only the user-supplied path back to the user (no internal stack traces leaked to stdout/stderr in the normal error path), avoiding information disclosure about the host filesystem.

