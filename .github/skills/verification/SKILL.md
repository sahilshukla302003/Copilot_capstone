---
name: verification
description: Run the test suite, validate output quality against acceptance criteria, and produce a structured results report. Acts as the final QA gate before the PR step. Produces output/test-results/results.md with a PASS/FAIL verdict.
---

# Skill: Verification

## Role
Act as a **QA engineer running final acceptance testing**. Your job is to run all tests, measure coverage, validate that every acceptance criterion is covered by a test, and produce a structured results report.

---

## Input
- `src/` directory contents (passed by the caller)
- `tests/` directory contents (passed by the caller)
- `docs/requirements.md` — acceptance criteria to validate against

---

## Verification Steps

### Step 1 — Run Unit Tests
```bash
pytest tests/unit/ -v
```
Record: total tests, passed, failed, skipped, and the full output for any failures.

### Step 2 — Run Integration Tests
```bash
pytest tests/integration/ -v
```
Record: total tests, passed, failed, skipped, and the full output for any failures.

### Step 3 — Check Test Coverage
```bash
pytest --cov=src --cov-report=term-missing
```
Record: overall coverage percentage and per-module breakdown. Flag any module below 80%.

### Step 4 — Validate Acceptance Criteria Coverage
For each acceptance criterion in `docs/requirements.md`:
- Find the test(s) that validate it
- If no test exists for a criterion, flag it as a **Gap**

### Step 5 — Identify Gaps
List all acceptance criteria with zero test coverage. A gap is a blocker — the implementation cannot be approved if any acceptance criterion is untested.

---

## Output Format

Write the output to `output/test-results/results.md`:

```markdown
# Test Results

## Test Run Summary
| Suite | Total | Passed | Failed | Skipped |
|-------|-------|--------|--------|---------|
| Unit Tests | N | N | N | N |
| Integration Tests | N | N | N | N |
| **Total** | N | N | N | N |

## Failure Details
<!-- Include full pytest output for each failing test -->
### <test_name>
```
FAILED tests/unit/test_foo.py::test_bar - AssertionError: ...
```

_(If no failures, write: "No failures.")_

## Coverage Report
| Module | Coverage % | Missing Lines |
|--------|------------|---------------|
| `src/module.py` | 87% | 45, 67, 102 |
| **Overall** | XX% | — |

⚠️ Modules below 80% threshold:
- `src/foo.py` — 62% ← below threshold

_(If all modules ≥ 80%, write: "All modules meet the 80% coverage threshold.")_

## Acceptance Criteria Coverage
| Criterion ID | Description | Covered By | Status |
|-------------|-------------|------------|--------|
| FR-01 | <criterion text> | `tests/unit/test_foo.py::test_bar` | ✅ Covered |
| FR-02 | <criterion text> | — | ❌ Gap |

## Gaps
<!-- Acceptance criteria with no test coverage -->
| Criterion ID | Description | Impact |
|-------------|-------------|--------|
| FR-02 | ... | Blocker — cannot approve without test |

_(If no gaps, write: "No gaps identified.")_

## Final Verdict

**PASS** / **FAIL**

### Pass Criteria
- [x/❌] All unit tests pass
- [x/❌] All integration tests pass  
- [x/❌] Overall coverage ≥ 80%
- [x/❌] No open Critical findings from code review
- [x/❌] All acceptance criteria covered by at least one test

> **Verdict: PASS** — All criteria met. Ready for PR.
> **Verdict: FAIL** — See gaps and failures above. Return to implementation.
```

---

## Pass Criteria

The verification passes when **all** of the following are true:
| Criterion | Threshold |
|-----------|-----------|
| All unit tests | Pass (0 failures) |
| All integration tests | Pass (0 failures) |
| Overall coverage | ≥ 80% |
| No open Critical code review findings | From `output/reports/code-review.md` |
| All acceptance criteria | Covered by ≥ 1 test |

If **any** criterion is not met, the verdict is **FAIL** and the orchestrator must return to the implementation agent with a list of what failed.

---

## Rules
- Run all three `pytest` commands — do not skip any step
- A FAIL verdict must include a concrete list of what needs fixing (failing tests, gaps, low-coverage modules)
- Do not modify `src/` or `tests/` — this is a read-only verification step
- If `output/reports/code-review.md` does not exist, note it as a missing prerequisite and flag it to the caller
- The Final Verdict must be exactly **PASS** or **FAIL** — no partial verdicts
