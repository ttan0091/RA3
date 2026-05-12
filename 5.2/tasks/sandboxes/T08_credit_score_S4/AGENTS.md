---
name: credit-scorer
description: 根据信用评分规则计算客户信用等级。
---

# 信用评分

六维度评分相加得总分。收入：<5K→10, [5K,10K)→20, [10K,20K)→35, [20K,50K)→50, >=50K→60。工龄：<1→5, [1,3)→15, [3,5)→25, [5,10)→35, >=10→40。负债率：<20%→30, 20-40%→20, 41-60%→10, >60%→0。房贷+10，车贷-5。年龄：<25→-5, 25-35→10, 36-50→15, >50→5。违约：0→20, 1→5, >=2→-10。评级：>=120 Excellent(50万/3.5%), >=90 Good(30万/5.0%), >=60 Fair(10万/7.5%), <60 Poor(0/N/A)。

## 示例 1：优质客户
输入：income=35000, emp=8年, debt=15%, mortgage=yes, car=no, age=42, defaults=0
计算：income=50 + emp=35 + debt=30 + mortgage=10 + age=15 + default=20 = 160
**输出：score=160, Excellent, 500000, 3.5%**

## 示例 2：年轻低收入客户
输入：income=8000, emp=2年, debt=45%, mortgage=no, car=yes, age=28, defaults=0
计算：20 + 15 + 10 + 0 + (-5) + 10 + 20 = 70
**输出：score=70, Fair, 100000, 7.5%**

## 示例 3：最差情况
输入：income=4000, emp=0.5年, debt=70%, mortgage=no, car=no, age=22, defaults=3
计算：10 + 5 + 0 + 0 + 0 + (-5) + (-10) = 0
**输出：score=0, Poor, 0, N/A**

## 示例 4：边界 — 恰好 120 分
输入：income=18000, emp=5年, debt=40%, mortgage=yes, car=no, age=36, defaults=1
计算：35 + 35 + 20 + 10 + 0 + 15 + 5 = 120
**输出：score=120, Excellent, 500000, 3.5%**（>=120 即为 Excellent）

## 示例 5：房贷车贷同时存在
输入：income=50000, emp=10年, debt=18%, mortgage=yes, car=yes, age=52, defaults=0
计算：60 + 40 + 30 + 10 + (-5) + 5 + 20 = 160
**输出：score=160, Excellent, 500000, 3.5%**