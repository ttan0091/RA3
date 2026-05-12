---
name: bonus-calculator
description: 根据公司规则计算员工年终奖金。
---

# 年终奖金计算

按以下逻辑计算每位员工的年终奖金。

```python
PERF_MULT = {"S": 3.0, "A": 2.0, "B": 1.0}

def team_mult(team_avg: float) -> float:
    # team_avg 由 S=4,A=3,B=2,C=1 编码取均值
    if team_avg >= 3.5:
        return 1.2
    elif team_avg >= 2.5:
        return 1.0
    else:
        return 0.8

def seniority_mult(years: float) -> float:
    if years >= 10:
        return 1.5
    elif years >= 5:
        return 1.2
    elif years >= 3:
        return 1.0
    elif years >= 1:
        return 0.8
    else:
        return 0.5

def calc_bonus(emp: dict) -> int:
    if emp["performance"] == "C":
        return 0
    if emp["months_worked"] < 6:
        return 0
    raw = (
        emp["base_salary"]
        * PERF_MULT[emp["performance"]]
        * team_mult(emp["team_avg_score"])
        * seniority_mult(emp["seniority_years"])
        * (emp["months_worked"] / 12)
    )
    cap = emp["base_salary"] * 4
    return round(min(raw, cap))
```