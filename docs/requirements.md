# Requirements: CSV Summary Report Generator

## 1. Functional Requirements

1. FR-01: The system SHALL provide a CLI entry point invocable as `python -m csv_summary <path-to-csv>`.
2. FR-02: The system SHALL read the CSV file at the given path and parse its header and data rows. Only comma-delimited CSV files encoded as UTF-8 or UTF-8-with-BOM are supported; other delimiters or encodings produce undefined behavior.
3. FR-03: The system SHALL print a summary report to stdout containing the total row count, excluding the header row. The total row count includes malformed rows (see FR-11).
4. FR-04: The system SHALL infer and report a data type (numeric, text, or date) for each column, using the following heuristics applied to each column's non-null values:
   - **Date**: classified as `date` if at least 90% of non-null values parse successfully as ISO 8601 dates (`YYYY-MM-DD`, optionally with a time component).
   - **Numeric**: classified as `numeric` if at least 90% of non-null values parse successfully as integers or finite floats. Non-finite values (`NaN`, `Infinity`, `-Infinity`) do not count toward the numeric threshold.
   - **Text**: classified as `text` if neither the date nor numeric threshold is met.
   - A column's null values are determined per FR-04a before the above thresholds are evaluated.
5. FR-04a: The system SHALL treat the following values as null when parsing cells: the empty string, and the case-insensitive tokens `NA`, `N/A`, `NULL`, and `None`.
6. FR-05: For each numeric column, the system SHALL report the minimum, maximum, mean, and count of null values.
7. FR-06: For each text column, the system SHALL report the count of unique values and the count of null values.
8. FR-07: For each date column (ISO 8601 format), the system SHALL report the earliest date, latest date, and count of null values.
9. FR-08: If the file path does not exist, the system SHALL print a clear error message to stderr and exit with status code 1.
10. FR-09: If the file is empty or contains only a header row, the system SHALL print "No data rows found" and exit with status code 0.
11. FR-10: The system SHALL process CSV files up to 100MB in size using a streaming/chunked read strategy rather than loading the entire file into memory at once.
12. FR-11: The system SHALL detect rows with a field count different from the header's field count, skip them from per-column statistics, emit a warning to stderr identifying the row number, and still include them in the total row count reported by FR-03.
13. FR-12: The system SHALL print the summary report as plain, human-readable text with one section per column (not JSON or another structured format).

## 2. Non-Functional Requirements

- NFR-01 (Performance): The system SHALL process a 100MB CSV file without exceeding 512MB of peak memory usage. This is verified via an automated benchmark test that measures peak resident set size (RSS) while processing a 100MB generated CSV fixture, run as part of the `verification` pipeline step.
  - Known limitation: the benchmark test measures peak RSS using `psutil` (a test-only dependency, not a runtime dependency of `src/csv_summary`) so it runs cross-platform, including Windows, where the POSIX-only `resource` module is unavailable.
- NFR-02 (Security): The system SHALL make no external network calls or service requests during execution.
- NFR-03 (Reliability): The system SHALL handle malformed CSV rows (e.g., inconsistent column counts, unparsable values) without crashing. Rows with a field count differing from the header are skipped from per-column statistics (with a stderr warning) per FR-11; unparsable individual values within otherwise well-formed rows are treated as null for the purposes of statistics.
- NFR-04 (Usability): Error messages SHALL be human-readable and SHALL identify the specific problem (e.g., missing file, permission denied).
- NFR-05 (Portability): The system SHALL run on Python >= 3.11 with no mandatory third-party runtime dependencies beyond the standard library, unless a dependency is explicitly approved in architecture.
- NFR-06 (Maintainability): The system SHALL be structured as a standalone, runnable module (`python -m csv_summary`) with no interactive/TUI mode.

## 3. Acceptance Criteria

### FR-01 / FR-02 / FR-03
- **Given** a valid, non-empty CSV file with a header and at least one data row
- **When** the user runs `python -m csv_summary <path-to-csv>`
- **Then** the tool prints a summary report to stdout including the total row count (excluding header)

### FR-04
- **Given** a valid CSV with columns of mixed types
- **When** the summary report is generated
- **Then** each column name is listed with an inferred type of `numeric`, `text`, or `date`

### FR-05
- **Given** a numeric column containing some null/empty values
- **When** the summary report is generated
- **Then** the report shows min, max, mean, and null count for that column, and the null count matches the actual number of empty/missing cells

### FR-06
- **Given** a text column containing duplicate and null values
- **When** the summary report is generated
- **Then** the report shows the count of distinct non-null values and the count of null values

### FR-07
- **Given** a date column formatted in ISO 8601 (e.g., `YYYY-MM-DD`) containing some null values
- **When** the summary report is generated
- **Then** the report shows the earliest date, latest date, and null count

### FR-08
- **Given** a file path that does not exist on disk
- **When** the user runs `python -m csv_summary <path-to-csv>`
- **Then** the tool prints a clear error message and exits with status code 1

### FR-09
- **Given** a CSV file that is empty or contains only a header row
- **When** the user runs `python -m csv_summary <path-to-csv>`
- **Then** the tool prints "No data rows found" and exits with status code 0

### FR-10 / NFR-01
- **Given** a CSV file up to 100MB in size
- **When** the tool processes the file
- **Then** the tool completes successfully while peak memory usage, measured as peak RSS via the automated 100MB-fixture benchmark in the verification step, stays at or below 512MB

### FR-11
- **Given** a CSV file containing one or more rows with a field count different from the header's field count
- **When** the summary report is generated
- **Then** each malformed row is excluded from per-column statistics, a warning is written to stderr identifying the row number, and the row is still included in the total row count reported by FR-03

### FR-12
- **Given** any valid CSV input
- **When** the summary report is generated
- **Then** the report is emitted as plain human-readable text on stdout, with one section per column, and is not JSON or any other structured/serialized format

## 4. Constraints

- Must be implemented in Python >= 3.11.
- No external network calls or services are permitted at runtime.
- Must run as a standalone CLI via `python -m csv_summary`.
- Output is stdout only; no files are written by the tool itself. Output format is plain human-readable text (not JSON).
- Must handle CSV files up to 100MB without exceeding 512MB peak RSS, as verified by an automated benchmark using a 100MB generated CSV fixture.
- Only comma-delimited CSV files encoded as UTF-8 or UTF-8-with-BOM are supported.

## 5. Out of Scope

- Writing the report to a file (stdout only).
- Visualizations or charts.
- Support for non-CSV formats (e.g., Excel, JSON).
- Interactive/TUI mode.
- Support for CSV files larger than 100MB.
- Internationalized/locale-specific number or date formats beyond ISO 8601 dates.
- Schema validation or data cleaning/transformation features.

## 6. Resolved Decisions

All previously open questions have been reviewed and confirmed by the user. The following decisions are final and are reflected in the relevant FR/NFR/AC sections above:

1. **Date detection** — A column is classified as `date` if at least 90% of its non-null values parse as ISO 8601 dates (FR-04).
2. **Numeric detection** — A column is classified as `numeric` if at least 90% of its non-null values parse as int/float (FR-04).
3. **Null tokens** — Empty string and the case-insensitive tokens `NA`, `N/A`, `NULL`, `None` are treated as null (FR-04a).
4. **Output format** — Plain human-readable text, one section per column; not JSON (FR-12, Constraints).
5. **CSV dialect** — Comma-delimited, UTF-8 or UTF-8-with-BOM only (FR-02, Constraints).
6. **Malformed row handling** — Rows with a mismatched field count are skipped from per-column statistics with a stderr warning, but still counted in the total row count (FR-11, NFR-03).
7. **Memory measurement** — Peak RSS measured via an automated benchmark test using a 100MB generated CSV fixture, verified in the `verification` pipeline step (NFR-01).
