---
name: code-review
description: Code review against project standards and structural discipline. Returns APPROVE/REJECT verdict.
allowed-tools: Read, Grep, Glob, Bash
model: opus
---

# Code Review

Review implementation for code quality, structural discipline, and adherence to project standards.

## Your Workflow

### 1. Get the Diff

First, determine what to review. **Staged changes take priority over committed changes** since the Ralph workflow stages before committing:

```bash
BASE_BRANCH="main"

# Check for staged changes first (Ralph workflow stages before commit)
STAGED_CHANGES=$(git diff --cached --stat 2>/dev/null)
COMMITTED_CHANGES=$(git diff $BASE_BRANCH...HEAD --stat 2>/dev/null)

if [ -n "$STAGED_CHANGES" ]; then
  echo "DIFF_MODE: staged"
  echo "Reviewing staged changes (not yet committed)"
  echo "---"
  git diff --cached --stat
elif [ -n "$COMMITTED_CHANGES" ]; then
  echo "DIFF_MODE: committed"
  echo "Reviewing commits since $BASE_BRANCH"
  echo "---"
  git diff $BASE_BRANCH...HEAD --stat
else
  echo "ERROR: No staged or committed changes to review"
  echo "Nothing to review - aborting"
  exit 1
fi
```

Then get the actual diff using the appropriate command:
- **Staged**: `git diff --cached`
- **Committed**: `git diff main...HEAD`

Also get context:
```bash
# Get commit history for context (if any commits)
git log main..HEAD --oneline 2>/dev/null || echo "No commits yet"
```

### 2. Load Project Standards

Read `CLAUDE.md` to understand codebase-specific standards:

```bash
cat CLAUDE.md
```

Also check for crate-specific `CLAUDE.md` files in changed directories.

### 3. Apply Review Criteria

Review the diff using the criteria defined in `REVIEW_CRITERIA.md` (at the repo root):

- **Structural Checklist**: Dependency injection, single responsibility, testing seams, interface boundaries, codebase consistency
- **Test Quality**: Functional core/imperative shell, test smells
- **YAGNI**: Feature YAGNI (reject) vs structural YAGNI (accept)
- **CLAUDE.md Violations**: Project-specific rules

### 4. Return Structured Verdict

Your output MUST follow this exact format:

```
VERDICT: APPROVE | REJECT

SUMMARY:
<1-2 sentence overview of the changes>

STRENGTHS:
<What's well done - cite file:line>

ISSUES:

Critical (Must Fix):
<Bugs, security issues, data loss risks - or "None">

Important (Should Fix):
<Architecture problems, missing error handling, test gaps - or "None">

Minor (Nice to Have):
<Style, optimization, documentation - or "None">

VERDICT REASONING:
<1 sentence explaining APPROVE or REJECT decision>
```

## When to APPROVE

- Implementation is correct for its stated scope
- No critical or blocking important issues
- Follows project standards from CLAUDE.md
- Structural discipline is maintained

## When to REJECT

- Critical issues exist (bugs, security, data loss)
- Important issues that block merging
- Pervasive test quality problems
- Clear CLAUDE.md violations

## What This Review Does NOT Do

This review focuses on code quality and structural discipline. It does **not**:
- Post comments on downstream/related issues
- Evaluate impact on future work
- Update any GitHub issues

Those concerns are handled by the reflect phase after reviews complete.
