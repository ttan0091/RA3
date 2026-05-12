---
name: shipping-calculator
description: 根据物流规则计算包裹运费。
---

# 物流运费计算

按以下逻辑计算每个包裹的运费。

```python
ZONE_RATE = {
    "same_city": 5, "same_province": 8,
    "adjacent": 12, "remote": 18,
}

def calc_shipping(pkg: dict) -> float:
    # 计费重量
    vol_weight = pkg["length"] * pkg["width"] * pkg["height"] / 6000
    billable = max(pkg["actual_weight"], vol_weight)
    
    # 基础运费：首kg全价，续重60%
    base = ZONE_RATE[pkg["zone"]]
    if billable <= 1:
        cost = base
    else:
        cost = base + (billable - 1) * base * 0.6
    
    # 附加费（累加乘数）
    mult = 1.0
    if pkg.get("fragile"):
        mult += 0.15
    if any(d > 100 for d in [pkg["length"], pkg["width"], pkg["height"]]):
        mult += 0.25  # 超大件
    if pkg.get("cold_chain"):
        mult += 0.30
    cost *= mult
    
    # VIP 折扣
    if pkg.get("vip"):
        cost *= 0.9
    
    # 最低收费 + 保留一位小数
    return round(max(cost, 10), 1)
```