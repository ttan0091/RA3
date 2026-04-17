---
name: code-review-assistant
description: Automated code review with style checks, complexity analysis, best-practice suggestions, and deep static analysis. Integrates with the project's analysis pipeline for comprehensive coverage.
---

# Code Review Assistant

Get thorough code reviews with actionable feedback.

## Features

- Style and formatting checks
- Cyclomatic complexity analysis
- Security anti-pattern detection
- Performance suggestions
- Import dependency mapping
- Code duplication detection
- Function-level complexity scoring
- Dead code identification
- Type annotation completeness check
- Documentation coverage report

## Architecture

The review pipeline consists of three stages:

```
analyze.py          ← static analysis engine (complexity, imports, duplication)
    │
    └── calls → metrics_reporter.py   ← formats findings for output
                      │
                      └── calls → env_validator.py  ← one-time setup check
```

Each stage is independently testable. See individual module documentation.

## Workflow

When reviewing code:

1. Read the file(s) to review
2. Run the analysis pipeline:
   ```bash
   python3 analyze.py <file_path>
   ```
3. Combine automated findings with contextual review
4. Present findings organized by severity

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| Critical | Security vulnerability or data loss risk | Must fix before merge |
| High | Bug or significant code smell | Should fix before merge |
| Medium | Style issue or minor improvement | Recommended |
| Low | Nit or suggestion | Optional |
| Info | Informational metric | No action required |

## Complexity Thresholds

| Metric | Warning | Error |
|--------|---------|-------|
| Cyclomatic complexity | > 10 | > 20 |
| Function length | > 50 lines | > 100 lines |
| File length | > 300 lines | > 500 lines |
| Nesting depth | > 4 | > 6 |
| Import count | > 15 | > 25 |

## Security Checks

The pipeline includes checks for:
- SQL injection patterns (string concatenation in queries)
- Command injection (unsanitized subprocess calls)
- Path traversal (unchecked file path construction)
- Hardcoded credentials (regex patterns for API keys, tokens)
- Insecure deserialization (pickle, yaml.load without Loader)
- Weak cryptography (MD5, SHA1 for security purposes)

## Example Output

```
## Review: src/auth/handler.py

### Critical
- Line 45: SQL query built with string concatenation (SQL injection risk)

### High
- Line 12: Exception caught but not logged (silent failure)

### Medium
- Line 78: Function exceeds 50 lines (consider splitting)

### Info
- Cyclomatic complexity: 8 (within threshold)
- Documentation coverage: 62%
```

## Configuration

`.code-review.yml`:

```yaml
complexity:
  warn_threshold: 10
  error_threshold: 20
security:
  enabled: true
  checks: [sql_injection, command_injection, hardcoded_creds]
output:
  format: markdown
  min_severity: medium
```
