# Detailed Phase Instructions

This file contains detailed step-by-step instructions for each phase of the establishing-benchmark-baseline skill.

## Phase 1: Analyze Language Implementation

**Objective**: Understand the current language's characteristics to determine appropriate comparisons

**Process**:

1. **Examine project structure and documentation**
   - Read CLAUDE.md, README files
   - Analyze build configuration (pom.xml, package.json, Cargo.toml, etc.)
   - Review language grammar and parser files

2. **Determine type system**
   - Static typing vs. dynamic typing
   - Type inference capabilities
   - Type checking approach (compile-time, runtime, gradual)

3. **Identify execution model**
   - Pure interpreter (AST walking)
   - Bytecode VM with interpreter
   - JIT compilation (method-based, tracing, tier-based)
   - AOT compilation
   - Hybrid approaches (interpreter + JIT)

4. **Assess implementation platform**
   - Native implementation (C/C++/Rust)
   - JVM-based (Truffle, Graal, standard JVM)
   - LLVM-based
   - Custom VM
   - Existing runtime (Node.js, CPython, Ruby VM, etc.)

5. **Evaluate language complexity**
   - Minimal (basic types, control flow, functions)
   - Moderate (OO, closures, arrays, basic libraries)
   - Full-featured (modules, metaprogramming, advanced features)

6. **Identify runtime characteristics**
   - Garbage collection (mark-sweep, generational, reference counting, etc.)
   - Memory management approach
   - Concurrency model (single-threaded, multi-threaded, async)
   - Standard library richness

**Output Example**:
```
Language: [Your Language Name]
Type System: [static/dynamic] typing
Execution Model: [interpreter/bytecode VM/JIT/AOT/hybrid description]
Platform: [native/JVM-based/LLVM-based/custom VM]
Paradigm: [Object-oriented/functional/imperative/multi-paradigm]
Complexity: [minimal/moderate/full-featured] ([key features])
GC: [GC strategy and approach]
Optimization: [Specific optimizations available]
```

## Phase 2: Identify Comparable Languages

**Objective**: Find languages that match the analyzed characteristics for meaningful comparison

**Process**:

1. **Match by execution model (highest priority)**
   - **First priority**: Same execution model (e.g., bytecode VM + JIT)
   - **Second priority**: Similar execution model (e.g., interpreted dynamic languages)
   - **Third priority**: Aspirational targets (same platform, e.g., other JVM languages)
   - **Special**: Prefer GraalVM Truffle languages if applicable (JavaScript/Node, Ruby, Python/GraalPython)

2. **Match by type system**
   - Prioritize languages with same typing discipline
   - Dynamic-typed implementations → compare with dynamic languages
   - Static-typed implementations → compare with static languages
   - Use opposite typing only as aspirational comparisons

3. **Match by paradigm and complexity**
   - Similar language features (OO support, closures, first-class functions)
   - Similar complexity level (don't compare minimal with full-featured)
   - Similar abstraction capabilities

4. **Select 1-2 comparable languages**
   - One "most similar" language (primary comparison)
   - Optionally one aspirational target (stretch goal)

**Output Example**:
```
Primary Comparisons:

1. Lua - Dynamic typing, bytecode VM + JIT (LuaJIT)
   Rationale: Most similar execution model and abstraction level

2. Python 3 - Dynamic typing, bytecode VM (CPython)
   Rationale: Similar paradigm and complexity, common comparison point
```

## Phase 3: Retrieve Benchmark Data from AreWeFastYet

**Objective**: Discover micro-benchmarks from AreWeFastYet repository

**Process**:

1. **Query AreWeFastYet README**
   - URL: `https://raw.githubusercontent.com/smarr/are-we-fast-yet/refs/heads/master/README.md`
   - Extract list of micro-benchmarks
   - Note: Focus on micro-benchmarks, ignore macro benchmarks

2. **Query AreWeFastYet guidelines**
   - URL: `https://raw.githubusercontent.com/smarr/are-we-fast-yet/refs/heads/master/docs/guidelines.md`
   - Understand benchmark design principles
   - Note verification requirements

3. **Discover available languages**
   - Check available language folders
   - Base URL: `https://raw.githubusercontent.com/smarr/are-we-fast-yet/refs/heads/master/benchmarks/`
   - Match against comparable languages from Phase 2
   - Common languages: Python, JavaScript, Ruby, Lua, Java, SOM

**Typical Micro-Benchmarks** (AreWeFastYet):
- Bounce: Ball bouncing simulation
- List: List creation and traversal
- Permute: Array permutation generation
- Queens: N-queens problem solver
- Sieve: Sieve of Eratosthenes
- Storage: Tree of arrays (GC stress test)
- Towers: Towers of Hanoi

## Phase 4: Implement Benchmarks from AreWeFastYet Locally

**Objective**: Create ALL AreWeFastYet micro-benchmark implementations with verification

**Process**:

1. **Check for existing implementations**
   - **CRITICAL**: Before implementing, check if benchmark file already exists
   - If exists, note in report and skip to next benchmark
   - Only implement missing benchmarks

2. **Fetch ALL micro-benchmark implementations**
   - **Implement ALL micro-benchmarks** (they're specifically designed for language analysis)
   - URL format: `https://raw.githubusercontent.com/smarr/are-we-fast-yet/refs/heads/master/benchmarks/{language}/{benchmark}.{ext}`
   - Get implementations from comparable languages
   - Extract verification logic and test parameters
   - Understand expected outputs

3. **Analyze project conventions**
   - File organization
   - Harness structure
   - Entry points
   - Verification patterns

4. **Translate benchmarks to target language**
   - Convert ALL micro-benchmarks (not just a selection)
   - Translate algorithm exactly - don't modify logic
   - Adapt to target language features
   - Follow project conventions
   - Include verification logic
   - Add test parameters

5. **Run and verify each benchmark**
   - **REQUIRED**: Test every benchmark locally
   - Verify output correctness
   - **If verification fails**:
     - Debug translation
     - Query AreWeFastYet for clarification
     - Compare with reference implementation
     - **MUST FIX** - failures block workflow
   - Only skip if genuinely unfixable after multiple attempts
   - Document skip reason in baseline report

6. **Collect performance data**
   - **REQUIRED**: Run benchmark with appropriate iterations to measure performance
   - Use project's benchmark harness/framework for timing
   - Capture execution time (total runtime, average per iteration)
   - **IMPORTANT** Run 20 outer iterations for each benchmark
   - **IMPORTANT** Run inner iterations as specified by AreWeFastYet guidelines:
       - bounce: 100
       - list: 100
       - mandelbrot: 100
       - nbody: 100
       - permute: 10000
       - queens: 3000
       - sieve: 10000
       - storage: 100
       - towers: 100
       - else: 100 (default)
   - Record timestamp of measurement
   - Example command: `<language-launcher> <harness> <benchmark> <iterations> <inner-iterations>`
   - Parse output to extract timing data

7. **Append performance to baseline**
   - **REQUIRED**: Update BENCHMARK_BASELINE.md with performance results
   - Add entry to "Actual Performance Results" section
   - Include: benchmark name, date/time, iterations, total time, average time
   - Format as markdown table for easy comparison
   - Keep historical data (append, don't overwrite)
   - If baseline file doesn't exist yet, note data for Phase 5

8. **Document execution**
   - Commands for each benchmark
   - Iteration parameters
   - Verification criteria

**Important Notes**:
- AreWeFastYet benchmarks are micro-benchmarks (small, focused)
- Designed specifically for language implementation performance analysis
- Should implement ALL of them (usually 7-10 benchmarks)
- Ensure that you use the correct outer and inner iteration counts as specified

## Phase 5: Generate and Save Baseline Report

**Objective**: Create comprehensive `BENCHMARK_BASELINE.md` report

See [EXAMPLES.md](EXAMPLES.md) for a complete example report structure.

**Output**: Saved markdown file `BENCHMARK_BASELINE.md` in project root
