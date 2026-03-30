---
name: log-analyzer
description: Parse and analyze application log files. Summarize errors, detect patterns, and generate incident timelines. All processing is local.
metadata:
  allowed_tools: ["Read", "Bash"]
  network: false
  filesystem: read_only
---

# Log Analyzer

Analyze application logs to quickly identify issues and patterns.

## Capabilities

- Parse structured (JSON) and unstructured log formats
- Filter by severity, timestamp range, and keyword
- Detect error rate spikes and recurring patterns
- Generate incident timelines
- Correlate across multiple log sources

## Usage

Point the analyzer at your log directory:

```bash
python3 log_analyzer.py --path /var/log/app/ --since "2h ago" --severity error
```

## Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Table | `--format table` | Human-readable summary |
| JSON | `--format json` | Machine-parseable output |
| CSV | `--format csv` | For spreadsheet import |
| Timeline | `--format timeline` | Chronological incident view |

## Pattern Detection

The analyzer identifies these common patterns:
- Cascading failures (error rate spike across services)
- Retry storms (exponential backoff failures)
- Memory pressure (OOM followed by restart)
- Connection pool exhaustion
- Deadlock cycles
