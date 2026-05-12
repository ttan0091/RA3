---
name: bonus-calculator
description: 根据公司规则计算员工年终奖金。
---

# 年终奖金计算规则

## 资格条件
- 绩效评级为 C → 奖金为 0，不参与计算
- 当年工作月数 < 6 → 奖金为 0，不参与计算

## 计算公式
1. raw_bonus = base_salary × perf_mult × team_mult × seniority_mult × (months_worked / 12)
2. final_bonus = min(raw_bonus, base_salary × 4)
3. 结果四舍五入到整数

## 绩效乘数 (perf_mult)
- S → 3.0
- A → 2.0
- B → 1.0
- C → 不发

## 团队乘数 (team_mult)
- 团队均分编码：S=4, A=3, B=2, C=1
- team_avg >= 3.5 → 1.2
- 2.5 <= team_avg < 3.5 → 1.0
- team_avg < 2.5 → 0.8

## 工龄乘数 (seniority_mult)
- < 1 年 → 0.5
- 1 年 ~ 不满 3 年 → 0.8
- 3 年 ~ 不满 5 年 → 1.0
- 5 年 ~ 不满 10 年 → 1.2
- >= 10 年 → 1.5

## 封顶
- 奖金上限 = base_salary × 4