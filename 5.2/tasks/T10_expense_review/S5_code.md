---
name: expense-reviewer
description: 根据差旅报销规则审核费用报销申请。
---

# 差旅费报销审核

按以下逻辑审核每笔报销申请。

```python
TIER_MAP = {
    "北京": "T1", "上海": "T1", "广州": "T1", "深圳": "T1",
    "杭州": "T2", "成都": "T2", "武汉": "T2", "南京": "T2", "西安": "T2",
}  # 其他城市默认 T3

LIMITS = {
    "T1": {"meals": 200, "hotel": 500, "transport": 200},
    "T2": {"meals": 150, "hotel": 350, "transport": 150},
    "T3": {"meals": 100, "hotel": 250, "transport": 100},
}

def review_expense(trip: dict) -> dict:
    # 天数限制
    if trip["days"] > 14:
        return {"result": "REJECT", "approved_amount": 0, "approval_level": "N/A"}
    
    tier = TIER_MAP.get(trip["city"], "T3")
    daily = LIMITS[tier]
    days = trip["days"]
    client = trip["client_facing"]
    
    approved = 0
    has_rejected = False
    has_approved = False
    
    for item in trip["items"]:
        cat, amt, receipt = item["category"], item["amount"], item.get("has_receipt", True)
        
        # entertainment 检查
        if cat == "entertainment" and not client:
            has_rejected = True
            continue
        
        # 发票检查：单项 > 200 需发票
        if amt > 200 and not receipt:
            has_rejected = True
            continue
        
        # 计算批准金额
        if cat in daily:
            approved += min(amt, daily[cat] * days)
        else:
            approved += amt  # entertainment 无每日限额
        has_approved = True
    
    # 判定结果
    if not has_approved:
        return {"result": "REJECT", "approved_amount": 0, "approval_level": "N/A"}
    result = "PARTIAL" if has_rejected else "APPROVE"
    
    # 审批级别
    if approved <= 5000:
        level = "auto"
    elif approved <= 20000:
        level = "manager"
    else:
        level = "director"
    
    return {"result": result, "approved_amount": approved, "approval_level": level}
```