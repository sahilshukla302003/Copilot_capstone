# Implementation Plan: CSV Summary Report Generator

## Task Table

| # | Task | Type | File(s) | Depends On | Blocked By | Definition of Done |
|---|------|------|---------|------------|------------|---------------------|
| 1 | Configure package layout | impl | `pyproject.toml`, `src/csv_summary/__init__.py` | — | — | `pyproject.toml` declares the `csv_summary` package under `src/`; `pip install -e .` succeeds; `src/csv_summary/__init__.py` exists (may be empty / version string only). |
| 2 | Test: package import smoke test | test | `tests/unit/test_package.py` | Task 1 | — | `import csv_summary` succeeds in a test; `pytest tests/unit/test_package.py -v` passes. |
| 3 | Define shared data models | impl | `src/csv_summary/models.py` | Task 1 | — | `ColumnType` enum (`NUMERIC`, `TEXT`, `DATE`) and `ColumnStats` dataclass (fields for all three type's stats, all optional except the ones relevant to the column's type) are defined; a `NULL_TOKENS` frozenset (`""`, whitespace-only, `na`, `n/a`, `null`, `nan` case-insensitive) is defined; a `CsvFileNotFoundError(Exception)` type is defined. |
| 4 | Test: data models | test | `tests/unit/test_models.py` | Task 3 | — | Tests confirm `ColumnType` has exactly 3 members, `ColumnStats` can be constructed per type, and a null-token helper function correctly classifies all documented null tokens (case-insensitively) plus a non-null control value. `pytest tests/unit/test_models.py -v` passes. |
| 5 | Implement streaming CSV reader | impl | `src/csv_summary/reader.py` | Task 3 | — | `open_rows(path)` returns a fresh generator of `dict[str, str]` rows via `csv.DictReader` each time it is called (supports being called twice for two-pass reads); raises `CsvFileNotFoundError` for a missing path and `PermissionError` (or wraps it) for an unreadable file; `has_data_rows(path)` returns `False` for a header-only file and `True` otherwise, without loading the whole file. Ragged rows (extra/missing fields vs. header) do not raise — `DictReader`'s `None`-key/`None`-value behavior is documented and tolerated by downstream consumers. |
| 6 | Test: streaming CSV reader | test | `tests/unit/test_reader.py` | Task 5 | — | Tests cover: valid file (rows yielded correctly), missing file (`CsvFileNotFoundError` raised), header-only file (`has_data_rows` is `False`), and a ragged row (does not raise). `pytest tests/unit/test_reader.py -v` passes. |
| 7 | Implement type inference (pass 1) | impl | `src/csv_summary/type_inference.py` | Task 3, Task 5 | — | `infer_types(path) -> dict[str, ColumnType]` streams the file once via `reader.open_rows`, tallies per-column numeric/date/neither parse results (ignoring null tokens), and classifies each column using the ≥90% non-null-match threshold (numeric precedence over date; `YYYY-MM-DD` strict match required for date). Handles an all-null column by defaulting it to `TEXT`. |
| 8 | Test: type inference | test | `tests/unit/test_type_inference.py` | Task 7 | — | Tests cover: a pure numeric column, a pure ISO date column, a pure text column, a mixed column with <90% conformance to any type (classified `TEXT`), and an all-null column (classified `TEXT`). `pytest tests/unit/test_type_inference.py -v` passes. |
| 9 | Implement statistics accumulators (pass 2) | impl | `src/csv_summary/stats.py` | Task 3, Task 5, Task 7 | — | `compute_stats(path, column_types) -> dict[str, ColumnStats]` streams the file once more via `reader.open_rows`, maintaining O(1)-per-column accumulators: numeric (min/max/running mean via Welford or running sum+count, null count), date (min/max `date`, null count), text (`set()` of distinct non-null values for unique count, null count). Returns the total data row count alongside (or as part of) the stats mapping. |
| 10 | Test: statistics accumulators | test | `tests/unit/test_stats.py` | Task 9 | — | Tests cover: numeric column stats (min/max/mean rounded to 2 dp/null count) against a hand-computed fixture, date column stats (earliest/latest/null count), text column stats (unique count/null count), and that null-token variants are correctly excluded from the stats and counted as null. `pytest tests/unit/test_stats.py -v` passes. |
| 11 | Implement report formatter | impl | `src/csv_summary/report.py` | Task 3 | — | `render(row_count: int, stats: dict[str, ColumnStats]) -> str` returns a human-readable plain-text report including total row count and, per column, its type and the type-appropriate statistics; handles a zero-row/no-columns edge case without raising. |
| 12 | Test: report formatter | test | `tests/unit/test_report.py` | Task 11 | — | Tests confirm the rendered string contains the row count and the expected labeled values for one numeric, one text, and one date column fixture. `pytest tests/unit/test_report.py -v` passes. |
| 13 | Implement CLI entrypoint | impl | `src/csv_summary/cli.py` | Task 5, Task 7, Task 9, Task 11 | — | `main(argv: list[str]) -> int` parses exactly one positional `csv_path` argument via `argparse` (wrong arg count exits with argparse's own usage error, code 2); on missing file prints `Error: file not found: <path>` to stderr and returns 1 (FR-08); on header-only file prints `No data rows found` to stdout and returns 0 (FR-09); otherwise runs the two-pass pipeline (`type_inference.infer_types` → `stats.compute_stats` → `report.render`), prints the report to stdout, and returns 0. Any unexpected per-row parse exception is caught and treated as null for that cell (NFR-02) — never propagates out of `main`. |
| 14 | Test: CLI entrypoint (unit) | test | `tests/unit/test_cli.py` | Task 13 | — | Tests invoke `cli.main([...])` directly (capturing stdout/stderr via `capsys`) for: valid file happy path, missing file (asserts return code 1 and stderr message), header-only file (asserts return code 0 and stdout message), and wrong argument count (asserts return code 2). `pytest tests/unit/test_cli.py -v` passes. |
| 15 | Implement module entrypoint | impl | `src/csv_summary/__main__.py` | Task 13 | — | `python -m csv_summary <path>` invokes `cli.main(sys.argv[1:])` and exits with its return code via `sys.exit(...)`. |
| 16 | Create CSV test fixtures | impl | `tests/fixtures/valid.csv`, `tests/fixtures/header_only.csv`, `tests/fixtures/mixed_nulls.csv` | — | — | Three fixture files exist: `valid.csv` (numeric, text, and ISO date columns with a few rows), `header_only.csv` (header row only, zero data rows), `mixed_nulls.csv` (includes blank and `NA`/`null` tokens across column types). All are valid UTF-8 CSV with a header row. |
| 17 | Integration test: end-to-end CLI | test | `tests/integration/test_cli_e2e.py` | Task 15, Task 16 | — | Tests invoke `python -m csv_summary <fixture>` as a subprocess (or call `cli.main` end-to-end) against all three fixtures plus a non-existent path, asserting exit codes and key report content match acceptance criteria AC1–AC6. `pytest tests/integration/test_cli_e2e.py -v` passes. |

## Dependency Graph

```
T1 ──► T2
T1 ──► T3 ──► T4
T3 ──► T5 ──► T6
T3,T5 ──► T7 ──► T8
T3,T5,T7 ──► T9 ──► T10
T3 ──► T11 ──► T12
T5,T7,T9,T11 ──► T13 ──► T14
T13 ──► T15
T16 (independent)
T15,T16 ──► T17
```

## Blocked Tasks
None.

## Definition of Done — Full Pipeline
- All 17 tasks in the task table are marked complete.
- All unit tests pass: `pytest tests/unit/ -v`.
- All integration tests pass: `pytest tests/integration/ -v`.
- Coverage ≥ 80%: `pytest --cov=src --cov-report=term-missing`.
- No bare `except` clauses anywhere in `src/`.
- All public functions in `src/` have type hints (parameters and return types).
- No hardcoded secrets or credentials anywhere in `src/` or `tests/`.
- `python -m csv_summary --help` and `python -m csv_summary <valid.csv>` both work from a clean `pip install -e .`.
- No open Critical or Major findings remain from `output/reports/code-review.md`.
- `docs/` reflects the final implementation (verified in Step 8 — Documentation Sync).
