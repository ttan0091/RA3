---
name: expense-reviewer
description: 根据差旅报销规则审核费用报销申请。
---

城市分级：T1(北京/上海/广州/深圳)→餐200/宿500/交通200每天，T2(杭州/成都/武汉/南京/西安)→150/350/150，T3(其他)→100/250/100。每项限额=日限×天数，报销取 min(申报额, 限额)。单项>200 需发票，无发票拒该项。出差超 14 天拒全部。entertainment 仅 client_facing=true 时允许（无每日限额）。全部通过→APPROVE，部分拒→PARTIAL，全拒→REJECT。审批：总额≤5000→auto，5001-20000→manager，>20000→director。REJECT 时 approved_amount=0，level=N/A。