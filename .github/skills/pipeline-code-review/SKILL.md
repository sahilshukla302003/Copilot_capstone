---
name: pipeline-code-review
description: Perform a structured code review against a defined checklist covering correctness, security, error handling, test coverage, code clarity, DRY principle, dependency safety, and Python conventions. Produces output/reports/code-review.md with severity-tagged findings and an overall recommendation.
---

# Skill: Pipeline Code Review

## Role
Act as a **senior Python code reviewer**. Your job is to review the implementation against the specification and a structured quality checklist — not against personal preference.

---

## Input
- `src/` directory contents (passed by the caller)
- `tests/` directory contents (passed by the caller)
- `docs/requirements.md` (passed by the caller — review against spec, not assumptions)

---

## Review Checklist

Work through each area systematically. For each finding, record: area, severity, file, line (if applicable), description, and a concrete suggestion.

### Area 1 — Correctness
- Does each component behave as specified in `docs/requirements.md`?
- Does the output match the acceptance criteria?
- Are edge cases from the requirements handled (empty input, boundary values, invalid format)?

### Area 2 — Security
- Are secrets and credentials excluded from output, logs, and source code?
- Is user input validated at **all** entry boundaries (CLI args, file paths, API responses)?
- Are file paths sanitized to prevent path traversal?
- Are there any SQL/command injection risks?

### Area 3 — Error Handling
- Are API failures, missing files, and network errors handled gracefully?
- Do error messages help the user understand what went wrong and how to fix it?
- Are exceptions specific (no bare `except:` or `except Exception:` without logging)?
- Are resources (files, connections) properly closed on error paths?

### Area 4 — Test Coverage
- Do tests cover the **happy path** for every functional requirement?
- Do tests cover the **key edge cases**: Not Found, empty input, invalid format, boundary values?
- Are there tests for error paths (e.g., what happens when a file is missing)?
- Are test assertions meaningful (not just `assert result is not None`)?

### Area 5 — Code Clarity
- Are function and variable names self-explanatory (no single-letter names outside loops)?
- Is complex logic broken into named helper functions?
- Is the code readable without needing to read comments to understand intent?
- Are magic numbers replaced with named constants?

### Area 6 — DRY Principle
- Is there duplicated logic that should be refactored into a shared function?
- Are there copy-pasted blocks that differ only in a parameter?
- Is configuration repeated across multiple files instead of centralized?

### Area 7 — Dependency Safety
- Are all third-party packages pinned to a specific version in `pyproject.toml`?
- Are there any known-vulnerable package versions (check against current knowledge)?
- Are unused imports or dependencies present?

### Area 8 — Python Conventions
- Is the code PEP 8 compliant (naming, spacing, line length)?
- Do all public functions have type hints on parameters and return values?
- Are there bare `except:` clauses (flag as Critical)?
- Are there mutable default arguments (e.g., `def f(x=[])`) (flag as Major)?
- Are f-strings used instead of `%` formatting or `.format()` where applicable?

---

## Severity Definitions

| Severity | Meaning |
|----------|---------|
| **Critical** | Would break functionality or expose a security risk — must be fixed before approval |
| **Major** | Degrades quality, reliability, or maintainability significantly — should be fixed |
| **Minor** | Style, convention, or improvement suggestion — fix if time allows |

---

## Output Format

Write the output to `output/reports/code-review.md`:

```markdown
# Code Review Report

## Summary
- **Result**: Pass / Fail / Needs Changes
- **Total Findings**: X (Critical: N, Major: N, Minor: N)
- **Reviewed Against**: `docs/requirements.md`
- **Files Reviewed**: list of src/ and tests/ files

## Findings

### Area 1 — Correctness
| Severity | File | Line | Description | Suggestion |
|----------|------|------|-------------|------------|
| Critical | `src/foo.py` | 42 | ... | ... |

### Area 2 — Security
_(No findings)_ or table as above

### Area 3 — Error Handling
...

### Area 4 — Test Coverage
...

### Area 5 — Code Clarity
...

### Area 6 — DRY Principle
...

### Area 7 — Dependency Safety
...

### Area 8 — Python Conventions
...

## Overall Recommendation
**Approve** / **Request Changes** / **Reject**

> _Approve_: No Critical findings, ≤ 3 Major findings, implementation meets all requirements.
> _Request Changes_: 1+ Critical findings OR > 3 Major findings OR requirement not met.
> _Reject_: Fundamental design or security flaw requiring re-architecture.

### Required Changes Before Approval
<!-- List only Critical and Major findings that must be resolved -->
1. ...
```

---

## Rules
- Only report **actual findings** — do not invent hypothetical issues
- Always cite the specific file and line number for each finding
- Severity = Critical if it would break functionality **or** expose a security risk
- Always review against `docs/requirements.md` — not against assumptions or personal style
- If a section has no findings, write `_(No findings)_` — do not omit the section
- The Overall Recommendation must be one of: **Approve**, **Request Changes**, or **Reject**
