---
name: order-risk-classifier
description: 根据风控规则对订单进行风险分类。
---

# 订单风控分类

按优先级依次匹配5级规则，首条命中为最终结果：P1=FRAUD_SUSPECTED, P2=HIGH_VALUE_REVIEW, P3=BULK_ORDER, P4=PAYMENT_RISK, P5=NORMAL。

P1触发条件：(a) amount>5000 AND new AND !addr_match; (b) amount>10000 AND off_hours AND digital_wallet。
P2触发条件：amount > 阈值（vip→15000, 其他→8000）。
P3触发条件：(a) items>20; (b) items>10 AND avg_price<50。
P4触发条件：(a) bank_transfer AND amount>3000; (b) credit_card AND new AND amount>2000。
P5：以上均不匹配。

## 示例 1
输入：amount=7000, payment=credit_card, customer=new, addr_match=false, time=business, items=2, avg=3500
分析：P1(a) amount>5000 ✓ AND new ✓ AND !addr_match ✓ → 命中
**结果：FRAUD_SUSPECTED**

## 示例 2
输入：amount=9500, payment=debit_card, customer=regular, addr_match=true, time=business, items=3, avg=3167
分析：P1 不满足(regular且addr_match)。P2 regular阈值=8000, 9500>8000 → 命中
**结果：HIGH_VALUE_REVIEW**

## 示例 3（VIP 高额不触发）
输入：amount=13000, payment=debit_card, customer=vip, addr_match=true, time=business, items=1, avg=13000
分析：P1 不满足。P2 vip阈值=15000, 13000<15000 → 不命中。P3/P4 不满足。
**结果：NORMAL**

## 示例 4（优先级竞争）
输入：amount=5000, payment=bank_transfer, customer=regular, addr_match=true, time=business, items=22, avg=227
分析：P1 不满足。P2 5000<8000 不满足。P3(a) items=22>20 → 命中（不再检查P4的bank_transfer>3000）
**结果：BULK_ORDER**

## 示例 5
输入：amount=2500, payment=credit_card, customer=new, addr_match=true, time=off_hours, items=1, avg=2500
分析：P1 不满足(addr_match=true; amount<10000)。P2 不满足。P3 不满足。P4(b) credit_card AND new AND 2500>2000 → 命中
**结果：PAYMENT_RISK**