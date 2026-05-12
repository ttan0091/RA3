# T05 Inventory Replenishment Decision — Internal Spec

## Purpose
Agent must decide whether to reorder inventory and compute order quantities using safety factors, seasonal adjustments, and supplier availability rules.

## Input Fields
- category: "A" | "B" | "C" (product category)
- daily_sales: average daily sales volume (float)
- lead_time: supplier lead time in days (int)
- current_stock: current inventory quantity (int)
- supplier: "available" | "unavailable"
- month: current month (int, 1-12)
- min_order: minimum order quantity (int)

## Reorder Point
```
reorder_point = daily_sales × lead_time × safety_factor
```
Safety factor by category: A=1.5, B=1.2, C=1.0

## Decision Rules (evaluated in order)
1. If supplier = "unavailable" → BACKORDER (regardless of stock level), order_qty = 0
2. If current_stock ≤ reorder_point → REORDER
3. Otherwise → HOLD, order_qty = 0

## Order Quantity (when REORDER)
```
order_qty = max(min_order, ceil(daily_sales × 30 - current_stock))
```
Round order_qty to nearest 10 (四舍五入).

## Seasonal Adjustment
If month ∈ {11, 12, 1} AND category = "A":
- order_qty = order_qty × 1.5
- Round result to nearest 10

## Output
- decision: "REORDER" | "HOLD" | "BACKORDER"
- order_qty: int (0 for HOLD and BACKORDER)
