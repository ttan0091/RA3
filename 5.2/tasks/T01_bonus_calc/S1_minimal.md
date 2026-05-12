---
name: bonus-calculator
description: 根据公司规则计算员工年终奖金。
---

奖金公式：final_bonus = min(base_salary × perf_mult × team_mult × seniority_mult × (months_worked / 12), base_salary × 4)。绩效 C 或工作不满 6 个月的员工奖金为 0。绩效乘数：S=3.0, A=2.0, B=1.0, C=不发。团队乘数（团队均分 S=4/A=3/B=2/C=1）：>=3.5 → 1.2, [2.5,3.5) → 1.0, <2.5 → 0.8。工龄乘数：<1年 → 0.5, [1,3) → 0.8, [3,5) → 1.0, [5,10) → 1.2, >=10 → 1.5。结果四舍五入到整数。