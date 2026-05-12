---
name: credit-scorer
description: 根据信用评分规则计算客户信用等级。
---

# 信用评分

按以下逻辑计算每位客户的信用评分和贷款等级。

```python
def calc_credit(c: dict) -> dict:
    income = c["monthly_income"]
    emp = c["employment_years"]
    debt = c["debt_ratio"]
    age = c["age"]
    defaults = c["past_defaults"]
    
    # 收入分
    if income >= 50000:   pts_inc = 60
    elif income >= 20000: pts_inc = 50
    elif income >= 10000: pts_inc = 35
    elif income >= 5000:  pts_inc = 20
    else:                 pts_inc = 10
    
    # 工龄分
    if emp >= 10:    pts_emp = 40
    elif emp >= 5:   pts_emp = 35
    elif emp >= 3:   pts_emp = 25
    elif emp >= 1:   pts_emp = 15
    else:            pts_emp = 5
    
    # 负债率分
    if debt < 20:      pts_debt = 30
    elif debt <= 40:   pts_debt = 20
    elif debt <= 60:   pts_debt = 10
    else:              pts_debt = 0
    
    # 资产分
    pts_asset = (10 if c["has_mortgage"] else 0) + (-5 if c["has_car_loan"] else 0)
    
    # 年龄分
    if age < 25:       pts_age = -5
    elif age <= 35:    pts_age = 10
    elif age <= 50:    pts_age = 15
    else:              pts_age = 5
    
    # 违约分
    if defaults == 0:    pts_def = 20
    elif defaults == 1:  pts_def = 5
    else:                pts_def = -10
    
    score = pts_inc + pts_emp + pts_debt + pts_asset + pts_age + pts_def
    
    # 评级
    if score >= 120:
        return {"score": score, "tier": "Excellent", "max_loan": 500000, "rate": "3.5%"}
    elif score >= 90:
        return {"score": score, "tier": "Good", "max_loan": 300000, "rate": "5.0%"}
    elif score >= 60:
        return {"score": score, "tier": "Fair", "max_loan": 100000, "rate": "7.5%"}
    else:
        return {"score": score, "tier": "Poor", "max_loan": 0, "rate": "N/A"}
```