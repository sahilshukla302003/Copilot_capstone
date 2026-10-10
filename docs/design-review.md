# Design Review: CSV Summary Report Generator

## Summary
The revised architecture closes the previous blocker: § 7 "Error Handling Taxonomy" now enumerates every realistic failure mode at the `cli.py`/`reader.py` boundary (file-not-found, permission-denied, directory-not-file, non-UTF-8 decode, and an unhandled-exception catch-all), each mapped to a specific exception type, stderr message pattern, and exit code, backed by a concrete top-level `try/except` implementation sketch in `cli.py`. This satisfies NFR-04 in full. The remaining findings below are all non-blocking refinements; the architecture is approved for implementation.

## Previous Blocker — Resolution Check

| Previous Finding | Status | Evidence |
|---|---|---|
| Error-handling taxonomy only named `CsvFileNotFoundError`/`PermissionError`; `IsADirectoryError`, `UnicodeDecodeError`, and a catch-all were unmapped | ✅ **Resolved** | § 7 Taxonomy Table rows 1–6 now map all five named failure modes plus a generic catch-all to explicit exception types, stderr message patterns, and exit codes |
| No documented top-level catch-all in `cli.py` for unexpected exceptions | ✅ **Resolved** | § 7 "`cli.py` Top-Level Boundary (Confirmed)" gives a concrete `try/except` ordering (`CsvFileNotFoundError` → `PermissionError` → `IsADirectoryError` → `UnicodeDecodeError` → `Exception`) and states no raw traceback can escape |

## Risk Table

| Risk | Category | Severity | Recommendation |
|------|----------|----------|----------------|
| `reader.py`/`type_inference.py`/`stats.py` each independently open the file by path rather than accepting an injected stream/file-like object or shared file-handle abstraction | Missing Component Interfaces | Medium | Clarify in the impl plan whether these functions accept a path, an open handle, or both — passing an already-open stream (or a factory) improves unit-testability (in-memory `StringIO` fixtures) without changing runtime behavior |
| `RawRow`/`MalformedRow` shapes in `models.py` are named but not structurally specified (field names/types, how a consumer distinguishes a malformed row from a well-formed one while iterating) | Missing Component Interfaces | Low | Add a short data-contract snippet (field names/types) for `RawRow`/`MalformedRow` before implementation planning to avoid divergent assumptions between `reader.py` consumers |
| The two-pass design reads the same file twice; the architecture does not address what happens if the file changes on disk between the two passes (TOCTOU) | Missing Error Handling Strategy | Low | Out of scope for a local CLI tool's trust model; acceptable as-is, but worth a one-line note accepting this as a known limitation |
| Exact in-memory `set` per text column for uniqueness (FR-06) has unbounded worst-case memory growth for adversarially high-cardinality columns; already called out in Security Considerations with no concrete test | Scalability Risks | Medium | Acceptable given the 100MB file-size ceiling as reasoned in the doc; ensure the `verification` step's NFR-01 benchmark fixture includes a high-cardinality text column to empirically confirm the bound holds in practice |
| The row-6 catch-all in § 7 maps *any* exception to a generic "unexpected error occurred" message; correct for robustness, but a bug surfaced as, e.g., a `TypeError` in `stats.py` will look identical to a genuine unanticipated runtime fault | Missing Error Handling Strategy | Low | Acceptable trade-off for a CLI tool (no stack trace leakage); consider noting in code-review that catch-all exceptions should still be logged with full detail if a future `--debug` mode is added — no architecture change required now |
| No logging module usage; all diagnostics go directly to stderr via `print` | Over-engineering / Under-engineering | Low | Appropriate for this CLI's scope (NFR-06); no change required |

## Design Decisions Confirmed
- Error-handling taxonomy (§ 7) is now complete, specific, and ordered from most-specific to least-specific exception handling, with a concrete `try/except` boundary sketch in `cli.py` — fully satisfies NFR-04.
- Streaming/generator pipeline with O(1) per-row memory and bounded accumulator state — correctly sized for the 512MB/100MB budget (NFR-01).
- Two-pass design (type inference, then aggregation) is justified and the trade-off (double I/O vs. memory safety) is explicitly reasoned rather than implicit.
- `csv.reader` (iterator-based) over `csv.DictReader`/`pandas` avoids unnecessary materialization — appropriate technology choice for the constraints.
- No third-party runtime dependencies — satisfies NFR-05 and keeps the security/attack surface minimal.
- Null-token handling (FR-04a) centralized in `models.py` as a single predicate, avoiding duplicated null-checking logic across `type_inference.py` and `stats.py`.
- Malformed-row handling (FR-11) correctly separates "counted in total rows" from "excluded from column statistics," with row numbering ambiguity pre-resolved (1-indexed over data rows).
- Security Considerations section correctly rules out `eval`/`exec`/`pickle`/subprocess execution paths on untrusted CSV content, and confirms no network surface (NFR-02).
- Numeric/date rendering rules (whole-number formatting, date-vs-datetime rendering) are unambiguous and testable as stated.

## Required Changes Before Implementation
None — architecture is approved for implementation.
