---
name: leave-approver
description: 根据公司规则审批请假申请。
---

# 请假审批规则

两阶段决策：先检查拒绝规则（任一命中即拒绝），未被拒绝再检查批准规则，均未命中则升级至主管。

## 拒绝规则

| 编号 | 条件 | 拒绝原因 |
|------|------|----------|
| R1 | leave_type = "annual" AND balance < days | 余额不足 |
| R2 | leave_type = "personal" AND days > 3 | 事假单次不超过3天 |
| R3 | dept_absence >= 0.30 AND type NOT IN (sick, maternity) | 部门在岗率不足 |
| R4 | peak_season AND type = "annual" AND advance < 14 | 旺季年假需提前14天申请 |
| R5 | type = "sick" AND days > 2 AND no certificate | 病假超过2天需提供医疗证明 |

病假和产假不受 R3 限制——即使部门缺勤率已达 40%，员工因病或生育仍可请假。

## 批准规则

| 编号 | 条件 | 说明 |
|------|------|------|
| A1 | type = "maternity" | 产假无条件批准 |
| A2 | type = "sick" AND days <= 2 | 短期病假免证明 |
| A3 | type = "annual" AND advance >= 7 AND dept < 0.20 | 常规年假 |
| A4 | type = "personal" AND days <= 1 AND advance >= 3 | 短期事假 |

## 兜底
均未命中 → ESCALATE "需主管审批"

## 示例
输入：type=sick, days=1, dept=0.35, peak=true
→ R3 sick 豁免，R5 days<=2 不触发 → 无拒绝。A2 命中 → **APPROVE**

输入：type=annual, days=2, advance=5, dept=0.22, peak=false
→ 无拒绝。A3 advance=5<7 不满足 → **ESCALATE**