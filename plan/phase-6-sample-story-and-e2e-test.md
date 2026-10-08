# Phase 6 — Sample User Story & End-to-End Test

## Goal
Validate the entire pipeline works by running it against a concrete, well-defined Python project user story. This phase produces the first real output from all 9 agents and confirms the orchestrator drives them correctly from start to PR.

---

## Prerequisites
- All previous phases complete (Phases 1–5)
- Git repository initialized with a remote on GitHub (needed for `gh pr create` in the PR agent)
- `gh` CLI authenticated: `gh auth status`
- `pytest` available in the environment

---

## Step 6.1 — Create the Sample User Story

Create `user-stories/user-story-1.md` (and a blank `user-stories/user-story-template.md`) with a complete, realistic Python user story that is:
- Simple enough to implement in a single session
- Complex enough to exercise all pipeline stages meaningfully
- Self-contained (no external APIs or services required)

**Recommended story — CSV Summary CLI Tool:**

```markdown
# User Story: CSV Summary Report Generator

**As a** data analyst,  
**I want** a CLI tool that reads a CSV file and outputs a summary report,  
**So that** I can quickly understand the shape and content of any dataset without writing custom scripts.

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
```

---

## Step 6.2 — Prepare the Environment

Before running the pipeline:

```bash
# Confirm gh CLI is authenticated
gh auth status

# Confirm pytest is available
pytest --version

# Confirm the repo has a remote set
git remote -v

# If no remote, add one:
git remote add origin https://github.com/<your-username>/agentic-sdlc-pipeline.git
git push -u origin main
```

---

## Step 6.3 — Run the Pipeline

Open GitHub Copilot Chat in VS Code, select the `orchestrator` agent, and send:

```
process user-stories/user-story-1.md
```

To regenerate all artifacts from scratch, send:
```
process user-stories/user-story-1.md --fresh
```

**Step 1 — Requirements (L1)**
- Orchestrator invokes the `requirements` agent as a tool, passing the user story content as input context
- The agent writes a draft `docs/requirements.md` with clarifying questions under Open Questions
- Orchestrator reads the file, surfaces the questions to you; you answer (e.g., "use pandas for CSV reading", "output format is plain text, not JSON")
- Orchestrator re-invokes the agent with your answers (max 2 rounds), then you approve / revise / abort
- Orchestrator gates on the file and passes its content to Step 2

**Step 2 — Architecture (L1)**
- Orchestrator invokes the `architecture` agent as a tool, passing `docs/requirements.md` content as input context
- The agent writes a proposed Python module structure to `docs/architecture.md`, with design questions under Open Design Questions
- Orchestrator reads the file, surfaces the questions; you may answer or ask for adjustments (e.g., "use argparse not click")
- Orchestrator re-invokes the agent with your answers (max 2 rounds), then you approve / revise / abort
- Orchestrator gates and passes `docs/architecture.md` content to Step 3

**Step 3 — Design Review (L2)**
- Orchestrator invokes the `design-review` agent as a tool, passing `docs/architecture.md` content
- Agent runs autonomously, writes `docs/design-review.md`
- Orchestrator reads and shows the review (risks, decisions, required changes)
- You choose approve / revise / abort (blockers cause the orchestrator to re-invoke the architecture agent with the feedback, max 2 retries)

**Step 4 — Implementation Planning (L2)**
- Orchestrator invokes the `implementation-planner` agent as a tool, passing `docs/architecture.md` + `docs/design-review.md` content
- Agent runs autonomously, writes `docs/impl-plan.md`
- Orchestrator reads and shows the task table
- You choose approve / revise / abort

**Step 5 — Implementation (L2)**
- Orchestrator invokes the `implementation` agent as a tool, passing `docs/impl-plan.md` + `docs/requirements.md` + `docs/architecture.md` content
- Agent runs autonomously, writes `src/csv_summary/__init__.py`, `src/csv_summary/cli.py`, `src/csv_summary/analyzer.py`, etc.
- Agent writes `tests/unit/test_analyzer.py`, `tests/integration/test_cli.py`
- Orchestrator reads output and shows file list and test summary
- You choose approve / revise / abort

**Step 6 — Code Review (L2)**
- Orchestrator invokes the `code-review` agent as a tool, passing `src/` + `tests/` + `docs/requirements.md` content
- Agent reviews all Python files against requirements, writes `output/reports/code-review.md`
- Orchestrator reads and shows the review report with findings and recommendation
- "Request Changes" causes orchestrator to re-invoke the implementation agent with findings (max 2 retries), then re-invoke code-review
- You choose approve / revise / abort

**Step 7 — Verification (L2)**
- Orchestrator invokes the `verification` agent as a tool, passing `src/` + `tests/` + `docs/requirements.md` content
- Agent runs full test suite + coverage, writes `output/test-results/results.md`
- Orchestrator reads and shows the results with PASS/FAIL verdict
- FAIL causes orchestrator to re-invoke implementation agent with failures (max 2 retries), then re-invoke code-review and verification agents
- You choose approve / revise / abort

**Step 8 — Documentation Sync (L2)**
- Orchestrator invokes the `documentation-sync` agent as a tool, passing final `src/` + `docs/` content
- Agent scans the final `src/`, updates any docs that diverged, writes sync report
- Orchestrator reads and shows `output/reports/doc-sync-report.md`
- You choose approve / revise / abort

**Step 9 — PR (L3)**
- Orchestrator invokes the `pr` agent as a tool in draft mode, passing all docs + output content
- Agent generates full PR description draft WITHOUT creating the PR
- Orchestrator shows the full draft
- You type `y` to confirm
- Orchestrator re-invokes the pr agent with confirmation signal; agent creates a feature branch, commits, pushes, and runs `gh pr create` (test results are embedded in the PR body since `output/test-results/` is gitignored; `output/reports/` is tracked)
- Orchestrator displays the PR URL and prints the pipeline summary table

---

## Step 6.4 — Validate Artifacts

After the pipeline completes, check each artifact:

### docs/ artifacts
- [ ] `docs/requirements.md` — has Functional Requirements, Non-Functional Requirements, Acceptance Criteria sections
- [ ] `docs/architecture.md` — has Component Diagram, Technology Choices, Data Flow
- [ ] `docs/design-review.md` — has Risk Table, Design Decisions, Required Changes
- [ ] `docs/impl-plan.md` — has ordered task table with dependencies
- [ ] `docs/changelog.md` — has one entry per completed step with timestamps

### src/ artifacts
- [ ] At least 3 Python source files in `src/`
- [ ] All files have type hints
- [ ] No hardcoded secrets or credentials
- [ ] `python -m csv_summary --help` works

### tests/ artifacts
- [ ] Unit tests in `tests/unit/`
- [ ] Integration tests in `tests/integration/`
- [ ] `pytest tests/ -v` passes with 0 failures

### output/ artifacts
- [ ] `output/reports/doc-sync-report.md` exists
- [ ] `output/reports/code-review.md` has an Overall Recommendation
- [ ] `output/test-results/results.md` has Final Verdict: PASS

### GitHub
- [ ] PR exists with all 5 required sections (Summary, Changes Made, Test Evidence, Known Limitations, Reviewer Checklist)
- [ ] PR description ends with the attribution line

---

## Step 6.5 — Final Commit

If any pipeline run outputs were not auto-committed by the agents, commit them:

```bash
git add docs/ src/ tests/   # output/ is gitignored, so it is not committed
git commit -m "feat: run agentic pipeline on CSV summary user story"
```

---

## Deliverables Checklist
- [ ] `user-stories/user-story-1.md` created with the CSV Summary story (plus blank `user-story-template.md`)
- [ ] Full pipeline run completed without manual intervention beyond L1/L2/L3 interaction points
- [ ] All 9 artifact files validated
- [ ] `pytest tests/ -v` passes
- [ ] GitHub PR created with correct description
- [ ] All artifacts committed

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Gate fails on `docs/requirements.md` | Requirements agent returned early or output was empty | Re-open Copilot Chat, select `orchestrator`, and re-send `process user-stories/user-story-1.md` — completed steps are skipped automatically; or send `process user-stories/user-story-1.md --fresh` to regenerate all |
| `gh pr create` fails | No GitHub remote or not authenticated | Run `gh auth login`, confirm `git remote -v` shows the correct remote |
| pytest fails | Implementation agent missed a case | Orchestrator will loop back to Implementation automatically on Verification FAIL (max 2 retries); or choose "revise" and provide the failing test output as feedback |
| Coverage < 80% | Tests incomplete | Choose "revise" at the Verification step and ask the orchestrator to re-invoke the implementation agent to add more tests |
| Specialist agent not found | `tools` frontmatter in orchestrator.md missing an agent name | Open `.github/agents/orchestrator.md` and confirm all 9 specialist agent names are listed under `tools` |

---

## Success Definition
The pipeline is considered complete when:
1. A user story dropped into `user-stories/` can be processed to a merged (or mergeable) PR by opening Copilot Chat, selecting the `orchestrator` agent, and sending one `process` command
2. All 9 specialist agents run without being invoked directly by the user — the orchestrator invokes each one as a tool in sequence
3. Human interaction is limited to: answering L1 questions, approving/revising L2 steps, and confirming the L3 PR
