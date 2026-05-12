# T03 Leave Approval Rule Engine — Internal Spec

## Purpose
Agent must apply a priority-ordered decision tree to approve, reject, or escalate leave requests.
The rules include exemptions (e.g., sick/maternity exempt from department cap) and edge cases.

## Input Fields (per request)
- leave_type: "annual" | "sick" | "personal" | "maternity"
- days_requested: int
- advance_notice_days: int
- annual_leave_balance: float
- dept_absence_rate: float (fraction, e.g. 0.30 = 30%)
- is_peak_season: bool
- consecutive_sick_days_quarter: int (including current request)
- has_medical_certificate: bool

## Decision Rules (evaluate reject rules first, then approve rules)

### Reject Rules (any one → REJECT)
R1. leave_type = "annual" AND annual_leave_balance < days_requested
    → REJECT "余额不足"
R2. leave_type = "personal" AND days_requested > 3
    → REJECT "事假单次不超过3天"
R3. dept_absence_rate >= 0.30 AND leave_type NOT IN ("sick", "maternity")
    → REJECT "部门在岗率不足"
R4. is_peak_season = true AND leave_type = "annual" AND advance_notice_days < 14
    → REJECT "旺季年假需提前14天申请"
R5. leave_type = "sick" AND days_requested > 2 AND has_medical_certificate = false
    → REJECT "病假超过2天需提供医疗证明"

### Approve Rules (if no reject triggered)
A1. leave_type = "maternity" → APPROVE
A2. leave_type = "sick" AND days_requested <= 2 → APPROVE
A3. leave_type = "annual" AND advance_notice_days >= 7 AND dept_absence_rate < 0.20 → APPROVE
A4. leave_type = "personal" AND days_requested <= 1 AND advance_notice_days >= 3 → APPROVE

### Escalate
E1. If no reject and no approve rule matches → ESCALATE "需主管审批"

## Key Edge Cases
- Sick and maternity leave are exempt from R3 (department cap)
- R5 only applies to sick leave > 2 days
- VIP/seniority do NOT affect leave rules (unlike T01)
- Reject rules take absolute priority over approve rules
