# UCP Type Catalog

Complete catalog of reusable types in `source/schemas/shopping/types/`.

## Money & Currency

### money.json
Represents monetary amounts with currency.

```json
{
  "type": "object",
  "properties": {
    "amount": { "type": "string", "pattern": "^-?\\d+(\\.\\d{2})?$" },
    "currency": { "type": "string", "pattern": "^[A-Z]{3}$" }
  },
  "required": ["amount", "currency"]
}
```

**Usage:** Prices, totals, discounts, taxes

## Address

### address.json
Postal address for shipping and billing.

```json
{
  "type": "object",
  "properties": {
    "line1": { "type": "string" },
    "line2": { "type": "string" },
    "city": { "type": "string" },
    "state": { "type": "string" },
    "postal_code": { "type": "string" },
    "country": { "type": "string", "pattern": "^[A-Z]{2}$" }
  },
  "required": ["line1", "city", "country"]
}
```

**Usage:** Shipping addresses, billing addresses

## Product Types

### product-variant.json
Product variant with SKU and options.

**Properties:**
- `id`: Variant identifier
- `sku`: Stock keeping unit
- `title`: Variant title
- `price`: Reference to money.json
- `available`: Boolean availability
- `options`: Array of selected options

### product-option.json
Product option (size, color, etc.).

**Properties:**
- `name`: Option name (e.g., "Size")
- `value`: Selected value (e.g., "Large")

### inventory.json
Stock level information.

**Properties:**
- `quantity`: Available quantity
- `location`: Warehouse/store location
- `reserved`: Reserved quantity

## Order Types

### line-item.json
Order line item.

**Properties:**
- `id`: Line item ID
- `product_id`: Reference to product
- `variant_id`: Reference to variant
- `quantity`: Item quantity
- `price`: Unit price (money.json)
- `total`: Line total (money.json)
- `discounts`: Applied discounts

### discount.json
Discount applied to order or item.

**Properties:**
- `id`: Discount ID
- `code`: Discount code
- `type`: "percentage" | "fixed_amount"
- `value`: Discount value
- `description`: Human-readable description

### shipping-rate.json
Shipping rate option.

**Properties:**
- `id`: Rate ID
- `carrier`: Shipping carrier
- `service`: Service level
- `price`: Shipping cost (money.json)
- `estimated_days`: Delivery estimate

## Customer Types

### customer.json
Customer information.

**Properties:**
- `id`: Customer ID
- `email`: Email address
- `first_name`: First name
- `last_name`: Last name
- `phone`: Phone number
- `addresses`: Array of addresses

### payment-method.json
Saved payment method.

**Properties:**
- `id`: Payment method ID
- `type`: "card" | "bank" | "wallet"
- `last_four`: Last 4 digits
- `brand`: Card brand
- `expiry`: Expiration date

## Pagination

### pagination.json
Pagination metadata for list responses.

**Properties:**
- `total`: Total items
- `page`: Current page
- `per_page`: Items per page
- `has_next`: More pages available
- `has_prev`: Previous pages available
- `cursor`: Cursor for cursor-based pagination

## Error Handling

### error.json
Error response structure.

**Properties:**
- `code`: Error code
- `message`: Human-readable message
- `details`: Additional error details
- `field`: Field that caused error (validation)
