# T09 Meeting Room Booking — Internal Spec

## Purpose
Agent must evaluate meeting room booking requests against capacity, time, equipment, and conflict rules.
Model pre-training cannot help because the rooms, equipment, priority rules, and time constraints are custom.

## Room Definitions (provided as context)
| Room | Capacity | Equipment                          |
|------|----------|------------------------------------|
| R01  | 10       | projector, whiteboard              |
| R02  | 20       | projector, whiteboard, video_conf  |
| R03  | 6        | whiteboard                         |

## Existing Bookings (provided as context)
| Room | Date       | Time        | Role    | Recurring | Holder           |
|------|------------|-------------|---------|-----------|------------------|
| R01  | 2024-03-15 | 09:00-11:00 | manager | No        | existing_meeting_A |
| R02  | 2024-03-16 | 13:00-15:00 | staff   | Yes       | weekly_standup   |

## Validation Rules (checked in order; first failure → REJECTED)

### 1. Capacity Check
- attendees must be ≤ room_capacity
- Else → REJECTED, reason: "capacity_exceeded"

### 2. Time Check
- Booking must be within 8:00-20:00 (start ≥ 08:00, end ≤ 20:00)
- Duration must be 30 minutes to 4 hours (30-240 minutes)
- Else → REJECTED, reason: "time_invalid"

### 3. Equipment Check
- All required_equipment must be available in the room
- Else → REJECTED, reason: "equipment_missing"

### 4. Conflict Check
- If the requested room/date/time overlaps with an existing booking:
  - Compare priority levels: board=4 > dept_head=3 > manager=2 > staff=1
  - Higher priority wins → new booking APPROVED (bumps existing)
  - Same priority: recurring booking beats one-time booking
  - Same priority + same type: existing booking wins (first come first served)
  - Lower priority → REJECTED, reason: "conflict"

## Output
- result: "APPROVED" | "REJECTED"
- reason: string (empty for APPROVED, one of: capacity_exceeded, time_invalid, equipment_missing, conflict)
