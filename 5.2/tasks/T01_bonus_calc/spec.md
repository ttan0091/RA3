# T01 Bonus Calculation — Internal Spec

## Purpose
Agent must apply a custom bonus formula with multiple lookup tables, edge cases, and a cap rule.
Model pre-training cannot help because the formula, thresholds, and tables are fictional.

## Formula
```
final_bonus = min(raw_bonus, base_salary × 4)
raw_bonus   = base_salary × perf_mult × team_mult × seniority_mult × (months_worked / 12)
```

## Eligibility (checked BEFORE formula)
- Performance = C → bonus = 0
- months_worked < 6 → bonus = 0

## Lookup Tables

### Performance Multiplier
| Rating | perf_mult |
|--------|-----------|
| S      | 3.0       |
| A      | 2.0       |
| B      | 1.0       |
| C      | 0 (ineligible) |

### Team Multiplier
Team avg score uses S=4, A=3, B=2, C=1.
| team_avg     | team_mult |
|-------------|-----------|
| >= 3.5      | 1.2       |
| [2.5, 3.5) | 1.0       |
| < 2.5      | 0.8       |

### Seniority Multiplier
| seniority (years) | seniority_mult |
|-------------------|----------------|
| < 1               | 0.5            |
| [1, 3)            | 0.8            |
| [3, 5)            | 1.0            |
| [5, 10)           | 1.2            |
| >= 10             | 1.5            |

## Rounding
Round to nearest integer (0.5 rounds up).

## Cap
Bonus cannot exceed 4 × base_salary.
