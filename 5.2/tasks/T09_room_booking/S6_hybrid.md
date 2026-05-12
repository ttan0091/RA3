---
name: room-booking
description: 根据会议室预订规则审批预订请求。
---

# 会议室预订规则

依次检查容量、时间、设备和冲突，首个失败即拒绝。

## 会议室信息

| 房间 | 容量 | 设备                              |
|------|-----|-----------------------------------|
| R01  | 10  | projector, whiteboard             |
| R02  | 20  | projector, whiteboard, video_conf |
| R03  | 6   | whiteboard                        |

## 已有预订

| 房间 | 日期       | 时间        | 级别    | 周期性 |
|------|-----------|-------------|---------|-------|
| R01  | 2024-03-15 | 09:00-11:00 | manager | 否    |
| R02  | 2024-03-16 | 13:00-15:00 | staff   | 是    |

## 审批检查

1. **容量**：attendees ≤ capacity → 否则 REJECTED (capacity_exceeded)
2. **时间**：08:00-20:00，时长 30-240 分钟 → 否则 REJECTED (time_invalid)
3. **设备**：required ⊆ room_equipment → 否则 REJECTED (equipment_missing)
4. **冲突**：同房间同日时间重叠时比较优先级

## 优先级规则

| 级别      | 优先级 |
|-----------|-------|
| board     | 4     |
| dept_head | 3     |
| manager   | 2     |
| staff     | 1     |

- 高优先级 > 低优先级（新请求高则抢占成功）
- 同优先级：周期性 > 一次性
- 同优先级同类型：已有优先（先到先得）

## 示例
请求：R01, 2024-03-15 10:00-12:00, board
→ 冲突 existing_meeting_A(manager=2), board(4)>manager(2) → **APPROVED**

请求：R01, 2024-03-15 09:30-10:30, staff
→ 冲突 existing_meeting_A(manager=2), staff(1)<manager(2) → **REJECTED, conflict**