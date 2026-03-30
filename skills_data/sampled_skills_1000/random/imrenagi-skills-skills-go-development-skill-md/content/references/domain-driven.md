---
title: Favor Rich Domain Models
impact: HIGH
impactDescription: Encourages encapsulation of business logic within domain entities, preventing anemic models and improving maintainability.
tags: architecture, ddd, go-patterns
---

## Favor Rich Domain Models

**Impact: HIGH**

Internal implementations should be driven by business logic (Domain-Driven Design). Avoid creating "Anemic Domain Models" where structs are mere data containers and logic is scattered across various service layers. Instead, strive for **Rich Domain Models** where entities encapsulate both data and the behaviors that operate on that data.

### Implement Rich Models

Rich models encapsulate their behavior and enforce business rules (invariants) through well-defined methods. This ensures that an entity is always in a valid state.

To facilitate easy data mapping during queries (e.g., when loading from a database), **export important variables by default** (including status). Reserve private fields for internal behavior handlers or complex state logic that shouldn't be exposed or manipulated directly.

**Correct (Rich Domain Model with Behavioral State):**

```go
type Order struct {
    ID     string // Exported for easy mapping/querying
    Items  []Item // Exported for easy mapping/querying
    Status string // Exported for easy mapping/querying

    state orderState // Private interface defining behavioral logic
}

type orderState interface {
    AddItem(o *Order, item Item) error
    Complete(o *Order) error
}

// NewOrder is a factory that ensures valid initial state and behavior
func NewOrder(id string) *Order {
    o := &Order{
        ID:     id,
        Status: "pending",
        Items:  []Item{},
    }
    o.state = &pendingState{} // Initialize with specific behavioral logic
    return o
}

// Complete delegates behavior to the internal state handler
func (o *Order) Complete() error {
    return o.state.Complete(o)
}

// AddItem delegates behavior to the internal state handler
func (o *Order) AddItem(item Item) error {
    return o.state.AddItem(o, item)
}
```

### Define Domain Enums

Go does not have a native `enum` type. To implement enums in the domain layer, use a custom defined type based on `int` combined with `const` and `iota`. This provides type safety and allows validation behavior directly on the enum type.

```go
type OrderStatus int

const (
    OrderStatusUnknown OrderStatus = iota // Zero-value catches uninitialized states
    OrderStatusPending
    OrderStatusProcessing
    OrderStatusCompleted
    OrderStatusCancelled
)

// IsValid checks if the enum value is within the allowed set
func (s OrderStatus) IsValid() bool {
    return s > OrderStatusUnknown && s <= OrderStatusCancelled
}

// ToProto converts the domain enum to the generated gRPC status enum
func (s OrderStatus) ToProto() pb.OrderStatus {
    switch s {
    case OrderStatusPending:
        return pb.OrderStatus_ORDER_STATUS_PENDING
    // ... other cases
    default:
        return pb.OrderStatus_ORDER_STATUS_UNSPECIFIED
    }
}
```

**Key Practices:**

- **Use `iota` for Integers**: Prefer integer-based enums with `iota` for internal logic as they are more efficient.
- **Zero-Value is Unknown**: Always define the `0` value as `Unknown` or `Unspecified`.
- **Encapsulate Validation**: Use an `IsValid()` method before performing logic that depends on the enum value.
- **Avoid Naked Strings**: Never use raw strings (e.g., `"pending"`) for status or types in your business logic.
- **Favor gRPC Conversion**: Implement `ToProto`/`FromProto` methods to maintain type safety across the API boundary.

### Best Practices

1.  **Selective Encapsulation**: Export fields that are primarily data containers for easy persistence mapping. Use private fields for sensitive internal state or state that requires complex validation during transitions.
2.  **Ensure Invariants**: Every method on a domain entity should leave the entity in a valid state. If an action would violate a business rule, return a domain error (refer to [Define and Return Domain Errors](error-domain-error.md)).
3.  **Constructors (Factories)**: Use constructor functions (e.g., `NewUser`, `NewOrder`) to ensure that entities are created with all required data and in a valid initial state.
4.  **Behavior Over Data**: When adding a feature, ask: "Which domain object's responsibility is this?" before automatically putting it in a Service.
5.  **Ubiquitous Language**: Use method names that reflect the business language (e.g., `DeactivateUser()` instead of `SetDeleted(true)`).

### References

- [Define and Return Domain Errors](error-domain-error.md)
- [Martin Fowler: Anemic Domain Model](https://martinfowler.com/bliki/AnemicDomainModel.html)
- [Domain-Driven Design: Tackling Complexity in the Heart of Software by Eric Evans](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)
