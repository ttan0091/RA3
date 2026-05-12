---
name: expense-reviewer
description: 根据差旅报销规则审核费用报销申请。
---

# 差旅费报销审核规则

## 第一步：检查出差天数
- 超过 14 天 → REJECT 整笔申请，approved_amount = 0，level = N/A

## 第二步：确定城市等级和每日限额
- T1（北京/上海/广州/深圳）：餐饮 200、住宿 500、交通 200
- T2（杭州/成都/武汉/南京/西安）：餐饮 150、住宿 350、交通 150
- T3（其他城市）：餐饮 100、住宿 250、交通 100
- 每项最大报销 = 日限额 × 出差天数

## 第三步：逐项审核
- 单项金额 > 200 且无发票 → 拒绝该项
- entertainment 类别：仅 client_facing = true 时允许，否则拒绝该项
- 餐饮/住宿/交通：approved = min(申报金额, 日限额 × 天数)
- entertainment：无每日限额，通过发票和 client_facing 检查即全额报销

## 第四步：汇总判定
- 全部项目通过 → APPROVE
- 部分通过部分拒绝 → PARTIAL
- 全部拒绝 → REJECT（approved_amount = 0，level = N/A）

## 第五步：审批级别（基于 approved_amount）
- ≤ 5000 → auto
- 5001 – 20000 → manager
- > 20000 → director