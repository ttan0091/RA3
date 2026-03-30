---
title: Pass Context to Loggers
impact: HIGH
impactDescription: Pass context to loggers to carry request-scoped metadata
---

## Pass Context to Loggers

**Impact: HIGH**

Use `rs/zerolog` for logging. It is faster than the standard library and provides structured JSON output which is essential for observability.

**Using passed context:**

Whenever `context` object is passed to a function, pass it to the logger as well.

```go
import (
    "context"
    "github.com/rs/zerolog/log"
)

func process(ctx context.Context, userID string) {
    log := log.Ctx(ctx)
    log.Info().Msg("starting processing")
}
```

**Contextual logging:**

When additional context is needed within a function scope multiple times, define the logger with some initial contexts.

```go
func process(ctx context.Context, userID string) {
    log := log.Ctx(ctx).With().
        Str("userID", userID).
        Logger()
    log.Info().Msg("processing completed")
}
```

When there is error, use `Err` method to log it.

```go
if err != nil {
    log.Error().Err(err).Msg("processing failed")
}
```

Reference: [Zerolog Documentation](https://github.com/rs/zerolog)
