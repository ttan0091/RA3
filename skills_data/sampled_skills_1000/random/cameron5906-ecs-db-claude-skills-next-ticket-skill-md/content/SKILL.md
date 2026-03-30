---
name: next-ticket
description: Find and load the next ticket to work on based on dependencies and priority
allowed-tools: Read, Glob, Grep
model: haiku
---

# Find Next Ticket

You are finding the next ticket that is ready to be worked on.

## Selection Criteria (in order of priority)

1. **Status**: Must be 🔴 (Not Started)
2. **Dependencies**: All tickets in "Depends On" must be 🟢 (Complete)
3. **Priority**: P0 before P1, P1 before P2
4. **Sprint Order**: Earlier sprints before later sprints
5. **Ticket Order**: Lower ticket numbers before higher

## Process

1. Read `sprints/SPRINT_TRACKER.md` to find active sprints

2. For each sprint (in order):
   - Read `sprints/sprint-XX-*/README.md`
   - Find all 🔴 tickets
   - Check each ticket's dependencies

3. For each candidate ticket:
   - Read the full ticket file: `sprints/sprint-XX-*/TICKET-XX-YYY*.md`
   - Verify "Depends On" tickets are complete
   - Note the Priority and Complexity

4. Select the highest priority ticket with satisfied dependencies

## Output Format

```
# Next Ticket Ready for Work

**TICKET-XX-YYY: <Full Title>**

## Metadata
- Sprint: XX - <Sprint Name>
- Priority: PX (Critical/High/Medium/Low)
- Complexity: S/M/L
- Dependencies: All satisfied ✓

## Summary
<Brief description from ticket>

## Acceptance Criteria
<List from ticket>

## Key Technical Details
<Highlight important implementation notes>

---

To begin work on this ticket, use:
/ticket XX-YYY

Or to see full ticket:
Read sprints/sprint-XX-*/TICKET-XX-YYY*.md
```

If no tickets are ready (all blocked), report the blocking situation.
