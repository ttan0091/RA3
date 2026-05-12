---
name: leave-approver
description: 根据公司规则审批请假申请。
---

# 请假审批规则

先检查拒绝规则，任一命中即拒绝。全部通过后再检查批准规则。两者均未命中则升级。

## 拒绝规则（优先级最高）
- R1: leave_type = "annual" AND annual_leave_balance < days_requested → REJECT "余额不足"
- R2: leave_type = "personal" AND days_requested > 3 → REJECT "事假单次不超过3天"
- R3: dept_absence_rate >= 0.30 AND leave_type NOT IN ("sick", "maternity") → REJECT "部门在岗率不足"
- R4: is_peak_season = true AND leave_type = "annual" AND advance_notice_days < 14 → REJECT "旺季年假需提前14天申请"
- R5: leave_type = "sick" AND days_requested > 2 AND has_medical_certificate = false → REJECT "病假超过2天需提供医疗证明"

## 批准规则（无拒绝时检查）
- A1: leave_type = "maternity" → APPROVE
- A2: leave_type = "sick" AND days_requested <= 2 → APPROVE
- A3: leave_type = "annual" AND advance_notice_days >= 7 AND dept_absence_rate < 0.20 → APPROVE
- A4: leave_type = "personal" AND days_requested <= 1 AND advance_notice_days >= 3 → APPROVE

## 兜底
- E1: 以上均未命中 → ESCALATE "需主管审批"