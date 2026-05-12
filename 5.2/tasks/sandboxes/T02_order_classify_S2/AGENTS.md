---
name: order-risk-classifier
description: 根据风控规则对订单进行风险分类。
---

# 订单风控分类规则

按以下优先级顺序逐条匹配，首条命中即为最终分类。

## Priority 1 — FRAUD_SUSPECTED
满足以下任一条件：
- order_amount > 5000 AND customer_type = "new" AND address_match = false
- order_amount > 10000 AND order_time = "off_hours" AND payment_method = "digital_wallet"

## Priority 2 — HIGH_VALUE_REVIEW
- 金额超过阈值：
  - customer_type = "vip" → 阈值 = 15000
  - 其他 → 阈值 = 8000
- order_amount > 阈值 → HIGH_VALUE_REVIEW

## Priority 3 — BULK_ORDER
满足以下任一条件：
- item_count > 20
- item_count > 10 AND avg_item_price < 50

## Priority 4 — PAYMENT_RISK
满足以下任一条件：
- payment_method = "bank_transfer" AND order_amount > 3000
- payment_method = "credit_card" AND customer_type = "new" AND order_amount > 2000

## Priority 5 — NORMAL
- 以上规则均未命中