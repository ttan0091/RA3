---
name: tax-calculator
description: 根据公司规则计算员工个人所得税。
---

# 个人所得税计算

按以下逻辑计算每位员工的个人所得税。

```python
def calc_tax(emp: dict) -> int:
    salary = emp["salary"]
    
    # 社保：8% of salary, base capped at 35000
    si = min(salary, 35000) * 0.08
    
    # 专项扣除
    child_ded = min(emp["children"], 3) * 1000
    mortgage_ded = min(emp["mortgage"], 2000)
    edu_ded = 500 if emp["education"] else 0
    deductions = child_ded + mortgage_ded + edu_ded
    
    # 应纳税所得额
    taxable = salary - si - 5000 - deductions
    if taxable <= 0:
        return 0
    
    # 累进税率
    brackets = [
        (5000,  0.00),   # 0-5000: 0%
        (10000, 0.10),   # 5001-15000: 10%
        (15000, 0.20),   # 15001-30000: 20%
        (20000, 0.25),   # 30001-50000: 25%
        (float('inf'), 0.35),  # 50001+: 35%
    ]
    
    tax = 0
    remaining = taxable
    for width, rate in brackets:
        chunk = min(remaining, width)
        tax += chunk * rate
        remaining -= chunk
        if remaining <= 0:
            break
    
    return round(tax)
```