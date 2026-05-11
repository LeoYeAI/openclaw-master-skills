# Crossmint Wallet — Purchase Guide

Companion to [skill.md](https://creditclaw.com/skill.md). Covers how to make purchases using the Crossmint Wallet for supported merchants.

**Prerequisite:** Your owner must have set up a Crossmint Wallet for you. Check `GET /bot/status` first.

> **Draft — this file is not yet listed in the skill manifest.**

---

## How It Works

The Crossmint Wallet uses Crossmint's infrastructure to hold funds and execute purchases on your behalf. When you submit a purchase request, CreditClaw routes the order through Crossmint and places a real order with the merchant.

**Endpoint:** `POST /card-wallet/bot/purchase`

---

## Supported Merchants

| Merchant | Product ID Format | Variant Lookup | Order Tracking |
|----------|------------------|----------------|----------------|
| Amazon | ASIN (e.g. `B01DFKC2SO`) | Not needed | Full (carrier, tracking number, URL, ETA) |
| Shopify | `{product_url}:{variant_id}` | Required | Order placed only |
| URL (any store) | `{url}:default` | Not needed | Order placed only |

---

## Purchase Request

```bash
curl -X POST https://creditclaw.com/api/v1/card-wallet/bot/purchase \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant": "amazon",
    "product_id": "B0EXAMPLE123",
    "quantity": 1,
    "product_name": "Wireless Mouse",
    "estimated_price_usd": 29.99,
    "shipping_address": {
      "name": "Jane Smith",
      "line1": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94111",
      "country": "US"
    }
  }'
```

### Request Fields

| Field | Required | Notes |
|-------|----------|-------|
| `merchant` | Yes | `amazon`, `shopify`, or `url` |
| `product_id` | Yes | Format depends on merchant (see Supported Merchants table) |
| `quantity` | Yes | 1–100 |
| `product_name` | Yes | Human-readable name for approval screen |
| `estimated_price_usd` | Yes | Best estimate — actual charge may differ slightly |
| `shipping_address` | Yes | US addresses only. Fields: `name`, `line1`, `line2` (optional), `city`, `state`, `zip`, `country` |

---

## Order Tracking

After a purchase is approved, poll for status updates:

```bash
curl https://creditclaw.com/api/v1/card-wallet/bot/purchase/status?approval_id=X \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

### Order Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Awaiting owner approval |
| `quote` | Pricing the order |
| `processing` | Payment succeeded, order in progress |
| `shipped` | In transit with tracking info (Amazon only) |
| `delivered` | Successfully delivered (Amazon only) |
| `payment_failed` | Payment could not be processed |
| `delivery_failed` | Delivery unsuccessful (Amazon only) |
