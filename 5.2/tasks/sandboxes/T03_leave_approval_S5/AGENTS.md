---
name: leave-approver
description: 根据公司规则审批请假申请。
---

# 请假审批规则

按以下逻辑处理每个请假申请。

```python
def decide(r: dict) -> tuple[str, str]:
    lt = r["leave_type"]
    days = r["days_requested"]
    adv = r["advance_notice_days"]
    bal = r["annual_leave_balance"]
    dept = r["dept_absence_rate"]
    peak = r["is_peak_season"]
    cert = r["has_medical_certificate"]

    # --- Reject rules (any match → reject) ---
    if lt == "annual" and bal < days:
        return "REJECT", "余额不足"
    if lt == "personal" and days > 3:
        return "REJECT", "事假单次不超过3天"
    if dept >= 0.30 and lt not in ("sick", "maternity"):
        return "REJECT", "部门在岗率不足"
    if peak and lt == "annual" and adv < 14:
        return "REJECT", "旺季年假需提前14天申请"
    if lt == "sick" and days > 2 and not cert:
        return "REJECT", "病假超过2天需提供医疗证明"

    # --- Approve rules ---
    if lt == "maternity":
        return "APPROVE", "产假"
    if lt == "sick" and days <= 2:
        return "APPROVE", "短期病假"
    if lt == "annual" and adv >= 7 and dept < 0.20:
        return "APPROVE", "年假"
    if lt == "personal" and days <= 1 and adv >= 3:
        return "APPROVE", "短期事假"

    return "ESCALATE", "需主管审批"
```