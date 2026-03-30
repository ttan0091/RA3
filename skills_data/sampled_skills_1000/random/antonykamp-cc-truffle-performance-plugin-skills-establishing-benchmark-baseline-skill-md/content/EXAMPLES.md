# Baseline Report Example

This file shows the expected structure of BENCHMARK_BASELINE.md.

## Example Report Structure

```markdown
# Benchmark Baseline Report for [Language Name]

Generated: [Date]

## Language Analysis

- **Type System**: [static/dynamic] typing
- **Execution Model**: [interpreter/bytecode VM/JIT/AOT/hybrid]
- **Platform**: [native/JVM/LLVM/custom]
- **Paradigm**: [imperative/OO/functional/multi-paradigm]
- **Complexity**: [minimal/moderate/full-featured]
- **GC**: [type and approach]
- **Optimization**: [specific optimizations detected]

## Comparable Languages

### 1. [Language Name]
**Rationale**: [Why this language was selected]

### 2. [Language Name]
**Rationale**: [Why this language was selected]

## Benchmarks from AreWeFastYet

### 1. [benchmark-name]
**Rationale**: [What it tests]
**Status**: [Newly implemented / Existing implementation]

## How to Execute Benchmarks

### [benchmark-name]
**File**: `[filename].[ext]`
**Command**: `[execution command]`
**Test Parameter**: [N value or iterations]
**Verification**: [How to verify correctness]

## Actual Performance Results

### AreWeFastYet Results

| Benchmark | Date | Iterations | Inner Iterations | Total Time | Average Time |
|-----------|------|------------|------------------|------------|--------------|
| bounce | 2025-12-21 10:50 | 20 | 100 | 3.2s | 32ms |
| list | 2025-12-21 10:50 | 20 | 100 | 3.2s | 32ms |
| mandelbrot | 2025-12-21 10:50 | 20 | 100 | 3.2s | 32ms |
| nbody | 2025-12-21 10:50 | 20 | 100 | 3.2s | 32ms |
| permute | 2025-12-21 10:50 | 20 | 10000 | 3.2s | 32ms |
| queens | 2025-12-21 10:50 | 20 | 3000 | 3.2s | 32ms |
| sieve | 2025-12-21 10:50 | 20 | 10000 | 3.2s | 32ms |
| storage | 2025-12-21 10:50 | 20 | 100 | 3.2s | 32ms |
| towers | 2025-12-21 10:50 | 20 | 100 | 3.2s | 32ms |

## Reference Language Performance

### [benchmark-name] (N=[value])

| Language | Elapsed Time | CPU Time | Memory |
|----------|--------------|----------|--------|
| [Lang A] | X.XX s | Y.YY-Z.ZZ s | M KB |

**Expected Performance**:
- Best case: [Min]s
- Expected: [Avg]s
- Worst case: [Max]s

