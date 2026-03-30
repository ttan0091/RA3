# UCP Annotation Guide

Detailed guide for using UCP-specific JSON Schema annotations.

## Core Annotations

### ucp_request

Marks a schema definition as a request schema for a specific method.

**Format:**
```json
{
  "ucp_request": "domain.capability.method"
}
```

**Example:**
```json
{
  "$defs": {
    "CreateCartRequest": {
      "type": "object",
      "ucp_request": "shopping.cart.create",
      "properties": {
        "customer_id": { "type": "string" }
      }
    }
  }
}
```

**Rules:**
- Must be at definition level (inside `$defs`)
- Method name must follow `domain.capability.action` pattern
- One `ucp_request` per definition
- Must have corresponding `ucp_response` definition

### ucp_response

Marks a schema definition as a response schema for a specific method.

**Format:**
```json
{
  "ucp_response": "domain.capability.method"
}
```

**Example:**
```json
{
  "$defs": {
    "CreateCartResponse": {
      "type": "object",
      "ucp_response": "shopping.cart.create",
      "properties": {
        "cart": { "$ref": "types/cart.json" }
      },
      "required": ["cart"]
    }
  }
}
```

**Rules:**
- Method name must match corresponding `ucp_request`
- Should define the success response structure
- Can reference shared response types

### ucp_shared_request

Marks a schema as shared across multiple methods.

**Format:**
```json
{
  "ucp_shared_request": ["method1", "method2"]
}
```

**Example:**
```json
{
  "$defs": {
    "CartItemRequest": {
      "type": "object",
      "ucp_shared_request": [
        "shopping.cart.add_item",
        "shopping.cart.update_item"
      ],
      "properties": {
        "product_id": { "type": "string" },
        "quantity": { "type": "integer", "minimum": 1 }
      },
      "required": ["product_id", "quantity"]
    }
  }
}
```

**Use cases:**
- Same input structure for create/update operations
- Common request parameters across methods

### ucp_core

Marks a field or schema as part of the core protocol.

**Format:**
```json
{
  "ucp_core": true
}
```

**Example:**
```json
{
  "properties": {
    "request_id": {
      "type": "string",
      "ucp_core": true,
      "description": "Unique request identifier"
    }
  }
}
```

**Use cases:**
- Protocol-level fields (request_id, timestamp)
- Fields present in all requests/responses
- Not capability-specific fields

## Naming Conventions

### Method Names

**Pattern:** `domain.capability.action`

**Components:**
- `domain`: Always "shopping" for commerce operations
- `capability`: The resource (cart, order, product, etc.)
- `action`: The operation (create, get, update, delete, list)

**Standard Actions:**
| Action | Description | Example |
|--------|-------------|---------|
| create | Create new resource | shopping.cart.create |
| get | Get single resource | shopping.order.get |
| update | Update resource | shopping.cart.update |
| delete | Delete resource | shopping.cart.delete |
| list | List resources | shopping.order.list |
| search | Search with filters | shopping.product.search |
| add_item | Add to collection | shopping.cart.add_item |
| remove_item | Remove from collection | shopping.cart.remove_item |

### Definition Names

**Pattern:** `<Action><Resource><Type>`

**Examples:**
- `CreateCartRequest`
- `CreateCartResponse`
- `GetOrderRequest`
- `GetOrderResponse`
- `AddCartItemRequest`
- `ListProductsResponse`

## Validation Rules

1. **Request must have response:** Every `ucp_request` needs matching `ucp_response`
2. **Method names match:** Request and response method names must be identical
3. **Valid method format:** Must be `domain.capability.action`
4. **No duplicate methods:** Each method can only have one request/response pair
5. **Shared request array:** `ucp_shared_request` must be an array of strings

## Best Practices

1. Keep request/response in same file
2. Group related methods in one schema file
3. Use descriptive definition names
4. Reference types instead of duplicating
5. Add descriptions to all annotations
6. Validate after adding annotations
