# Test Fixtures

| File | Purpose | Taxonomy row / FR exercised |
|------|---------|------------------------------|
| `valid_basic.csv` | Well-formed CSV with numeric (`id`, `score`), text (`name`), and date (`signup_date`) columns, 6 data rows | FR-02, FR-03, FR-04, FR-05, FR-06, FR-07 |
| `header_only.csv` | Header row with zero data rows | FR-09 (taxonomy row 5) |
| `mixed_nulls.csv` | Mix of empty string, `NA`, `N/A`, `NULL`, `None` (mixed case) across numeric, text, and date columns | FR-04a, FR-05, FR-06, FR-07 |
| `malformed_rows.csv` | Rows with fewer/more fields than the header | FR-11, NFR-03 |
| `not_utf8.csv` | Raw bytes that are not valid UTF-8 / UTF-8-with-BOM | Taxonomy row 4 (`UnicodeDecodeError`) |
| `a_directory/` | Empty directory passed as a CLI path to trigger `IsADirectoryError` | Taxonomy row 3 |
| `generate_large_csv.py` | Deterministic, streaming generator for the NFR-01 100MB memory benchmark | NFR-01 |

No fixture exists for "missing file" or "permission denied" (taxonomy rows 1 and 2): the missing-file case is
exercised against a deliberately nonexistent path, and the permission-denied case against an OS-level
permission-restricted temp file created at test time (POSIX only).
