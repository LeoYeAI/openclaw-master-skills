---
name: squarespace
description: |
  Squarespace Commerce API integration with managed OAuth. Manage products, inventory, orders, customer profiles, and transactions.
  Use this skill when users want to manage e-commerce operations on Squarespace stores.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji:
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Squarespace

Access the Squarespace Commerce API with managed OAuth authentication. Manage products, inventory, orders, customer profiles, and transactions.

## Quick Start

```bash
# List all products (v2 API)
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/squarespace/v2/commerce/products')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('User-Agent', 'MyClaude/1.0')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/squarespace/{native-api-path}
```

Replace `{native-api-path}` with the actual Squarespace API endpoint path. The gateway proxies requests to `api.squarespace.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Squarespace OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=squarespace&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'squarespace'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "squarespace",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Squarespace connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/squarespace/v2/commerce/products')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('User-Agent', 'MyClaude/1.0')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Inventory

#### List All Inventory

```bash
GET /squarespace/1.0/commerce/inventory
```

Query parameters:
- `cursor` (optional): Pagination cursor from previous response

**Response:**
```json
{
  "inventory": [
    {
      "variantId": "5ba1418df4204bb2d21eac3f",
      "sku": "SQ0001",
      "descriptor": "Product Name - Size: Medium",
      "isUnlimited": false,
      "quantity": 25
    }
  ],
  "pagination": {
    "hasNextPage": true,
    "nextPageCursor": "abc123",
    "nextPageUrl": "https://api.squarespace.com/1.0/commerce/inventory?cursor=abc123"
  }
}
```

#### Get Specific Inventory

```bash
GET /squarespace/1.0/commerce/inventory/{variantIds}
```

- `{variantIds}`: Comma-separated variant IDs (max 50)

#### Adjust Stock Quantities

```bash
POST /squarespace/1.0/commerce/inventory/adjustments
Content-Type: application/json
Idempotency-Key: unique-key-here

{
  "incrementOperations": [{"variantId": "variant-id-1", "quantity": 5}],
  "decrementOperations": [{"variantId": "variant-id-2", "quantity": 2}],
  "setFiniteOperations": [{"variantId": "variant-id-3", "quantity": 100}],
  "setUnlimitedOperations": ["variant-id-4"]
}
```

**Response:** 204 No Content on success

---

### Orders

#### List All Orders

```bash
GET /squarespace/1.0/commerce/orders
```

Query parameters:
- `customerId` (optional): Filter by customer ID
- `modifiedAfter` (conditional): ISO 8601 datetime (e.g., `2024-01-01T00:00:00Z`) - required with `modifiedBefore`
- `modifiedBefore` (conditional): ISO 8601 datetime - required with `modifiedAfter`
- `cursor` (optional): Pagination cursor
- `fulfillmentStatus` (optional): `PENDING`, `FULFILLED`, or `CANCELED`

Note: Cannot combine cursor with date range parameters. Date filters must be used together.

**Response:**
```json
{
  "result": [
    {
      "id": "order-id",
      "orderNumber": "1001",
      "createdOn": "2024-01-15T10:30:00Z",
      "modifiedOn": "2024-01-15T12:00:00Z",
      "channel": "web",
      "testmode": false,
      "customerEmail": "customer@example.com",
      "fulfillmentStatus": "PENDING",
      "lineItems": [...],
      "subtotal": {"value": "99.99", "currency": "USD"},
      "shippingTotal": {"value": "9.99", "currency": "USD"},
      "taxTotal": {"value": "8.50", "currency": "USD"},
      "grandTotal": {"value": "118.48", "currency": "USD"}
    }
  ],
  "pagination": {
    "hasNextPage": true,
    "nextPageCursor": "abc123",
    "nextPageUrl": "..."
  }
}
```

#### Get Specific Order

```bash
GET /squarespace/1.0/commerce/orders/{orderId}
```

#### Create Order

```bash
POST /squarespace/1.0/commerce/orders
Content-Type: application/json
Idempotency-Key: unique-key-here

{
  "channelName": "External Store",
  "externalOrderReference": "ORDER-12345",
  "customerEmail": "customer@example.com",
  "lineItems": [
    {
      "lineItemType": "PHYSICAL_PRODUCT",
      "variantId": "variant-id",
      "quantity": 2,
      "unitPricePaid": {"currency": "USD", "value": "29.99"}
    }
  ],
  "subtotal": {"currency": "USD", "value": "59.98"},
  "priceTaxInterpretation": "EXCLUSIVE",
  "grandTotal": {"currency": "USD", "value": "59.98"},
  "createdOn": "2024-01-15T10:30:00Z"
}
```

**Response:** 201 Created with Order object

Note: `subtotal` must equal the sum of `lineItems.unitPricePaid.value * quantity`.

#### Fulfill Order

```bash
POST /squarespace/1.0/commerce/orders/{orderId}/fulfillments
Content-Type: application/json

{
  "shouldSendNotification": true,
  "shipments": [
    {
      "shipDate": "2024-01-16T08:00:00Z",
      "carrierName": "USPS",
      "service": "Priority Mail",
      "trackingNumber": "9400111899223456789012",
      "trackingUrl": "https://tools.usps.com/go/TrackConfirmAction?tLabels=9400111899223456789012"
    }
  ]
}
```

**Response:** 204 No Content on success

---

### Products

#### List Store Pages

```bash
GET /squarespace/1.0/commerce/store_pages
```

Query parameters:
- `cursor` (optional): Pagination cursor

**Response:**
```json
{
  "storePages": [
    {
      "id": "store-page-id",
      "title": "Main Store",
      "isEnabled": true,
      "urlSlug": "store"
    }
  ],
  "pagination": {...}
}
```

#### List All Products

```bash
GET /squarespace/v2/commerce/products
```

Query parameters:
- `modifiedAfter` (optional): ISO 8601 datetime
- `modifiedBefore` (optional): ISO 8601 datetime
- `type` (optional): Comma-separated types: `PHYSICAL`, `SERVICE`, `GIFT_CARD`, `DIGITAL`
- `cursor` (optional): Pagination cursor

Note: Cannot combine cursor with date/type filters.

**Response:**
```json
{
  "products": [
    {
      "id": "product-id",
      "type": "PHYSICAL",
      "storePageId": "store-page-id",
      "name": "Product Name",
      "description": "<p>HTML description</p>",
      "url": "https://example.squarespace.com/store/product-slug",
      "urlSlug": "product-slug",
      "tags": ["tag1", "tag2"],
      "isVisible": true,
      "variants": [...],
      "images": [...],
      "createdOn": "2024-01-01T00:00:00Z",
      "modifiedOn": "2024-01-15T12:00:00Z"
    }
  ],
  "pagination": {...}
}
```

#### Get Specific Products

```bash
GET /squarespace/v2/commerce/products/{productIds}
```

- `{productIds}`: Comma-separated product IDs (max 50)

#### Create Product

```bash
POST /squarespace/v2/commerce/products
Content-Type: application/json

{
  "type": "PHYSICAL",
  "storePageId": "store-page-id",
  "name": "New Product",
  "description": "<p>Product description</p>",
  "urlSlug": "new-product",
  "tags": ["new", "featured"],
  "isVisible": true,
  "variants": [
    {
      "sku": "SKU-001",
      "pricing": {
        "basePrice": {"currency": "USD", "value": "49.99"}
      },
      "stock": {"quantity": 100, "unlimited": false}
    }
  ]
}
```

**Response:** 201 Created with Product object

#### Update Product

```bash
POST /squarespace/v2/commerce/products/{productId}
Content-Type: application/json

{
  "name": "Updated Product Name",
  "description": "<p>Updated description</p>",
  "isVisible": true,
  "tags": ["updated", "sale"]
}
```

**Response:** 200 OK with Product object

#### Delete Product

```bash
DELETE /squarespace/v2/commerce/products/{productId}
```

**Response:** 204 No Content on success

---

### Product Variants

#### Create Variant

```bash
POST /squarespace/v2/commerce/products/{productId}/variants
Content-Type: application/json

{
  "sku": "SKU-002",
  "pricing": {
    "basePrice": {"currency": "USD", "value": "59.99"},
    "salePrice": {"currency": "USD", "value": "49.99"},
    "onSale": true
  },
  "stock": {"quantity": 50, "unlimited": false},
  "attributes": {"Size": "Large"},
  "shippingMeasurements": {
    "weight": {"unit": "POUND", "value": 1.5},
    "dimensions": {"unit": "INCH", "length": 10, "width": 8, "height": 4}
  }
}
```

**Response:** 201 Created with ProductVariant object

Note: To use `attributes`, the product must first have matching `variantAttributes` set via Update Product (e.g., `"variantAttributes": ["Size"]`).

#### Update Variant

```bash
POST /squarespace/v2/commerce/products/{productId}/variants/{variantId}
Content-Type: application/json

{
  "sku": "SKU-002-UPDATED",
  "pricing": {
    "basePrice": {"currency": "USD", "value": "64.99"},
    "onSale": false
  }
}
```

**Response:** 200 OK with ProductVariant object

Note: Stock and images cannot be updated via this endpoint.

#### Delete Variant

```bash
DELETE /squarespace/v2/commerce/products/{productId}/variants/{variantId}
```

**Response:** 204 No Content on success

Note: Cannot delete the only variant of a product.

---

### Product Images

#### Upload Image

```bash
POST /squarespace/v2/commerce/products/{productId}/images
Content-Type: multipart/form-data

curl "https://gateway.maton.ai/squarespace/v2/commerce/products/{productId}/images" \
  -H "Authorization: Bearer $MATON_API_KEY" \
  -H "User-Agent: MyClaude/1.0" \
  -X POST \
  -F file=@image.png
```

**Response:** 202 Accepted
```json
{
  "imageId": "image-id"
}
```

Requirements:
- Dimensions: less than 60MP
- File types: JPEG, JPG, PNG, GIF
- Max file size: 20MB (under 500KB recommended)
- Max 100 images per product

#### Check Upload Status

```bash
GET /squarespace/v2/commerce/products/{productId}/images/{imageId}/status
```

**Response:**
```json
{
  "status": "PROCESSING"
}
```

Status values: `PROCESSING`, `READY`, `ERROR`

#### Update Image (Alt Text)

```bash
POST /squarespace/v2/commerce/products/{productId}/images/{imageId}
Content-Type: application/json

{
  "altText": "Product image description"
}
```

**Response:** 200 OK with ProductImage object

#### Reorder Image

```bash
POST /squarespace/v2/commerce/products/{productId}/images/{imageId}/order
Content-Type: application/json

{
  "afterImageId": "other-image-id"
}
```

Use `null` for `afterImageId` to move image to the top.

**Response:** 204 No Content

#### Assign Image to Variant

```bash
POST /squarespace/v2/commerce/products/{productId}/variants/{variantId}/image
Content-Type: application/json

{
  "imageId": "image-id"
}
```

Use `null` for `imageId` to remove the image from the variant.

**Response:** 204 No Content

#### Delete Image

```bash
DELETE /squarespace/v2/commerce/products/{productId}/images/{imageId}
```

**Response:** 204 No Content

---

### Profiles (Customers)

#### List All Profiles

```bash
GET /squarespace/1.0/profiles
```

Query parameters:
- `cursor` (optional): Pagination cursor
- `filter` (optional): Semicolon-separated filters (e.g., `isCustomer,true;hasAccount,true`)
- `sortDirection` (optional): `asc` or `dsc` (default: `dsc`)
- `sortField` (optional): `createdOn`, `id`, `email`, or `lastName` (default: `id`)

Filter options:
- `isCustomer,true` or `isCustomer,false`
- `hasAccount,true` or `hasAccount,false`
- `email,customer@example.com`

**Response:**
```json
{
  "profiles": [
    {
      "id": "profile-id",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john@example.com",
      "hasAccount": true,
      "isCustomer": true,
      "createdOn": "2024-01-01T00:00:00Z",
      "address": {
        "address1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "countryCode": "US",
        "postalCode": "10001"
      },
      "acceptsMarketing": true,
      "transactionsSummary": {
        "orderCount": 5,
        "totalOrderAmount": {"value": "499.95", "currency": "USD"}
      }
    }
  ],
  "pagination": {...}
}
```

#### Get Specific Profiles

```bash
GET /squarespace/1.0/profiles/{profileIds}
```

- `{profileIds}`: Comma-separated profile IDs (max 50)

---

### Transactions

#### List All Transactions

```bash
GET /squarespace/1.0/commerce/transactions
```

Query parameters:
- `modifiedAfter` (conditional): ISO 8601 datetime - required with `modifiedBefore`
- `modifiedBefore` (conditional): ISO 8601 datetime - required with `modifiedAfter`
- `cursor` (optional): Pagination cursor

Note: Date filters must be used together (both `modifiedAfter` and `modifiedBefore` are required when filtering by date).

**Response:**
```json
{
  "documents": [
    {
      "id": "document-id",
      "createdOn": "2024-01-15T10:30:00Z",
      "modifiedOn": "2024-01-15T12:00:00Z",
      "customerEmail": "customer@example.com",
      "salesOrderId": "order-id",
      "voided": false,
      "totalSales": {"value": "99.99", "currency": "USD"},
      "totalNetSales": {"value": "99.99", "currency": "USD"},
      "totalTaxes": {"value": "8.50", "currency": "USD"},
      "total": {"value": "108.49", "currency": "USD"},
      "payments": [
        {
          "id": "payment-id",
          "amount": {"value": "108.49", "currency": "USD"},
          "creditCardType": "VISA",
          "provider": "STRIPE",
          "paidOn": "2024-01-15T10:35:00Z"
        }
      ]
    }
  ],
  "pagination": {...}
}
```

#### Get Specific Transactions

```bash
GET /squarespace/1.0/commerce/transactions/{documentIds}
```

- `{documentIds}`: Comma-separated document IDs (max 50)

---

## Pagination

Squarespace uses cursor-based pagination. Response includes:

```json
{
  "pagination": {
    "hasNextPage": true,
    "nextPageCursor": "cursor-value",
    "nextPageUrl": "https://api.squarespace.com/..."
  }
}
```

To get the next page, use the `cursor` parameter:

```bash
GET /squarespace/v2/commerce/products?cursor=cursor-value
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/squarespace/v2/commerce/products',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'User-Agent': 'MyClaude/1.0'
    }
  }
);
const data = await response.json();
console.log(data.products);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/squarespace/v2/commerce/products',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'User-Agent': 'MyClaude/1.0'
    }
)
products = response.json()['products']
```

## Notes

- **Products API uses version `v2`** (e.g., `/squarespace/v2/commerce/products`)
- Store Pages endpoint uses version `1.0` (e.g., `/squarespace/1.0/commerce/store_pages`)
- Inventory, Orders, Profiles, and Transactions APIs use version `1.0`
- All requests require a `User-Agent` header describing your application
- Requests without a custom User-Agent are subject to stricter rate limits
- Maximum 50 items per batch request (inventory, products, profiles, transactions)
- Create Order has a stricter rate limit: 100 requests per hour per website
- Idempotency-Key header is required for stock adjustments and order creation
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Rate Limits

- General: 300 requests per minute (5 per second)
- Create Order: 100 requests per hour per website (with API key auth)
- Exceeding limits returns 429 Too Many Requests with a one-minute cooldown

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Invalid request parameters or missing Squarespace connection |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 405 | Method not allowed for product type |
| 409 | Conflict (duplicate SKU, concurrent modification, etc.) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Squarespace API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

Ensure your URL path starts with `squarespace`. For example:

- Correct: `https://gateway.maton.ai/squarespace/1.0/commerce/products`
- Incorrect: `https://gateway.maton.ai/1.0/commerce/products`

## Resources

- [Squarespace Commerce APIs Overview](https://developers.squarespace.com/commerce-apis/overview)
- [Inventory API](https://developers.squarespace.com/commerce-apis/inventory-overview)
- [Orders API](https://developers.squarespace.com/commerce-apis/orders-overview)
- [Products API](https://developers.squarespace.com/commerce-apis/products-overview)
- [Profiles API](https://developers.squarespace.com/commerce-apis/profiles-overview)
- [Transactions API](https://developers.squarespace.com/commerce-apis/transactions-overview)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
