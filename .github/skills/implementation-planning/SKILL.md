---
name: implementation-planning
description: Break an approved architecture into an ordered, dependency-aware implementation task list. Produces a structured impl-plan.md with a task table, dependency graph, blocked tasks, and a Definition of Done.
---

# Skill: Implementation Planning

## Role
Act as a **senior engineering lead doing sprint planning**. Your job is to convert an approved architecture and design review into a precise, dependency-ordered implementation plan that any developer can follow.

---

## Input
- `docs/architecture.md` (content passed by the caller)
- `docs/design-review.md` (content passed by the caller)

---

## Planning Process

### Step 1 — List All Implementation Tasks
Read the architecture and design review. For every component and data flow, derive implementation tasks. A task is:
- A cohesive unit of work (one module, one class, one integration point)
- Completable and testable in isolation
- No larger than "1 day of focused work"

### Step 2 — Identify Dependencies
For each task, determine:
- Which other tasks must be complete before this one can start
- Which tasks can run in parallel

### Step 3 — Topological Sort
Order tasks so that all dependencies come before dependants. Tasks with no dependencies go first.

### Step 4 — Estimate Complexity
Assign a complexity estimate to each task:
| Label | Meaning |
|-------|---------|
| **S** | < 2 hours — simple function, data class, config |
| **M** | 2–5 hours — module with multiple functions, basic integration |
| **L** | 5–8 hours — complex logic, external integration, heavy testing |

### Step 5 — Flag Blocked Tasks
If a task cannot start until an external factor is resolved (missing credentials, third-party API access, design decision), mark it as BLOCKED and document the blocker.

### Step 6 — Pair Tests with Implementation Tasks
Every implementation task must have a corresponding test task. Test tasks are separate rows in the task table and must declare their dependency on the implementation task.

---

## Output Format

Write the output to `docs/impl-plan.md` with the following sections:

```markdown
# Implementation Plan

## Task Table
| ID | Task Name | Description | Depends On | Complexity | File(s) Affected |
|----|-----------|-------------|------------|------------|-----------------|
| T-01 | ... | ... | — | S/M/L | `src/...` |
| T-02 | ... | ... | T-01 | M | `src/...` |
| T-T01 | Test: <T-01 name> | Unit tests for T-01 | T-01 | S | `tests/unit/...` |

## Dependency Graph
<!-- ASCII diagram showing task ordering -->
T-01 ──► T-02 ──► T-03
              └──► T-04
T-T01 (after T-01)
T-T02 (after T-02)

## Blocked Tasks
<!-- Tasks that cannot start without external resolution -->
| ID | Blocker | Resolution Required |
|----|---------|---------------------|
| T-XX | Missing X credential | ... |

_(If no blocked tasks, write: "None")_

## Definition of Done
The implementation is complete when:
- [ ] All tasks in the task table are marked complete
- [ ] All unit tests pass (`pytest tests/unit/ -v`)
- [ ] All integration tests pass (`pytest tests/integration/ -v`)
- [ ] Test coverage ≥ 80% (`pytest --cov=src --cov-report=term-missing`)
- [ ] No open Critical or Major findings from code review
- [ ] `docs/` reflects the final implementation
```

---

## Quality Criteria
- Every architecture component maps to at least one implementation task
- Every implementation task has a paired test task
- No task is larger than L complexity (if it is, break it down)
- Dependency graph accurately reflects the task table
- The plan is ordered — a developer can execute tasks top-to-bottom without backtracking

---

## Rules
- Tasks must result in **runnable, testable code** — no "research" or "decide" tasks
- Test tasks use the prefix `T-T<NN>` and reference their implementation task in "Depends On"
- Blocked tasks must state a concrete resolution path, not just the blocker
- Do not include tasks for things already provided by the framework/stdlib without justification
- The Definition of Done is mandatory — do not omit it
