---
name: inventory-reorder
description: 根据库存规则判断商品补货决策并计算补货量。
---

# 库存补货决策规则

## 第一步：计算补货点
- reorder_point = daily_sales × lead_time × safety_factor
- 安全系数：A 类 = 1.5，B 类 = 1.2，C 类 = 1.0

## 第二步：判断决策
- 若 supplier = "unavailable" → BACKORDER，order_qty = 0（不论库存多少）
- 若 current_stock ≤ reorder_point → REORDER（进入第三步计算数量）
- 否则 → HOLD，order_qty = 0

## 第三步：计算补货量
- order_qty = max(min_order, ceil(daily_sales × 30 - current_stock))
- 将 order_qty 四舍五入到最近的 10

## 第四步：季节性调整
- 条件：月份 ∈ {11, 12, 1} 且 category = "A"
- 满足条件时：order_qty = order_qty × 1.5
- 结果再次四舍五入到最近的 10

## 输出
- decision: REORDER / HOLD / BACKORDER
- order_qty: 整数（HOLD 和 BACKORDER 时为 0）