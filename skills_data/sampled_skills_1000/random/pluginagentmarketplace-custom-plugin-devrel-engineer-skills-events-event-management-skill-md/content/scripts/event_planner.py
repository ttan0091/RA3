#!/usr/bin/env python3
"""Developer event planning assistant."""
import json

def plan_event(event_type="meetup"):
    return {
        "event_type": event_type,
        "timeline": {
            "8_weeks": "venue_budget",
            "6_weeks": "speakers_sponsors",
            "4_weeks": "marketing_registration",
            "2_weeks": "final_logistics",
            "1_week": "reminders_prep"
        },
        "budget_categories": ["venue", "catering", "swag", "av_equipment", "marketing"]
    }

if __name__ == "__main__":
    print(json.dumps(plan_event("hackathon"), indent=2))
