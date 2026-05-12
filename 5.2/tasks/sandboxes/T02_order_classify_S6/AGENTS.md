---
name: order-risk-classifier
description: 根据风控规则对订单进行风险分类。
---

# 订单风控分类规则

将每笔订单按优先级规则分为 5 个风险等级。规则按优先级从高到低依次匹配，首条命中即为最终分类。

## 规则总览

| 优先级 | 分类 | 触发条件 |
|--------|------|----------|
| 1 | FRAUD_SUSPECTED | 见下方详细条件 |
| 2 | HIGH_VALUE_REVIEW | 金额超过客户类型对应阈值 |
| 3 | BULK_ORDER | 大量商品或低价批发 |
| 4 | PAYMENT_RISK | 特定支付方式的高风险组合 |
| 5 | NORMAL | 以上均不匹配 |

## 详细条件

### P1 — FRAUD_SUSPECTED
- 条件 A：order_amount > 5000 AND customer_type = "new" AND address_match = false
- 条件 B：order_amount > 10000 AND order_time = "off_hours" AND payment_method = "digital_wallet"

### P2 — HIGH_VALUE_REVIEW
金额阈值因客户类型而异：
- VIP 客户：阈值 = 15000
- 其他客户：阈值 = 8000

### P3 — BULK_ORDER
- 条件 A：item_count > 20
- 条件 B：item_count > 10 AND avg_item_price < 50

### P4 — PAYMENT_RISK
- 条件 A：payment_method = "bank_transfer" AND order_amount > 3000
- 条件 B：payment_method = "credit_card" AND customer_type = "new" AND order_amount > 2000

## 示例
输入：amount=13000, customer=vip, payment=debit_card, addr=true, time=business, items=1
→ P1 不满足。P2 vip 阈值=15000, 13000<15000 → 不命中。P3/P4 不满足。→ **NORMAL**

输入：amount=5000, payment=bank_transfer, items=22, customer=regular
→ P1 不满足。P2 5000<8000。P3(a) 22>20 → **BULK_ORDER**（不再检查 P4）