---
name: inventpay
description: Accept crypto payments, manage a digital storefront, and track balances through the InventPay REST API
version: 1.0.0
author: jams24
homepage: https://inventpay.io
source: https://github.com/jams24/inventpay-mcp
license: MIT-0
tags:
  - payments
  - crypto
  - store
  - ecommerce
  - bitcoin
  - solana
  - usdt
  - usdc
  - invoicing
  - digital-products
  - monetization
metadata: {"openclaw":{"requires":{"env":["INVENTPAY_API_KEY"]},"primaryEnv":"INVENTPAY_API_KEY","emoji":"💰"}}
---

# InventPay Skill

Accept crypto payments, run a digital storefront, and track balances through the InventPay REST API.

## What this skill does

This skill teaches your agent how to interact with the [InventPay](https://inventpay.io) payment platform using direct HTTP requests. No external packages or binaries required — your agent makes standard REST API calls.

Your agent can:

- Create crypto payment links and multi-currency invoices (BTC, ETH, LTC, SOL, USDT, USDC)
- Set up and manage a digital storefront with automatic product delivery
- Manage a key pool for unique license keys per customer
- Check balances across all currencies
- Track orders and view store analytics

## Quick start

### Install

```bash
openclaw install inventpay
```

No binaries or packages needed. This skill is instruction-only.

### Configure

1. Sign up at [inventpay.io](https://inventpay.io) and go to **Dashboard > Settings**
2. Copy your API key (starts with `pk_live_`)
3. Set the environment variable:

```bash
export INVENTPAY_API_KEY="pk_live_your_key_here"
```

### Verify

Ask your agent: "What's my InventPay balance?"

The agent should make a GET request to `https://api.inventpay.io/v1/merchant/balance` with your API key and return your balances. If you see an auth error, check that `INVENTPAY_API_KEY` is set and starts with `pk_live_`.

## Base URL

```
https://api.inventpay.io
```

## Authentication

All authenticated endpoints require:

```
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json
```

The API key (`pk_live_...`) is your main merchant key for all operations: payments, invoices, store, products, orders, and balances.

## IMPORTANT: correct endpoint paths

- Payment creation is `POST /v1/create_payment` — NOT `/v1/payments`
- Invoice creation is `POST /v1/create_invoice` — NOT `/v1/invoices` or `/v1/store/manage/invoices`
- Balance endpoint is `GET /v1/merchant/balance` — NOT `/v1/balance`
- Store checkout is `POST /v1/store/{slug}/checkout` — uses the store URL slug (e.g. "my-store"), NOT a store ID
- Do NOT guess or invent endpoint paths. Use ONLY the exact paths listed below.

## Important URLs

- Store page: `https://inventpay.io/store/{slug}`
- Product page: `https://inventpay.io/store/{slug}/product/{productSlug}` — the `/product/` segment is required
- Invoice/payment page: `https://inventpay.io/invoice/{paymentId}`
- Do NOT omit `/product/` from product URLs — `/store/{slug}/{productSlug}` will NOT work

## API endpoints

All responses follow the format: `{ "success": true/false, "data": {...}, "message": "..." }`

---

### Payments

#### Create a fixed-currency payment

Use when you know which cryptocurrency the buyer will pay with.

```
POST /v1/create_payment
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json

{
  "amount": 50.00,                        // required — payment amount
  "currency": "USDT_BEP20",              // required — BTC, ETH, LTC, USDT_ERC20, USDT_BEP20, SOL, USDC_SOL, USDC_BEP20
  "amountCurrency": "USD",               // optional, default "USDT" — USD, USDT, BTC, ETH, LTC, SOL
  "orderId": "order-123",                // optional — your reference ID (max 100 chars)
  "description": "Payment for service",  // optional (max 500 chars)
  "callbackUrl": "https://your-site.com/webhook",  // optional — webhook for status updates
  "expirationMinutes": 30                // optional, default 30, range 5-1440
}
```

Response includes: `paymentId`, `amount` (crypto amount), `currency`, `address` (wallet to pay), `invoiceUrl` (shareable link), `qrCode`, `expiresAt`.

Use `/v1/create_payment` for single-crypto payments. Use `/v1/create_invoice` for multi-crypto choice.

#### Create a multi-currency invoice

Use when you want the buyer to choose which crypto to pay with.

```
POST /v1/create_invoice
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json

{
  "amount": 100.00,                       // required
  "amountCurrency": "USD",               // optional, default "USDT"
  "orderId": "inv-456",                  // optional
  "description": "Monthly subscription", // optional
  "callbackUrl": "https://your-site.com/webhook",  // optional
  "expirationMinutes": 60                // optional, default 60
}
```

Response includes: `paymentId`, `invoiceUrl` (send this to the buyer), `expiresAt`, `availableCurrencies`.

#### Check payment status

```
GET /v1/invoice/{paymentId}/status
No authentication required (public endpoint)
```

Response: `{ "status": "PENDING", "currentBalance": 0, "confirmations": 0 }`

Statuses: `PENDING`, `PROCESSING`, `COMPLETED`, `EXPIRED`, `CANCELLED`, `FAILED`, `UNDERPAID`.

---

### Balances

#### Get all balances

```
GET /v1/merchant/balance
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Response:
```json
{
  "success": true,
  "data": {
    "merchantId": "...",
    "businessName": "...",
    "balances": {
      "balances": [
        {
          "currency": "USDT_BEP20",
          "totalEarned": 812.71,
          "totalWithdrawn": 25.30,
          "totalFees": 1.41,
          "availableBalance": 504.87,
          "lockedBalance": 265.10,
          "pendingBalance": 0
        }
      ],
      "summary": {
        "totalAvailable": 504.92,
        "totalLocked": 265.10,
        "totalPending": 0,
        "totalEarned": 812.77,
        "totalWithdrawn": 25.30,
        "totalFees": 1.41
      }
    }
  }
}
```

#### Get balance for a specific currency

```
GET /v1/merchant/balance/{currency}
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Currency must be: BTC, ETH, LTC, USDT_ERC20, USDT_BEP20, SOL, USDC_SOL, or USDC_BEP20.

---

### Store management

#### Create a store

```
POST /v1/store/manage
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json

{
  "name": "My Digital Store",             // required, 2-100 chars
  "description": "Selling digital goods"  // optional, max 1000 chars
}
```

Response includes: `id`, `name`, `slug`, `url` (public store page at `inventpay.io/store/{slug}`), `isActive`, product/order counts.

#### Get your store

```
GET /v1/store/manage
Header: X-API-Key: <INVENTPAY_API_KEY>
```

#### Update your store

```
PUT /v1/store/manage
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json

{
  "name": "Updated Name",        // optional
  "description": "New desc",     // optional
  "logo": "https://...",         // optional, HTTPS URL
  "banner": "https://...",       // optional, HTTPS URL
  "isPublished": true            // optional
}
```

---

### Products

#### Create a product

```
POST /v1/store/manage/products
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json

{
  "name": "Premium Skill Bundle",         // required, 1-200 chars
  "price": 9.99,                          // required, 0.01-1000000 (in USDT)
  "description": "10 advanced skills",    // optional, max 5000 chars
  "images": ["https://example.com/img.jpg"],  // optional, max 10 URLs
  "stock": 100,                           // optional, omit for unlimited
  "contentType": "GENERAL",              // optional — "GENERAL" (default) or "SKILL"
  "skillContent": "---\nname: ...\n---\n...",  // optional — raw SKILL.md content, only when contentType is "SKILL"
  "digitalContent": {                     // optional — for automatic delivery on payment
    "fileUrl": "https://example.com/bundle.zip",  // download link
    "fileName": "skill-bundle-v2.zip",    // display name
    "instructions": "Extract and copy to your skills folder",
    "licenseKey": "SKILL-PRO-2026",       // access code
    "textContent": "Inline content here"  // or deliver text directly
  }
}
```

Response includes: `id`, `name`, `slug`, `price`, `isActive`, `productUrl`, `contentType`, `skillMeta`.

Digital products auto-deliver after payment via the `digitalContent` field.

When `contentType` is `"SKILL"`, the backend automatically parses YAML frontmatter from `skillContent` and stores it as `skillMeta` (name, version, author, tags, etc.) for storefront display. The raw `skillContent` is never exposed publicly — it is delivered to the buyer after payment.

#### List products

```
GET /v1/store/manage/products?page=1&limit=20&search=skill
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Query parameters: `page` (default 1), `limit` (default 20, max 50), `search` (by name).

#### Update a product

```
PUT /v1/store/manage/products/{productId}
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json

{
  "name": "Updated Name",      // optional
  "price": 14.99,              // optional
  "description": "...",        // optional
  "stock": 50,                 // optional
  "isActive": true,            // optional
  "contentType": "SKILL",      // optional — "GENERAL" or "SKILL"
  "skillContent": "---\n...",  // optional — raw SKILL.md, only for SKILL type
  "digitalContent": { ... }    // optional
}
```

#### Delete a product

```
DELETE /v1/store/manage/products/{productId}
Header: X-API-Key: <INVENTPAY_API_KEY>
```

If the product has order history it gets deactivated (soft delete). If no orders exist it gets permanently removed.

---

### Key pool (unique keys per customer)

For products where each buyer gets a unique license key, activation code, or content.

#### Upload keys

```
POST /v1/store/manage/products/{productId}/keys
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json

{
  "keys": ["KEY-001", "KEY-002", "KEY-003"],  // required, 1-10000 unique keys
  "label": "Batch #1"                         // optional, max 200 chars
}
```

Response: `{ "added": 3, "duplicates": 0 }`

#### List keys

```
GET /v1/store/manage/products/{productId}/keys?page=1&limit=50&status=AVAILABLE
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Query: `page`, `limit` (max 100), `status` (AVAILABLE, ASSIGNED, REVOKED).

#### Get key pool stats

```
GET /v1/store/manage/products/{productId}/keys/stats
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Returns: `total`, `available`, `assigned`, `revoked`, `useKeyPool`.

#### Remove all available keys

```
DELETE /v1/store/manage/products/{productId}/keys
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Only removes unassigned (AVAILABLE) keys. Assigned keys are preserved.

---

### Orders

#### List orders

```
GET /v1/store/manage/orders?page=1&limit=20&status=PAID
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Query: `page`, `limit` (max 50), `status` (PENDING, PAID, PROCESSING, SHIPPED, COMPLETED, CANCELLED, REFUNDED).

#### Get order details

```
GET /v1/store/manage/orders/{orderId}
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Returns full order with items, payment info, customer details, and delivery status.

#### Update order status

```
PUT /v1/store/manage/orders/{orderId}/status
Header: X-API-Key: <INVENTPAY_API_KEY>
Content-Type: application/json

{
  "status": "COMPLETED",           // PROCESSING, SHIPPED, COMPLETED, CANCELLED, REFUNDED
  "notes": "Delivered successfully" // optional, max 500 chars
}
```

Valid transitions: PAID can go to PROCESSING/SHIPPED/COMPLETED/CANCELLED/REFUNDED. Digital products auto-complete on payment.

---

### Store checkout (public, no auth)

```
POST /v1/store/{slug}/checkout
Content-Type: application/json

{
  "items": [{ "productId": "prod_...", "quantity": 1, "variant": {} }],
  "customerEmail": "buyer@example.com",
  "customerName": "John Doe",
  "currency": "USDT_BEP20"   // optional
}
```

Uses the store URL slug (e.g. "my-store"), NOT a store ID.

---

### Store analytics

```
GET /v1/store/manage/analytics
Header: X-API-Key: <INVENTPAY_API_KEY>
```

Returns: order counts by status, total/confirmed revenue in USDT, product count, store info.

---

## Agent behavior when creating products

When the user asks to create or add a new product, ALWAYS ask them:

1. **Product name** (required)
2. **Price in USDT** (required)
3. **Content type** — ask: "Is this a regular digital product or a SKILL file (.md)?"
   - If **SKILL**: ask the user to paste or provide the SKILL.md content. Set `contentType: "SKILL"` and put the raw markdown in `skillContent`. The backend will auto-parse the YAML frontmatter.
   - If **regular/general**: ask about digital delivery (file URL, license key, instructions, or text content). Set `contentType: "GENERAL"` or omit it.
4. **Description** (optional)
5. **Stock** (optional, omit for unlimited)
6. **Images** (optional)

Do NOT skip the content type question. This is important because SKILL products get special storefront display (skill badge, version, author, tags) and the raw .md file is delivered to the buyer after payment.

## Example conversations

**Creating a payment:**
> "Create a $25 USDT payment for the logo design"

Agent makes: `POST /v1/create_payment` with `{"amount": 25, "currency": "USDT_BEP20", "description": "Logo design"}` and returns the payment link.

**Setting up a store:**
> "Create a store called AI Skill Shop"

Agent makes: `POST /v1/store/manage` with `{"name": "AI Skill Shop"}` and returns the store URL.

**Adding a product:**
> "Add a product called Code Review Skill for $8 with download URL https://files.example.com/review-skill.md"

Agent makes: `POST /v1/store/manage/products` with name, price, and `digitalContent.fileUrl`.

**Adding a skill product:**
> "Create a skill product called 'SEO Audit Skill' for $5 with this SKILL.md content: ---\nname: seo-audit\nauthor: devtools\nversion: 1.0.0\ntags: [seo, audit]\n---\n\n# SEO Audit\n..."

Agent makes: `POST /v1/store/manage/products` with name, price, `contentType: "SKILL"`, and `skillContent` containing the raw markdown.

**Checking balance:**
> "What's my balance?"

Agent makes: `GET /v1/merchant/balance` and summarizes available amounts per currency.

**Checking orders:**
> "Show me recent paid orders"

Agent makes: `GET /v1/store/manage/orders?status=PAID` and lists them.

**Managing key pool:**
> "Upload 50 license keys for the Pro Skill product"

Agent makes: `POST /v1/store/manage/products/{id}/keys` with the keys array.

## Selling OpenClaw skills through your store

Practical setup for monetizing premium skill files:

1. **Create your store** — agent calls `POST /v1/store/manage`
2. **Add skill files as products** — set `contentType: "SKILL"`, paste the raw SKILL.md into `skillContent`, set a price. The backend parses frontmatter automatically for the storefront. Alternatively, use `contentType: "GENERAL"` with a `digitalContent.fileUrl` for a hosted download link.
3. **Share your store link** — `inventpay.io/store/your-slug`
4. **Buyers see rich skill cards** — storefront shows skill name, version, author, and tags from parsed frontmatter
5. **Buyers pay with crypto** — BTC, ETH, LTC, SOL, USDT, or USDC
6. **Delivery is automatic** — buyer pays, gets the skill file immediately
7. **Check earnings** — agent calls `GET /v1/merchant/balance`

What sells well: industry-specific skills, complex automation chains, curated skill bundles, premium versions of popular free skills, API integration skills. Price range $3-15 for individual skills, $20-40 for bundles.

## Guidelines

- All amounts default to USD/USDT unless specified otherwise
- Supported cryptos: BTC, ETH, LTC, USDT_ERC20, USDT_BEP20, SOL, USDC_SOL, USDC_BEP20
- Payment expiration: 5-1440 minutes (default 30)
- The API key (`pk_live_...`) is used for all operations
- Store checkout uses the store slug in the URL path, NOT a store ID
- Digital products auto-deliver after payment via the `digitalContent` field
- Product URLs require the `/product/` segment: `/store/{slug}/product/{productSlug}`
- To withdraw funds, use the InventPay dashboard at [inventpay.io](https://inventpay.io)

## Security notes

- The `INVENTPAY_API_KEY` can create payments, manage your store, and read balances. It **cannot** withdraw or transfer funds.
- Never pass credentials, secrets, or private keys as product delivery content. Use hosted file URLs for delivery.
- You can revoke and regenerate your API key from the dashboard at any time.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `INVENTPAY_API_KEY` | **Yes** | Merchant API key (`pk_live_...`). Used for payments, store, products, orders, balances. Cannot withdraw funds. |

## Links

- **Source:** [github.com/jams24/inventpay-mcp](https://github.com/jams24/inventpay-mcp)
- **Dashboard:** [inventpay.io](https://inventpay.io)
- **API Docs:** [docs.inventpay.io](https://docs.inventpay.io)
- **JavaScript SDK:** [npmjs.com/package/inventpay](https://www.npmjs.com/package/inventpay)
- **Python SDK:** [pypi.org/project/inventpay](https://pypi.org/project/inventpay)

## Publisher

**InventPay** — Crypto payment infrastructure for developers and AI agents.

- Website: [inventpay.io](https://inventpay.io)
- GitHub: [github.com/jams24](https://github.com/jams24)
- npm: [npmjs.com/~jams24](https://www.npmjs.com/~jams24)
