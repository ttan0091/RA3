---
name: inventory-reorder
description: 根据库存规则判断商品补货决策并计算补货量。
---

# 库存补货决策

按以下逻辑判断每个商品的补货决策。

```python
import math
from decimal import Decimal, ROUND_HALF_UP

SAFETY = {"A": 1.5, "B": 1.2, "C": 1.0}

def round_to_10(x):
    """四舍五入到最近的 10"""
    return int(Decimal(str(x / 10)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)) * 10

def calc_reorder(item: dict) -> dict:
    rp = item["daily_sales"] * item["lead_time"] * SAFETY[item["category"]]
    
    if item["supplier"] == "unavailable":
        return {"decision": "BACKORDER", "order_qty": 0}
    
    if item["current_stock"] <= rp:
        raw = max(item["min_order"],
                  math.ceil(item["daily_sales"] * 30 - item["current_stock"]))
        qty = round_to_10(raw)
        
        # 旺季调整：11/12/1月 + A类
        if item["month"] in (11, 12, 1) and item["category"] == "A":
            qty = round_to_10(qty * 1.5)
        
        return {"decision": "REORDER", "order_qty": qty}
    
    return {"decision": "HOLD", "order_qty": 0}
```