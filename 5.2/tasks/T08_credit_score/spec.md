# T08 Credit Scoring — Internal Spec

## Purpose
Agent must compute a credit score from multiple factors using lookup tables, then determine loan tier.
Model pre-training cannot help because the point values, tiers, and thresholds are custom.

## Input Fields
- monthly_income: float
- employment_years: float
- debt_ratio: percentage (0-100)
- has_mortgage: bool
- has_car_loan: bool
- age: int
- past_defaults: int (number of past loan defaults)

## Point Scoring

### Income Points
| Monthly Income     | Points |
|-------------------|--------|
| < 5000            | 10     |
| 5000 – 9999       | 20     |
| 10000 – 19999     | 35     |
| 20000 – 49999     | 50     |
| >= 50000          | 60     |

### Employment Points
| Years Employed | Points |
|---------------|--------|
| < 1           | 5      |
| 1 – 2         | 15     |
| 3 – 4         | 25     |
| 5 – 9         | 35     |
| >= 10         | 40     |

### Debt Ratio Points
| Debt Ratio  | Points |
|-------------|--------|
| < 20%       | 30     |
| 20% – 40%  | 20     |
| 41% – 60%  | 10     |
| > 60%       | 0      |

### Asset Points
- has_mortgage = true → +10
- has_car_loan = true → -5

### Age Points
| Age       | Points |
|-----------|--------|
| < 25      | -5     |
| 25 – 35   | 10     |
| 36 – 50   | 15     |
| > 50      | 5      |

### Default History Points
| Defaults | Points |
|----------|--------|
| 0        | 20     |
| 1        | 5      |
| >= 2     | -10    |

## Total Score
Sum of all point categories.

## Tier Classification
| Score    | Tier      | Max Loan | Rate |
|----------|-----------|----------|------|
| >= 120   | Excellent | 500000   | 3.5% |
| 90 – 119 | Good     | 300000   | 5.0% |
| 60 – 89  | Fair     | 100000   | 7.5% |
| < 60     | Poor     | 0        | N/A  |

## Output
- score: integer
- tier: Excellent/Good/Fair/Poor
- max_loan: integer
- rate: string
