---
name: expense-reviewer
description: 根据差旅报销规则审核费用报销申请。
---

# 差旅费报销审核规则

根据城市等级设定每日限额，逐项审核后汇总判定。

## 城市等级

| 等级 | 城市                          |
|------|-------------------------------|
| T1   | 北京、上海、广州、深圳        |
| T2   | 杭州、成都、武汉、南京、西安  |
| T3   | 其他城市                      |

## 每日限额

| 类别     | T1  | T2  | T3  |
|----------|-----|-----|-----|
| meals    | 200 | 150 | 100 |
| hotel    | 500 | 350 | 250 |
| transport| 200 | 150 | 100 |

每项限额 = 日限额 × 出差天数。entertainment 无每日限额。

## 审核规则

1. **天数**：> 14 天 → REJECT 全部
2. **发票**：单项 > 200 必须有发票，否则拒绝该项
3. **招待费**：仅 client_facing = true 时允许
4. **限额**：approved = min(申报额, 日限额 × 天数)

## 结果判定
- 全部通过 → APPROVE
- 部分拒绝 → PARTIAL
- 全部拒绝 → REJECT (amount=0, level=N/A)

## 审批级别

| 批准总额       | 级别     |
|---------------|----------|
| ≤ 5000        | auto     |
| 5001 – 20000  | manager  |
| > 20000       | director |

## 示例
输入：city=上海(T1), days=3, items=[meals=500, hotel=1400, transport=300]
→ 500+1400+300=2200, 全通 → **APPROVE, 2200, auto**

输入：city=杭州(T2), days=4, client_facing=true, items=[meals=500, hotel=1200, transport=250(无发票), entertainment=600]
→ transport拒(>200无发票), 500+1200+600=2300 → **PARTIAL, 2300, auto**