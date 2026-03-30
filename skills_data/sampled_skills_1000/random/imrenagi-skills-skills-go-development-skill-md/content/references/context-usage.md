---
title: Proper Context Usage
impact: HIGH
impactDescription: Ensures request cancellation, timeouts, and metadata are correctly propagated throughout the application.
tags: go, context, concurrency
---

## Proper Context Usage

**Impact: HIGH**

In Go, `context.Context` is used to carry deadlines, cancellation signals, and other request-scoped values across API boundaries and between processes. Proper usage is critical for building responsive and observable services.

### When to add Context as the First Argument

As a rule of thumb, you should add `ctx context.Context` as the **first argument** to a function or method in the following scenarios:

#### 1. Functions Performing I/O

Any function that interacts with an external system (Database, Redis, Internal/External APIs, File System) must take a context to handle timeouts and cancellations.

```go
// Correct: Database operation with context
func (r *Repository) GetUser(ctx context.Context, id string) (*User, error) {
    return r.db.QueryContext(ctx, "SELECT ...", id)
}
```

#### 2. Functions Carrying Metadata

If a function needs to access request-scoped metadata (e.g., Trace IDs for logging, Authenticated Principal), it must receive a context.

```go
// Correct: Passing context for logging and auth checks
func (s *Service) ProcessPayments(ctx context.Context, orderID string) error {
    log.Ctx(ctx).Info().Msg("starting payment processing")
    // ...
}
```

#### 3. Long-Running or Computational Tasks

If a function might take a significant amount of time to execute, passing a context allows the caller to cancel the work if it's no longer needed.

```go
func HeavyComputation(ctx context.Context, data []byte) ([]byte, error) {
    for {
        select {
        case <-ctx.Done():
            return nil, ctx.Err()
        default:
            // perform chunk of work
        }
    }
}
```

### When NOT to use Context

Avoid adding context to "pure" functions that only perform memory-based operations or simple data transformations that are guaranteed to be fast and don't require metadata.

```go
// Incorrect: Context is unnecessary for simple math
func Add(ctx context.Context, a, b int) int {
    return a + b
}
```

### Best Practices

1.  **First Parameter**: `context.Context` should always be the first parameter, typically named `ctx`.
2.  **Do Not Store in Structs**: Never store a `Context` inside a struct type; instead, pass a `Context` explicitly to each function that needs it. (Exceptions include `http.Request`).
3.  **Pass, Don't Store**: Functions should pass the context down to the next layer (e.g., Service -> Repository).
4.  **Use `context.Background()` sparingly**: Only use it at the very top level (e.g., main function, background workers) when no existing context is available.
5.  **Handling Cancellation**: Check `ctx.Err()` or `<-ctx.Done()` in long loops or before starting expensive operations.

### References

- [Go Blog: Context](https://go.dev/blog/context)
- [Uber Go Style Guide: Context](https://github.com/uber-go/guide/blob/master/style.md#context)
- [Pass Context to Loggers](logging-context.md)
