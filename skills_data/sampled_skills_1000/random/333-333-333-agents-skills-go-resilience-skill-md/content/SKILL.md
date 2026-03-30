---
name: go-resilience
description: >
  Resilience patterns for Go microservices: circuit breaker, retry with backoff, timeouts, graceful degradation, and failure injection testing.
  Trigger: When implementing circuit breakers, adding retry logic, configuring timeouts, or testing service resilience under failure.
metadata:
  author: 333-333-333
  version: "1.0"
  type: generic
  scope: [api]
  auto_invoke:
    - "Implementing circuit breaker patterns"
    - "Adding retry policies to HTTP clients"
    - "Configuring timeouts and graceful degradation"
    - "Testing service resilience under failure"
    - "Wrapping external calls with resilience patterns"
---

## When to Use

- Service calls external providers (FCM, SendGrid, Twilio, Flow.cl)
- Need to handle transient failures gracefully
- Want to prevent cascading failures when a dependency is down
- Configuring timeouts at HTTP, database, and external call levels
- Testing that the service degrades gracefully under failure

---

## Critical Patterns

### The Three Pillars

Every external call should be wrapped with these three patterns, in order:

```
Request → Timeout → Retry (with backoff) → Circuit Breaker → External Service
```

1. **Timeout**: Every external call has a context timeout — never wait forever
2. **Retry with Backoff**: Retry transient failures with exponential delay + jitter
3. **Circuit Breaker**: Stop calling a failing dependency after N consecutive failures

### Timeout Configuration

| Layer | Timeout | Where |
|-------|---------|-------|
| HTTP server read/write | 30s | `http.Server{ReadTimeout, WriteTimeout}` |
| External HTTP calls | 5-10s | `context.WithTimeout` per call |
| Database queries | 5s | `context.WithTimeout` per query |
| Graceful shutdown | 10s | `srv.Shutdown(ctx)` |

### Circuit Breaker

The circuit breaker tracks consecutive failures and opens (stops calling) when a threshold is reached. After a cooldown period, it half-opens to test if the dependency has recovered.

```
CLOSED  ──(N failures)──▶  OPEN  ──(cooldown)──▶  HALF-OPEN
   ▲                                                   │
   └──────────(success)────────────────────────────────┘
   └──────────(failure)──▶  OPEN (reset cooldown)
```

> See [assets/circuit_breaker.go](assets/circuit_breaker.go) for a lightweight circuit breaker implementation.

### Retry with Exponential Backoff

Retries use exponential backoff with jitter to avoid thundering herd:

```
Attempt 1: immediate
Attempt 2: 100ms + jitter
Attempt 3: 200ms + jitter
Attempt 4: 400ms + jitter
...capped at maxDelay
```

> See [assets/retry.go](assets/retry.go) for retry with exponential backoff and jitter.

### Resilient Sender Wrapper

The resilient sender combines all three patterns into a single decorator that wraps any `NotificationSender` (or any external call interface):

> See [assets/resilient_sender.go](assets/resilient_sender.go) for the combined wrapper.

---

## Testing Resilience

Test resilience by injecting failures:

| Scenario | How to test | Expected behavior |
|----------|------------|-------------------|
| Provider timeout | Mock sender with `time.Sleep` > timeout | Returns error, resource marked as failed |
| Provider 5xx | Mock sender returns error | Circuit breaker opens after N failures |
| DB connection lost | Stop testcontainer mid-test | Returns 503 on /ready, 200 on /health |
| Memory pressure | k6 soak test for 30min+ | No memory growth, stable response times |
| Connection pool exhaustion | Load test > pool.MaxConns | Requests queue, don't crash |

> See [assets/resilience_test.go](assets/resilience_test.go) for resilience test examples with failure injection.

---

## Decision Tree

```
Service calls external provider?
  → Wrap with timeout + retry + circuit breaker

Provider is down?
  → Circuit breaker opens, fail fast, degrade gracefully

Transient network error?
  → Retry with exponential backoff + jitter

Database query?
  → Add context.WithTimeout (5s default)

HTTP server?
  → Set ReadTimeout + WriteTimeout (30s default)
```

---

## Assets

| File | Description |
|------|-------------|
| `assets/circuit_breaker.go` | Lightweight circuit breaker with closed/open/half-open states |
| `assets/retry.go` | Retry with exponential backoff and jitter |
| `assets/resilient_sender.go` | Wrapper combining circuit breaker + retry + timeout |
| `assets/resilience_test.go` | Unit tests for resilience patterns (timeout, failure injection) |

---

## Anti-Patterns

| Don't | Do |
|----------|-------|
| Call external services without timeout | Always `context.WithTimeout` |
| Retry without backoff | Exponential backoff + jitter |
| Retry non-idempotent operations | Only retry idempotent calls (GET, or operations with idempotency keys) |
| Ignore circuit breaker state | Log state changes, expose in metrics |
| No fallback when circuit is open | Return cached result, queue for later, or return graceful error |
| Test only happy path | Inject failures: timeout, 5xx, connection refused |
