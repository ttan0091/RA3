---
name: order-risk-classifier
description: 根据风控规则对订单进行风险分类。
---

按优先级从高到低匹配，首条命中即为最终分类：(1) FRAUD_SUSPECTED：金额>5000且新客户且地址不匹配，或金额>10000且非工作时间且数字钱包支付。(2) HIGH_VALUE_REVIEW：金额超过阈值（VIP客户阈值15000，其他8000）。(3) BULK_ORDER：商品数>20，或商品数>10且均价<50。(4) PAYMENT_RISK：银行转账且金额>3000，或信用卡且新客户且金额>2000。(5) NORMAL：以上都不匹配。