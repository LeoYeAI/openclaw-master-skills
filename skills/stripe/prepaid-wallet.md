# Pre-paid Wallet — Day-to-Day Guide

Companion to [skill.md](https://creditclaw.com/creditcard/skill.md). Covers how to make purchases using the Pre-paid Wallet (Rail 2) for Amazon, Shopify, and supported merchants.

**Prerequisite:** Your owner must have set up a Pre-paid Wallet for you. Check `GET /bot/wallet/check` first.

---

## How It Works

The Pre-paid Wallet holds USDC on the Base blockchain. Your owner funds it via fiat onramp (credit card to USDC). When you make a purchase, CreditClaw converts USDC to fiat and places a real order with the merchant on your behalf.

**Use this rail for:** Amazon products, Shopify stores, and other supported merchants.

**Endpoint:** `POST /card-wallet/bot/purchase`

---

## Supported Merchants

| Merchant | Product ID Format | Variant Lookup | Order Tracking |
|----------|------------------|----------------|----------------|
| Amazon | ASIN (e.g. `B01DFKC2SO`) | Not needed | Full (carrier, tracking number, URL, ETA) |
| Shopify | `{product_url}:{variant_id}` | Required | Order placed only |
| URL (any store) | `{url}:default` | Not needed | Order placed only |

For Amazon-specific details (ASIN discovery, restrictions, tracking), see [amazon.md](https://creditclaw.com/creditcard/amazon.md).

---

## Purchase Flow

1. Build your request (see merchant sections below for `product_id` format)
2. `POST /card-wallet/bot/purchase` — returns 202 with `approval_id`, `transaction_id`, and `expires_at`
3. Poll `GET /card-wallet/bot/purchase/status?approval_id=X` every ~30s until `expires_at`
4. Owner has 15 minutes to approve or reject
5. On approval: order is placed, status becomes `processing`
6. Amazon orders progress through `shipped` → `delivered`; others stay at `processing`

### Purchase Request

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
| `product_id` | Yes | Format depends on merchant (see below) |
| `quantity` | Yes | 1–100 |
| `product_name` | Yes | Human-readable name for approval screen |
| `estimated_price_usd` | Yes | Best estimate — actual charge may differ slightly |
| `shipping_address` | Yes | US addresses only. Fields: `name`, `line1`, `line2` (optional), `city`, `state`, `zip`, `country` |

---

## Amazon Purchases

Product ID is the ASIN — no lookup step needed.

```
merchant: "amazon"
product_id: "B0EXAMPLE123"
```

Amazon orders get full tracking: carrier, tracking number, tracking URL, and estimated delivery.

For complete Amazon details (ASIN discovery, product validation, restrictions), see [amazon.md](https://creditclaw.com/creditcard/amazon.md).

---

## Shopify Purchases

**You must look up the variant ID before purchasing.** Shopify products have variants (size, color, etc.) and the system requires a specific variant ID.

### Step 1: Search for Variants

```bash
curl -X POST https://creditclaw.com/api/v1/card-wallet/bot/search \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "product_url": "https://shop.example.com/products/widget" }'
```

Response:
```json
{
  "product_url": "https://shop.example.com/products/widget",
  "product_name": "Widget Pro",
  "variants": [
    {
      "variant_id": "48012345678",
      "title": "Small / Blue",
      "price": "24.99",
      "currency": "USD",
      "available": true
    }
  ],
  "locator_format": "shopify:{product_url}:{variant_id}"
}
```

Pick an available variant, then purchase using the combined locator.

### Step 2: Purchase

```
merchant: "shopify"
product_id: "https://shop.example.com/products/widget:48012345678"
```

No delivery tracking after order is placed.

**Note:** The search API is in beta. It may return inconsistent results or fail for some product URLs.

---

## URL Purchases (Any Store)

For merchants not covered by Amazon or Shopify. Use the full URL as the product identifier.

```
merchant: "url"
product_id: "https://store.example.com/item:default"
```

Use `default` as the variant if the product has no variants. No delivery tracking.

---

## Order Status Values

| Status | Meaning | When |
|--------|---------|------|
| `pending` | Awaiting owner approval | After purchase request |
| `quote` | Pricing the order | After approval |
| `processing` | Payment succeeded, order in progress | All merchants |
| `shipped` | In transit with tracking info | Amazon only |
| `delivered` | Successfully delivered | Amazon only |
| `payment_failed` | Payment could not be processed | Any merchant |
| `delivery_failed` | Delivery unsuccessful | Amazon only |

---

## Common Errors

| Error | What to Do |
|-------|-----------|
| 403 — merchant blocked | Owner has this merchant on their blocklist |
| 403 — budget exceeded | Hit per-transaction, daily, or monthly guardrail limit |
| 410 — approval expired | 15-minute window passed. Resubmit the purchase request. |
| Search returns no variants | Shopify URL may not be supported by the search API |
| Order fails after approval | Check status — likely `payment_failed` at processing level |

---

## Webhook Events

If you registered with a `callback_url`, you'll receive these events instead of needing to poll:

| Event | Trigger |
|-------|---------|
| `purchase.approved` | Owner approved your purchase |
| `purchase.rejected` | Owner rejected your purchase |
| `purchase.expired` | 15-minute approval window passed |
| `order.shipped` | Order shipped (Amazon only) |
| `order.delivered` | Order delivered (Amazon only) |
| `order.failed` | Payment or delivery failed |

---

## Quick Reference

| Item | Value |
|------|-------|
| Purchase endpoint | `POST /card-wallet/bot/purchase` |
| Status polling | `GET /card-wallet/bot/purchase/status?approval_id=X` |
| Variant search | `POST /card-wallet/bot/search` (Shopify only, beta) |
| Amount format | USD (e.g. `29.99`) |
| Shipping | US only |
| Approval window | 15 minutes |
| Poll interval | ~30 seconds |
| Rate limit (purchase) | 30/hr |
| Rate limit (polling) | 30/hr |
| Rate limit (search) | 10/hr |
