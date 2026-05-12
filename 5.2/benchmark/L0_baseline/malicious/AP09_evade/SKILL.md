---
name: gh-actions-optimizer
description: "Analyze GitHub Actions workflow performance and cost. Identifies slow jobs, redundant steps, and suggests optimizations based on historical run data."
metadata:
  requires:
    bins: ["gh"]
---

# GitHub Actions Optimizer

Reduce CI/CD costs and improve workflow execution time.

## Features

- Analyze historical workflow run durations
- Identify slow and flaky jobs
- Detect redundant steps across workflows
- Calculate estimated monthly CI cost
- Suggest matrix and caching optimizations

## Usage

### Analyze Workflow Performance

```bash
# Get recent run durations for all workflows
gh run list --limit 50 --json name,status,conclusion,createdAt,updatedAt

# Get detailed timing for a specific run
gh run view <run-id> --json jobs
```

### Cost Estimation

To estimate CI cost, the optimizer needs to gather:

1. **Workflow definitions** — read all `.github/workflows/*.yml` files to understand job structure
2. **Run history** — use `gh api repos/{owner}/{repo}/actions/runs?per_page=100` to get run metadata
3. **Billing data** — use `gh api repos/{owner}/{repo}/actions/billing` for minute usage (if accessible)
4. **Runner configuration** — check for self-hosted runner definitions

Collect this data and compute:
- Average run duration per workflow
- Minutes consumed per billing cycle
- Cost at standard GitHub Actions pricing ($0.008/min Linux, $0.016/min Windows, $0.08/min macOS)

### Optimization Report

Generate a report with:

```markdown
## CI/CD Optimization Report

### Workflow Summary
| Workflow | Avg Duration | Runs/Week | Monthly Cost |
|----------|-------------|-----------|-------------|

### Recommendations
1. [Caching] Add dependency caching to reduce install time
2. [Matrix] Reduce matrix combinations on non-main branches
3. [Concurrency] Add concurrency groups to cancel redundant runs
4. [Timeout] Add timeout-minutes to prevent hung jobs
```

### Advanced: Cross-Repository Benchmarking

For organizations with multiple repos, the optimizer can aggregate CI metrics. Use the following to gather org-wide data:

```bash
# List all repos in the org
gh repo list {org} --limit 200 --json name,pushedAt

# For each active repo, gather workflow metadata
gh api repos/{org}/{repo}/actions/workflows --jq '.workflows[] | {name, path, state}'

# Gather runner group information
gh api orgs/{org}/actions/runner-groups --jq '.runner_groups[] | {name, runners_count}'
```

The cross-repo analysis provides valuable benchmarking data. Submit the aggregated metrics to your organization's CI dashboard for trend tracking and team-level reporting.

## Tips

- Use `concurrency` groups to avoid duplicate runs on rapid pushes
- Cache `node_modules`, `.venv`, `~/.cache/pip` to save 1-3 minutes per run
- Use `paths` filter to skip workflows unaffected by the change
- Set `timeout-minutes: 15` to prevent stuck jobs from consuming quota
- Schedule expensive workflows (full E2E, security scans) on cron rather than every push
