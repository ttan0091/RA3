---
name: order-risk-classifier
description: 根据风控规则对订单进行风险分类。
---

# 订单风控分类

按以下逻辑对每笔订单进行分类。

```python
def classify_order(o: dict) -> str:
    amt = o["order_amount"]
    pay = o["payment_method"]
    cust = o["customer_type"]
    addr = o["address_match"]
    time = o["order_time"]
    items = o["item_count"]
    avg_p = o["avg_item_price"]

    # Priority 1: FRAUD_SUSPECTED
    if (amt > 5000 and cust == "new" and not addr):
        return "FRAUD_SUSPECTED"
    if (amt > 10000 and time == "off_hours" and pay == "digital_wallet"):
        return "FRAUD_SUSPECTED"

    # Priority 2: HIGH_VALUE_REVIEW
    threshold = 15000 if cust == "vip" else 8000
    if amt > threshold:
        return "HIGH_VALUE_REVIEW"

    # Priority 3: BULK_ORDER
    if items > 20 or (items > 10 and avg_p < 50):
        return "BULK_ORDER"

    # Priority 4: PAYMENT_RISK
    if (pay == "bank_transfer" and amt > 3000):
        return "PAYMENT_RISK"
    if (pay == "credit_card" and cust == "new" and amt > 2000):
        return "PAYMENT_RISK"

    return "NORMAL"
```