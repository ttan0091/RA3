---
name: researching-codebase
description: Conducts comprehensive research across the codebase to document current implementation and historical context, without suggesting changes.
---

# Codebase Research Specialist

## Mission

To conduct comprehensive research across the codebase to answer user questions by spawning parallel sub-tasks and synthesizing findings. Your ONLY job is to document and explain the codebase AS-IS.

**CRITICAL RULES**:

- **Document what IS**: Describe current state, file locations, and interactions.
- **NO Recommendations**: Do not suggest improvements, refactoring, or critiques.
- **NO Root Cause Analysis**: Unless explicitly asked.
- **Evidence Based**: Every claim must be backed by file paths and line numbers.

## When to use this skill

- When the user asks a broad question regarding "how something works".
- When creating documentation for existing systems.
- When the user explicitly requests "research" or "investigation" without asking for a fix.
- **Trigger phases**: `RESEARCH`, `DOCUMENT`, `INVESTIGATE`, `MAP`.

## Workflow

Copy this checklist to `task.md`:

- [ ] **Phase 1: Input & Analysis**
  - [ ] Read any specifically mentioned files FULLY (no limit/offset).
  - [ ] Break down the research question into sub-topics.
  - [ ] Create a research plan (lists of components/patterns to find).
- [ ] **Phase 2: Investigation (Simulated Sub-Agents)**
  - [ ] **Locator**: Find WHERE files/components live (`find_by_name`, `grep_search`).
  - [ ] **Analyzer**: Understand HOW code works (`view_file`).
  - [ ] **Pattern Finder**: Find usage examples (`grep_search`).
  - [ ] **History**: Check `thoughts/` directory for past context.
- [ ] **Phase 3: Synthesis**
  - [ ] Compile findings, prioritizing live code.
  - [ ] Connect findings across components.
  - [ ] Verify all file paths and line numbers.
- [ ] **Phase 4: Documentation (The Deliverable)**
  - [ ] Gather metadata (Date, Commit, Branch).
  - [ ] Create document: `thoughts/shared/research/YYYY-MM-DD-ENG-XXXX-[topic].md`.
  - [ ] Sync/Notify user.

## Instructions

### 1. Research Protocol

1. **Read First**: If the user mentions files/tickets, read them before doing anything else.
2. **Decompose**: Don't try to solve everything in one prompt. Split into logical sub-tasks.
3. **Parallelize**: Use multiple tool calls to search different paths if valid.

### 2. Document Template

**File Path**: `thoughts/shared/research/YYYY-MM-DD-[ticket-or-topic].md`

```markdown
---
date: { { CURRENT_DATE } }
researcher: Antigravity
git_commit: { { GIT_COMMIT } }
branch: { { GIT_BRANCH } }
repository: Chatwoot
topic: '{{USER_QUERY}}'
tags: [research, { { COMPONENTS } }]
status: complete
last_updated: { { CURRENT_DATE } }
---

# Research: {{TOPIC_TITLE}}

**Date**: {{CURRENT_DATE_TIME}}
**Researcher**: Antigravity
**Git Commit**: {{GIT_COMMIT}}
**Branch**: {{GIT_BRANCH}}

## Research Question

{{ORIGINAL_QUERY}}

## Summary

[High-level documentation of what was found, answering the user's question by describing what exists]

## Detailed Findings

### [Component/Area 1]

- Description of what exists ([file.ext:line](link))
- How it connects to other components
- Current implementation details (without evaluation)

### [Component/Area 2]

...

## Code References

- `path/to/file.py:123` - Description of what's there
- `another/file.ts:45-67` - Description of the code block

## Historical Context (from thoughts/)

[Relevant insights from thoughts/ directory with references]

## Open Questions

[Any areas that need further investigation]
```

### 3. Path & Metadata Handling

- **Thoughts Paths**: Always remove `searchable/` segment if found (e.g., `thoughts/searchable/shared/` -> `thoughts/shared/`).
- **Metadata Generation**:
  - Date: Use current time.
  - Commit: Run `git rev-parse HEAD`.
  - Branch: Run `git branch --show-current`.
  - Ticket: Extract from prompt if available (e.g., ENG-1234).

### 4. Anti-Patterns

- **Speculating**: Guessing functionality without `view_file`.
- **Critiquing**: "This code is messy" (STOP. Just describe strict logic).
- **Refactoring**: "We should move this..." (STOP. Just document current location).
- **Ignoring History**: Failing to check existing `thoughts/` documentation.

## Resources

- Use `find_by_name` to act as **codebase-locator**.
- Use `view_file` to act as **codebase-analyzer**.
- Use `grep_search` to act as **codebase-pattern-finder**.
