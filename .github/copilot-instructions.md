# GitHub Copilot — Repository Instructions

## 1. Project Overview

This repository implements an **Agentic SDLC Pipeline** driven entirely by GitHub Copilot agents. Given any Python project user story, the pipeline drives the full software development lifecycle — from requirements elicitation through to a merged GitHub Pull Request — without any manual steps. A single **orchestrator** agent controls the pipeline; it invokes each specialist agent as a tool, collects and validates the agent's output file, surfaces a summary to the human for feedback, and then passes the approved output as context input to the next specialist agent. The result is a traceable, human-in-the-loop relay chain that produces professional-grade artifacts at every stage.

---

## 2. How to Run the Pipeline

```
1. Open GitHub Copilot Chat in VS Code
2. Select the `orchestrator` agent from the agent picker
3. Send:  process user-stories/<filename>.md
   or:    process user-stories/<filename>.md --fresh   (to regenerate all artifacts from scratch)
4. Follow the prompts — approve, revise, or abort at each step
```

The orchestrator handles everything from there. You never need to open or invoke any specialist agent directly.

---

## 3. Relay-Chain Model

The orchestrator is the **only** entry point. For each of the 9 pipeline steps it:

1. **Invokes** the specialist agent as a tool, passing the previous step's approved output file content as input context
2. **Waits** for the specialist agent to write its output file
3. **Reads** the output file and displays a summary to you
4. **Asks**: `approve / revise (with feedback) / abort`
5. **If revised**: re-invokes the same specialist with your feedback included (max 2 retries before escalating)
6. **If approved**: appends a timestamped entry to `docs/changelog.md` and proceeds to the next specialist

Each specialist writes exactly one output artifact. The orchestrator validates it is non-empty before moving on.

---

## 4. Pipeline Steps

| # | Agent | Interaction | Input | Output |
|---|-------|-------------|-------|--------|
| 1 | `requirements` | L1 — Interactive | user story file | `docs/requirements.md` |
| 2 | `architecture` | L1 — Interactive | `docs/requirements.md` | `docs/architecture.md` |
| 3 | `design-review` | L2 — Run + Approve | `docs/architecture.md` | `docs/design-review.md` |
| 4 | `implementation-planner` | L2 — Run + Approve | `docs/architecture.md` + `docs/design-review.md` | `docs/impl-plan.md` |
| 5 | `implementation` | L2 — Run + Approve | `docs/impl-plan.md` | `src/**/*.py` + `tests/**/*.py` |
| 6 | `code-review` | L2 — Run + Approve | `src/` + `tests/` | `output/reports/code-review.md` |
| 7 | `verification` | L2 — Run + Approve | `src/` + `tests/` | `output/test-results/results.md` |
| 8 | `documentation-sync` | L2 — Run + Approve | final `src/` + `docs/*.md` | updated `docs/` files |
| 9 | `pr` | L3 — Explicit Confirm | all docs + review + test results | GitHub Pull Request URL |

---

## 5. Interaction Levels

| Level | Steps | Behavior |
|-------|-------|----------|
| **L1 — Deep Interactive** | Requirements, Architecture | The specialist drafts the document and surfaces open questions. The orchestrator relays them to you (max 2 rounds), re-invokes with your answers, and iterates until you approve. |
| **L2 — Run + Approve** | Design Review, Impl Planner, Implementation, Code Review, Verification, Doc Sync | The specialist runs autonomously and writes its output file. The orchestrator shows a summary and asks: **approve / revise (with feedback) / abort**. |
| **L3 — Explicit Confirm** | PR | The orchestrator shows the full PR draft. It only proceeds to create the PR after your **explicit** written confirmation. |

**Feedback loops**: Design Review blockers return to Architecture. Code Review issues or failing Verification return to Implementation. Each loop is capped at 2 retries before the orchestrator escalates to you.

---

## 6. File Conventions

### Artifact locations
| Artifact | Path |
|----------|------|
| Requirements | `docs/requirements.md` |
| Architecture | `docs/architecture.md` |
| Design Review | `docs/design-review.md` |
| Implementation Plan | `docs/impl-plan.md` |
| Source code | `src/**/*.py` |
| Tests | `tests/unit/`, `tests/integration/`, `tests/fixtures/` |
| Code Review report | `output/reports/code-review.md` _(git-tracked)_ |
| Test results | `output/test-results/results.md` _(gitignored)_ |
| Changelog | `docs/changelog.md` |

### User story naming
- Files must live in `user-stories/`
- Naming convention: `user-story-<N>.md` (e.g. `user-story-1.md`)
- One active story per branch — `docs/` and `src/` are shared

### Required fields in every user story file
```
## Title
## Problem Statement
## Acceptance Criteria
## Constraints
## Out of Scope
```

---

## 7. Do Not

- **Never** invoke a specialist agent directly — users must always go through the orchestrator
- **Never** skip output gate checks — every specialist's output file must be validated non-empty before the next step begins
- **Never** create the PR without explicit user confirmation (L3)
- **Never** proceed to the next pipeline step if the current step's output file is empty or missing
- **Never** declare a step complete if the specialist agent returned an error or produced no file
- **Never** modify `output/reports/` gitignore rules — this directory must remain git-tracked so the PR agent can embed review results in the PR body
