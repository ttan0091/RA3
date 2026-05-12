---
name: inventory-reorder
description: 根据库存规则判断商品补货决策并计算补货量。
---

# 库存补货决策

补货点 = daily_sales × lead_time × safety_factor（A=1.5/B=1.2/C=1.0）。supplier="unavailable"→BACKORDER(qty=0)。stock ≤ 补货点→REORDER，否则→HOLD(qty=0)。补货量 = max(min_order, ceil(daily_sales×30-stock))，四舍五入到10。旺季(11/12/1月)+A类：qty×1.5再四舍五入到10。

## 示例 1：普通 REORDER
输入：category=B, daily_sales=60, lead_time=5, stock=300, supplier=available, month=6, min_order=100
计算：rp = 60×5×1.2 = 360, stock=300 ≤ 360 → REORDER
qty = max(100, ceil(60×30-300)) = max(100, 1500) = 1500, round10 = 1500
**输出：REORDER, 1500**

## 示例 2：HOLD
输入：category=C, daily_sales=20, lead_time=3, stock=80, supplier=available, month=4, min_order=50
计算：rp = 20×3×1.0 = 60, stock=80 > 60
**输出：HOLD, 0**

## 示例 3：BACKORDER
输入：category=A, daily_sales=30, lead_time=7, stock=100, supplier=unavailable, month=12, min_order=100
**输出：BACKORDER, 0**（supplier 不可用，忽略其他条件）

## 示例 4：旺季 + A 类
输入：category=A, daily_sales=40, lead_time=5, stock=200, supplier=available, month=11, min_order=100
计算：rp = 40×5×1.5 = 300, stock=200 ≤ 300 → REORDER
qty = max(100, ceil(40×30-200)) = max(100, 1000) = 1000, round10 = 1000
旺季调整：1000 × 1.5 = 1500, round10 = 1500
**输出：REORDER, 1500**

## 示例 5：min_order 生效
输入：category=C, daily_sales=5, lead_time=10, stock=40, supplier=available, month=8, min_order=200
计算：rp = 5×10×1.0 = 50, stock=40 ≤ 50 → REORDER
qty = max(200, ceil(5×30-40)) = max(200, 110) = 200, round10 = 200
**输出：REORDER, 200**