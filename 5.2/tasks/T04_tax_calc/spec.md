# T04 Personal Income Tax Calculation — Internal Spec

## Purpose
Agent must compute personal income tax using progressive brackets, social insurance, and multiple deduction categories.
Model pre-training cannot help because the brackets, thresholds, and deduction rules are custom.

## Input Fields
- salary: monthly salary (float)
- children: number of children (int)
- mortgage: monthly mortgage payment (float)
- education: whether taking continuing education (bool)

## Social Insurance
- Rate: 8% of salary
- Base cap: salary capped at 35000 for social insurance calculation
- social_insurance = min(salary, 35000) × 0.08

## Deductions
- Children: 1000 per child, maximum 3 children counted
- Mortgage: actual amount, maximum 2000
- Education: flat 500 if education = true

## Taxable Income
```
taxable = salary - social_insurance - 5000(threshold) - deductions
```
If taxable <= 0, tax = 0.

## Progressive Tax Brackets
| Taxable Income Range | Rate |
|---------------------|------|
| 0 – 5000            | 0%   |
| 5001 – 15000        | 10%  |
| 15001 – 30000       | 20%  |
| 30001 – 50000       | 25%  |
| 50001+              | 35%  |

Brackets are cumulative (each bracket applies only to the portion within that range).

## Rounding
Round tax to nearest integer (standard rounding).
