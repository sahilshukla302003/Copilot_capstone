# Agentic SDLC Pipeline

## What This Is

This repository implements a **GitHub Copilot-native agentic SDLC pipeline**. Given any Python project user story, it drives the full software development lifecycle — from requirements elicitation to a merged GitHub Pull Request — entirely through GitHub Copilot agents. You interact only with the `orchestrator` agent; it invokes each specialist agent as a tool, collects its output, asks you for feedback, and passes the approved output as input to the next specialist.

---

## Quick Start

1. **Clone** this repository
2. **Add a user story** — copy `user-stories/user-story-template.md` to `user-stories/user-story-<N>.md` and fill in all required fields
3. **Open Copilot Chat** in VS Code and select the `orchestrator` agent from the agent picker
4. **Send**: `process user-stories/user-story-1.md` and follow the prompts — approve, revise, or abort at each step

> Add `--fresh` to regenerate all artifacts from scratch: `process user-stories/user-story-1.md --fresh`

---

## Pipeline Architecture

```
user-stories/user-story-N.md
        │
        ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │                        ORCHESTRATOR                             │
 │  (single entry point — invokes all specialist agents as tools)  │
 └──────────────────────────────┬──────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
  [L1] Requirements       [L1] Architecture       [L2] Design Review
  ──────────────          ─────────────────       ──────────────────
  docs/requirements.md    docs/architecture.md    docs/design-review.md
        │                       ▲ (feedback loop if blockers found)
        └───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
 [L2] Impl Planner      [L2] Implementation      [L2] Code Review
 ─────────────────      ──────────────────       ────────────────
 docs/impl-plan.md      src/**/*.py              output/reports/
                        tests/**/*.py            code-review.md
                                ▲ (feedback loop if review/tests fail)
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
 [L2] Verification      [L2] Doc Sync            [L3] PR
 ─────────────────      ─────────────            ────────
 output/test-results/   docs/ (updated)          GitHub Pull Request
 results.md
```

Each step: orchestrator invokes specialist → specialist writes output file → orchestrator reads + summarises → **human: approve / revise / abort** → next specialist receives approved output as input context.

---

## Folder Structure

```
agentic-sdlc-pipeline/
├── .github/
│   ├── agents/                        # All agent definition files
│   │   ├── orchestrator.md            # Controller — relay-chain driver
│   │   ├── requirements.md            # L1: elicits requirements
│   │   ├── architecture.md            # L1: proposes system design
│   │   ├── design-review.md           # L2: reviews architecture for risks
│   │   ├── implementation-planner.md  # L2: ordered task breakdown
│   │   ├── implementation.md          # L2: writes Python source + tests
│   │   ├── code-review.md             # L2: structured code review
│   │   ├── verification.md            # L2: runs tests, reports results
│   │   ├── documentation-sync.md      # L2: keeps docs in sync with code
│   │   └── pr.md                      # L3: drafts + creates GitHub PR
│   ├── skills/                        # Reusable skill files for specialists
│   │   ├── requirement-analysis/SKILL.md
│   │   ├── architecture-design/SKILL.md
│   │   ├── implementation-planning/SKILL.md
│   │   ├── documentation-sync/SKILL.md
│   │   ├── pipeline-code-review/SKILL.md
│   │   └── verification/SKILL.md
│   └── copilot-instructions.md        # Auto-loaded by Copilot; pipeline overview
├── user-stories/
│   ├── user-story-template.md         # Blank template
│   └── user-story-1.md                # Sample story
├── docs/
│   ├── requirements.md                # Step 1 output
│   ├── architecture.md                # Step 2 output
│   ├── design-review.md               # Step 3 output
│   ├── impl-plan.md                   # Step 4 output
│   └── changelog.md                   # Timestamped log; appended after each step
├── src/                               # Step 5 output — generated Python source
├── tests/
│   ├── unit/                          # Unit tests
│   ├── integration/                   # Integration tests
│   └── fixtures/                      # Test fixtures
├── output/
│   ├── reports/                       # code-review.md — Step 6 (git-tracked)
│   └── test-results/                  # results.md — Step 7 (gitignored)
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## Agent Reference

| # | Agent | Role | Level | Input | Output |
|---|-------|------|-------|-------|--------|
| 1 | `requirements` | Elicits and documents requirements | L1 | user story file | `docs/requirements.md` |
| 2 | `architecture` | Proposes system design | L1 | `docs/requirements.md` | `docs/architecture.md` |
| 3 | `design-review` | Reviews architecture for risks/gaps | L2 | `docs/architecture.md` | `docs/design-review.md` |
| 4 | `implementation-planner` | Ordered task breakdown | L2 | architecture + design review | `docs/impl-plan.md` |
| 5 | `implementation` | Writes Python source and tests | L2 | `docs/impl-plan.md` | `src/` + `tests/` |
| 6 | `code-review` | Structured code review | L2 | `src/` + `tests/` | `output/reports/code-review.md` |
| 7 | `verification` | Runs tests, reports results | L2 | `src/` + `tests/` | `output/test-results/results.md` |
| 8 | `documentation-sync` | Keeps docs in sync with final code | L2 | `src/` + `docs/` | updated `docs/` files |
| 9 | `pr` | Drafts and creates GitHub PR | L3 | all docs + reports | GitHub Pull Request URL |

---

## Requirements

| Requirement | Version |
|-------------|---------|
| GitHub Copilot extension | Latest (agent mode required) |
| Python | ≥ 3.11 |
| `gh` CLI | Latest (required for PR creation — run `gh auth login` before first use) |
| Git | Any recent version |

> **Verify `gh` is authenticated** before running the pipeline: `gh auth status`

---

## Contributing

### Adding a new specialist agent
1. Create `.github/agents/<name>.md` with a YAML frontmatter block (`name`, `description`, `tools`) and a clear system prompt
2. Add the agent to the orchestrator's `tools` frontmatter in `.github/agents/orchestrator.md`
3. Document the new step in `.github/copilot-instructions.md` and this README
4. Add a corresponding entry to the pipeline steps table above

### Adding a new skill
1. Create `.github/skills/<name>/SKILL.md` with `name` and `description` frontmatter
2. Reference the skill from the relevant specialist agent's system prompt
