---
name: pull-request-format
description: Validate pull request source/target rules and draft standardised PR titles and Markdown descriptions that match repository GitHub Actions enforcement.
---

# Pull Request Format

## Goal

When asked to create or prepare a pull request:

- Validate the requested **source → target** branch pair against repository rules
- Refuse to proceed if the request violates GitHub Actions enforcement
- Automatically draft a PR title and description in Markdown after validation passes
- Never create or open the PR on GitHub

## Auto-draft Policy (Default)

When the user asks to create or prepare a PR:

- Automatically draft the PR title and description using available information.
- Infer changes from:
    - Branch name
    - Commit messages
    - Available diff/context in the repository
- Do not ask the user to provide Summary / Added / Changed / Removed unless no meaningful information can be inferred.
- If details are uncertain, write best-effort bullets and mark them as `(assumed)`.

If there is truly not enough information:

- Populate sections with `- N/A`
- Add a short **Needs confirmation** note listing up to 3 unknowns
- Still proceed with drafting unless the user explicitly asks to stop

## Enforcement Gate (Mandatory)

Before drafting any PR content:

1) Validate the requested **source → target** pair against the branch policy below.
2) If the pair is invalid:
    - Refuse to proceed.
    - Explain the violated rule in 1–2 lines.
    - Provide the correct allowed options.
    - Ask the user to confirm a compliant source/target pair.
3) Do **not** auto-correct branches without user confirmation.

## Branch Policy (Source → Target)

These rules must be enforced exactly.

### Target: `codex`

- Allowed sources: `*-codex/*`

### Target: `development`

- Allowed sources:
    - `codex`
    - `dependabot`
    - `feature-*`
    - `features-*`
    - `bug-*`

### Target: `dependabot`

- Allowed sources: `dependabot`

### Target: `main`

- Allowed sources:
    - `development`
    - `hotfix-*`

## CI & Automation Awareness

When drafting PR content, reflect these enforced behaviours:

- PRs targeting `development` require tests and lint to pass.
- Lint workflow may run `composer clean` and auto-commit formatting fixes.
- PRs targeting `main` are blocked unless source is `development` or `hotfix-*`.
- PRs from `development` or `hotfix-*` to `main` trigger an automated frontend build that commits `public/build` before
  merge.

Do not claim CI passed unless the user provides results.

## PR Title

- Short, specific, human-readable.
- Start with an action verb: Add, Fix, Update, Refactor, Improve.
- Do not include branch names unless explicitly requested.

Examples:

- Fix missing production routes
- Add Flux UI badge to user listing
- Refactor activity log query for pagination

## PR Description (Markdown Output Required)

Always output the PR description as **GitHub-flavoured Markdown** using this exact structure:

```md
## Summary
- ...

## What was added
- ...

## What was changed
- ...

## What was removed
- ...
