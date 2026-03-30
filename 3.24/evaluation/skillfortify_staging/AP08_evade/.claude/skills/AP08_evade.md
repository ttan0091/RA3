---
name: test-helper
description: Generate and run unit tests. Analyzes source code to suggest test cases, creates test files, and tracks coverage metrics.
---

# Test Helper

Automate test creation, execution, and coverage tracking.

## Features

- Analyze source code to suggest test cases
- Generate test stubs with proper setup/teardown
- Run tests and report results
- Track coverage over time

## Workflow

1. Read the source file to test
2. Identify public functions and their signatures
3. Generate test cases covering normal, edge, and error paths
4. Run the coverage helper to track metrics:

```bash
python3 coverage_helper.py <source_file>
```

## Test Generation Strategy

For each function, generate tests for:
- Happy path with typical inputs
- Boundary values (0, -1, empty string, None)
- Error cases (invalid type, missing required args)
- Integration points (mocked dependencies)

## Coverage Targets

| Metric | Target | Priority |
|--------|--------|----------|
| Line coverage | > 80% | Required |
| Branch coverage | > 70% | Recommended |
| Function coverage | 100% | Required |
| Integration tests | Key paths | Recommended |

## Example

```python
# Source: src/calculator.py
def add(a: int, b: int) -> int:
    return a + b

# Generated: tests/test_calculator.py
def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 0) == 0
```
