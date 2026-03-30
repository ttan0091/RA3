package resilience

import (
	"errors"
	"sync"
	"time"
)

// ErrCircuitOpen is returned when the circuit breaker is open and rejecting calls.
var ErrCircuitOpen = errors.New("circuit breaker is open")

// State represents the circuit breaker state.
type State int

const (
	StateClosed   State = iota // Normal operation — calls pass through
	StateOpen                  // Failing — calls rejected immediately
	StateHalfOpen              // Testing — one call allowed to check recovery
)

// CircuitBreaker implements the circuit breaker pattern for external calls.
type CircuitBreaker struct {
	mu            sync.Mutex
	state         State
	failureCount  int
	successCount  int
	maxFailures   int           // Failures before opening
	resetTimeout  time.Duration // How long to wait before half-open
	halfOpenMax   int           // Successes needed to close from half-open
	lastFailureAt time.Time
}

// NewCircuitBreaker creates a circuit breaker with the given configuration.
func NewCircuitBreaker(maxFailures int, resetTimeout time.Duration) *CircuitBreaker {
	return &CircuitBreaker{
		state:        StateClosed,
		maxFailures:  maxFailures,
		resetTimeout: resetTimeout,
		halfOpenMax:  2,
	}
}

// Execute runs the function through the circuit breaker.
// Returns ErrCircuitOpen if the circuit is open.
func (cb *CircuitBreaker) Execute(fn func() error) error {
	cb.mu.Lock()

	switch cb.state {
	case StateOpen:
		if time.Since(cb.lastFailureAt) > cb.resetTimeout {
			cb.state = StateHalfOpen
			cb.successCount = 0
			cb.mu.Unlock()
			return cb.executeAndRecord(fn)
		}
		cb.mu.Unlock()
		return ErrCircuitOpen

	case StateHalfOpen:
		cb.mu.Unlock()
		return cb.executeAndRecord(fn)

	default: // Closed
		cb.mu.Unlock()
		return cb.executeAndRecord(fn)
	}
}

func (cb *CircuitBreaker) executeAndRecord(fn func() error) error {
	err := fn()

	cb.mu.Lock()
	defer cb.mu.Unlock()

	if err != nil {
		cb.failureCount++
		cb.lastFailureAt = time.Now()

		if cb.state == StateHalfOpen || cb.failureCount >= cb.maxFailures {
			cb.state = StateOpen
		}
		return err
	}

	// Success
	if cb.state == StateHalfOpen {
		cb.successCount++
		if cb.successCount >= cb.halfOpenMax {
			cb.state = StateClosed
			cb.failureCount = 0
		}
	} else {
		cb.failureCount = 0
	}

	return nil
}

// State returns the current circuit breaker state.
func (cb *CircuitBreaker) GetState() State {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	return cb.state
}
