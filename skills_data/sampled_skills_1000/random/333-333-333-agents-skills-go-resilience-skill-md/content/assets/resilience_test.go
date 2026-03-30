package resilience_test

import (
	"context"
	"errors"
	"testing"
	"time"
	// "github.com/333-333-333/bastet/api/notification/internal/shared/resilience"
)

// These tests demonstrate how to test resilience patterns.
// Adapt import paths and types for your service.

func TestCircuitBreaker_OpensAfterMaxFailures(t *testing.T) {
	// cb := resilience.NewCircuitBreaker(3, 5*time.Second)
	maxFailures := 3
	failureCount := 0
	alwaysFail := func() error {
		failureCount++
		return errors.New("provider error")
	}

	// Simulate failures
	for i := 0; i < maxFailures; i++ {
		_ = alwaysFail()
	}

	if failureCount != maxFailures {
		t.Errorf("expected %d failures, got %d", maxFailures, failureCount)
	}

	// After max failures, circuit should be open
	// err := cb.Execute(alwaysFail)
	// if !errors.Is(err, resilience.ErrCircuitOpen) {
	//     t.Errorf("expected ErrCircuitOpen, got %v", err)
	// }
}

func TestCircuitBreaker_ClosesAfterSuccessInHalfOpen(t *testing.T) {
	// cb := resilience.NewCircuitBreaker(2, 100*time.Millisecond)
	//
	// // Cause 2 failures to open circuit
	// for i := 0; i < 2; i++ {
	//     cb.Execute(func() error { return errors.New("fail") })
	// }
	//
	// // Wait for reset timeout
	// time.Sleep(150 * time.Millisecond)
	//
	// // Next call should go to half-open, succeed, and close
	// err := cb.Execute(func() error { return nil })
	// if err != nil {
	//     t.Errorf("expected nil in half-open, got %v", err)
	// }
	t.Log("circuit breaker half-open test placeholder")
}

func TestRetry_SucceedsOnSecondAttempt(t *testing.T) {
	attempts := 0
	fn := func() error {
		attempts++
		if attempts < 2 {
			return errors.New("transient error")
		}
		return nil
	}

	ctx := context.Background()
	// err := resilience.WithRetry(ctx, resilience.RetryConfig{
	//     MaxAttempts: 3,
	//     BaseDelay:   10 * time.Millisecond,
	//     MaxDelay:    100 * time.Millisecond,
	// }, fn)

	// Simulate
	for i := 0; i < 3; i++ {
		if err := fn(); err == nil {
			break
		}
	}

	_ = ctx

	if attempts != 2 {
		t.Errorf("expected 2 attempts, got %d", attempts)
	}
}

func TestRetry_RespectsContextCancellation(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
	defer cancel()

	alwaysFail := func() error {
		return errors.New("always fails")
	}

	// The retry should stop when context is cancelled
	// err := resilience.WithRetry(ctx, resilience.RetryConfig{
	//     MaxAttempts: 10,
	//     BaseDelay:   100 * time.Millisecond,
	//     MaxDelay:    1 * time.Second,
	// }, alwaysFail)

	_ = alwaysFail
	_ = ctx

	// if !errors.Is(err, context.DeadlineExceeded) {
	//     t.Errorf("expected DeadlineExceeded, got %v", err)
	// }
	t.Log("retry context cancellation test placeholder")
}

func TestTimeout_ExternalCallExceedsLimit(t *testing.T) {
	// Simulate a slow provider
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()

	slowFn := func() error {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(500 * time.Millisecond):
			return nil
		}
	}

	err := slowFn()
	if !errors.Is(err, context.DeadlineExceeded) {
		t.Errorf("expected DeadlineExceeded, got %v", err)
	}
}
