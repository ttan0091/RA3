---
name: bonus-calculator
description: 根据公司规则计算员工年终奖金。
---

# 年终奖金计算

按以下规则计算奖金：raw_bonus = base_salary × perf_mult × team_mult × seniority_mult × (months_worked / 12)，final_bonus = min(raw_bonus, base_salary × 4)，四舍五入到整数。

查表参数：绩效乘数 S=3.0/A=2.0/B=1.0/C=不发。团队均分编码 S=4/A=3/B=2/C=1，>=3.5→1.2, [2.5,3.5)→1.0, <2.5→0.8。工龄乘数 <1年→0.5, [1,3)→0.8, [3,5)→1.0, [5,10)→1.2, >=10→1.5。绩效 C 或工作不满 6 月奖金为 0。

## 示例 1：标准计算
输入：salary=20000, perf=A, seniority=6年, team_avg=3.2, months=12
计算：perf_mult=2.0, team_mult=1.0 (3.2在[2.5,3.5)区间), seniority_mult=1.2 (6年在[5,10)区间)
raw = 20000 × 2.0 × 1.0 × 1.2 × 1.0 = 48000
cap = 20000 × 4 = 80000
**输出：48000**

## 示例 2：触发封顶
输入：salary=8000, perf=S, seniority=11年, team_avg=3.8, months=12
计算：perf_mult=3.0, team_mult=1.2, seniority_mult=1.5
raw = 8000 × 3.0 × 1.2 × 1.5 × 1.0 = 43200
cap = 8000 × 4 = 32000
**输出：32000**（被封顶）

## 示例 3：不满 6 个月
输入：salary=15000, perf=S, seniority=0.3年, team_avg=3.9, months=4
**输出：0**（工作月数 < 6，不符合资格）

## 示例 4：绩效 C
输入：salary=30000, perf=C, seniority=5年, team_avg=3.5, months=12
**输出：0**（绩效 C 不发放）

## 示例 5：需要四舍五入
输入：salary=13000, perf=B, seniority=2年, team_avg=2.8, months=7
计算：perf_mult=1.0, team_mult=1.0, seniority_mult=0.8
raw = 13000 × 1.0 × 1.0 × 0.8 × (7/12) = 6066.666...
cap = 13000 × 4 = 52000
**输出：6067**（四舍五入）