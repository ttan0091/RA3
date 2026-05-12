---
name: student-grader
description: 根据学校规则评定学生成绩等级。
---

# 学生成绩评定规则

综合成绩、出勤、荣誉和预警四个维度评定学生表现。

## 加权分计算

```
weighted = homework × 0.20 + midterm × 0.25 + final × 0.35 + project × 0.20
```

## 出勤规则

| 出勤率        | 处理方式                     |
|--------------|------------------------------|
| < 60%        | 自动 F（覆盖一切）            |
| [60%, 80%)   | adjusted = weighted × 0.9   |
| >= 80%       | adjusted = weighted          |

## 等级（基于 adjusted 分数）

| 分数     | 等级 |
|----------|------|
| >= 90    | A    |
| >= 80    | B    |
| >= 70    | C    |
| >= 60    | D    |
| < 60     | F    |

## 特殊标记
- **荣誉 (honor)**：grade = A 且四项单科均 >= 85
- **预警 (warning)**：grade 为 D 或 F 且任一单科 < 50

## 示例
输入：homework=92, midterm=88, final=95, project=90, attendance=95
→ weighted=91.65, 无惩罚, A, 四项均>=85 → **grade=A, honor=true, warning=false**

输入：homework=88, midterm=92, final=86, project=90, attendance=75
→ weighted=88.7, ×0.9=79.83, C → **grade=C, honor=false, warning=false**