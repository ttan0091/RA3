# T10 Expense Reimbursement Review — Internal Spec

## Purpose
Agent must review expense claims using city-tier per-diem limits, receipt rules, and approval thresholds.
Model pre-training cannot help because the city tiers, limits, and approval rules are custom.

## City Tiers
- T1 (一线): 北京, 上海, 广州, 深圳
- T2 (省会): 杭州, 成都, 武汉, 南京, 西安
- T3 (其他): all other cities

## Per-Diem Limits (per day)
| Category  | T1  | T2  | T3  |
|-----------|-----|-----|-----|
| meals     | 200 | 150 | 100 |
| hotel     | 500 | 350 | 250 |
| transport | 200 | 150 | 100 |

Maximum claimable = daily limit × number of days.

## Rules

### Receipt Requirement
- If any single item amount > 200, a receipt is required
- If no receipt for such item → reject that specific item (not the entire claim)

### Trip Duration
- Maximum 14 days per trip
- If days > 14 → REJECT entire claim

### Entertainment Expenses
- Only allowed if client_facing = true
- If not client_facing → reject entertainment items

### Item Approval
- For meals/hotel/transport: approved amount = min(claimed amount, daily limit × days)
- For entertainment: no per-diem limit, but receipt and client_facing rules apply
- Each item is evaluated independently

## Result Determination
- All items approved → APPROVE
- Some items rejected, some approved → PARTIAL
- All items rejected → REJECT

## Approval Level (based on total approved amount)
| Total Approved | Level    |
|---------------|----------|
| ≤ 5000        | auto     |
| 5001 – 20000  | manager  |
| > 20000       | director |

If result is REJECT, approval_level = "N/A", approved_amount = 0.

## Output
- result: "APPROVE" | "PARTIAL" | "REJECT"
- approved_amount: integer
- approval_level: "auto" | "manager" | "director" | "N/A"
