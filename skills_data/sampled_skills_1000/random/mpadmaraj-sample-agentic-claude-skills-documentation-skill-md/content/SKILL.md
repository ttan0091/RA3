---
name: documentation
description: Defines a structured workflow for creating r improving README.md files, ensuring clarity, accuracy, and consistency while deferring content decisions and execution to a documentation-focused agent.
---

# Skill: README Documentation Workflow

## Purpose
Provide a repeatable workflow for improving `README.md` files
without prescribing specific wording or content.

This skill defines **how documentation work should proceed**,
not what the documentation must say.

---

## When to Use
- Creating a new README.md
- Improving or restructuring an existing README.md
- Reviewing README.md for clarity and completeness

---

## Inputs
- Existing README.md (if present)
- Project structure
- Project intent and audience
- Documentation guidelines from `agents.md`
- perform git remote pull for README.md before you start updating

---

## Outputs
- Updated README.md that is:
  - Clear and scannable
  - Accurate with respect to the project
  - Consistent with repository structure

---

## Governing Rules
This workflow must align with:
- Documentation-related guidance in `agents.md`
- Scope and limitations defined by the active documentation agent

If conflicts arise, the agent’s role definition and `agents.md` take precedence.

---

## Workflow
1. Assess the current README.md (if it exists)
2. Identify missing or unclear sections
3. Propose a logical section structure
4. Improve clarity and scannability
5. Validate links and references
6. Ensure content reflects the current state of the repository
7. Perform a final readability pass

---

## Quality Checks
Before completion, ensure:
- Headings follow a clear hierarchy
- Sections are concise and skimmable
- Instructions are actionable
- No misleading or speculative content is introduced

---

## Failure Handling
- Stop if project purpose is unclear
- Stop if documentation would contradict the codebase
- Ask for clarification rather than guessing

---

## Output Files

### 1. `docs/{random-no}/review-document.md`

## Notes for Review
Record:
- Assumptions made
- Sections intentionally left out
- Follow-up documentation needs
