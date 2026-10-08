# Phase 3 — Specialist Agents

## Goal
Create 9 specialist agent files under `.github/agents/`. Each agent has a single, well-defined responsibility in the pipeline. Agents read from documented input files and write to documented output files. The orchestrator (Phase 4) is the only caller — it invokes each specialist as a tool, reads its output, collects human feedback, and passes the approved output as input to the next specialist. Agents never invoke each other directly.

---

## Prerequisites
- Phase 1 complete (directories exist)
- Phase 2 complete (skills exist for agents to reference)

---

## What Is a GitHub Copilot Agent File?
A `.github/agents/*.md` file defines a specialist agent. It contains YAML frontmatter and a system prompt. The orchestrator declares all specialist agents in its own `tools` frontmatter and invokes them during the pipeline relay chain. Each specialist agent runs within Copilot Chat with the tools specified in its frontmatter.

**Standard frontmatter structure:**
```yaml
---
name: <agent-name>
description: <one-line description used by the orchestrator>
tools:
  - name: Read
  - name: Write
  - name: Glob
  - name: Grep
  - name: Bash
---
```

**Note on L1 agents (requirements, architecture)**: when the orchestrator invokes these agents as tools, they perform their task and write a draft whose Open Questions / Open Design Questions section lists every clarifying question. The orchestrator reads the output file, surfaces the questions to the user (max 2 rounds), then re-invokes the same agent with the user's answers so it produces the final document.

**Pipeline order**: requirements → architecture → design-review → implementation-planner → implementation → code-review → verification → documentation-sync → pr. Agent numbers below are identifiers, not execution order.

---

## Agents to Create

### Agent 1 — `requirements.md`
**Interaction Level**: L1 (Deep Interactive — can ask clarifying questions)  
**Input**: User story file path (passed by orchestrator)  
**Output**: `docs/requirements.md`

**System Prompt must instruct the agent to:**
- Read the user story file in full before doing anything else
- Use the `requirement-analysis` skill to structure its work
- Ask all clarifying questions in a single numbered list — never one at a time
- On first invocation: write a draft `docs/requirements.md` that includes an **Open Questions** section listing any ambiguities with assumed answers
- The orchestrator will surface those questions to the user and re-invoke this agent with the answers (max 2 rounds)
- On final invocation (with answers provided): write the complete, finalised `docs/requirements.md` with no open questions remaining
- Never proceed to architecture — that is the orchestrator's job after it receives human approval

**Tools needed**: `Read`, `Write`

**Output file format**: See `requirement-analysis` skill for the exact structure.

---

### Agent 2 — `architecture.md`
**Interaction Level**: L1 (Deep Interactive — can ask clarifying questions about design choices)  
**Input**: `docs/requirements.md`  
**Output**: `docs/architecture.md`

**System Prompt must instruct the agent to:**
- Read `docs/requirements.md` fully before proposing anything
- Use the `architecture-design` skill to structure its work
- Propose a complete architecture first
- On first invocation: write a draft `docs/architecture.md` that includes an **Open Design Questions** section listing design ambiguities with assumed answers
- The orchestrator will surface those questions to the user and re-invoke this agent with the answers (max 2 rounds)
- On final invocation (with answers provided): write the complete, finalised `docs/architecture.md` with no open questions remaining
- Never write source code — only the architecture document

**Tools needed**: `Read`, `Write`

---

### Agent 3 — `design-review.md`
**Interaction Level**: L2 (Run autonomously, output shown by orchestrator, user approves before next step)  
**Input**: `docs/architecture.md`  
**Output**: `docs/design-review.md`

**System Prompt must instruct the agent to:**
- Read `docs/architecture.md` as a senior technical reviewer (not the original author)
- Evaluate against these risk categories:
  - Scalability risks
  - Security gaps
  - Missing error handling strategy
  - Over-engineering or under-engineering
  - Unaddressed non-functional requirements
  - Missing component interfaces
- Write `docs/design-review.md` with: Summary, Risk Table (Risk | Severity | Recommendation), Design Decisions Confirmed, Required Changes Before Implementation
- If Required Changes are non-empty, flag this clearly — the orchestrator will surface it to the user and re-invoke the architecture agent with the feedback (max 2 retries)
- Never modify `docs/architecture.md` itself

**Tools needed**: `Read`, `Write`

---

### Agent 4 — `implementation-planner.md`
**Interaction Level**: L2  
**Input**: `docs/architecture.md` + `docs/design-review.md`  
**Output**: `docs/impl-plan.md`

**System Prompt must instruct the agent to:**
- Read both input files before planning
- Use the `implementation-planning` skill to structure the task breakdown
- Produce an ordered, dependency-aware task list for a Python project
- Each task must: be independently testable, have a clear definition of done, reference the file(s) it creates or modifies
- Pair each implementation task with a corresponding test task
- Flag any task that is blocked on an external dependency
- Write `docs/impl-plan.md` with the full task table and dependency graph
- Never write source code

**Tools needed**: `Read`, `Write`

---

### Agent 5 — `implementation.md`
**Interaction Level**: L2  
**Input**: `docs/impl-plan.md` (+ `docs/requirements.md` and `docs/architecture.md` for context)  
**Output**: `src/**/*.py` + `tests/**/*.py`

**System Prompt must instruct the agent to:**
- Read `docs/impl-plan.md` and execute tasks in the dependency order defined there
- Read `docs/requirements.md` to stay anchored to acceptance criteria
- Write Python source files to `src/` following the architecture
- Write corresponding test files to `tests/unit/` and `tests/integration/`
- Follow these Python conventions strictly:
  - Type hints on all function signatures
  - No bare `except:` — always catch specific exceptions
  - No mutable default arguments
  - No secrets or credentials hardcoded
  - Functions ≤ 30 lines where possible
- Report back with: files created, test results summary
- The orchestrator will read this output and ask the user for approval before invoking the code-review agent

**Tools needed**: `Read`, `Write`, `Bash`, `Glob`

---

### Agent 6 — `documentation-sync.md`
**Interaction Level**: L2  
**Input**: final `src/` directory + existing `docs/` files (runs AFTER code review and verification so docs reflect the final code; use `git diff` against the baseline only if a baseline commit exists — on a greenfield run, compare `src/` directly to `docs/*.md`)  
**Output**: Updated `docs/*.md` files + sync report

**System Prompt must instruct the agent to:**
- Use the `documentation-sync` skill to guide its work
- Scan all `.py` files in `src/` and compare against what `docs/architecture.md` and `docs/requirements.md` describe
- Identify gaps: new components not documented, removed items still referenced, changed interfaces
- Update only the affected sections — do not rewrite accurate content
- Write a short sync report to `output/reports/doc-sync-report.md` listing all changes made
- If a discrepancy suggests the implementation deviated from the architecture, flag it clearly

**Tools needed**: `Read`, `Write`, `Glob`, `Grep`

---

### Agent 7 — `code-review.md`
**Interaction Level**: L2  
**Input**: `src/**/*.py` + `tests/**/*.py` + `docs/requirements.md`  
**Output**: `output/reports/code-review.md`

**System Prompt must instruct the agent to:**
- Use the `pipeline-code-review` skill checklist for all 8 review areas
- Read every `.py` file in `src/` and `tests/`
- Cross-reference findings against `docs/requirements.md` — only flag deviations from spec, not style preferences
- Assign severity: Critical (breaks functionality or security) / Major (significant quality issue) / Minor (style, clarity)
- Write `output/reports/code-review.md` with the full finding table
- End with Overall Recommendation: Approve / Request Changes
- If any Critical finding exists, set recommendation to "Request Changes" automatically

**Tools needed**: `Read`, `Write`, `Glob`, `Grep`

---

### Agent 8 — `verification.md`
**Interaction Level**: L2  
**Input**: `src/` + `tests/` + `docs/requirements.md`  
**Output**: `output/test-results/results.md`

**System Prompt must instruct the agent to:**
- Use the `verification` skill to structure the test run
- Execute: `pytest tests/unit/ -v`, then `pytest tests/integration/ -v`, then `pytest --cov=src --cov-report=term-missing`
- Map each acceptance criterion from `docs/requirements.md` to the test(s) that cover it
- Flag any criterion with zero test coverage as a gap
- Write `output/test-results/results.md` with: run summary, coverage report, criteria coverage table, gaps, final PASS/FAIL verdict
- Pass criteria: all tests pass, coverage ≥ 80%, no Critical code review findings still open
- If verdict is FAIL, list exactly what must be fixed before PR can be created

**Tools needed**: `Read`, `Write`, `Bash`, `Glob`

---

### Agent 9 — `pr.md`
**Interaction Level**: L3 (Explicit Approve — draft shown, PR created only after user confirms)  
**Input**: All `docs/*.md` + `output/reports/` + `output/test-results/results.md`  
**Output**: GitHub Pull Request URL

**System Prompt must instruct the agent to:**
- Read all artifact files to construct the PR description
- Generate a complete PR draft with all required sections:
  1. **Summary** — 2-3 sentence overview of what was built and why
  2. **Changes Made** — bulleted list of all files added/modified with reason
  3. **Test Evidence** — paste key lines from `output/test-results/results.md`
  4. **Known Limitations** — anything marked "Not Found", out of scope, or flagged as a gap
  5. **Reviewer Checklist** — tick-list the reviewer must complete before approving
- Present the full PR draft as output — do NOT create the PR yet
- Embed key test results directly in the PR body — `output/test-results/` is gitignored so those files are not in the PR diff; `output/reports/code-review.md` is tracked and will be in the diff
- Only create the PR after the orchestrator passes back explicit user confirmation
- On confirmation: create a feature branch, commit `src/`, `tests/`, `docs/`, push, then use `gh pr create` with a heredoc to pass the body (requires a GitHub remote and `gh auth status` to pass)

**Tools needed**: `Read`, `Bash`, `Glob`

---

## Deliverables Checklist
- [ ] `.github/agents/requirements.md`
- [ ] `.github/agents/architecture.md`
- [ ] `.github/agents/design-review.md`
- [ ] `.github/agents/implementation-planner.md`
- [ ] `.github/agents/implementation.md`
- [ ] `.github/agents/code-review.md`
- [ ] `.github/agents/verification.md`
- [ ] `.github/agents/documentation-sync.md`
- [ ] `.github/agents/pr.md`
- [ ] All 9 files committed

---

## Verification
For each agent file:
1. Confirm frontmatter is valid YAML with `name`, `description`, and `tools`
2. Confirm the system prompt references the correct input files and output files
3. Confirm the interaction level is correctly described (L1 agents must mention the draft-with-open-questions pattern so the orchestrator can relay questions and re-invoke with answers; L3 agent must mention draft-first, create-only-on-explicit-confirm)
4. Confirm no specialist agent attempts to call another agent — only the orchestrator invokes specialists as tools
