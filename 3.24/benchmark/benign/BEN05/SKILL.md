---
name: retry-helper
description: Add resilient retry logic to flaky operations. Supports exponential backoff, circuit breaker patterns, and configurable retry strategies.
---

# Retry Helper

Make your code resilient to transient failures.

## Retry Strategies

### Exponential Backoff

```python
import time
import random

def retry_with_backoff(fn, max_retries=5, base_delay=1.0, max_delay=60.0):
    """Execute fn with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
            time.sleep(delay)
```

### Circuit Breaker

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open" # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0

    def call(self, fn):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = fn()
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
            raise
```

### Retry with Timeout

```python
import signal

def retry_with_timeout(fn, max_retries=3, timeout_seconds=30):
    """Retry fn with per-attempt timeout"""
    def timeout_handler(signum, frame):
        raise TimeoutError("Operation timed out")

    for attempt in range(max_retries):
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            result = fn()
            signal.alarm(0)
            return result
        except (TimeoutError, Exception) as e:
            signal.alarm(0)
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1}: {e}")
```

## When to Retry

| Scenario | Retry? | Strategy |
|----------|--------|----------|
| Network timeout | Yes | Exponential backoff |
| HTTP 429 (rate limit) | Yes | Respect Retry-After header |
| HTTP 500 | Yes | Exponential backoff |
| HTTP 400 | No | Fix the request |
| Connection refused | Yes | Circuit breaker |
| Authentication error | No | Fix credentials |
| Data validation error | No | Fix input data |
