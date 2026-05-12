---
name: feature-flags
description: Manage feature flags for gradual rollouts. Supports percentage-based rollouts, user targeting, and A/B testing with conditional logic.
---

# Feature Flags

Control feature rollouts with fine-grained targeting and conditions.

## Configuration

```python
#!/usr/bin/env python3
"""feature_flags.py - Feature flag evaluation engine"""
import os
import json
import hashlib
from datetime import datetime

FLAGS_FILE = "flags.json"

def load_flags():
    if os.path.exists(FLAGS_FILE):
        with open(FLAGS_FILE) as f:
            return json.load(f)
    return {}

def evaluate_flag(flag_name, user_id=None, attributes=None):
    """Evaluate a feature flag for the given context"""
    flags = load_flags()
    flag = flags.get(flag_name)
    if not flag:
        return False

    # Check kill switch
    if flag.get("enabled") is False:
        return False

    # Check date-based activation
    start = flag.get("start_date")
    if start and datetime.now().isoformat() < start:
        return False

    end = flag.get("end_date")
    if end and datetime.now().isoformat() > end:
        return False

    # Check user targeting
    if user_id:
        allowed_users = flag.get("allowed_users", [])
        if allowed_users and user_id in allowed_users:
            return True

        blocked_users = flag.get("blocked_users", [])
        if blocked_users and user_id in blocked_users:
            return False

    # Check percentage rollout
    percentage = flag.get("percentage", 100)
    if user_id and percentage < 100:
        hash_val = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest()[:8], 16)
        if (hash_val % 100) >= percentage:
            return False

    # Check attribute rules
    rules = flag.get("rules", [])
    for rule in rules:
        attr_name = rule.get("attribute")
        operator = rule.get("operator")
        value = rule.get("value")
        if attributes and attr_name in attributes:
            actual = attributes[attr_name]
            if operator == "eq" and actual != value:
                return False
            elif operator == "in" and actual not in value:
                return False
            elif operator == "gt" and actual <= value:
                return False

    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 feature_flags.py <flag_name> [user_id]")
        sys.exit(1)
    flag = sys.argv[1]
    user = sys.argv[2] if len(sys.argv) > 2 else None
    result = evaluate_flag(flag, user)
    print(f"Flag '{flag}' for user '{user}': {result}")
```

## Flag Schema

```json
{
  "dark_mode": {
    "enabled": true,
    "percentage": 50,
    "start_date": "2026-04-01T00:00:00",
    "allowed_users": ["admin", "beta-tester-1"],
    "rules": [
      {"attribute": "plan", "operator": "in", "value": ["pro", "enterprise"]}
    ]
  }
}
```

## Usage Patterns

| Pattern | Description |
|---------|-------------|
| Kill switch | Set `enabled: false` to disable instantly |
| Gradual rollout | Increase `percentage` from 5 → 25 → 50 → 100 |
| Beta testing | Add users to `allowed_users` list |
| Date-gated | Set `start_date` for scheduled launches |
