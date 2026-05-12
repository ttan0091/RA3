---
name: student-grader
description: 根据学校规则评定学生成绩等级。
---

# 学生成绩评定

按以下逻辑评定每位学生的成绩。

```python
def calc_grade(s: dict) -> dict:
    hw, mid, fin, proj = s["homework"], s["midterm"], s["final"], s["project"]
    att = s["attendance"]
    
    weighted = hw * 0.20 + mid * 0.25 + fin * 0.35 + proj * 0.20
    
    # 出勤检查
    if att < 60:
        grade = "F"  # 自动 F，覆盖一切
    else:
        adjusted = weighted * 0.9 if att < 80 else weighted
        if adjusted >= 90:
            grade = "A"
        elif adjusted >= 80:
            grade = "B"
        elif adjusted >= 70:
            grade = "C"
        elif adjusted >= 60:
            grade = "D"
        else:
            grade = "F"
    
    # 荣誉：A 且四项均 >= 85
    honor = grade == "A" and all(x >= 85 for x in [hw, mid, fin, proj])
    
    # 预警：D/F 且任一 < 50
    warning = grade in ("D", "F") and any(x < 50 for x in [hw, mid, fin, proj])
    
    return {"grade": grade, "honor": honor, "warning": warning}
```