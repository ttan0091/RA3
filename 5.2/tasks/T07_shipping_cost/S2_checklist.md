---
name: shipping-calculator
description: 根据物流规则计算包裹运费。
---

# 物流运费计算规则

## 第一步：计算计费重量
- 体积重量 = 长 × 宽 × 高 / 6000（单位 cm → kg）
- 计费重量 = max(实际重量, 体积重量)

## 第二步：查基础费率
- 同城 (same_city): 5 元/kg
- 省内 (same_province): 8 元/kg
- 邻省 (adjacent): 12 元/kg
- 偏远 (remote): 18 元/kg

## 第三步：计算基础运费
- 首公斤：base_rate
- 续重（超过 1kg 部分）：每 kg 按 base_rate × 60%
- cost = base_rate + max(0, 计费重量 - 1) × base_rate × 0.6

## 第四步：附加费（累加乘数）
- 易碎品 (fragile): +15%
- 超大件（任一维度 > 100cm）: +25%
- 冷链运输 (cold_chain): +30%
- 乘数 = 1 + 各项附加百分比之和
- cost = cost × 乘数

## 第五步：VIP 折扣
- VIP 客户：最终费用 × 0.9（九折）

## 第六步：兜底和取整
- 最低收费 10 元（如计算结果 < 10，则收 10）
- 结果保留一位小数