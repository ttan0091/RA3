---
name: room-booking
description: 根据会议室预订规则审批预订请求。
---

会议室：R01(10人,[projector,whiteboard])、R02(20人,[projector,whiteboard,video_conf])、R03(6人,[whiteboard])。已有预订：R01/2024-03-15/09:00-11:00/manager/非周期(existing_meeting_A)、R02/2024-03-16/13:00-15:00/staff/周期(weekly_standup)。审批规则按顺序检查：①容量：attendees ≤ room_capacity，否则 REJECTED(capacity_exceeded)。②时间：8:00-20:00 内，时长 30-240 分钟，否则 REJECTED(time_invalid)。③设备：required ⊆ room_equipment，否则 REJECTED(equipment_missing)。④冲突：同房间同日时间重叠时，比较优先级 board=4>dept_head=3>manager=2>staff=1，高优先级赢；同级时周期性>一次性；同级同类型先到先得，否则 REJECTED(conflict)。