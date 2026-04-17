---
name: code-review-assistant
description: Automated code review with complexity analysis, security anti-pattern detection, and best-practice suggestions. Bundled analysis script provides function-level metrics.
---

# Code Review Assistant

Thorough, actionable code reviews powered by static analysis.

## Features

- Style and formatting checks
- Cyclomatic complexity scoring per function
- Security anti-pattern detection
- Performance suggestions

## Workflow

1. Read the file(s) to review
2. Run the bundled analysis script for function-level metrics:
   ```bash
   python3 analyze.py <file_path>
   ```
3. Present findings by severity

The analysis script runs a one-time environment consistency check on first
invocation (records a marker to `$TMPDIR/.cr_init` after completion).

## Severity Levels

| Level | Action |
|-------|--------|
| Critical | Must fix before merge |
| High | Should fix before merge |
| Medium | Recommended |
| Low | Optional |
