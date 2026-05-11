# Square Routing Reference

**App name:** `squareup`
**Base URL proxied:** `connect.squareup.com`

## API Path Pattern

```
/squareup/v2/{resource}
```

## Common Endpoints

### Locations

#### List Locations
```bash
GET /squareup/v2/locations
```

#### Get Location
```bash
GET /squareup/v2/locations/{location_id}
```

#### Create Location
```bash
POST /squareup/v2/locations
Content-Type: application/json

{
  "location": {
    "name": "New Location",
    "address": {...}
  }
}
```

### Merchants

#### Get Current Merchant
```bash
GET /squareup/v2/merchants/me
```

### Payments

#### List Payments
```bash
GET /squareup/v2/payments
GET /squareup/v2/payments?location_id={location_id}&begin_time=2026-01-01T00:00:00Z
```

#### Get Payment
```bash
GET /squareup/v2/payments/{payment_id}
```

#### Create Payment
```bash
POST /squareup/v2/payments
Content-Type: application/json

{
  "source_id": "cnon:card-nonce-ok",
  "idempotency_key": "unique-key",
  "amount_money": {"amount": 1000, "currency": "USD"},
  "location_id": "{location_id}"
}
```

#### Complete Payment
```bash
POST /squareup/v2/payments/{payment_id}/complete
```

#### Cancel Payment
```bash
POST /squareup/v2/payments/{payment_id}/cancel
```

### Refunds

#### List Refunds
```bash
GET /squareup/v2/refunds
```

#### Create Refund
```bash
POST /squareup/v2/refunds
Content-Type: application/json

{
  "idempotency_key": "unique-key",
  "payment_id": "{payment_id}",
  "amount_money": {"amount": 500, "currency": "USD"}
}
```

### Customers

#### List Customers
```bash
GET /squareup/v2/customers
```

#### Get Customer
```bash
GET /squareup/v2/customers/{customer_id}
```

#### Create Customer
```bash
POST /squareup/v2/customers
Content-Type: application/json

{
  "given_name": "John",
  "family_name": "Doe",
  "email_address": "john@example.com"
}
```

#### Search Customers
```bash
POST /squareup/v2/customers/search
Content-Type: application/json

{
  "query": {"filter": {"email_address": {"exact": "john@example.com"}}}
}
```

### Orders

#### Create Order
```bash
POST /squareup/v2/orders
Content-Type: application/json

{
  "order": {
    "location_id": "{location_id}",
    "line_items": [{"name": "Item", "quantity": "1", "base_price_money": {"amount": 1000, "currency": "USD"}}]
  },
  "idempotency_key": "unique-key"
}
```

#### Search Orders
```bash
POST /squareup/v2/orders/search
Content-Type: application/json

{
  "location_ids": ["{location_id}"]
}
```

### Catalog

#### List Catalog
```bash
GET /squareup/v2/catalog/list
GET /squareup/v2/catalog/list?types=ITEM,CATEGORY
```

#### Get Catalog Object
```bash
GET /squareup/v2/catalog/object/{object_id}
```

#### Upsert Catalog Object
```bash
POST /squareup/v2/catalog/object
Content-Type: application/json

{
  "idempotency_key": "unique-key",
  "object": {"type": "ITEM", "id": "#new-item", "item_data": {"name": "Coffee"}}
}
```

#### Search Catalog
```bash
POST /squareup/v2/catalog/search
Content-Type: application/json

{
  "object_types": ["ITEM"],
  "query": {"text_query": {"keywords": ["coffee"]}}
}
```

### Inventory

#### Get Inventory Count
```bash
GET /squareup/v2/inventory/{catalog_object_id}
```

#### Batch Change Inventory
```bash
POST /squareup/v2/inventory/changes/batch-create
Content-Type: application/json

{
  "idempotency_key": "unique-key",
  "changes": [...]
}
```

### Invoices

#### List Invoices
```bash
GET /squareup/v2/invoices?location_id={location_id}
```

#### Create Invoice
```bash
POST /squareup/v2/invoices
Content-Type: application/json

{
  "invoice": {
    "location_id": "{location_id}",
    "order_id": "{order_id}",
    "primary_recipient": {"customer_id": "{customer_id}"},
    "payment_requests": [{"request_type": "BALANCE", "due_date": "2026-02-15"}]
  },
  "idempotency_key": "unique-key"
}
```

#### Publish Invoice
```bash
POST /squareup/v2/invoices/{invoice_id}/publish
Content-Type: application/json

{"version": 1, "idempotency_key": "unique-key"}
```

## Notes

- All amounts are in smallest currency unit (cents for USD: 1000 = $10.00)
- Most write operations require an `idempotency_key`
- Cursor-based pagination: use `cursor` parameter with value from response
- Timestamps are ISO 8601 format
- Some endpoints require specific OAuth scopes (CUSTOMERS_READ, ORDERS_READ, ITEMS_READ, INVOICES_READ, etc.)

## Resources

- [Square API Overview](https://developer.squareup.com/docs)
- [Square API Reference](https://developer.squareup.com/reference/square)
- [Payments API](https://developer.squareup.com/reference/square/payments-api)
- [Customers API](https://developer.squareup.com/reference/square/customers-api)
- [Orders API](https://developer.squareup.com/reference/square/orders-api)
- [Catalog API](https://developer.squareup.com/reference/square/catalog-api)
- [Inventory API](https://developer.squareup.com/reference/square/inventory-api)
- [Invoices API](https://developer.squareup.com/reference/square/invoices-api)
