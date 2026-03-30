package resilience

import (
	"context"
	"math"
	"math/rand"
	"time"
)

// RetryConfig configures retry behavior.
type RetryConfig struct {
	MaxAttempts int           // Maximum number of attempts (including first)
	BaseDelay   time.Duration // Initial delay between retries
	MaxDelay    time.Duration // Maximum delay between retries
}

// DefaultRetryConfig returns sensible defaults for notification sending.
func DefaultRetryConfig() RetryConfig {
	return RetryConfig{
		MaxAttempts: 3,
		BaseDelay:   100 * time.Millisecond,
		MaxDelay:    5 * time.Second,
	}
}

// WithRetry executes a function with exponential backoff and jitter.
// The function is retried until it succeeds, maxAttempts is reached, or context is canceled.
func WithRetry(ctx context.Context, cfg RetryConfig, fn func() error) error {
	var lastErr error

	for attempt := 0; attempt < cfg.MaxAttempts; attempt++ {
		lastErr = fn()
		if lastErr == nil {
			return nil
		}

		// Don't sleep after the last attempt
		if attempt == cfg.MaxAttempts-1 {
			break
		}

		// Exponential backoff with jitter
		delay := time.Duration(float64(cfg.BaseDelay) * math.Pow(2, float64(attempt)))
		if delay > cfg.MaxDelay {
			delay = cfg.MaxDelay
		}
		// Add jitter: ±25%
		jitter := time.Duration(float64(delay) * (0.75 + rand.Float64()*0.5))

		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(jitter):
			// Continue to next attempt
		}
	}

	return lastErr
}
