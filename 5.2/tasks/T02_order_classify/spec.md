# T02 Order Anomaly Classification — Internal Spec

## Purpose
Agent must classify orders into risk categories using a priority-ordered rule set.
Rules involve compound conditions on structured fields. Model cannot guess the thresholds.

## Input Fields (per order)
- order_amount: float
- payment_method: "credit_card" | "debit_card" | "bank_transfer" | "digital_wallet"
- customer_type: "new" | "regular" | "vip"
- address_match: bool (delivery address matches registered address)
- order_time: "business_hours" | "off_hours"
- item_count: int
- avg_item_price: float

## Classification Rules (evaluated in priority order; first match wins)

### Priority 1 — FRAUD_SUSPECTED
Condition A: order_amount > 5000 AND customer_type = "new" AND address_match = false
Condition B: order_amount > 10000 AND order_time = "off_hours" AND payment_method = "digital_wallet"
→ If A OR B is true → FRAUD_SUSPECTED

### Priority 2 — HIGH_VALUE_REVIEW
Condition: order_amount > threshold, where:
  - threshold = 15000 if customer_type = "vip"
  - threshold = 8000 otherwise
→ If amount > threshold AND not already FRAUD_SUSPECTED → HIGH_VALUE_REVIEW

### Priority 3 — BULK_ORDER
Condition A: item_count > 20
Condition B: item_count > 10 AND avg_item_price < 50
→ If A OR B is true → BULK_ORDER

### Priority 4 — PAYMENT_RISK
Condition A: payment_method = "bank_transfer" AND order_amount > 3000
Condition B: payment_method = "credit_card" AND customer_type = "new" AND order_amount > 2000
→ If A OR B is true → PAYMENT_RISK

### Priority 5 — NORMAL
Everything else → NORMAL
