# Requirements: CSV Summary Report Generator

## 1. Functional Requirements
1. FR-01: The system SHALL accept a single CSV file path as a command-line argument when invoked as `python -m csv_summary <path-to-csv>`.
2. FR-02: The system SHALL read the CSV file and parse its header row to determine column names.
3. FR-03: The system SHALL infer a data type (numeric, text, or date) for each column based on its values.
4. FR-04: The system SHALL compute and print the total number of data rows (excluding the header).
5. FR-05: For each numeric column, the system SHALL compute and print the minimum, maximum, mean, and count of null/missing values.
6. FR-06: For each text column, the system SHALL compute and print the count of unique values and the count of null/missing values.
7. FR-07: For each date column (ISO 8601 format, e.g. `YYYY-MM-DD`), the system SHALL compute and print the earliest date, latest date, and count of null/missing values.
8. FR-08: If the given file path does not exist, the system SHALL print an error message to stderr and exit with status code 1.
9. FR-09: If the CSV file contains only a header row (no data rows), the system SHALL print "No data rows found" to stdout and exit with status code 0.
10. FR-10: The system SHALL print the full summary report to stdout in plain text.

## 2. Non-Functional Requirements
- NFR-01 (Performance): The system SHALL process a CSV file up to 100 MB in size without exceeding 512 MB of peak memory usage (requires streaming/chunked reads rather than loading the entire file into memory at once).
- NFR-02 (Reliability): The system SHALL not crash with an unhandled traceback on malformed CSV rows; it SHALL treat unparsable values as null for the purposes of that column's statistics.
- NFR-03 (Usability): Error messages SHALL be printed to stderr and be understandable without reading source code (e.g. `Error: file not found: <path>`).
- NFR-04 (Portability): The system SHALL run on Python >= 3.11 with no network access required.

## 3. Acceptance Criteria
### FR-01 / FR-10
- **Given** a valid CSV file path
- **When** the tool is invoked via `python -m csv_summary <path>`
- **Then** a summary report is printed to stdout and the process exits with code 0

### FR-08
- **Given** a file path that does not exist
- **When** the tool is invoked
- **Then** an error message is printed to stderr and the process exits with code 1

### FR-09
- **Given** a CSV file with only a header row and no data rows
- **When** the tool is invoked
- **Then** "No data rows found" is printed to stdout and the process exits with code 0

### FR-05
- **Given** a numeric column with some null values
- **When** the summary is generated
- **Then** min, max, mean, and null count are printed for that column

### FR-06
- **Given** a text column
- **When** the summary is generated
- **Then** unique value count and null count are printed for that column

### FR-07
- **Given** a date column in ISO 8601 format
- **When** the summary is generated
- **Then** earliest date, latest date, and null count are printed for that column

### NFR-01
- **Given** a 100 MB CSV file
- **When** the tool processes it
- **Then** peak memory usage stays under 512 MB

## 4. Constraints
- Must be implemented in Python >= 3.11.
- No external network calls or services.
- Must run as a standalone CLI invoked via `python -m csv_summary`.
- No GUI or web interface.

## 5. Out of Scope
- Writing the report to a file (stdout only).
- Visualizations or charts.
- Support for non-CSV formats (e.g., Excel, JSON).
- Interactive/TUI mode.
- Internationalization/localization of output.
- Handling multiple files in a single invocation.

## 6. Design Decisions (resolved)
These were raised as open questions during drafting and are now finalized:
1. **Column type inference precedence**: numeric takes precedence over date unless the column strictly matches `YYYY-MM-DD` format; text is the fallback for anything that doesn't fully parse as numeric or date.
2. **Mixed-type columns**: a column is classified by the type that >= 90% of its non-null values match; non-conforming values are counted as null for statistics purposes.
3. **Null representation**: empty string, whitespace-only, and the literal strings `NA`, `N/A`, `null`, `NaN` (case-insensitive) are treated as null.
4. **Third-party library use**: standard library only (`csv` module with a streaming/chunked read) — no `pandas` — to make the 512 MB/100 MB memory constraint easy to guarantee.
5. **Numeric formatting**: mean values are rounded to 2 decimal places.
6. **Report format**: any clear, human-readable plain-text layout is acceptable; no specific column alignment is required.
