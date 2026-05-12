---
name: room-booking
description: 根据会议室预订规则审批预订请求。
---

# 会议室预订规则

## 会议室信息
- R01：容量 10 人，设备 [projector, whiteboard]
- R02：容量 20 人，设备 [projector, whiteboard, video_conf]
- R03：容量 6 人，设备 [whiteboard]

## 已有预订
- R01，2024-03-15，09:00-11:00，manager，非周期性 (existing_meeting_A)
- R02，2024-03-16，13:00-15:00，staff，周期性 (weekly_standup)

## 审批流程（按顺序检查，首个失败即拒绝）

### 第一步：容量检查
- attendees ≤ room_capacity → 通过
- 否则 → REJECTED，reason = "capacity_exceeded"

### 第二步：时间检查
- 开始时间 >= 08:00 且结束时间 <= 20:00
- 会议时长 >= 30 分钟且 <= 4 小时（240 分钟）
- 不满足任一条件 → REJECTED，reason = "time_invalid"

### 第三步：设备检查
- 所需设备必须是会议室现有设备的子集
- 否则 → REJECTED，reason = "equipment_missing"

### 第四步：冲突检查
- 与已有预订在同一房间、同一日期有时间重叠时：
  - 优先级：board=4 > dept_head=3 > manager=2 > staff=1
  - 新请求优先级更高 → APPROVED（抢占）
  - 同优先级：周期性预订优先于一次性预订
  - 同优先级同类型：已有预订优先 → REJECTED
  - 新请求优先级更低 → REJECTED，reason = "conflict"