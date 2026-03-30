package sender

import (
	"context"
	"fmt"
	"log/slog"
	"time"
	// "github.com/333-333-333/bastet/api/notification/internal/notification/domain"
	// "github.com/333-333-333/bastet/api/notification/internal/shared/resilience"
)

// ResilientSender wraps a NotificationSender with circuit breaker, retry, and timeout.
// Use this to wrap real provider senders (FCM, SendGrid, Twilio).
//
// Usage in composition root:
//
//	fcmSender := sender.NewFCMSender(fcmClient)
//	resilientFCM := sender.NewResilientSender(fcmSender, logger, sender.ResilientConfig{
//	    Timeout:          5 * time.Second,
//	    MaxFailures:      5,
//	    ResetTimeout:     30 * time.Second,
//	    RetryMaxAttempts: 3,
//	    RetryBaseDelay:   100 * time.Millisecond,
//	})

// ResilientConfig holds configuration for the resilient sender wrapper.
type ResilientConfig struct {
	Timeout          time.Duration // Per-call timeout
	MaxFailures      int           // Circuit breaker: failures before opening
	ResetTimeout     time.Duration // Circuit breaker: wait before half-open
	RetryMaxAttempts int           // Retry: max attempts
	RetryBaseDelay   time.Duration // Retry: initial delay
}

// DefaultResilientConfig returns production-ready defaults.
func DefaultResilientConfig() ResilientConfig {
	return ResilientConfig{
		Timeout:          5 * time.Second,
		MaxFailures:      5,
		ResetTimeout:     30 * time.Second,
		RetryMaxAttempts: 3,
		RetryBaseDelay:   100 * time.Millisecond,
	}
}

// Example: how to wrap a sender
//
// type ResilientSender struct {
//     inner   domain.NotificationSender
//     cb      *resilience.CircuitBreaker
//     retry   resilience.RetryConfig
//     timeout time.Duration
//     logger  *slog.Logger
// }
//
// func (s *ResilientSender) Send(ctx context.Context, n *domain.Notification) error {
//     return s.cb.Execute(func() error {
//         return resilience.WithRetry(ctx, s.retry, func() error {
//             callCtx, cancel := context.WithTimeout(ctx, s.timeout)
//             defer cancel()
//             return s.inner.Send(callCtx, n)
//         })
//     })
// }
//
// func (s *ResilientSender) Channel() domain.Channel {
//     return s.inner.Channel()
// }

// Placeholder to make the file valid Go.
func init() {
	_ = slog.Default()
	_ = fmt.Sprintf
	_ = time.Second
}
