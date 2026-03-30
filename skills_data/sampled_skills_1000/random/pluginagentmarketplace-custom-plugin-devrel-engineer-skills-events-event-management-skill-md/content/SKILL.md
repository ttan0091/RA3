---
name: event-management
description: Planning, promoting, and executing developer events from meetups to conferences
sasmp_version: "1.4.0"
version: "2.0.0"
updated: "2025-01"
bonded_agent: 05-event-manager
bond_type: PRIMARY_BOND
---

# Developer Event Management

Plan and execute **successful developer events** that create lasting impact.

## Skill Contract

### Parameters
```yaml
parameters:
  required:
    - event_type: enum[meetup, webinar, workshop, hackathon, conference]
    - event_goal: string
  optional:
    - format: enum[in_person, virtual, hybrid]
    - target_attendance: integer
    - budget: float
```

### Output
```yaml
output:
  event_plan:
    overview: object
    timeline: array[Milestone]
    budget: object
    run_of_show: array[Session]
```

## Event Types

| Type | Size | Duration | Lead Time |
|------|------|----------|-----------|
| Meetup | 20-100 | 2-3 hours | 4-6 weeks |
| Workshop | 10-50 | Half/full day | 6-8 weeks |
| Webinar | 50-500 | 1 hour | 2-4 weeks |
| Hackathon | 50-500 | 24-48 hours | 8-12 weeks |
| Conference | 200-2000 | 1-3 days | 3-6 months |

## Event Planning Timeline

### T-12 to T-8 Weeks
```
□ Define goals and success metrics
□ Set budget
□ Book venue (if in-person)
□ Recruit speakers
□ Create event branding
```

### T-8 to T-4 Weeks
```
□ Open registration
□ Launch promotion
□ Finalize agenda
□ Confirm sponsors
□ Plan logistics
```

### T-4 to T-1 Weeks
```
□ Speaker prep calls
□ Finalize catering/A/V
□ Send attendee reminders
□ Prepare materials
□ Test technology
```

### Day Before
```
□ Venue walkthrough
□ Test all equipment
□ Brief volunteers
□ Prepare swag bags
□ Final speaker check
```

## Promotion Strategy

```
Email → Social → Partners → Community → Press
  ↓        ↓         ↓           ↓         ↓
List     Posts   Co-promo    Members    PR
Sequence Campaign  Shares   Announce   Outreach
```

## Post-Event

| Activity | Timing |
|----------|--------|
| Thank you emails | Same day |
| Feedback survey | 1-3 days |
| Photo gallery | 1 week |
| Recording publish | 1 week |
| ROI report | 2-4 weeks |

## Retry Logic

```yaml
retry_patterns:
  low_registrations:
    strategy: "Boost promotion, add incentive"
    trigger: "<50% target at T-2 weeks"

  speaker_cancellation:
    strategy: "Activate backup speaker"
    fallback: "Panel discussion"

  technical_issues:
    strategy: "Switch to backup equipment"
```

## Failure Modes & Recovery

| Failure Mode | Detection | Recovery |
|--------------|-----------|----------|
| Low registrations | <50% at T-2w | Boost promo |
| Low show rate | <60% attendance | Better reminders |
| Speaker no-show | Day-of absence | Backup speaker |
| A/V failure | Tech issues | Backup equipment |

## Debug Checklist

```
□ Goals and metrics defined?
□ Budget approved?
□ Venue/platform confirmed?
□ Speakers confirmed?
□ Registration working?
□ Promotion calendar active?
□ A/V tested?
□ Backup plans documented?
```

## Test Template

```yaml
test_event_management:
  unit_tests:
    - test_registration_flow:
        assert: "Confirmation email received"

  integration_tests:
    - test_day_of_flow:
        assert: "All sessions on time"
```

## Success Metrics

| Metric | Target |
|--------|--------|
| Reg to attendance | >60% |
| NPS score | >40 |
| Content engagement | >50% |

## Observability

```yaml
metrics:
  - registrations: integer
  - attendees: integer
  - show_rate: float
  - nps_score: float
```

See `assets/` for event checklists and templates.
