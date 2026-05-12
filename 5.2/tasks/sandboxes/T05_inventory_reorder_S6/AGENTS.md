---
name: inventory-reorder
description: 根据库存规则判断商品补货决策并计算补货量。
---

# 库存补货决策规则

通过安全库存机制判断补货时机，结合季节性调整计算补货量。

## 补货点计算

```
reorder_point = daily_sales × lead_time × safety_factor
```

| 商品类别 | 安全系数 |
|---------|---------|
| A       | 1.5     |
| B       | 1.2     |
| C       | 1.0     |

## 决策判断（按优先级）
1. supplier = "unavailable" → **BACKORDER**，qty = 0
2. current_stock ≤ reorder_point → **REORDER**
3. 否则 → **HOLD**，qty = 0

## 补货量计算（REORDER 时）

```
order_qty = max(min_order, ceil(daily_sales × 30 - current_stock))
→ 四舍五入到最近的 10
```

### 季节性调整
- 月份 ∈ {11, 12, 1} 且 category = "A" 时：qty × 1.5，再四舍五入到 10

## 示例
输入：category=A, daily_sales=40, lead_time=5, stock=200, supplier=available, month=11, min_order=100
→ rp=300, stock≤rp → REORDER, qty=max(100,ceil(1200-200))=1000, round10=1000
→ 旺季+A类: 1000×1.5=1500, round10=1500 → **REORDER, 1500**

输入：category=B, daily_sales=15, lead_time=4, stock=100, supplier=available, month=1, min_order=50
→ rp=72, stock=100>72 → **HOLD, 0**（month=1 但 category≠A，无季节调整）