---
name: documentation-sync
description: Keep docs/ files in sync with actual source code after implementation. Diffs the current code against what the docs describe, updates affected sections, and produces a sync report listing every change made.
---

# Skill: Documentation Sync

## Role
Act as a **technical writer reviewing code changes**. Your job is to ensure that `docs/` accurately reflects the final state of `src/` — without rewriting accurate sections or losing design history.

---

## Input
- Contents of the `src/` directory (passed by the caller)
- Contents of existing `docs/*.md` files (passed by the caller)

---

## Sync Process

### Step 1 — Inventory the Code
Scan `src/` and build a list of:
- All public modules, classes, functions, and their signatures
- All third-party dependencies imported
- All configuration or environment variables read
- All CLI entry points, endpoints, or public APIs

### Step 2 — Inventory the Docs
For each `docs/*.md` file, identify all sections that describe:
- Components, classes, or functions by name
- Data flows or processing steps
- Technology choices and dependencies
- API or CLI interfaces

### Step 3 — Diff Code vs Docs
Compare the two inventories and flag:
| Change Type | Action |
|-------------|--------|
| New function/class not in docs | Add documentation |
| Removed function/class still referenced in docs | Mark as `[DEPRECATED]` |
| Changed signature or behavior | Update the affected section |
| New dependency not listed | Add to technology/dependency table |
| Removed dependency still listed | Remove from table |
| New CLI flag or config option | Document it |

### Step 4 — Apply Updates
- Edit only the sections that need updating — do not rewrite accurate sections
- Preserve all design decisions and rationale — only update factual descriptions
- Use `[DEPRECATED as of implementation]` tag for removed items instead of deleting

### Step 5 — Write Sync Report
Produce a concise summary of what changed.

---

## Output

### Primary Output
In-place updates to affected `docs/*.md` files. Apply only targeted, minimal edits.

### Sync Report (append to bottom of the relevant doc or return inline)
```markdown
## Documentation Sync Report
_Synced: <date>_

| Change | File | Section | Description |
|--------|------|---------|-------------|
| Added | docs/architecture.md | Component Descriptions | Added `csv_parser.parse_file()` |
| Updated | docs/architecture.md | Technology Choices | Removed `pandas`; added `csv` (stdlib) |
| Deprecated | docs/architecture.md | Component Descriptions | `DataLoader` class removed from src/ |
| No change | docs/requirements.md | — | All requirements still accurate |
```

---

## Quality Criteria
- Every public function/class in `src/` has a corresponding entry in `docs/`
- No `docs/` section references code that no longer exists (unless tagged `[DEPRECATED]`)
- Design decisions and rationale are preserved — only factual descriptions are updated
- The sync report lists every change made — no silent edits

---

## Rules
- **Never delete** documented design decisions — only update factual descriptions
- **Never rewrite** sections that are still accurate — do the minimum necessary
- Deprecated items use the tag `[DEPRECATED as of implementation]` and remain in the doc
- Keep documentation **concise** — do not add padding or restate obvious information
- If a doc section cannot be reconciled with the code (e.g., conflicting design), flag it in the sync report as `CONFLICT` and surface it to the caller for resolution
