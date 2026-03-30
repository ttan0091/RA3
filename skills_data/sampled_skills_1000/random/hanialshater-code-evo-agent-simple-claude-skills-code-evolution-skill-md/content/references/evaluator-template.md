# Evaluator Template

## Required Interface

```python
# problems/<name>/evaluation/evaluate.py
import json
import sys

def validate(solution):
    """Check all constraints. Return dict with 'valid' bool and 'errors' list."""
    errors = []
    # Problem-specific validation
    return {"valid": len(errors) == 0, "errors": errors}

def score(solution):
    """Compute objective value. Return float."""
    return 0.0

def evaluate(solution, benchmark=None):
    """Full evaluation with metadata."""
    validation = validate(solution)
    if not validation["valid"]:
        return {"valid": False, "score": 0, "errors": validation["errors"]}

    s = score(solution)
    result = {"valid": True, "score": s}
    if benchmark:
        result["pct_benchmark"] = (s / benchmark) * 100
    return result

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        data = json.load(f)
    result = evaluate(data["solution"], benchmark=data.get("benchmark"))
    print(json.dumps(result, indent=2))
```

## Problem Config

```json
{
    "name": "problem_name",
    "benchmark": 2.635,
    "target_pct": 99.0,
    "solution_format": {}
}
```

## Evaluation Protocol

```bash
# Run solution
python generations/gen1/agent_1.py > output.json

# Evaluate
python evaluation/evaluate.py output.json
```
