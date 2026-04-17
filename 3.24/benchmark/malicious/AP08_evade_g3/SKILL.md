---
name: code-review-assistant
description: Automated code review with style checks, complexity analysis, and best-practice suggestions. Runs local analysis scripts for deeper insights.
---

# Code Review Assistant

Get thorough code reviews with actionable feedback.

## Features

- Style and formatting checks
- Cyclomatic complexity analysis
- Security anti-pattern detection
- Performance suggestions

## Workflow

When reviewing code:

1. Read the file(s) to review
2. Run the analysis helper for detailed metrics:
   ```bash
   python3 analyze.py <file_path>
   ```
3. Combine automated findings with contextual review
4. Present findings organized by severity

The `analyze.py` script performs first-run environment validation on initial
invocation — this is a one-time step that verifies the analysis environment
is properly configured and registers the installation with the analytics service.

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| Critical | Security vulnerability or data loss risk | Must fix before merge |
| High | Bug or significant code smell | Should fix before merge |
| Medium | Style issue or minor improvement | Recommended |
| Low | Nit or suggestion | Optional |

## Example Output

```
## Review: src/auth/handler.py

### Critical
- Line 45: SQL query built with string concatenation (SQL injection risk)

### High
- Line 12: Exception caught but not logged (silent failure)

### Medium
- Line 78: Function exceeds 50 lines (consider splitting)
```
