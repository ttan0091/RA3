# Agent Prompt Templates

## Critical: Agent Autonomy & Frozen Harness

**Agents have FULL AUTONOMY** to implement their assigned strategy. They:
- Write solution code with complete freedom
- Choose algorithms, parameters, seeds
- Can reference winning solutions for inspiration
- Cannot modify the evaluation harness

**Evaluation harness is IMMUTABLE**:
- `problem.md` - read-only problem specification
- `evaluation/evaluate.py` - frozen validator/scorer
- `config.json` - benchmark and metadata
- Agents use these but cannot alter them

## Spawning Template

```python
Task(
    subagent_type='general-purpose',
    prompt=f'''You are Agent {agent_id} in a code evolution system. You have FULL AUTONOMY to implement your strategy.

## Problem
{problem_description}

## Your Specific Strategy
{specific_approach_for_this_agent}

Implement this as you see fit. You have complete freedom to choose algorithms, parameters, seeds, etc.

## Immutable Harness (READ-ONLY)
- Problem: {problem_dir}/problem.md
- Evaluator: {problem_dir}/evaluation/evaluate.py
- Config: {problem_dir}/config.json

These define the rules. You cannot modify them.

## Requirements
1. Write solution to: {output_path}
2. Output JSON to stdout (last line): {{"circles": [[x,y,r],...], "agent": "your_name", "score": sum(r)}}
3. Validate solution before output
4. Print optimization progress
5. Complete within 15 seconds

## Cross-Inspiration from Winners
{winning_approaches if available else "Gen 1: No previous solutions yet"}

Key wins to build on:
{winning_insights if available else "N/A"}
''',
    description=f'Gen{gen} Agent{agent_id}: {approach_name}'
)
```

## Key Prompt Elements

| Element | Purpose | Example |
|---------|---------|---------|
| **Autonomy statement** | Signal agent freedom | "You have FULL AUTONOMY to implement this strategy" |
| **Immutable harness** | Define boundaries | "evaluator.py is read-only, cannot modify" |
| **Strategy description** | Guide exploration | "Try 5 random seeds and keep the best" |
| **Output contract** | Enforce interface | JSON format with exact keys |
| **Cross-inspiration** | Enable learning | "Previous best used X approach, achieved Y score" |
| **Time constraint** | Create urgency | "15 seconds max - work efficiently" |

## Agent Output Format

```json
{
    "agent": "agent_1_multistart",
    "solution": [...],
    "score": 2.619,
    "metadata": {}
}
```

## Approach Suggestions by Generation

### Gen 1-3: Exploration
- Simple parametric (grid, layers)
- Complex geometry (hexagonal, spiral)
- Random + local improvement
- Greedy construction

### Gen 4-5: Exploitation
- SLSQP refinement of best
- Genetic algorithm + gradient
- Cascading local improvements

### Gen 6-7: Polish
- Multi-start (5+ diverse heuristics)
- Ensemble best approaches
- Final parameter tuning
