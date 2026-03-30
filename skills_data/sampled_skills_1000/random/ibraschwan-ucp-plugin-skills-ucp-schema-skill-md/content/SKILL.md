---
name: UCP Schema Design
description: This skill should be used when the user asks to "create a UCP schema", "design a new capability", "add a schema type", "define request/response schemas", "work with UCP annotations", or mentions JSON Schema for UCP. Provides guidance on UCP schema patterns, annotations, and validation rules.
version: 1.0.0
---

# UCP Schema Design

## Overview

This skill provides guidance for designing schemas in the Universal Commerce Protocol (UCP). UCP uses JSON Schema (Draft 2020-12) with custom annotations to define capability request/response structures.

## Schema Location

All source schemas reside in:
```
source/schemas/shopping/
├── checkout.json
├── order.json
├── payment.json
├── product.json
├── cart.json
├── customer.json
├── fulfillment.json
└── types/          # 35+ reusable type definitions
```

## UCP Schema Annotations

UCP extends JSON Schema with these annotations:

| Annotation | Purpose | Example |
|------------|---------|---------|
| `ucp_request` | Marks request schema for a method | `"ucp_request": "shopping.cart.create"` |
| `ucp_response` | Marks response schema for a method | `"ucp_response": "shopping.cart.create"` |
| `ucp_shared_request` | Shared request schema for multiple methods | `"ucp_shared_request": ["method1", "method2"]` |
| `ucp_core` | Core protocol field (not capability-specific) | `"ucp_core": true` |

## Schema Structure Pattern

Follow this pattern for capability schemas:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ucp.dev/schemas/shopping/capability-name.json",
  "title": "Capability Name Schemas",
  "description": "Request and response schemas for capability operations",
  "$defs": {
    "MethodNameRequest": {
      "type": "object",
      "ucp_request": "shopping.capability.method",
      "properties": {
        "required_field": { "type": "string" },
        "optional_field": { "$ref": "types/common-type.json" }
      },
      "required": ["required_field"]
    },
    "MethodNameResponse": {
      "type": "object",
      "ucp_response": "shopping.capability.method",
      "properties": {
        "result": { "$ref": "types/result-type.json" }
      },
      "required": ["result"]
    }
  }
}
```

## Type References

Reference reusable types from `types/` directory:

```json
{ "$ref": "types/money.json" }
{ "$ref": "types/address.json" }
{ "$ref": "types/product-variant.json" }
```

Available types include: `money.json`, `address.json`, `product-variant.json`, `line-item.json`, `discount.json`, `shipping-rate.json`, and 30+ more.

## Validation Rules

1. **$id required** - Every schema file must have unique `$id`
2. **Annotations required** - Request/response schemas must have `ucp_request` or `ucp_response`
3. **References valid** - All `$ref` must resolve to existing files
4. **Draft 2020-12** - Must use JSON Schema Draft 2020-12
5. **Naming convention** - Use PascalCase for definition names, dot notation for methods

## Creating New Schemas

To create a new capability schema:

1. Create file in `source/schemas/shopping/`
2. Add `$schema` and `$id` headers
3. Define request schemas with `ucp_request` annotation
4. Define response schemas with `ucp_response` annotation
5. Reference types from `types/` directory
6. Run validation: `python scripts/validate_specs.py`
7. Generate outputs: `python scripts/generate_schemas.py`

## Common Patterns

### Paginated Response
```json
{
  "items": { "type": "array", "items": { "$ref": "types/item.json" } },
  "pagination": { "$ref": "types/pagination.json" }
}
```

### Error Response
```json
{
  "error": { "$ref": "types/error.json" },
  "details": { "type": "object" }
}
```

### Optional ID Field
```json
{
  "id": { "type": "string", "format": "uuid" }
}
```

## Additional Resources

### Reference Files

For detailed patterns and type documentation:
- **`references/type-catalog.md`** - Complete catalog of reusable types
- **`references/annotation-guide.md`** - UCP annotation usage guide

### Examples

- **`examples/capability-template.json`** - Template for new capabilities
- **`examples/cart-schema.json`** - Real cart capability example
