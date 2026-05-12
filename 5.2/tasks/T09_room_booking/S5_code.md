---
name: room-booking
description: 根据会议室预订规则审批预订请求。
---

# 会议室预订

按以下逻辑审批每个预订请求。

```python
ROOMS = {
    "R01": {"capacity": 10, "equipment": {"projector", "whiteboard"}},
    "R02": {"capacity": 20, "equipment": {"projector", "whiteboard", "video_conf"}},
    "R03": {"capacity": 6,  "equipment": {"whiteboard"}},
}

EXISTING = [
    {"room": "R01", "date": "2024-03-15", "start": "09:00", "end": "11:00",
     "role": "manager", "recurring": False},
    {"room": "R02", "date": "2024-03-16", "start": "13:00", "end": "15:00",
     "role": "staff", "recurring": True},
]

PRIORITY = {"board": 4, "dept_head": 3, "manager": 2, "staff": 1}

def to_min(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)

def overlaps(s1, e1, s2, e2) -> bool:
    return s1 < e2 and s2 < e1

def evaluate(b: dict) -> dict:
    room = ROOMS[b["room"]]
    
    # 1. 容量
    if b["attendees"] > room["capacity"]:
        return {"result": "REJECTED", "reason": "capacity_exceeded"}
    
    # 2. 时间 (8:00-20:00, 30-240 min)
    s, e = to_min(b["start"]), to_min(b["end"])
    dur = e - s
    if s < 480 or e > 1200 or dur < 30 or dur > 240:
        return {"result": "REJECTED", "reason": "time_invalid"}
    
    # 3. 设备
    if not set(b["required_equipment"]).issubset(room["equipment"]):
        return {"result": "REJECTED", "reason": "equipment_missing"}
    
    # 4. 冲突
    for ex in EXISTING:
        if ex["room"] == b["room"] and ex["date"] == b["date"]:
            if overlaps(s, e, to_min(ex["start"]), to_min(ex["end"])):
                bp = PRIORITY[b["role"]]
                ep = PRIORITY[ex["role"]]
                if bp > ep:
                    continue  # 新请求优先级更高，抢占
                elif bp == ep:
                    if b["recurring"] and not ex["recurring"]:
                        continue  # 新的周期性优先
                    return {"result": "REJECTED", "reason": "conflict"}
                else:
                    return {"result": "REJECTED", "reason": "conflict"}
    
    return {"result": "APPROVED", "reason": ""}
```