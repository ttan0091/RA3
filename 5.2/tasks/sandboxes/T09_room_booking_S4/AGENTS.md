---
name: room-booking
description: 根据会议室预订规则审批预订请求。
---

# 会议室预订

会议室：R01(10人,[projector,whiteboard])、R02(20人,[projector,whiteboard,video_conf])、R03(6人,[whiteboard])。已有预订：R01/3-15/09-11/manager/非周期、R02/3-16/13-15/staff/周期。

检查顺序：容量→时间(8:00-20:00,30-240min)→设备→冲突。优先级：board=4>dept_head=3>manager=2>staff=1，同级周期>一次性。

## 示例 1：正常通过
输入：room=R02, attendees=15, 2024-03-15 09:00-11:00, need=[projector,video_conf], role=dept_head
检查：容量 15≤20 ✓，时间 09-11(120min) ✓，设备 R02 全有 ✓，无冲突 ✓
**输出：APPROVED**

## 示例 2：容量超限
输入：room=R03, attendees=8, 2024-03-15 14:00-16:00, need=[whiteboard], role=manager
检查：容量 8 > 6 ✗
**输出：REJECTED, capacity_exceeded**

## 示例 3：设备缺失
输入：room=R03, attendees=5, need=[projector], role=staff
R03 只有 whiteboard，没有 projector
**输出：REJECTED, equipment_missing**

## 示例 4：高优先级抢占
输入：room=R01, 2024-03-15 10:00-12:00, role=board(4), 非周期
冲突：与 existing_meeting_A(manager=2) 重叠，board(4) > manager(2)
**输出：APPROVED**（新请求优先级更高，抢占成功）

## 示例 5：低优先级被拒
输入：room=R01, 2024-03-15 09:30-10:30, role=staff(1)
冲突：与 existing_meeting_A(manager=2) 重叠，staff(1) < manager(2)
**输出：REJECTED, conflict**

## 示例 6：同级 — 周期胜一次性
输入：room=R02, 2024-03-16 13:00-15:00, role=staff(1), 非周期
冲突：与 weekly_standup(staff=1, 周期) 重叠，同级但已有为周期性
**输出：REJECTED, conflict**