---
name: shipping-calculator
description: 根据物流规则计算包裹运费。
---

# 物流运费计算

计费重量=max(实际重量, L×W×H/6000)。基础费率/kg：同城=5, 省内=8, 邻省=12, 偏远=18。首kg按基础费率，续重按60%。附加费（累加）：易碎+15%, 超大件(任一边>100cm)+25%, 冷链+30%。VIP 九折。最低 10 元。保留一位小数。

## 示例 1：普通同城件
输入：weight=3kg, 30×20×15cm, zone=same_city, 无附加, 非VIP
计算：vol=30×20×15/6000=1.5, bill=max(3,1.5)=3
cost = 5 + 2×5×0.6 = 11.0
**输出：11.0**

## 示例 2：体积重量远超实际 + 易碎
输入：weight=2kg, 80×60×50cm, zone=same_province, fragile=true
计算：vol=80×60×50/6000=40, bill=40
cost = 8 + 39×4.8 = 195.2, ×1.15(易碎) = 224.48
**输出：224.5**

## 示例 3：VIP + 轻小件
输入：weight=0.5kg, 10×10×5cm, zone=remote, vip=true
计算：vol=0.08, bill=0.5, ≤1kg → cost=18
VIP: 18×0.9 = 16.2
**输出：16.2**

## 示例 4：超大件 + 易碎 + VIP（三重叠加）
输入：weight=5kg, 120×40×30cm, zone=same_province, fragile=true, vip=true
计算：vol=24, bill=24, cost=8+23×4.8=118.4
surcharge: 1+0.15(易碎)+0.25(120>100超大)=1.4, 118.4×1.4=165.76
VIP: 165.76×0.9 = 149.184
**输出：149.2**

## 示例 5：触发最低收费
输入：weight=1.5kg, 20×15×10cm, zone=same_city, 无附加, 非VIP
计算：vol=0.5, bill=1.5, cost=5+0.5×3=6.5
6.5 < 10 → 最低收费 10
**输出：10.0**