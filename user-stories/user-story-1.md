# User Story: CSV Summary Report Generator

**As a** data analyst,
**I want** a CLI tool that reads a CSV file and outputs a summary report,
**So that** I can quickly understand the shape and content of any dataset without writing custom scripts.

## Title
CSV Summary Report Generator

## Problem Statement
Data analysts routinely receive unfamiliar CSV files and need a quick, consistent way to understand their shape (row count, columns, types) and basic statistics before deciding how to process them further. Writing a one-off script for this every time is wasteful. This story delivers a single CLI tool that produces a consistent summary report for any CSV file.

## Details
- The tool is invoked from the command line: `python -m csv_summary <path-to-csv>`
- It reads the CSV file and produces a summary report printed to stdout
- The report must include:
  - Total row count (excluding header)
  - Column names and their inferred data types (numeric, text, date)
  - For numeric columns: min, max, mean, and count of null values
  - For text columns: count of unique values and count of null values
  - For date columns: earliest and latest date and count of null values
- If the file does not exist, print a clear error and exit with code 1
- If the file is empty or has only a header row, print a message and exit with code 0
- The tool must handle CSV files up to 100MB without running out of memory

## Acceptance Criteria
1. Given a valid CSV, the tool prints a summary report to stdout
2. Given a non-existent file path, the tool prints an error and exits with code 1
3. Given a CSV with only a header row, the tool prints "No data rows found" and exits with code 0
4. Numeric columns show min, max, mean, and null count
5. Text columns show unique count and null count
6. Date columns (ISO 8601 format) show earliest, latest, and null count
7. The tool processes a 100MB CSV file without exceeding 512MB memory usage

## Constraints
- Must be implemented in Python >= 3.11
- No external network calls or services
- Must run as a standalone CLI (`python -m csv_summary`)

## Out of Scope
- Writing the report to a file (stdout only)
- Visualizations or charts
- Support for non-CSV formats (e.g., Excel, JSON)
- Interactive/TUI mode
