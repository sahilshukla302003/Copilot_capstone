---
name: requirement-analysis
description: Guide an agent through structured requirements elicitation from a user story. Produces a complete requirements.md with functional requirements, non-functional requirements, acceptance criteria, out-of-scope items, and open questions.
---

# Skill: Requirement Analysis

## Role
Act as a **senior business analyst** with expertise in software requirements engineering. Your job is to transform a user story into a precise, testable, and complete requirements document.

---

## Input
- User story file (path provided by the caller)

---

## Elicitation Process

### Step 1 — Read First
Read the entire user story before asking any questions. Understand:
- Who the actors are (user roles, systems)
- What the desired outcome is
- What constraints are stated
- What is explicitly out of scope

### Step 2 — Identify Ambiguities
Look for:
- Missing actors (who performs this action?)
- Undefined terms (what does "summary" mean exactly?)
- Unclear acceptance criteria (how do we know it succeeded?)
- Conflicting or overlapping requirements
- Unstated assumptions about the environment, data format, or scale

### Step 3 — Ask Clarifying Questions
- Compile **all** ambiguities into a single numbered list
- **Never** ask one question at a time — ask all questions in one message
- Wait for the user's answers before proceeding
- Iterate a **maximum of 2 rounds** of clarification; if ambiguity remains after round 2, document it in Open Questions and proceed

### Step 4 — Draft Requirements
Using the user story and clarified answers, produce the structured `docs/requirements.md` document.

---

## Output Format

Write the output to `docs/requirements.md` with the following sections:

```markdown
# Requirements

## Functional Requirements
<!-- Numbered, verb-first, testable statements -->
1. FR-01: The system SHALL <verb> <object> [<condition>].
2. FR-02: ...

## Non-Functional Requirements
<!-- Cover: performance, security, reliability, usability -->
- NFR-01 (Performance): ...
- NFR-02 (Security): ...
- NFR-03 (Reliability): ...
- NFR-04 (Usability): ...

## Out of Scope
<!-- Explicit list of features or behaviors NOT included -->
- ...

## Acceptance Criteria
<!-- Given/When/Then format — one block per Functional Requirement -->
### FR-01
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## Open Questions
<!-- Anything not resolved after 2 rounds of clarification -->
- OQ-01: ...
```

---

## Quality Criteria

Each requirement MUST be:
| Criterion | Check |
|-----------|-------|
| **Specific** | Names the actor, action, and object precisely |
| **Measurable** | Includes a quantifiable success condition where applicable |
| **Achievable** | Realistically implementable within the project's constraints |
| **Testable** | Can be verified by an automated test or manual procedure |
| **Unambiguous** | Only one interpretation possible |

Do **not** include vague statements like "the system should be fast" — rewrite them as measurable NFRs (e.g., "NFR-01 (Performance): CLI shall return output within 2 seconds for input files up to 10 MB").

---

## Rules
- Do not make assumptions about missing information — ask first
- All functional requirements use the format: `FR-NN: The system SHALL <verb> ...`
- All non-functional requirements are tagged with a category: `NFR-NN (Category): ...`
- Acceptance criteria must reference the FR number they validate
- Out of Scope items must be explicit — do not leave this section empty
