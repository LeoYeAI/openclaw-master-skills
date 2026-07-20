---
name: stripe
description: |
  Stripe API integration with managed OAuth. Manage customers, subscriptions, invoices, products, prices, and payments.
  Use this skill when users want to process payments, manage billing, or handle subscriptions with Stripe.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Stripe

Access the Stripe API with managed OAuth authentication. Manage customers, subscriptions, invoices, products, prices, and process payments.

## Quick Start

```bash
# List customers
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/stripe/v1/customers?limit=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/stripe/{native-api-path}
```

Replace `{native-api-path}` with the actual Stripe API endpoint path. The gateway proxies requests to `api.stripe.com` and automatically injects your OAuth token.

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

Manage your Stripe OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=stripe&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'stripe'}).encode()
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
    "connection_id": "c3c82a73-4c86-4c73-8ebd-1f325212fde6",
    "status": "ACTIVE",
    "creation_time": "2026-02-01T06:04:02.431819Z",
    "last_updated_time": "2026-02-10T22:40:01.061825Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "stripe",
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

If you have multiple Stripe connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/stripe/v1/customers')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'c3c82a73-4c86-4c73-8ebd-1f325212fde6')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

All Stripe API endpoints follow this pattern:

```
/stripe/v1/{resource}
```

---

## Balance

### Get Balance

```bash
GET /stripe/v1/balance
```

**Response:**
```json
{
  "object": "balance",
  "available": [
    {
      "amount": 0,
      "currency": "usd",
      "source_types": {"card": 0}
    }
  ],
  "pending": [
    {
      "amount": 5000,
      "currency": "usd",
      "source_types": {"card": 5000}
    }
  ]
}
```

### List Balance Transactions

```bash
GET /stripe/v1/balance_transactions?limit=10
```

---

## Customers

### List Customers

```bash
GET /stripe/v1/customers?limit=10
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| `limit` | Number of results (1-100, default: 10) |
| `starting_after` | Cursor for pagination |
| `ending_before` | Cursor for reverse pagination |
| `email` | Filter by email |
| `created` | Filter by creation date |

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "cus_TxKtN8Irvzx9BQ",
      "object": "customer",
      "email": "customer@example.com",
      "name": null,
      "balance": 0,
      "currency": "usd",
      "created": 1770765579,
      "metadata": {}
    }
  ],
  "has_more": true,
  "url": "/v1/customers"
}
```

### Get Customer

```bash
GET /stripe/v1/customers/{customer_id}
```

### Create Customer

```bash
POST /stripe/v1/customers
Content-Type: application/x-www-form-urlencoded

email=customer@example.com&name=John%20Doe&metadata[user_id]=123
```

### Update Customer

```bash
POST /stripe/v1/customers/{customer_id}
Content-Type: application/x-www-form-urlencoded

name=Jane%20Doe&email=jane@example.com
```

### Delete Customer

```bash
DELETE /stripe/v1/customers/{customer_id}
```

---

## Products

### List Products

```bash
GET /stripe/v1/products?limit=10
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| `active` | Filter by active status |
| `type` | Filter by type: `good` or `service` |

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "prod_TthCLBwTIXuzEw",
      "object": "product",
      "active": true,
      "name": "Premium Plan",
      "description": "Premium subscription",
      "type": "service",
      "created": 1769926024,
      "metadata": {}
    }
  ],
  "has_more": true
}
```

### Get Product

```bash
GET /stripe/v1/products/{product_id}
```

### Create Product

```bash
POST /stripe/v1/products
Content-Type: application/x-www-form-urlencoded

name=Premium%20Plan&description=Premium%20subscription&type=service
```

### Update Product

```bash
POST /stripe/v1/products/{product_id}
Content-Type: application/x-www-form-urlencoded

name=Updated%20Plan&active=true
```

### Delete Product

```bash
DELETE /stripe/v1/products/{product_id}
```

---

## Prices

### List Prices

```bash
GET /stripe/v1/prices?limit=10
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| `active` | Filter by active status |
| `product` | Filter by product ID |
| `type` | Filter: `one_time` or `recurring` |
| `currency` | Filter by currency |

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "price_1SvtoVDfFKJhF88gKJv2eSmO",
      "object": "price",
      "active": true,
      "currency": "usd",
      "product": "prod_TthCLBwTIXuzEw",
      "unit_amount": 1999,
      "recurring": {
        "interval": "month",
        "interval_count": 1
      },
      "type": "recurring"
    }
  ],
  "has_more": true
}
```

### Get Price

```bash
GET /stripe/v1/prices/{price_id}
```

### Create Price

```bash
POST /stripe/v1/prices
Content-Type: application/x-www-form-urlencoded

product=prod_XXX&unit_amount=1999&currency=usd&recurring[interval]=month
```

### Update Price

```bash
POST /stripe/v1/prices/{price_id}
Content-Type: application/x-www-form-urlencoded

active=false
```

---

## Subscriptions

### List Subscriptions

```bash
GET /stripe/v1/subscriptions?limit=10
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| `customer` | Filter by customer ID |
| `price` | Filter by price ID |
| `status` | Filter: `active`, `canceled`, `past_due`, etc. |

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "sub_1SzQDXDfFKJhF88gf72x6tDh",
      "object": "subscription",
      "customer": "cus_TxKtN8Irvzx9BQ",
      "status": "active",
      "current_period_start": 1770765579,
      "current_period_end": 1773184779,
      "items": {
        "data": [
          {
            "id": "si_TxKtFWxlUW50cR",
            "price": {
              "id": "price_1RGbXsDfFKJhF88gMIShAq9m",
              "unit_amount": 0
            },
            "quantity": 1
          }
        ]
      }
    }
  ],
  "has_more": true
}
```

### Get Subscription

```bash
GET /stripe/v1/subscriptions/{subscription_id}
```

### Create Subscription

```bash
POST /stripe/v1/subscriptions
Content-Type: application/x-www-form-urlencoded

customer=cus_XXX&items[0][price]=price_XXX
```

### Update Subscription

```bash
POST /stripe/v1/subscriptions/{subscription_id}
Content-Type: application/x-www-form-urlencoded

items[0][id]=si_XXX&items[0][price]=price_YYY
```

### Cancel Subscription

```bash
DELETE /stripe/v1/subscriptions/{subscription_id}
```

---

## Invoices

### List Invoices

```bash
GET /stripe/v1/invoices?limit=10
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| `customer` | Filter by customer ID |
| `subscription` | Filter by subscription ID |
| `status` | Filter: `draft`, `open`, `paid`, `void`, `uncollectible` |

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "in_1SzQDXDfFKJhF88g3nh4u2GS",
      "object": "invoice",
      "customer": "cus_TxKtN8Irvzx9BQ",
      "amount_due": 0,
      "amount_paid": 0,
      "currency": "usd",
      "status": "paid",
      "subscription": "sub_1SzQDXDfFKJhF88gf72x6tDh",
      "hosted_invoice_url": "https://invoice.stripe.com/...",
      "invoice_pdf": "https://pay.stripe.com/invoice/.../pdf"
    }
  ],
  "has_more": true
}
```

### Get Invoice

```bash
GET /stripe/v1/invoices/{invoice_id}
```

### Create Invoice

```bash
POST /stripe/v1/invoices
Content-Type: application/x-www-form-urlencoded

customer=cus_XXX
```

### Finalize Invoice

```bash
POST /stripe/v1/invoices/{invoice_id}/finalize
```

### Pay Invoice

```bash
POST /stripe/v1/invoices/{invoice_id}/pay
```

### Void Invoice

```bash
POST /stripe/v1/invoices/{invoice_id}/void
```

---

## Charges

### List Charges

```bash
GET /stripe/v1/charges?limit=10
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| `customer` | Filter by customer ID |
| `payment_intent` | Filter by payment intent |

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "ch_3SyXBvDfFKJhF88g1MHtT45f",
      "object": "charge",
      "amount": 5000,
      "currency": "usd",
      "customer": "cus_TuZ7GIjeZQOQ2m",
      "paid": true,
      "status": "succeeded",
      "payment_method_details": {
        "card": {
          "brand": "mastercard",
          "last4": "0833"
        },
        "type": "card"
      }
    }
  ],
  "has_more": true
}
```

### Get Charge

```bash
GET /stripe/v1/charges/{charge_id}
```

### Create Charge

```bash
POST /stripe/v1/charges
Content-Type: application/x-www-form-urlencoded

amount=2000&currency=usd&source=tok_XXX
```

---

## Payment Intents

### List Payment Intents

```bash
GET /stripe/v1/payment_intents?limit=10
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "pi_3SyXBvDfFKJhF88g17PeHdpE",
      "object": "payment_intent",
      "amount": 5000,
      "currency": "usd",
      "customer": "cus_TuZ7GIjeZQOQ2m",
      "status": "succeeded",
      "payment_method": "pm_1SyXBpDfFKJhF88gmP3IjC8C"
    }
  ],
  "has_more": true
}
```

### Get Payment Intent

```bash
GET /stripe/v1/payment_intents/{payment_intent_id}
```

### Create Payment Intent

```bash
POST /stripe/v1/payment_intents
Content-Type: application/x-www-form-urlencoded

amount=2000&currency=usd&customer=cus_XXX&payment_method_types[]=card
```

### Confirm Payment Intent

```bash
POST /stripe/v1/payment_intents/{payment_intent_id}/confirm
```

### Cancel Payment Intent

```bash
POST /stripe/v1/payment_intents/{payment_intent_id}/cancel
```

---

## Payment Methods

### List Payment Methods

```bash
GET /stripe/v1/payment_methods?customer=cus_XXX&type=card
```

### Get Payment Method

```bash
GET /stripe/v1/payment_methods/{payment_method_id}
```

### Attach Payment Method

```bash
POST /stripe/v1/payment_methods/{payment_method_id}/attach
Content-Type: application/x-www-form-urlencoded

customer=cus_XXX
```

### Detach Payment Method

```bash
POST /stripe/v1/payment_methods/{payment_method_id}/detach
```

---

## Coupons

### List Coupons

```bash
GET /stripe/v1/coupons?limit=10
```

### Get Coupon

```bash
GET /stripe/v1/coupons/{coupon_id}
```

### Create Coupon

```bash
POST /stripe/v1/coupons
Content-Type: application/x-www-form-urlencoded

percent_off=25&duration=once
```

### Delete Coupon

```bash
DELETE /stripe/v1/coupons/{coupon_id}
```

---

## Refunds

### List Refunds

```bash
GET /stripe/v1/refunds?limit=10
```

### Get Refund

```bash
GET /stripe/v1/refunds/{refund_id}
```

### Create Refund

```bash
POST /stripe/v1/refunds
Content-Type: application/x-www-form-urlencoded

charge=ch_XXX&amount=1000
```

---

## Pagination

Stripe uses cursor-based pagination with `starting_after` and `ending_before`:

```bash
GET /stripe/v1/customers?limit=10&starting_after=cus_XXX
```

**Response includes:**
```json
{
  "object": "list",
  "data": [...],
  "has_more": true,
  "url": "/v1/customers"
}
```

Use the last item's ID as `starting_after` for the next page.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/stripe/v1/customers?limit=10',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.data);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/stripe/v1/customers',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'limit': 10}
)
data = response.json()
for customer in data['data']:
    print(f"{customer['id']}: {customer['email']}")
```

## Notes

- Stripe API uses `application/x-www-form-urlencoded` for POST requests (not JSON)
- Amounts are in the smallest currency unit (e.g., cents for USD)
- IDs start with prefixes: `cus_` (customers), `prod_` (products), `price_` (prices), `sub_` (subscriptions), `in_` (invoices), `ch_` (charges), `pi_` (payment intents)
- Timestamps are Unix timestamps
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or invalid parameters |
| 401 | Invalid or missing Maton API key |
| 402 | Card declined or payment required |
| 404 | Resource not found |
| 429 | Rate limited |
| 500 | Stripe internal error |

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

1. Ensure your URL path starts with `stripe`. For example:

- Correct: `https://gateway.maton.ai/stripe/v1/customers`
- Incorrect: `https://gateway.maton.ai/v1/customers`

## Resources

- [Stripe API Reference](https://docs.stripe.com/api)
- [Stripe Dashboard](https://dashboard.stripe.com/)
- [Stripe Testing](https://docs.stripe.com/testing)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
