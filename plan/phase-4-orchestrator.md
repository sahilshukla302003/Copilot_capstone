# Phase 4 — Orchestrator Agent

## Goal
Create the orchestrator — the single entry point for the entire pipeline. The orchestrator reads the user story, invokes each specialist agent as a tool in sequence, enforces interaction-level rules, gates each step on output file validation, reads each step's output, asks the user for feedback, and passes the approved output as input to the next specialist agent. The user never invokes a specialist agent directly.

---

## Prerequisites
- Phase 1 complete (scaffold in place)
- Phase 2 complete (skills exist)
- Phase 3 complete (all 9 specialist agents exist)

---

## File to Create
`.github/agents/orchestrator.md`

---

## Orchestrator Design Principles

1. **Controller only** — the orchestrator never analyzes the user story itself beyond handing it to the requirements step. It coordinates from there.
2. **Single entry point, main-thread agent** — the user starts a session with `claude --agent orchestrator` (or sets `"agent": "orchestrator"` in `.claude/settings.json`). It cannot be launched as an `@orchestrator` subagent, because subagents cannot spawn other subagents. Specialist subagents are invisible to the user.
3. **Gating** — before calling the next step, the orchestrator validates the previous step's output file exists and is non-empty. If a gate fails, the pipeline stops and surfaces a clear error.
4. **Interaction levels** — the orchestrator enforces the L1/L2/L3 contract:
   - L1 (Requirements, Architecture): subagents cannot hold a Q&A with the user, so the orchestrator spawns the agent, which writes a draft with open questions; the orchestrator relays the questions to the user, re-spawns the agent with the answers (max 2 rounds), and iterates until approved
   - L2: orchestrator spawns agent, receives output, displays it, asks user **approve / revise / abort**
   - L3: orchestrator receives PR draft, displays it, asks explicit "Create this PR? (y/n)"
5. **Changelog** — after each successful step, the orchestrator appends an entry to `docs/changelog.md`
6. **Resumability** — if a pipeline run is interrupted, the orchestrator checks which output files already exist and skips completed steps (does not regenerate them). `--fresh` ignores existing outputs and regenerates everything.
7. **Feedback loops (max 2 retries each)** — Design Review blockers → re-run Architecture (L1); Code Review "Request Changes" or Verification FAIL → re-run Implementation with the findings. After 2 retries, stop and escalate to the user.
8. **Revise** — at any L2 prompt, "revise" collects user feedback and re-spawns the same agent with that feedback appended.

---

## Orchestrator System Prompt — Full Specification

### Frontmatter
```yaml
---
name: orchestrator
description: >
  Master controller for the agentic SDLC pipeline. Accepts a user story file path,
  invokes all specialist agents as tools in sequence, enforces gating and interaction
  levels, and drives the pipeline from requirements to a GitHub PR.
tools:
  - name: Read
  - name: Write
  - name: Glob
  - name: Bash
  - name: requirements
  - name: architecture
  - name: design-review
  - name: implementation-planner
  - name: implementation
  - name: code-review
  - name: verification
  - name: documentation-sync
  - name: pr
---
```

### System Prompt Sections

**Section 1: Role and Constraints**
- You are the pipeline controller. You coordinate; you do not analyze.
- Never write source code or design documents yourself. Every step is delegated to its specialist agent by invoking it as a tool; you pass each step’s approved output file content as input context to the next specialist.
- Always read and validate output files before proceeding. Never assume a specialist agent succeeded.

**Section 2: Invocation**
The orchestrator runs as a GitHub Copilot Chat agent. The user selects it in Copilot Chat and sends:
```
process user-stories/user-story-1.md [--fresh]
```
First action: verify the file exists. If not, stop immediately with a clear error.

**Section 3: Pipeline Sequence with Interaction Levels**

```
Step 1 — Requirements (L1)
  - Invoke: requirements agent (as tool), passing user story file content as input context
  - Behavior: agent writes docs/requirements.md with Open Questions section; orchestrator reads the file, surfaces questions to the user, re-invokes with answers (max 2 rounds)
  - Prompt: "Requirements ready. approve / revise / abort?"
  - Gate: docs/requirements.md exists AND size > 0
  - On gate fail: "Requirements step did not produce output. Please retry."
  - On gate pass: append changelog entry, pass docs/requirements.md content to Step 2

Step 2 — Architecture (L1)
  - Invoke: architecture agent (as tool), passing docs/requirements.md content as input context
  - Behavior: agent writes docs/architecture.md with Open Design Questions section; orchestrator reads the file, surfaces questions to the user, re-invokes with answers (max 2 rounds)
  - Prompt: "Architecture ready. approve / revise / abort?"
  - Gate: docs/architecture.md exists AND size > 0
  - On gate fail: "Architecture step did not produce output. Please retry."
  - On gate pass: append changelog entry, pass docs/architecture.md content to Step 3

Step 3 — Design Review (L2)
  - Invoke: design-review agent (as tool), passing docs/architecture.md content as input context
  - Behavior: agent runs autonomously, writes docs/design-review.md
  - Display: show contents of docs/design-review.md to user
  - If blockers are listed: re-invoke architecture agent with the blockers as feedback (max 2 retries), then re-invoke design-review agent
  - Prompt: "Design review complete. Required changes listed above. approve / revise / abort?"
  - On revise: collect feedback, re-invoke design-review agent with feedback. On abort: stop and await user instruction
  - Gate: docs/design-review.md exists AND size > 0
  - On gate pass: append changelog entry, pass docs/architecture.md + docs/design-review.md content to Step 4

Step 4 — Implementation Planning (L2)
  - Invoke: implementation-planner agent (as tool), passing docs/architecture.md + docs/design-review.md content as input context
  - Behavior: agent runs autonomously, writes docs/impl-plan.md
  - Display: show contents of docs/impl-plan.md to user
  - Prompt: "Implementation plan ready. approve / revise / abort?"
  - On revise: collect feedback, re-invoke agent with feedback. On abort: stop and await user instruction
  - Gate: docs/impl-plan.md exists AND size > 0
  - On gate pass: append changelog entry, pass docs/impl-plan.md + docs/requirements.md + docs/architecture.md content to Step 5

Step 5 — Implementation (L2)
  - Invoke: implementation agent (as tool), passing docs/impl-plan.md + docs/requirements.md + docs/architecture.md content as input context
  - Behavior: agent runs autonomously (writes src/ and tests/)
  - Display: list of files created + pytest summary
  - Prompt: "Implementation complete. approve / revise / abort?"
  - On revise: collect feedback, re-invoke agent with feedback. On abort: stop and await user instruction
  - Gate: at least one .py file exists in src/
  - On gate pass: append changelog entry, proceed to Step 6

Step 6 — Code Review (L2)
  - Invoke: code-review agent (as tool), passing src/ + tests/ + docs/requirements.md content as input context
  - Behavior: agent runs autonomously, writes output/reports/code-review.md
  - Display: show output/reports/code-review.md in full
  - If recommendation is "Request Changes": re-invoke implementation agent with findings as feedback (max 2 retries), then re-invoke code-review agent
  - Prompt: "Code review complete. Recommendation: [Approve/Request Changes]. approve / revise / abort?"
  - On revise: collect feedback, re-invoke code-review agent with feedback. On abort: stop and await user instruction
  - Gate: output/reports/code-review.md exists
  - On gate pass: append changelog entry, proceed to Step 7

Step 7 — Verification (L2)
  - Invoke: verification agent (as tool), passing src/ + tests/ + docs/requirements.md content as input context
  - Behavior: agent runs autonomously (runs pytest), writes output/test-results/results.md
  - Display: show output/test-results/results.md
  - If verdict is FAIL: re-invoke implementation agent with failures as feedback (max 2 retries), then re-invoke code-review and verification agents
  - Prompt: "Verification verdict: [PASS/FAIL]. approve / revise / abort?"
  - On approve with FAIL verdict (after retries exhausted): warn user "Verification failed. Failures will be listed under Known Limitations in the PR."
  - On abort: stop and await user instruction
  - Gate: output/test-results/results.md exists
  - On gate pass: append changelog entry, proceed to Step 8

Step 8 — Documentation Sync (L2)
  - Invoke: documentation-sync agent (as tool), passing final src/ directory + docs/ content as input context (runs after review/verification so docs reflect the final code)
  - Behavior: agent runs autonomously, writes output/reports/doc-sync-report.md + updates docs/
  - Display: show output/reports/doc-sync-report.md
  - Prompt: "Documentation synced. approve / revise / abort?"
  - On revise: collect feedback, re-invoke agent with feedback. On abort: stop and await user instruction
  - Gate: output/reports/doc-sync-report.md exists
  - On gate pass: append changelog entry, proceed to Step 9

Step 9 — PR Creation (L3)
  - Invoke: pr agent (as tool) in draft mode, passing all docs/*.md + output/reports/ + output/test-results/results.md content as input context (test results are embedded in PR body because output/test-results/ is gitignored; output/reports/ is tracked)
  - Behavior: agent generates PR draft and returns it WITHOUT creating the PR; on explicit confirm from orchestrator it creates a feature branch, commits, pushes, then runs `gh pr create`
  - Display: show full PR description draft to user
  - Prompt: "PR draft above. Create this PR on GitHub? (y/n)"
  - On n: "PR not created. You can re-invoke the orchestrator to retry the PR step."
  - On y: re-invoke pr agent with confirmation signal to execute `gh pr create`
  - Gate: PR URL returned
  - On gate pass: display PR URL, append final changelog entry, print pipeline summary table
```

**Section 4: Changelog Entry Format**
After each successful step, append to `docs/changelog.md`:
```
## Run: <ISO timestamp>
- Step <N> (<agent name>): COMPLETE
- Output: <output file path>
- Duration: <time taken if measurable>
```

**Section 5: Resumability Logic**
On startup, before Step 1 (skipped entirely when `--fresh` is passed), check which output files already exist:
- If `docs/requirements.md` exists → skip Step 1, inform user
- If `docs/architecture.md` exists → skip Step 2, inform user
- ... same for each step's output file
- Inform user of all skipped steps and ask: "Resuming from Step N. Continue? (y/n)"

**Section 6: Error Handling**
- Gate failure → clear message stating which agent failed, which file is missing, and how to retry
- User aborts (or types "n") at any prompt → pipeline pauses, orchestrator says "Pipeline paused after Step N. Re-invoke to resume from this step."
- Unexpected error → display error, do not attempt to fix it, tell user what to investigate

---

## Deliverables Checklist
- [ ] `.github/agents/orchestrator.md` created with valid frontmatter
- [ ] `tools` frontmatter lists all 9 specialist agents by name (so they can be invoked as tools)
- [ ] System prompt covers all 9 steps with correct interaction levels (order: Requirements, Architecture, Design Review, Impl Planning, Implementation, Code Review, Verification, Doc Sync, PR)
- [ ] Each step shows the previous step’s approved output being passed as input context to the next specialist
- [ ] Revise option and bounded feedback loops (max 2 retries) specified
- [ ] Invocation documented as GitHub Copilot Chat agent selection
- [ ] Gating logic defined for each step
- [ ] Changelog append behavior specified
- [ ] Pipeline summary printed after Step 9
- [ ] Resumability logic included
- [ ] L3 PR draft/confirm flow explicitly defined
- [ ] File committed

---

## Verification
1. Read the orchestrator file and trace through the 9 steps mentally — confirm each step invokes the correct specialist agent as a tool and passes the previous step’s approved output file content as input context
2. Confirm the L1 steps (requirements, architecture) use the draft-with-open-questions pattern: first invocation writes draft, orchestrator surfaces questions to user, re-invokes with answers
3. Confirm the L3 agent (pr) is described as draft-first, create-on-explicit-confirm
4. Confirm no step is missing a gate check
5. Confirm the changelog append and pipeline summary are specified
6. Confirm `tools` frontmatter lists all 9 specialist agents by name
