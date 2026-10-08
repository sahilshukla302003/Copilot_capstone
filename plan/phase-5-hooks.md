# Phase 5 — Quality Gates & Logging

## Goal
Ensure the orchestrator validates each specialist agent's output and maintains a run log after every step. GitHub Copilot has no external hook system — there are no shell scripts, no settings.json hooks, and no PreToolUse/PostToolUse/Stop events. All gate checks, changelog logging, retry tracking, resume logic, and the final pipeline summary are implemented as **inline logic inside `.github/agents/orchestrator.md`** (specified in Phase 4).

This phase documents what that inline logic must cover and provides verification steps to confirm it is correctly implemented.

---

## Prerequisites
- Phase 4 complete (`.github/agents/orchestrator.md` exists)

---

## Why No External Hooks?
Claude Code had a hooks system (PreToolUse / PostToolUse / Stop events triggered shell scripts via `.claude/settings.json`). GitHub Copilot agents do not have an equivalent mechanism. The orchestrator agent itself is responsible for all side effects that hooks would have handled:

| Claude Code Hook (old) | Replacement in orchestrator.md (new) |
|---|---|
| PreToolUse / Agent → log to changelog | Orchestrator appends changelog entry before invoking each specialist |
| PostToolUse / Write → validate non-empty | Orchestrator reads output file after each invocation and checks size > 0 |
| Stop → print pipeline summary | Orchestrator prints summary table after Step 9 completes |

---

## Gates and Logging to Verify in `orchestrator.md`

### Gate 1 — Output File Existence & Non-Empty Check
After invoking each specialist agent, the orchestrator must:
- Read the expected output file
- Check it exists AND has content (size > 0)
- If the check fails: display a clear error message stating which step failed and which file is missing, then stop — do not invoke the next specialist
- If the check passes: proceed to the human approval prompt

**Applies to all 9 steps.** Expected output files per step:

| Step | Expected Output File |
|---|---|
| 1 — Requirements | `docs/requirements.md` |
| 2 — Architecture | `docs/architecture.md` |
| 3 — Design Review | `docs/design-review.md` |
| 4 — Impl Planning | `docs/impl-plan.md` |
| 5 — Implementation | at least one `.py` file in `src/` |
| 6 — Code Review | `output/reports/code-review.md` |
| 7 — Verification | `output/test-results/results.md` |
| 8 — Doc Sync | `output/reports/doc-sync-report.md` |
| 9 — PR | PR URL returned |

---

### Gate 2 — Changelog Logging
After each step is approved (not just completed — only after human approval), the orchestrator must append a timestamped entry to `docs/changelog.md`.

**Required entry format:**
```markdown
## [YYYY-MM-DDTHH:MM:SSZ] Step N — <step name>
- Agent invoked: <specialist agent name>
- Output: <output file path>
- Status: approved
```

**Rules:**
- Timestamp must be ISO 8601 UTC
- Entry is only written after the user approves — not on revise or abort
- One entry per approved step; no duplicate entries on retry

---

### Gate 3 — Retry Tracking
For steps with feedback loops (Design Review → Architecture, Code Review/Verification → Implementation):
- The orchestrator must track how many times the loop has been attempted
- After 2 retries, stop looping and escalate to the user with a clear message:
  > "Step N has failed 2 times. Here is what went wrong: [summary]. Please review and choose: retry manually / abort pipeline."
- The retry counter must reset when moving to a new step

---

### Gate 4 — Resume Guard
On startup, before Step 1 (unless `--fresh` is passed):
- Check which output files from the table above already exist and are non-empty
- For each existing output file, skip the corresponding step and inform the user:
  > "Skipping Step N (output already exists): <file path>"
- After listing all skipped steps, ask: "Resuming from Step N. Continue? (y/n)"
- If `--fresh` is passed, ignore existing files and regenerate everything from Step 1

---

### Gate 5 — Pipeline Summary
After Step 9 completes (PR URL returned and changelog entry written), the orchestrator must print a summary table:

```
========================================
  PIPELINE RUN COMPLETE
========================================
  Step 1  Requirements        docs/requirements.md          [OK]
  Step 2  Architecture        docs/architecture.md          [OK]
  Step 3  Design Review       docs/design-review.md         [OK]
  Step 4  Impl Planning       docs/impl-plan.md             [OK]
  Step 5  Implementation      src/ (<N> .py files)          [OK]
  Step 6  Code Review         output/reports/code-review.md [OK]
  Step 7  Verification        output/test-results/results.md[OK]
  Step 8  Doc Sync            output/reports/doc-sync-report.md [OK]
  Step 9  PR                  <PR URL>                      [OK]
========================================
```
Lines where the output file is missing or empty show `[--]` instead of `[OK]`.

---

## Deliverables Checklist
All items below are verified inside `.github/agents/orchestrator.md` — no separate files needed.

- [ ] Output gate (existence + non-empty) documented for all 9 steps in orchestrator.md
- [ ] Changelog append (ISO timestamp, step name, agent, output file, status) specified after each approval
- [ ] Retry counter tracking specified for Design Review → Architecture and Code Review/Verification → Implementation loops
- [ ] Resume guard logic (skip existing outputs, list skipped steps, ask to continue) specified at startup
- [ ] Pipeline summary table specified to print after Step 9
- [ ] No `.claude/` directories, no `settings.json` hooks, no shell scripts created

---

## Verification
1. Open `.github/agents/orchestrator.md` and confirm each of the 5 gates above is covered
2. Trace through the 9-step sequence and confirm every step has a gate check immediately after the specialist agent is invoked
3. Confirm the changelog entry is written **after approval**, not after invocation
4. Confirm the retry counter is reset between steps (not a global counter)
5. Confirm the resume guard fires at startup and correctly maps each output file to its step
6. Confirm the pipeline summary lists all 9 steps with their output files