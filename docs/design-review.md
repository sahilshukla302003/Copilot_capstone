# Design Review: CSV Summary Report Generator

## Summary
The architecture is sound and appropriately scoped for a single-purpose CLI tool: the two-pass streaming design directly satisfies the memory constraint (NFR-01), and the component split (reader / type_inference / stats / report) follows single-responsibility cleanly. It is approved for implementation, with a small set of non-blocking gaps that should be addressed during implementation rather than requiring a return to the architecture step.

## Risk Table

| Risk | Category | Severity | Recommendation |
|------|----------|----------|----------------|
| No logging or diagnostic output is defined anywhere in the architecture — only stdout (report) and stderr (user-facing errors) are specified. | Under-engineering | Low | Not required for a stdout-only CLI of this scope; explicitly state in implementation that no logging framework is needed (plain print statements suffice) to avoid the implementation agent adding unnecessary complexity. |
| `ColumnType` and `ColumnStats` are referenced as data structures in component descriptions but their concrete shape (dataclass fields, enum values) is never defined. | Missing Component Interfaces | Medium | Implementation plan should pin down these as explicit `dataclass`/`Enum` definitions (e.g. in a shared `models.py` or within `type_inference.py`/`stats.py`) before coding begins, so `stats.py` and `report.py` agree on the contract. |
| Permission-denied / unreadable file (as opposed to missing file) is mentioned only in the External Dependencies table ("Unreadable/permission-denied file → same handling path") but FR-08 and the acceptance criteria only test the "does not exist" case. | Missing Error Handling Strategy | Medium | Implementation should catch `OSError`/`PermissionError` around the initial `open()` alongside `FileNotFoundError`, and verification should add a test case for a permission-denied file (or document it as a platform-dependent test limitation). |
| The architecture does not state what happens if a row has a different number of fields than the header (ragged CSV rows) — `csv.DictReader` behavior in this case (extra values under `None` key, missing values as `None`) is not addressed. | Missing Error Handling Strategy | Medium | Implementation should explicitly document/handle ragged rows: treat missing fields as null, and either ignore or null-out extra fields beyond the header, consistent with NFR-02 ("treat unparsable values as null"). |
| Two full file reads (pass 1 + pass 2) double the I/O time for very large files; no explicit statement of expected runtime for a 100MB file. | Scalability Risks | Low | Acceptable trade-off per the architecture's own stated rationale (memory correctness over I/O speed); no change needed, but verification should include a rough timing/smoke check on a large generated fixture rather than a strict SLA. |
| The `set()`-based unique-value tracking for text columns (flagged already in the architecture itself) has no enforced upper bound or fallback. | Scalability Risks | Low | Already acknowledged by the architecture as an accepted, documented limitation for this project's scope — no change required; carry the same note into `docs/impl-plan.md` so it isn't silently lost. |
| No explicit mention of how `argparse` will report *usage* errors (e.g., zero or >1 positional arguments) versus the FR-08 "file not found" error — both currently map to generic CLI error handling without distinct exit-code/message guidance. | Missing Component Interfaces | Low | Implementation should use `argparse`'s built-in usage-error exit code (2) for argument-count errors, reserving exit code 1 specifically for the "file not found" business-logic error per FR-08, and document this distinction in `cli.py`. |

## Design Decisions Confirmed
- Two-pass streaming pipeline (type inference pass, then stats pass) — correctly trades one extra file read for guaranteed O(columns) memory, directly satisfying NFR-01.
- Stdlib-only technology choice (`csv`, `datetime`, `argparse`) — appropriate given the explicit "no pandas" decision in requirements and keeps the dependency/security surface minimal.
- Component boundaries (`reader` / `type_inference` / `stats` / `report` / `cli`) — single responsibility per component, matches the data flow narrative, and every component maps back to at least one functional requirement.
- Security considerations are adequate for this tool's threat surface: no shell interpolation, no secrets, CSV values never evaluated — appropriately scoped to a local, offline CLI.
- Error handling for the two acceptance-critical flows (missing file → exit 1, header-only file → exit 0) is clearly specified and testable.

## Required Changes Before Implementation
None — architecture is approved for implementation. The Medium/Low findings above should be carried forward as implementation-plan tasks (data model definitions, ragged-row handling, permission-error handling, argparse exit-code distinction) but do not block starting implementation planning.
