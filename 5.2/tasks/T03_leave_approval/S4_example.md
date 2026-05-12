---
name: leave-approver
description: 根据公司规则审批请假申请。
---

# 请假审批规则

两阶段决策：先查拒绝规则（R1–R5，任一命中即拒绝），再查批准规则（A1–A4）。均未命中则 ESCALATE。

拒绝规则：R1 年假余额<天数→"余额不足"；R2 事假>3天→"事假单次不超过3天"；R3 部门缺勤>=30%且非病假产假→"部门在岗率不足"；R4 旺季+年假+提前<14天→"旺季年假需提前14天申请"；R5 病假>2天无证明→"病假超过2天需提供医疗证明"。
批准规则：A1 产假→批准；A2 病假<=2天→批准；A3 年假+提前>=7天+缺勤<20%→批准；A4 事假<=1天+提前>=3天→批准。

## 示例 1：标准年假批准
输入：type=annual, days=3, advance=10, balance=10, dept=0.15, peak=false
分析：R1 balance=10>=3 ✓, R3 dept=0.15<0.30 ✓, R4 non-peak ✓ → 无拒绝
A3: annual + advance=10>=7 + dept=0.15<0.20 → 命中
**结果：APPROVE**

## 示例 2：余额不足
输入：type=annual, days=5, advance=10, balance=3, dept=0.10, peak=false
分析：R1 balance=3 < days=5 → 命中
**结果：REJECT "余额不足"**

## 示例 3：病假豁免部门缺勤限制
输入：type=sick, days=1, advance=0, balance=10, dept=0.35, peak=true
分析：R3 dept=0.35>=0.30 但 sick 豁免 → 不触发。R5 days=1<=2 → 不触发。
A2: sick + days=1<=2 → 命中
**结果：APPROVE**（关键：病假不受 R3 限制）

## 示例 4：产假无条件批准
输入：type=maternity, days=90, advance=30, balance=0, dept=0.40, peak=true
分析：R3 maternity 豁免 → 无拒绝。A1: maternity → 命中
**结果：APPROVE**（即使部门缺勤 40%、旺季、余额为 0）

## 示例 5：升级处理
输入：type=annual, days=2, advance=5, balance=5, dept=0.22, peak=false
分析：R1 balance=5>=2 ✓, R3 dept=0.22<0.30 ✓ → 无拒绝
A3: advance=5 < 7 → 不满足。其他批准规则不匹配。
**结果：ESCALATE "需主管审批"**