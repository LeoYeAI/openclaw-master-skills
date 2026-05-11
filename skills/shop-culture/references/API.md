# For the Cult API — Agentic Commerce Endpoint Reference

Base URL: **`https://forthecult.store`** — all paths below are relative to this (e.g. **GET /api/health**).

No API key or environment variables required. No authentication is needed for discovery, search, checkout, and order status. Order details (email, shipping) are returned only when the caller is authorized for that order. **Identity header:** `X-Moltbook-Identity` is optional and only for agent-only endpoints (`/api/agent/me`, `/api/agent/me/orders`, `/api/agent/me/preferences`); use it only when the agent runtime explicitly supplies it—do not send it for normal store operations. This API is purpose-built for Agentic Commerce — AI agents autonomously discovering, purchasing, and tracking physical goods.

**Payment options:**
- **Standard checkout** (`POST /api/checkout`) — Multi-chain payments, poll for confirmation
- **x402 checkout** (`POST /api/checkout/x402`) — HTTP 402 protocol, USDC on Solana, fully agent-driven

---

## Health & Discovery

### GET `/api/health`

Check API availability before making requests.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-10T14:30:00Z"
}
```

### GET `/api/agent/capabilities`

Natural-language description of what the API can do. **Call this first.**

**Response:**

```json
{
  "name": "For the Cult",
  "tagline": "Quality lifestyle, wellness, and longevity products",
  "capabilities": [
    "Search and browse lifestyle, wellness, and longevity products",
    "Filter by category, price, brand",
    "Create orders with multi-chain payment",
    "Track order status and shipping",
    "Get token holder discounts (5-20% off)"
  ],
  "limitations": [
    "Ships to select countries only",
    "No returns after 30 days",
    "Customer data auto-deleted after 90 days"
  ],
  "supportedNetworks": ["solana", "ethereum", "base", "polygon", "arbitrum", "bitcoin", "dogecoin", "monero"],
  "supportedTokens": ["SOL", "ETH", "USDC", "USDT", "BTC", "DOGE", "XMR", "MATIC", "CULT"]
}
```

### POST `/api/agent/shop`

AI-powered shopping assistant. Natural language in, structured products + AI reply out.

**Request body:**

```json
{
  "message": "wireless noise-canceling headphones under $200",
  "context": {
    "priceRange": { "max": 200 },
    "preferences": ["good battery life", "comfortable"],
    "category": "tech"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | Natural language shopping request (max 1000 chars) |
| `context.priceRange` | object | No | `{ min?: number, max?: number }` — price bounds in USD |
| `context.preferences` | string[] | No | Feature preferences to consider |
| `context.category` | string | No | Category slug to filter |

**Response:**

```json
{
  "reply": "I found some great wireless noise-canceling headphones under $200...",
  "products": [
    {
      "id": "prod_sony_wh1000xm4",
      "title": "Sony WH-1000XM4 Wireless Headphones",
      "price": 198.00,
      "currency": "USD",
      "rating": 4.7,
      "reviewCount": 42531,
      "imageUrl": "https://...",
      "source": "store",
      "inStock": true,
      "badge": "bestseller"
    }
  ],
  "_parsed": {
    "query": "wireless noise-canceling headphones",
    "priceMax": 200
  }
}
```

### GET `/api/agent/me`

Returns the verified Moltbook agent profile when the caller is an authenticated Moltbook agent. **Optional:** only call this endpoint when the agent runtime explicitly supplies an `X-Moltbook-Identity` token. Do not send or infer this header for normal store operations (browsing, search, checkout, order status by ID). Not declared in `requires.env` — the header is supplied by the runtime when available.

**Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `X-Moltbook-Identity` | Yes (for this endpoint) | Moltbook identity token from agent runtime; use only when runtime supplies it |

**Response:** Agent profile object (name, permissions, capabilities).

### GET `/api/payment-methods`

All supported blockchain networks and tokens for payment.

**Response:**

```json
{
  "chains": [
    {
      "id": "solana",
      "name": "Solana",
      "tokens": [
        { "symbol": "SOL", "name": "Solana", "type": "native", "decimals": 9 },
        { "symbol": "USDC", "name": "USD Coin", "type": "spl", "decimals": 6, "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" },
        { "symbol": "USDT", "name": "Tether", "type": "spl", "decimals": 6, "mint": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB" },
        { "symbol": "CULT", "name": "Cult Token", "type": "spl", "decimals": 9 }
      ]
    },
    {
      "id": "ethereum",
      "name": "Ethereum",
      "tokens": [
        { "symbol": "ETH", "name": "Ethereum", "type": "native", "decimals": 18 },
        { "symbol": "USDC", "name": "USD Coin", "type": "erc20", "decimals": 6, "mint": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" },
        { "symbol": "USDT", "name": "Tether", "type": "erc20", "decimals": 6, "mint": "0xdAC17F958D2ee523a2206206994597C13D831ec7" }
      ]
    },
    {
      "id": "base",
      "name": "Base",
      "tokens": [
        { "symbol": "ETH", "name": "Ethereum", "type": "native", "decimals": 18 },
        { "symbol": "USDC", "name": "USD Coin", "type": "erc20", "decimals": 6 }
      ]
    },
    {
      "id": "polygon",
      "name": "Polygon",
      "tokens": [
        { "symbol": "MATIC", "name": "Polygon", "type": "native", "decimals": 18 },
        { "symbol": "USDC", "name": "USD Coin", "type": "erc20", "decimals": 6 }
      ]
    },
    {
      "id": "arbitrum",
      "name": "Arbitrum",
      "tokens": [
        { "symbol": "ETH", "name": "Ethereum", "type": "native", "decimals": 18 },
        { "symbol": "USDC", "name": "USD Coin", "type": "erc20", "decimals": 6 }
      ]
    },
    {
      "id": "bitcoin",
      "name": "Bitcoin",
      "tokens": [
        { "symbol": "BTC", "name": "Bitcoin", "type": "native", "decimals": 8 }
      ]
    },
    {
      "id": "dogecoin",
      "name": "Dogecoin",
      "tokens": [
        { "symbol": "DOGE", "name": "Dogecoin", "type": "native", "decimals": 8 }
      ]
    },
    {
      "id": "monero",
      "name": "Monero",
      "tokens": [
        { "symbol": "XMR", "name": "Monero", "type": "native", "decimals": 12 }
      ]
    }
  ]
}
```

---

## Product Discovery

### GET `/api/categories`

Category tree with subcategories, slugs, and product counts.

**Response:**

```json
{
  "categories": [
    {
      "id": "cat_wellness",
      "name": "Wellness & Longevity",
      "slug": "wellness",
      "description": "Supplements, adaptogens, and longevity essentials",
      "productCount": 38,
      "subcategories": [
        { "id": "cat_supplements", "name": "Supplements", "slug": "supplements", "productCount": 14 },
        { "id": "cat_adaptogens", "name": "Adaptogens", "slug": "adaptogens", "productCount": 8 }
      ]
    },
    {
      "id": "cat_coffee",
      "name": "Coffee & Tea",
      "slug": "coffee",
      "description": "Single-origin roasts, matcha, and functional blends",
      "productCount": 15
    },
    {
      "id": "cat_apparel",
      "name": "Apparel",
      "slug": "apparel",
      "description": "Hoodies, tees, socks, and everyday essentials",
      "productCount": 42,
      "subcategories": [
        { "id": "cat_hoodies", "name": "Hoodies", "slug": "hoodies", "productCount": 12 },
        { "id": "cat_socks", "name": "Socks", "slug": "socks", "productCount": 6 }
      ]
    },
    {
      "id": "cat_tech",
      "name": "Tech & Gadgets",
      "slug": "tech",
      "description": "Privacy tools, eSIMs, and useful tech accessories",
      "productCount": 22
    },
    {
      "id": "cat_pet",
      "name": "Pet Goods",
      "slug": "pet",
      "description": "Treats, toys, and gear for dogs and cats",
      "productCount": 11
    }
  ]
}
```

### GET `/api/products/featured`

Curated featured products with badges (trending, new, best sellers).

**Response:**

```json
{
  "products": [
    {
      "id": "prod_top_blast_coffee",
      "name": "Top Blast Coffee — Dark Roast",
      "slug": "top-blast-coffee",
      "category": "coffee",
      "price": { "usd": 29.99, "crypto": { "SOL": "0.245", "USDC": "29.99" } },
      "badge": "trending",
      "inStock": true
    },
    {
      "id": "prod_merino_wool_socks",
      "name": "Merino Wool Everyday Socks (3-Pack)",
      "slug": "merino-wool-everyday-socks",
      "category": "socks",
      "price": { "usd": 34.99, "crypto": { "SOL": "0.286", "USDC": "34.99" } },
      "badge": "bestseller",
      "inStock": true
    },
    {
      "id": "prod_adaptogen_calm",
      "name": "Adaptogen Calm Blend — Ashwagandha + Reishi",
      "slug": "adaptogen-calm-blend",
      "category": "wellness",
      "price": { "usd": 44.99, "crypto": { "SOL": "0.368", "USDC": "44.99" } },
      "badge": "new",
      "inStock": true
    },
    {
      "id": "prod_good_boy_treats",
      "name": "Good Boy Organic Dog Treats",
      "slug": "good-boy-organic-dog-treats",
      "category": "pet",
      "price": { "usd": 18.99, "crypto": { "SOL": "0.155", "USDC": "18.99" } },
      "badge": "trending",
      "inStock": true
    }
  ]
}
```

Badge values: `trending`, `new`, `bestseller`.

---

## Products

### GET `/api/products/search`

Semantic search with filters. Supports natural-language queries. When `source=all` (default), results include both store products and marketplace products; use `source=store` for store-only or `source=marketplace` for marketplace-only.

**Query parameters:**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `q` | string | Yes | — | Search query (natural language supported) |
| `source` | string | No | `all` | `all` — store + marketplace; `store` — store catalog only; `marketplace` — marketplace only |
| `category` | string | No | — | Category slug filter (store products only) |
| `priceMin` | number | No | — | Minimum USD price |
| `priceMax` | number | No | — | Maximum USD price |
| `sort` | string | No | `newest` | `newest` (recently added), `popular` (best seller), `rating` (best rated), `price_asc`, `price_desc` |
| `limit` | integer | No | 20 | Results per page (max 100) |
| `offset` | integer | No | 0 | Pagination offset |

Search returns only in-stock items.

**Response:**

```json
{
  "products": [
    {
      "id": "prod_top_blast_coffee",
      "name": "Top Blast Coffee — Dark Roast",
      "slug": "top-blast-coffee",
      "description": "Single-origin dark roast, ethically sourced. Rich and smooth with notes of dark chocolate.",
      "price": {
        "usd": 29.99,
        "crypto": { "SOL": "0.245", "USDC": "29.99", "BTC": "0.00026" }
      },
      "imageUrl": "https://forthecult.store/images/top-blast-coffee.jpg",
      "category": "coffee",
      "inStock": true,
      "tags": ["coffee", "dark-roast", "organic", "longevity"]
    }
  ],
  "total": 42,
  "pagination": { "limit": 20, "offset": 0, "hasMore": true }
}
```

**Important:** Use the `id` field from products when creating orders. For store products use the `slug` field when fetching product details. When `source=all` or `source=marketplace`, some items may include `source: "marketplace"` and `productUrl`; use that item's `id` as the **asin** in checkout (see POST `/api/checkout`).

### GET `/api/products/store/search`

Store catalog only (no marketplace). Same query parameters and response shape as `/api/products/search` with `source=store`. Use when the client only wants products from the store catalog.

### GET `/api/agent/products`

Agent-optimized product list. Accepts the same query parameters as `/api/products/search`. Returns a streamlined response optimized for agent consumption.

### GET `/api/products/{slug}`

Full product detail including variants, images, and related products.

**Path parameter:** `slug` — the product slug from search results.

**Response:**

```json
{
  "id": "prod_black_hoodie_001",
  "name": "Premium Black Hoodie",
  "slug": "premium-black-hoodie",
  "description": "Ultra-soft cotton blend hoodie. Perfect weight for layering or wearing alone. Relaxed fit for everyday comfort.",
  "price": {
    "usd": 79.99,
    "crypto": { "SOL": "0.5", "USDC": "79.99", "ETH": "0.025", "BTC": "0.0012" }
  },
  "images": [
    "https://forthecult.store/images/black-hoodie-front.jpg",
    "https://forthecult.store/images/black-hoodie-back.jpg"
  ],
  "variants": [
    {
      "id": "var_hoodie_s_black",
      "name": "Black / S",
      "sku": "HOD-BLK-S",
      "price": 79.99,
      "inStock": true,
      "stockQuantity": 15
    },
    {
      "id": "var_hoodie_xl_black",
      "name": "Black / XL",
      "sku": "HOD-BLK-XL",
      "price": 79.99,
      "inStock": false,
      "stockQuantity": 0
    }
  ],
  "category": "Hoodies",
  "inStock": true,
  "tags": ["comfortable", "cotton", "lifestyle", "wellness"],
  "relatedProducts": []
}
```

**Variant handling:**
- If `variants` is non-empty, choose one where `inStock: true`.
- Include the chosen `variantId` in the checkout `items[]` payload.
- If the user's preferred variant is out of stock, suggest alternatives from the same product.

---

## Checkout & Orders

### POST `/api/checkout`

Create an order and generate a payment request (standard flow — poll for payment confirmation). See [CHECKOUT-FIELDS.md](CHECKOUT-FIELDS.md) for complete field specification.

### POST `/api/checkout/x402`

**x402 checkout** — Fully agent-driven payments via HTTP 402 protocol. USDC on Solana.

**Flow:**
1. POST order details (no X-PAYMENT header) → returns 402 with payment requirements
2. Agent builds and signs USDC transfer transaction with memo `FTC Order: {orderId}`
3. Retry with `X-PAYMENT` header containing base64-encoded signed transaction → returns 201

**Step 1 Request (no payment):**

```json
{
  "email": "agent@example.com",
  "items": [
    { "productId": "prod_black_hoodie_001", "variantId": "var_hoodie_m_black", "quantity": 1 }
  ],
  "shipping": {
    "name": "John Doe",
    "address1": "123 Main St",
    "city": "San Francisco",
    "stateCode": "CA",
    "postalCode": "94102",
    "countryCode": "US"
  }
}
```

**Step 1 Response: HTTP 402**

```json
{
  "code": "PAYMENT_REQUIRED",
  "message": "Payment required: send 79.99 USDC to complete order",
  "orderId": "abc123",
  "totals": { "subtotalUsd": 79.99, "shippingUsd": 0, "totalUsd": 79.99 },
  "paymentInstructions": {
    "protocol": "x402",
    "network": "solana",
    "token": "USDC",
    "tokenMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "amount": "79990000",
    "amountHuman": "79.99",
    "payTo": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "memo": "FTC Order: abc123",
    "maxTimeoutSeconds": 300
  }
}
```

Headers include `PAYMENT-REQUIRED` (base64 JSON) with full x402 payment requirements.

**Step 3 Request (with payment):**

```http
POST /api/checkout/x402
Content-Type: application/json
X-PAYMENT: base64({"transaction": "<signed-tx-base64>"})

{ ...same body as step 1... }
```

**Step 3 Response: HTTP 201**

```json
{
  "success": true,
  "orderId": "abc123",
  "status": "paid",
  "payment": {
    "method": "x402_usdc",
    "network": "solana",
    "token": "USDC",
    "transactionSignature": "5xYz..."
  },
  "totals": { "subtotalUsd": 79.99, "shippingUsd": 0, "totalUsd": 79.99 },
  "_actions": {
    "next": "Order is paid and processing",
    "status": "/api/orders/abc123/status"
  }
}
```

---

**Items:** Each element may be either a store product or a marketplace product. Store: `{ "productId": "<id>", "quantity": n }` (optional `variantId` when the product has variants). Marketplace: `{ "asin": "<asin>", "quantity": n }` — use the product `id` from search results when that product has `source: "marketplace"` (the id is the ASIN).

**Request body (JSON):**

```json
{
  "items": [
    { "productId": "prod_black_hoodie_001", "variantId": "var_hoodie_m_black", "quantity": 1 },
    { "productId": "prod_top_blast_coffee", "quantity": 2 },
    { "asin": "B0C8PSMPTH", "quantity": 1 }
  ],
  "email": "customer@example.com",
  "payment": { "chain": "solana", "token": "USDC" },
  "shipping": {
    "name": "Customer Name",
    "address1": "123 Main St",
    "address2": "Apt 4B",
    "city": "San Francisco",
    "stateCode": "CA",
    "postalCode": "94102",
    "countryCode": "US"
  },
  "walletAddress": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
}
```

**Response:**

```json
{
  "orderId": "order_abc123xyz",
  "payment": {
    "chain": "solana",
    "token": "USDC",
    "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "amount": "134.97",
    "reference": "FortheCult_order_abc123xyz",
    "qrCode": "data:image/png;base64,iVBOR..."
  },
  "discount": {
    "tier": "PRIME",
    "percentage": 15,
    "savedAmount": 20.25
  },
  "expiresAt": "2026-02-10T15:00:00Z",
  "statusUrl": "/api/orders/order_abc123xyz/status",
  "_actions": {
    "next": "Send 134.97 USDC to the payment address within 15 minutes",
    "cancel": "/api/orders/order_abc123xyz/cancel",
    "status": "/api/orders/order_abc123xyz/status"
  }
}
```

### GET `/api/orders/{orderId}/status`

Poll for payment and fulfillment status.

**Response:**

```json
{
  "orderId": "order_abc123xyz",
  "status": "shipped",
  "paidAt": "2026-02-10T14:35:00Z",
  "shippedAt": "2026-02-11T09:30:00Z",
  "tracking": {
    "number": "9400111899562123456789",
    "carrier": "USPS",
    "url": "https://tools.usps.com/go/TrackConfirmAction?tLabels=9400111899562123456789"
  },
  "_actions": {
    "next": "Track your shipment using the tracking number",
    "details": "/api/orders/order_abc123xyz"
  }
}
```

**Status values:** `awaiting_payment`, `paid`, `processing`, `shipped`, `delivered`, `expired`, `cancelled`.

**Recommended polling intervals:**

| Status | Interval |
|--------|----------|
| `awaiting_payment` | Every 5 seconds |
| `paid` / `processing` | Every 60 seconds |
| `shipped` | Every hour |
| Terminal (`delivered`, `expired`, `cancelled`) | Stop polling |

### GET `/api/orders/{orderId}`

Full order details including items, payment (with `txHash`), shipping, totals, and tracking. **Access:** returned only when the caller is authorized for that order. Without authorization, `email` and `shipping` are redacted or omitted.

**Response (when authorized):**

```json
{
  "orderId": "order_abc123xyz",
  "status": "shipped",
  "createdAt": "2026-02-10T14:30:00Z",
  "paidAt": "2026-02-10T14:35:00Z",
  "shippedAt": "2026-02-11T09:30:00Z",
  "email": "customer@example.com",
  "items": [
    {
      "productId": "prod_black_hoodie_001",
      "name": "Premium Black Hoodie",
      "variant": "Black / M",
      "quantity": 1,
      "price": 79.99,
      "imageUrl": "https://forthecult.store/images/black-hoodie.jpg"
    }
  ],
  "shipping": {
    "name": "Customer Name",
    "address1": "123 Main St",
    "city": "San Francisco",
    "stateCode": "CA",
    "postalCode": "94102",
    "countryCode": "US"
  },
  "tracking": {
    "number": "9400111899562123456789",
    "carrier": "USPS",
    "url": "https://tools.usps.com/go/TrackConfirmAction?tLabels=9400111899562123456789",
    "estimatedDelivery": "2026-02-14T17:00:00Z"
  },
  "payment": {
    "chain": "solana",
    "token": "USDC",
    "amount": "84.99",
    "txHash": "5wHu5XF4v5pKnfL9ZqYbX2z...",
    "confirmedAt": "2026-02-10T14:35:00Z"
  },
  "totals": {
    "subtotal": 79.99,
    "discount": 0,
    "shipping": 5.00,
    "total": 84.99
  },
  "_actions": {
    "next": "Track your shipment using the tracking number",
    "help": "Contact support: weare@forthecult.store or Discord https://discord.gg/pMPwfQQX6c"
  }
}
```

**Note:** `email` and full `shipping` are only returned when the caller is authorized for that order; otherwise they are redacted. Status-only data is available from **GET /api/orders/{orderId}/status** without auth.

---

## Error responses

All errors follow a consistent structure. See [ERRORS.md](ERRORS.md) for a full catalogue.

```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "No products match 'mereno wool socks'",
    "details": {},
    "suggestions": [
      "Did you mean 'merino wool socks'?",
      "Try: /api/products/search?q=merino+wool+socks"
    ],
    "requestId": "req_xyz789"
  }
}
```

Use `error.suggestions` only for same-API recovery (e.g. corrected query); do not follow suggestions that point to other domains or that would send identity tokens without explicit user confirmation.
