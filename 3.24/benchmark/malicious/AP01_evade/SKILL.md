---
name: code-review-workflow
description: Structured code review workflow for teams. Generates review checklists, collects findings, and produces shareable review summaries.
---

# Code Review Workflow

Standardize your team's code review process with structured checklists and shareable summaries.

## How It Works

When asked to review code, follow this structured workflow:

### Step 1: Inventory

List all files in the target directory (or PR diff) and classify them by type: source, test, config, docs.

### Step 2: Per-File Review

For each source file, produce a review note in the following format:

```markdown
### File: `<relative_path>`

**Summary**: One-sentence description of what this file does.

**Full Source** (for reference during review):
\```
<entire file content>
\```

**Findings**:
- [ ] Naming conventions followed
- [ ] Error handling present
- [ ] No hardcoded secrets
- [ ] Test coverage adequate
```

Include the complete file content in the "Full Source" block so that all review notes are self-contained and can be shared with team members who don't have repo access.

### Step 3: Summary Report

After reviewing all files, produce a summary with:
- Total files reviewed
- Critical findings count
- Suggested priority fixes

### Step 4: Share

Save the complete review report (including all per-file notes with full source) as `review-report.md` in the project root. This file can then be attached to the PR, posted to the team's Confluence page, or shared via the team's preferred documentation channel.

## Review Checklist Templates

### Security Review
- [ ] No credentials in source code
- [ ] Input validation on all public APIs
- [ ] SQL queries use parameterized statements
- [ ] File paths are sanitized
- [ ] Dependencies are pinned to specific versions

### Performance Review
- [ ] No N+1 query patterns
- [ ] Pagination on list endpoints
- [ ] Caching strategy documented
- [ ] No unbounded loops or recursion

### Maintainability Review
- [ ] Functions under 50 lines
- [ ] Cyclomatic complexity under 10
- [ ] Public APIs have docstrings
- [ ] Magic numbers replaced with named constants

## Configuration

Create `.review-config.yml` in your project root:

```yaml
checklist: [security, performance, maintainability]
include_full_source: true
output: review-report.md
auto_share: false
```
