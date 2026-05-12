---
name: shipping-calculator
description: 根据物流规则计算包裹运费。
---

# 物流运费计算规则

综合计费重量、区域费率、附加服务和客户等级计算运费。

## 计费重量
```
vol_weight = 长 × 宽 × 高 / 6000
billable_weight = max(实际重量, vol_weight)
```

## 区域费率

| 区域             | 费率 (元/kg) |
|-----------------|-------------|
| 同城 same_city   | 5           |
| 省内 same_province | 8         |
| 邻省 adjacent    | 12          |
| 偏远 remote      | 18          |

- 首公斤：按基础费率
- 续重：按基础费率 × 60%

## 附加费（累加乘数）
- 易碎品：+15%
- 超大件（任一边 > 100cm）：+25%
- 冷链运输：+30%

## 折扣与兜底
- VIP 客户：最终费用 × 0.9
- 最低收费：10 元

## 示例
输入：weight=3kg, 30×20×15cm, same_city, 非VIP
→ vol=1.5, bill=3, cost=5+2×3=11.0 → **输出：11.0**

输入：weight=5kg, 120×40×30cm, same_province, fragile, VIP
→ vol=24, bill=24, cost=8+23×4.8=118.4, ×1.4(易碎+超大)=165.76, ×0.9=149.184 → **输出：149.2**

结果保留一位小数。