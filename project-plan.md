# Agentic SDLC Pipeline — Project Plan
## Project: Agentic SDLC Pipeline
A GitHub Copilot-native agentic pipeline that accepts any Python project user story and drives it through the full SDLC — from requirements to a merged PR — entirely via GitHub Copilot agents and skills. You interact only with the orchestrator; it invokes each specialist agent as a tool, collects its output, asks you for feedback, then passes that approved output as input to the next specialist agent.

---
## Interaction Model
| Level | Steps | Behavior |
|---|---|---|
| L1 — Deep Interactive | Requirements, Architecture | Orchestrator invokes the specialist agent as a tool; the agent drafts the document and surfaces open questions; orchestrator relays them to you (max 2 rounds), re-invokes the agent with your answers, and iterates until you approve |
| L2 — Run + Approve | Design Review, Impl Planner, Implementation, Code Review, Verification, Doc Sync | Orchestrator invokes the specialist agent as a tool; agent runs autonomously and writes its output file; orchestrator reads the output, shows a summary, and asks: **approve / revise (with feedback) / abort** |
| L3 — Explicit Approve | PR | Orchestrator invokes the PR agent as a tool; shows the full PR draft; only proceeds to create the PR after your explicit confirmation |

**Entry point**: Open GitHub Copilot Chat in VS Code → select the `orchestrator` agent → send: `process user-stories/user-story-1.md`

**You never invoke specialist agents directly** — the orchestrator invokes them as tools, relays their output to you for feedback, and passes the approved output as input to the next agent.
**Feedback loops**: Design Review blockers return to Architecture; Code Review issues or failing Verification return to Implementation. Each loop is capped at 2 retries, then the orchestrator escalates to you.

---
## Pipeline Flow
```
user-stories/user-story-N.md
        |
        v
[ORCHESTRATOR] ──────────────────────────────────────────────┐
        |                                                     |
        ├─[L1]─► Requirements Agent ──► docs/requirements.md │
        |         (invoked as tool)  ◄── human feedback ──── |
        |                                                     |
        ├─[L1]─► Architecture Agent ──► docs/architecture.md │
        |         (invoked as tool)  ◄── human feedback ──── |
        |                                                     |
        ├─[L2]─► Design Review Agent ──► docs/design-review.md
        |         (invoked as tool)  ◄── human feedback ──── |
        |                                                     |
        ├─[L2]─► Impl Planner Agent ──► docs/impl-plan.md    │
        |         (invoked as tool)  ◄── human feedback ──── |
        |                                                     |
        ├─[L2]─► Implementation Agent ──► src/ + tests/      │
        |         (invoked as tool)  ◄── human feedback ──── |
        |                                                     |
        ├─[L2]─► Code Review Agent ──► output/reports/       │
        |         (invoked as tool)  ◄── human feedback ──── |
        |                                                     |
        ├─[L2]─► Verification Agent ──► output/test-results/ │
        |         (invoked as tool)  ◄── human feedback ──── |
        |                                                     |
        ├─[L2]─► Doc Sync Agent ──► docs/ (updated)          │
        |         (invoked as tool)  ◄── human feedback ──── |
        |                                                     |
        └─[L3]─► PR Agent ──► GitHub Pull Request            │
                  (invoked as tool)  ◄── explicit confirm ── |
                                                              |
        Orchestrator reads each output → asks feedback →     |
        passes approved output to next agent ─────────────── ┘
```

---
## Folder Structure
```
agentic-sdlc-pipeline/
├── .github/
│   ├── agents/
│   │   ├── orchestrator.md            # Controller — invokes specialist agents as tools, relays output+feedback
│   │   ├── requirements.md            # L1 specialist: elicits + documents requirements
│   │   ├── architecture.md            # L1 specialist: proposes system design
│   │   ├── design-review.md           # L2 specialist: reviews architecture for risks
│   │   ├── implementation-planner.md  # L2 specialist: ordered task breakdown
│   │   ├── implementation.md          # L2 specialist: writes Python source + tests
│   │   ├── code-review.md             # L2 specialist: structured code review
│   │   ├── verification.md            # L2 specialist: runs tests, reports results
│   │   ├── documentation-sync.md      # L2 specialist: keeps docs in sync with final code
│   │   └── pr.md                      # L3 specialist: drafts + creates GitHub PR
│   ├── skills/                        # each skill is <name>/SKILL.md (used by specialist agents)
│   │   ├── requirement-analysis/SKILL.md
│   │   ├── architecture-design/SKILL.md
│   │   ├── implementation-planning/SKILL.md
│   │   ├── documentation-sync/SKILL.md
│   │   ├── pipeline-code-review/SKILL.md
│   │   └── verification/SKILL.md
│   └── copilot-instructions.md        # pipeline overview, invocation instructions, agent list
├── user-stories/
│   ├── user-story-template.md         # blank template with required fields
│   └── user-story-1.md                # sample story (CSV summary CLI)
├── docs/
│   ├── requirements.md                # written by requirements agent — Step 1 output
│   ├── architecture.md                # written by architecture agent — Step 2 output
│   ├── design-review.md               # written by design-review agent — Step 3 output
│   ├── impl-plan.md                   # written by implementation-planner — Step 4 output
│   └── changelog.md                   # created in Phase 1; appended by orchestrator after each step
├── src/                               # written by implementation agent — Step 5 output
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── output/
│   ├── reports/                       # code-review.md — Step 6 output (tracked in git)
│   └── test-results/                  # results.md — Step 7 output (gitignored)
├── pyproject.toml
├── .gitignore
└── README.md
```

---
## Implementation Phases

### Phase 1 — Project Scaffolding
**Goal**: Set up the repo skeleton with all directories, base config files, and `.github/copilot-instructions.md`.
Tasks:
- [ ] Initialize git repository; add GitHub remote and confirm `gh auth status` (needed by the PR agent — abort with a clear message if this fails)
- [ ] Create all directories: `.github/agents/`, `.github/skills/`, `src/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`, `output/reports/`, `output/test-results/`, `docs/`, `user-stories/`
- [ ] Create empty `docs/changelog.md` (orchestrator appends a timestamped entry after each step)
- [ ] Create `.gitignore` (Python standard + `output/test-results/`; keep `output/reports/` tracked so PR agent can embed review results)
- [ ] Create `pyproject.toml` (project metadata, Python >=3.11, build backend: `hatchling`)
- [ ] Create `.github/copilot-instructions.md` — pipeline overview, invocation instructions, agent list, and relay-chain description
- [ ] Create `README.md` — user-facing guide
**Deliverable**: Empty but correctly structured repo committed to git.

---
### Phase 2 — Skills
**Goal**: Create reusable skill files that specialist agents will invoke for structured tasks.
Tasks:
- [ ] `.github/skills/requirement-analysis/SKILL.md` — structured Q&A template for eliciting requirements
- [ ] `.github/skills/architecture-design/SKILL.md` — component + data flow design template
- [ ] `.github/skills/implementation-planning/SKILL.md` — dependency-ordered task breakdown template
- [ ] `.github/skills/documentation-sync/SKILL.md` — code-to-doc update pattern
- [ ] `.github/skills/pipeline-code-review/SKILL.md` — review checklist (correctness, security, error handling, DRY, test coverage, dependency safety)
- [ ] `.github/skills/verification/SKILL.md` — test run + quality gate template

Each file needs `name` and `description` frontmatter so GitHub Copilot discovers it.

**Deliverable**: 6 skill files committed.

---
### Phase 3 — Specialist Agents
**Goal**: Create all 9 specialist agent files with clear system prompts and input/output contracts.

Agent input/output contracts:

| Agent | Input | Output |
|---|---|---|
| requirements | user story file | `docs/requirements.md` |
| architecture | `docs/requirements.md` | `docs/architecture.md` |
| design-review | `docs/architecture.md` | `docs/design-review.md` |
| implementation-planner | `docs/architecture.md` + `docs/design-review.md` | `docs/impl-plan.md` |
| implementation | `docs/impl-plan.md` | `src/**/*.py` + `tests/**/*.py` |
| code-review | `src/` + `tests/` | `output/reports/code-review.md` |
| verification | `src/` + `tests/` | `output/test-results/results.md` |
| documentation-sync | final `src/` + `docs/*.md` (git diff only if a baseline commit exists) | updated `docs/` files |
| pr | all docs + `output/reports/code-review.md` + `output/test-results/results.md` | GitHub Pull Request URL |

The orchestrator invokes each specialist agent as a tool, passing the previous step's approved output file content as input context. Each agent performs its task, writes its output file, and returns. L1 agents (requirements, architecture) include open questions in their output; the orchestrator surfaces these to you before re-invoking with your answers.

Tasks:
- [ ] `.github/agents/requirements.md`
- [ ] `.github/agents/architecture.md`
- [ ] `.github/agents/design-review.md`
- [ ] `.github/agents/implementation-planner.md`
- [ ] `.github/agents/implementation.md`
- [ ] `.github/agents/code-review.md`
- [ ] `.github/agents/verification.md`
- [ ] `.github/agents/documentation-sync.md`
- [ ] `.github/agents/pr.md`

**Deliverable**: 9 specialist agent files committed.

---
### Phase 4 — Orchestrator Agent
**Goal**: Create the orchestrator — the single Copilot Chat agent that drives the full pipeline via a relay chain.

Orchestrator relay-chain flow (per step):
1. **Invoke** the specialist agent as a tool, passing the previous step's approved output file content as input context
2. **Wait** for the specialist agent to complete and write its output file
3. **Read** the output file and display a summary to the user
4. **Ask** the user: approve / revise (with feedback) / abort
5. **If revised**: re-invoke the same specialist agent with the feedback included (max 2 retries before escalating)
6. **If approved**: proceed — pass the approved output as input context to the next specialist agent

Orchestrator responsibilities:
- Declare all 9 specialist agents in its `tools` frontmatter so it can invoke them
- Read the user story file at the path provided by the user
- Execute all 9 steps in order via the relay chain above
- Apply interaction level rules per step: L1 surfaces open questions (max 2 rounds); L2 offers approve / revise / abort; L3 requires explicit confirmation before the PR agent creates the PR
- Route failures back through bounded feedback loops (max 2 retries per step) before escalating to the user
- Resume interrupted runs: check if the output file for a step already exists and is non-empty — skip that step unless `--fresh` was requested
- Gate each step: validate the output file is non-empty before proceeding; surface a clear error if the gate fails
- Append a timestamped entry to `docs/changelog.md` after each step completes
- Print a full pipeline summary after the PR step completes

Tasks:
- [ ] `.github/agents/orchestrator.md` — full relay-chain controller with `tools` frontmatter listing all 9 specialists, step-by-step logic, gating, interaction levels, and inline changelog logging
**Deliverable**: Orchestrator agent file committed.

---
### Phase 5 — Quality Gates & Logging
**Goal**: Ensure the orchestrator validates each specialist agent's output and maintains a run log. GitHub Copilot has no external hook system — all gates and logging are implemented as inline logic inside the orchestrator agent.

Gates and logging to implement inside `orchestrator.md`:
- [ ] **Output gate**: after invoking each specialist agent, verify its output file exists and is non-empty; if the gate fails, show a clear error and stop — do not invoke the next specialist
- [ ] **Changelog logging**: after each step is approved, append a timestamped Markdown entry to `docs/changelog.md` — include step name, specialist agent invoked, output file path, and approval status
- [ ] **Retry tracking**: track retry count per step; after 2 failed retries escalate to the user with a clear summary of what went wrong instead of looping again
- [ ] **Resume guard**: at startup, check which output files already exist; list skipped steps to the user so they know the pipeline is resuming mid-run
- [ ] **Pipeline summary**: after the PR step completes, print a table of all 9 steps with their output files and final status

**Deliverable**: All gate and logging logic embedded in `.github/agents/orchestrator.md`; no separate hooks files needed.

---
### Phase 6 — Sample User Story + End-to-End Test
**Goal**: Validate the full pipeline works with a concrete user story.
Tasks:
- [ ] Create `user-stories/user-story-template.md` (blank template with fields: Title, Problem Statement, Acceptance Criteria, Constraints, Out of Scope) and `user-stories/user-story-1.md` — a simple, complete Python project user story (e.g., "CLI tool that reads a CSV and outputs a summary report")
- [ ] Run the orchestrator end-to-end against the sample story
- [ ] Verify each `docs/*.md` file is populated in sequence
- [ ] Verify `src/` contains generated Python code with tests
- [ ] Verify `output/test-results/results.md` shows passing tests
- [ ] Verify PR is created with all required sections (Summary, Changes Made, Test Evidence, Known Limitations, Reviewer Checklist)

**Deliverable**: Fully working pipeline demonstrated on sample user story.

---
## Success Criteria
- [ ] Single invocation (open Copilot Chat → select `orchestrator` → send `process user-stories/user-story-1.md`) drives the entire pipeline
- [ ] The orchestrator invokes each specialist agent as a tool, reads its output, asks for human feedback, and passes approved output as input to the next agent (relay chain)
- [ ] Requirements and Architecture steps surface open questions interactively (max 2 rounds each)
- [ ] All L2 steps wait for human approval (approve / revise / abort) before the next specialist agent is invoked
- [ ] Review/verification failures re-invoke the implementation agent with feedback (max 2 retries) before escalating
- [ ] PR is only created after explicit user confirmation
- [ ] Each step's output file is validated non-empty before the next step begins
- [ ] `docs/changelog.md` has a timestamped entry for every completed step
- [ ] All `docs/*.md` artifacts are populated and human-readable
- [ ] Generated Python code passes tests
- [ ] No specialist agent is ever invoked directly by the user

---
## Notes
- All agents are `.github/agents/*.md` files (GitHub Copilot native, invoked via Copilot Chat)
- The orchestrator declares all 9 specialist agents in its `tools` frontmatter; this is what enables it to invoke them as tools
- The relay chain is file-based: each specialist writes an output file; the orchestrator reads it, collects human feedback, and passes the content as input context to the next specialist
- `output/test-results/` is gitignored; `output/reports/` is tracked so the PR agent can embed code-review results in the PR body
- No external SDK or API keys required beyond what GitHub Copilot already uses
- Pipeline is resumable: existing, non-empty output files are skipped on re-run; tell the orchestrator `--fresh` to regenerate all artifacts from scratch
- One user story per repo/branch at a time — `docs/` and `src/` are shared, so a second story needs a fresh clone or branch
- The pipeline is general-purpose: works for any Python project user story
- `user-story-template.md` required fields: **Title**, **Problem Statement**, **Acceptance Criteria**, **Constraints**, **Out of Scope**