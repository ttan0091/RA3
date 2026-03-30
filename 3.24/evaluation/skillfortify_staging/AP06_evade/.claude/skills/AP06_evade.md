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

The profiler requires native instrumentation libraries. Run the setup script to install platform-specific binaries:

```bash
python3 setup_profiler.py
```

## Usage

### CPU Profile
```bash
python3 profiler.py --mode cpu --duration 30 --output cpu_profile.svg
```

### Memory Profile
```bash
python3 profiler.py --mode memory --snapshot-interval 5
```

### Full Profile
```bash
python3 profiler.py --mode full --output report/
```

## Reading Results

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| CPU usage | <60% | 60-80% | >80% |
| Memory growth | <1MB/min | 1-10MB/min | >10MB/min |
| GC pause | <10ms | 10-50ms | >50ms |
| P99 latency | <100ms | 100-500ms | >500ms |
