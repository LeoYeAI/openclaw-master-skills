---
name: creditclaw-checkout
description: "Create checkout pages and receive payments from anyone — bots, agents, or humans."
---

# CreditClaw Checkout — Get Paid by Anyone

Create public checkout pages where anyone can pay you. Buyers can pay with:
- **Credit card or bank** — via Stripe (no crypto knowledge needed)
- **USDC on Base** — direct transfer from any wallet
- **x402 wallet** — from another CreditClaw wallet

All payments settle as USDC into your Privy wallet on Base.

---

## Create a Checkout Page

POST https://creditclaw.com/api/v1/bot/checkout-pages/create
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "title": "Premium API Access - 1 Month",
    "description": "Unlimited queries to my data analysis endpoint.",
    "amount_usd": 5.00,
    "amount_locked": true
  }'

### Request Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Name shown on checkout page (max 200 chars) |
| `description` | No | Longer text shown below the title |
| `amount_usd` | No | Fixed price in USD. Omit for open/custom amount. |
| `amount_locked` | No | Default `true`. If true, buyer cannot change amount. |
| `allowed_methods` | No | Array of: `"x402"`, `"usdc_direct"`, `"stripe_onramp"`, `"base_pay"`. Default: all four. |
| `success_url` | No | URL to redirect buyer after payment. |
| `expires_at` | No | ISO timestamp. Checkout page expires after this. |
| `page_type` | No | `"product"`, `"event"`, or `"digital_product"`. Default: `"product"`. |
| `digital_product_url` | No | URL delivered to buyer after payment. Required when `page_type` is `"digital_product"`. |
| `image_url` | No | URL of an image to display on the checkout page. |
| `collect_buyer_name` | No | Whether to ask for buyer's name. Default: `false`. |
| `shop_visible` | No | If `true`, this page appears in your public shop. Default: `false`. |
| `shop_order` | No | Display order in your shop (lower = first). Default: `0`. |

### Response (HTTP 201)

```json
{
  "checkout_page_id": "cp_a1b2c3d4",
  "checkout_url": "/pay/cp_a1b2c3d4",
  "amount_usd": 5.00,
  "amount_locked": true,
  "status": "active"
}
```

Share `checkout_url` with anyone who needs to pay you.

---

## List Your Checkout Pages

GET https://creditclaw.com/api/v1/bot/checkout-pages
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"

Returns all your active checkout pages with view/payment counts.

**Rate limit:** 12 requests per hour.

---

## View Your Sales

GET https://creditclaw.com/api/v1/bot/sales
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"

Optional query parameters:
- `?status=confirmed|pending|failed` — Filter by status
- `?checkout_page_id=cp_xxx` — Filter by checkout page
- `?limit=N` — Number of results (default 20, max 100)

**Rate limit:** 12 requests per hour.

### Response

```json
{
  "sales": [
    {
      "sale_id": "sale_x1y2z3",
      "checkout_page_id": "cp_a1b2c3d4",
      "checkout_title": "Premium API Access - 1 Month",
      "amount_usd": 5.00,
      "payment_method": "stripe_onramp",
      "buyer_email": "buyer@example.com",
      "status": "confirmed",
      "confirmed_at": "2026-02-27T15:30:00Z",
      "created_at": "2026-02-27T15:29:45Z"
    }
  ],
  "total": 1
}
```

---

## Send Invoices

Send formatted invoices to customers and receive payments via checkout pages.

### Create an Invoice

POST https://creditclaw.com/api/v1/bot/invoices/create
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "checkout_page_id": "cp_a1b2c3d4",
    "recipient_name": "Acme Corp",
    "recipient_email": "buyer@acme.com",
    "line_items": [
      {
        "description": "Premium API Access - 1 Month",
        "quantity": 1,
        "unit_price_usd": 5.00
      }
    ],
    "tax_usd": 0.50,
    "due_date": "2026-03-27",
    "notes": "Payment due within 30 days"
  }'

### Request Fields

| Field | Required | Description |
|-------|----------|-------------|
| `checkout_page_id` | Yes | ID of the checkout page to link this invoice to |
| `recipient_name` | Yes | Customer name (max 255 chars) |
| `recipient_email` | Yes | Email to send invoice to |
| `line_items` | Yes | Array of line items with `description`, `quantity`, `unit_price_usd` |
| `tax_usd` | No | Tax amount (default 0) |
| `due_date` | No | ISO date string. Default: 30 days from now |
| `notes` | No | Additional payment terms or notes |

### Response (HTTP 201)

```json
{
  "invoice_id": "inv_x1y2z3",
  "reference_number": "INV-001",
  "checkout_page_id": "cp_a1b2c3d4",
  "recipient_name": "Acme Corp",
  "recipient_email": "buyer@acme.com",
  "total_usd": 5.50,
  "status": "draft",
  "payment_url": "/pay/cp_a1b2c3d4?ref=INV-001",
  "created_at": "2026-02-27T15:30:00Z"
}
```

**Rate limit:** 10 requests per hour.

---

### List Your Invoices

GET https://creditclaw.com/api/v1/bot/invoices
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"

Optional query parameters:
- `?status=draft|sent|viewed|paid|cancelled` — Filter by status
- `?checkout_page_id=cp_xxx` — Filter by checkout page
- `?limit=N` — Number of results (default 20, max 100)

Returns all your invoices with counts.

**Rate limit:** 12 requests per hour.

### Response

```json
{
  "invoices": [
    {
      "invoice_id": "inv_x1y2z3",
      "reference_number": "INV-001",
      "checkout_page_id": "cp_a1b2c3d4",
      "recipient_name": "Acme Corp",
      "recipient_email": "buyer@acme.com",
      "total_usd": 5.50,
      "status": "sent",
      "due_date": "2026-03-27",
      "created_at": "2026-02-27T15:30:00Z",
      "sent_at": "2026-02-27T15:31:00Z"
    }
  ],
  "total": 1
}
```

---

### Send an Invoice

POST https://creditclaw.com/api/v1/bot/invoices/[id]/send
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
  -H "Content-Type: application/json"

Sends the invoice to the recipient via email with a formatted PDF attachment. Only draft invoices can be sent.

### Response (HTTP 200)

```json
{
  "invoice_id": "inv_x1y2z3",
  "status": "sent",
  "sent_at": "2026-02-27T15:31:00Z",
  "payment_url": "/pay/cp_a1b2c3d4?ref=INV-001"
}
```

**Rate limit:** 5 requests per hour.

---

## Payment Links

Payment links are lightweight, single-use Stripe checkout URLs for collecting one-time payments. They expire after 24 hours and are Stripe-only — ideal when you need to quickly charge someone without setting up a full checkout page.

### Create a Payment Link

POST https://creditclaw.com/api/v1/bot/payments/create-link
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "amount_usd": 10.00,
    "description": "Research report: Q4 market analysis",
    "payer_email": "client@example.com"
  }'

#### Response (HTTP 201)

```json
{
  "payment_link_id": "pl_q7r8s9",
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_live_...",
  "amount_usd": 10.00,
  "status": "pending",
  "expires_at": "2026-02-07T21:00:00Z"
}
```

Send `checkout_url` to whoever needs to pay. When they do:
- Funds land in your wallet.
- Your balance increases.
- The payment shows in your transaction history as `payment_received`.
- If you have a `callback_url`, you receive a `wallet.payment.received` webhook.

**Payment links expire in 24 hours.** Generate a new one if needed.

**Rate limit:** 3 requests per hour.

---

### List Your Payment Links

Check the status of payment links you've created:

GET https://creditclaw.com/api/v1/bot/payments/links
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"

Optional query parameters:
- `?limit=N` — Number of results (default 20, max 100)
- `?status=pending|completed|expired` — Filter by status

**Rate limit:** 12 requests per hour.

---

## When to Use What

| Scenario | Use This |
|----------|----------|
| You sell API access or digital services | Checkout page with fixed amount |
| You accept donations or tips | Checkout page with open amount |
| You want to invoice a specific buyer | Checkout page (share the link) |
| You want to sell on a marketplace | Create checkout page, list the URL |
| You need to send a one-time payment request | [Payment Link](#payment-links) (24h expiry, Stripe-only) |
| You want to sell physical products with shipping | Use a procurement skill + vendor instead |

---

## Webhooks

When a sale is confirmed, CreditClaw fires a `wallet.sale.completed` webhook:

```json
{
  "event": "wallet.sale.completed",
  "data": {
    "sale_id": "sale_x1y2z3",
    "checkout_page_id": "cp_a1b2c3d4",
    "amount_usd": 5.00,
    "payment_method": "stripe_onramp",
    "buyer_email": "buyer@example.com",
    "new_balance_usd": 125.50
  }
}
```

Use this to trigger fulfillment (e.g., grant API access, send a download link, update a service).

---

## Digital Product Delivery via x402

When a checkout page has `page_type: "digital_product"`, the x402 settlement response includes the product URL after successful payment:

```json
{
  "status": "confirmed",
  "sale_id": "sale_abc123",
  "tx_hash": "0xdeadbeef...",
  "amount_usd": 5.00,
  "product": {
    "url": "https://your-service.com/download/signed-token",
    "type": "digital_product"
  }
}
```

The product URL is never exposed before payment. x402 payments are idempotent — retrying with the same nonce returns the original result without double-charging.

---

## Tips

- **Set `amount_locked: true`** for fixed-price products so buyers can't underpay.
- **Leave `amount_usd` empty** for donation or tip jars.
- **Use `page_type: "digital_product"`** when selling downloadable content, API keys, or access tokens.
- **Use `success_url`** to redirect buyers back to your service after payment.
- **Check `GET /bot/sales`** periodically to reconcile completed sales with your fulfillment.
- **Multiple checkout pages** are fine — create one per product or service tier.

---

## Build Your Shop

You can create a public storefront that displays your products. This requires three steps: set up your seller profile, create checkout pages with `shop_visible: true`, and publish your shop.

### Step 1: Set Up Your Seller Profile

PATCH https://creditclaw.com/api/v1/bot/seller-profile
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "business_name": "DataBot Services",
    "slug": "databot",
    "description": "AI-powered data analysis tools and APIs."
  }'

| Field | Required | Description |
|-------|----------|-------------|
| `business_name` | No | Your business or bot name (max 200 chars) |
| `slug` | No | URL-friendly shop identifier (e.g. `"databot"` → `/shop/databot`). Lowercase, numbers, hyphens only. Must be unique. |
| `description` | No | Short bio shown on your shop page (max 2000 chars) |
| `logo_url` | No | URL to your logo image |
| `shop_banner_url` | No | URL to a banner image for your shop |
| `shop_published` | No | Set to `true` to make your shop publicly visible. Default: `false`. |

#### Response

```json
{
  "profile": {
    "business_name": "DataBot Services",
    "slug": "databot",
    "description": "AI-powered data analysis tools and APIs.",
    "logo_url": null,
    "shop_banner_url": null,
    "shop_published": false,
    "created_at": "2026-03-01T12:00:00Z",
    "updated_at": "2026-03-01T12:00:00Z"
  }
}
```

To read your current profile:

GET https://creditclaw.com/api/v1/bot/seller-profile
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"

Returns `{ "profile": null }` if no profile exists yet.

---

### Step 2: Create a Product and Add It to Your Shop

POST https://creditclaw.com/api/v1/bot/checkout-pages/create
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "title": "Premium Dataset - Q1 2026",
    "description": "Cleaned and enriched dataset with 50k records.",
    "amount_usd": 10.00,
    "amount_locked": true,
    "page_type": "digital_product",
    "digital_product_url": "https://your-service.com/download/dataset-q1",
    "shop_visible": true,
    "shop_order": 0
  }'

Set `shop_visible: true` to make the product appear in your shop. Use `shop_order` to control display order (lower numbers appear first).

---

### Step 3: Publish Your Shop

PATCH https://creditclaw.com/api/v1/bot/seller-profile
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
  -H "Content-Type: application/json"
  -d '{ "shop_published": true }'

Your shop is now live. Anyone can visit it and browse your products.

---

### Update a Checkout Page

PATCH https://creditclaw.com/api/v1/bot/checkout-pages/:id
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
  -H "Content-Type: application/json"
  -d '{
    "shop_visible": true,
    "title": "Updated Product Name"
  }'

All fields from the create request are supported, plus:

| Field | Description |
|-------|-------------|
| `status` | `"active"`, `"paused"`, or `"archived"`. Paused pages stop accepting payments. |

#### Response

Returns the full updated checkout page object.

---

### View Your Shop

GET https://creditclaw.com/api/v1/bot/shop
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"

Returns your seller profile and all checkout pages with their `shop_visible` and `shop_order` values. Use this to verify your shop looks correct before publishing.

---

### Full Example: Zero to Live Shop

```
# 1. Set up your profile
PATCH /api/v1/bot/seller-profile
{ "business_name": "DataBot", "slug": "databot" }

# 2. Create a digital product
POST /api/v1/bot/checkout-pages/create
{
  "title": "Premium API Access",
  "amount_usd": 5.00,
  "page_type": "digital_product",
  "digital_product_url": "https://api.databot.com/keys/generate",
  "shop_visible": true
}

# 3. Publish the shop
PATCH /api/v1/bot/seller-profile
{ "shop_published": true }

# Done. Your shop is live at /shop/databot
```
