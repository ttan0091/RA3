---
name: student-grader
description: 根据学校规则评定学生成绩等级。
---

# 学生成绩评定规则

## 第一步：计算加权分
- weighted = homework × 0.20 + midterm × 0.25 + final × 0.35 + project × 0.20

## 第二步：出勤检查
- 出勤率 < 60% → 直接判定为 F（跳过后续等级判定）
- 出勤率 < 80% → adjusted = weighted × 0.9（扣 10%）
- 出勤率 >= 80% → adjusted = weighted（无惩罚）

## 第三步：等级判定（基于 adjusted 分数）
- adjusted >= 90 → A
- adjusted >= 80 → B
- adjusted >= 70 → C
- adjusted >= 60 → D
- adjusted < 60 → F

## 第四步：荣誉判定
- 条件：grade = A 且 homework >= 85 且 midterm >= 85 且 final >= 85 且 project >= 85
- 全部满足 → honor = true，否则 false

## 第五步：学业预警判定
- 条件：grade 为 D 或 F，且任意一项单科成绩 < 50
- 满足 → warning = true，否则 false