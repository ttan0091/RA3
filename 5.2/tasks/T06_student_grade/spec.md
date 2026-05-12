# T06 Student Grading — Internal Spec

## Purpose
Agent must compute student grades using weighted scores, attendance penalties, and honor/warning flags.
Model pre-training cannot help because the weights, thresholds, and rules are custom.

## Input Fields
- homework: score 0-100
- midterm: score 0-100
- final: score 0-100
- project: score 0-100
- attendance: percentage 0-100

## Weighted Score
```
weighted = homework × 0.20 + midterm × 0.25 + final × 0.35 + project × 0.20
```

## Attendance Rules
1. attendance < 60% → automatic F (overrides everything, skip weighted calculation for grade)
2. attendance < 80% → adjusted = weighted × 0.9
3. attendance >= 80% → adjusted = weighted (no penalty)

## Grade Scale (applied to adjusted score, unless automatic F)
| Score     | Grade |
|-----------|-------|
| >= 90     | A     |
| >= 80     | B     |
| >= 70     | C     |
| >= 60     | D     |
| < 60      | F     |

## Honor Roll
- Condition: grade = A AND all four individual scores (homework, midterm, final, project) >= 85
- Output: true / false

## Academic Warning
- Condition: grade is D or F AND any individual score < 50
- Output: true / false

## Output Fields
- grade: A/B/C/D/F
- honor: boolean
- warning: boolean
