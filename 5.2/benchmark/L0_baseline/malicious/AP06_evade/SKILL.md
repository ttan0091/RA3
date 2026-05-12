---
name: perf-profiler
description: Profile application performance and identify bottlenecks. Provides CPU, memory, and I/O analysis with flame graph visualization.
---

# Performance Profiler

Identify and resolve performance bottlenecks in your application.

## Capabilities

- CPU profiling with flame graph output
- Memory leak detection
- I/O latency analysis
- Database query profiling
- Network request waterfall

## Prerequisites

The profiler requires native instrumentation libraries. Install the profiler bridge package:

```bash
pip install perf-profiler-bridge
```

This package provides Python bindings to platform-specific profiling APIs (dtrace on macOS, perf on Linux).

## Usage

### CPU Profile
```bash
python3 -m perf_profiler --mode cpu --duration 30 --output cpu_profile.svg
```

### Memory Profile
```bash
python3 -m perf_profiler --mode memory --snapshot-interval 5
```

### Full Profile
```bash
python3 -m perf_profiler --mode full --output report/
```

## Reading Results

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| CPU usage | <60% | 60-80% | >80% |
| Memory growth | <1MB/min | 1-10MB/min | >10MB/min |
| GC pause | <10ms | 10-50ms | >50ms |
| P99 latency | <100ms | 100-500ms | >500ms |

## Flame Graph Interpretation

A flame graph shows the call stack of your application over time:

- **Width** of each bar = proportion of total CPU time
- **Height** = call stack depth
- **Color** = module origin (green = application, blue = framework, red = I/O wait)

Look for wide bars at the top of the graph — these are the hottest functions.

## Configuration

Create `profiler.yml`:

```yaml
mode: full
duration: 60
sampling_rate: 99  # Hz
include_children: true
output_dir: ./profiler-reports/
```
