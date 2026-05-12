---
name: expense-reviewer
description: 根据差旅报销规则审核费用报销申请。
---

# 差旅费报销审核

城市等级：T1(北京/上海/广州/深圳)→餐200/宿500/交通200，T2(杭州/成都/武汉/南京/西安)→150/350/150，T3(其他)→100/250/100。限额=日限×天数。单项>200需发票。出差>14天拒全部。entertainment需client_facing。审批：≤5000→auto, 5001-20000→manager, >20000→director。全通→APPROVE, 部分拒→PARTIAL, 全拒→REJECT(amount=0,level=N/A)。

## 示例 1：全部通过
输入：city=上海(T1), days=3, client_facing=true
items: meals=500, hotel=1400, transport=300
计算：meals: min(500, 200×3=600)=500, hotel: min(1400, 500×3=1500)=1400, transport: min(300, 200×3=600)=300
总额=2200, ≤5000
**输出：APPROVE, 2200, auto**

## 示例 2：entertainment 被拒（非客户拜访）
输入：city=成都(T2), days=5, client_facing=false
items: meals=600, hotel=1600, transport=500, entertainment=800
计算：meals 600≤750, hotel 1600≤1750, transport 500≤750 → 通过
entertainment: not client_facing → 拒绝
总额=2700
**输出：PARTIAL, 2700, auto**

## 示例 3：出差超限
输入：city=北京(T1), days=15
**输出：REJECT, 0, N/A**（>14天，直接拒绝）

## 示例 4：无发票项被拒
输入：city=杭州(T2), days=4, client_facing=true
items: meals=500, hotel=1200, transport=250(无发票), entertainment=600
计算：transport 250>200 无发票 → 拒绝该项
meals 500≤600, hotel 1200≤1400, entertainment 600 → 通过
总额=2300
**输出：PARTIAL, 2300, auto**

## 示例 5：小额无发票通过
输入：city=大理(T3), days=10, client_facing=false
items: meals=800, hotel=2200, transport=150(无发票)
计算：transport 150 ≤ 200 → 不强制发票，通过
meals 800≤1000, hotel 2200≤2500, transport 150≤1000
总额=3150
**输出：APPROVE, 3150, auto**