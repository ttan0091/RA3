---
name: inventory-reorder
description: 根据库存规则判断商品补货决策并计算补货量。
---

补货点 reorder_point = daily_sales × lead_time × safety_factor（A=1.5, B=1.2, C=1.0）。supplier="unavailable" → BACKORDER，qty=0。current_stock ≤ reorder_point → REORDER，否则 HOLD，qty=0。补货量 order_qty = max(min_order, ceil(daily_sales×30 - current_stock))，四舍五入到最近的 10。季节性调整：月份为 11/12/1 且 category="A" 时，qty × 1.5 后再四舍五入到最近的 10。