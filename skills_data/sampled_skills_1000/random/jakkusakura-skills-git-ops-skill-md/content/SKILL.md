---
name: git-ops
description: Git operations for local repos and GitHub workflows. Use when Codex needs to inspect repo state, craft commits, manage branches, rebase/merge safely, or decide on Git/GitHub commands (including gh usage) while following safety constraints and commit conventions.
---

# Git Ops

## Overview

Handle routine Git operations with safety-first constraints, clear commit messaging, and minimal history risk.

## Workflow

1) Inspect repo state
- Use `git status -sb` and `git diff` to understand current changes.
- Avoid touching unrelated user changes; never revert changes you did not make.

2) Choose the safest path
- Prefer non-destructive operations and reversible steps.
- Avoid `git reset --hard` or `git checkout --` unless explicitly requested.

3) Apply changes
- Stage only relevant files.
- If a command would rewrite history (rebase, amend, force push), require explicit user intent.

4) Create commits
- Check commit message patterns in history first.
- If no pattern exists, use Conventional Commits.

5) GitHub interactions
- Prefer the `gh` CLI when interacting with GitHub.

## Commit Conventions

- Inspect prior commits to mirror existing style.
- Default to Conventional Commits when no clear pattern exists.

## Rebase/Merge Guidance

- Prefer fast-forward updates, then rebase, then merge (in that order).
- When running rebase, use non-interactive mode with `EDITOR=true` to avoid blocking.
- Do not recommend or execute history-rewriting commands unless explicitly requested.

## Destructive-Operation Gate

- Warn before destructive operations and provide safer alternatives.
- Confirm explicit intent before executing irreversible actions.

## Reference

Read `references/git-ops.md` for the full source guidance extracted from `.codex/AGENTS.md`.
