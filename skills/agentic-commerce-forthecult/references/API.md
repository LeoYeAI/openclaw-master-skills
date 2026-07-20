# For the Cult API — Agentic Commerce Endpoint Reference

Base URL: **`https://forthecult.store`** — all paths below are relative to this (e.g. **GET /api/health**).

No API key or environment variables required. No authentication is needed for discovery, search, checkout, and order status. Order details (email, shipping) require session owner, admin, or confirmation token. Admin endpoints (`/api/admin/*`) are not public. **Identity header:** `X-Moltbook-Identity` is optional and only for agent-only endpoints (`/api/agent/me`, `/api/agent/me/orders`, `/api/agent/me/preferences`); it is not declared in `requires.env` and must only be used when the agent runtime explicitly supplies it—do not send it for normal store operations. This API is purpose-built for Agentic Commerce — AI agents autonomously discovering, purchasing, and tracking physical goods.

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

### GET `/api/agent/me`

Returns the verified Moltbook agent profile when the caller is an authenticated Moltbook agent. **Optional:** only call this endpoint when the agent runtime explicitly supplies an `X-Moltbook-Identity` token. Do not send or infer this header for normal store operations (browsing, search, checkout, order status by ID). Not declared in `requires.env` — the header is supplied by the runtime when available.

**Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `X-Moltbook-Identity` | Yes (for this endpoint) | Moltbook identity token from agent runtime; use only when runtime supplies it |

**Response:** Agent profile object (name, permissions, capabilities).

### GET `/api/chains`

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

Semantic search with filters. Supports natural-language queries.

**Query parameters:**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `q` | string | Yes | — | Search query (natural language supported) |
| `category` | string | No | — | Category slug filter |
| `priceMin` | number | No | — | Minimum USD price |
| `priceMax` | number | No | — | Maximum USD price |
| `inStock` | boolean | No | — | Only in-stock items |
| `limit` | integer | No | 20 | Results per page (max 100) |
| `offset` | integer | No | 0 | Pagination offset |

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

**Important:** Use the `id` field from products when creating orders. Use the `slug` field when fetching product details.

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

Create an order and generate a payment request. See [CHECKOUT-FIELDS.md](CHECKOUT-FIELDS.md) for complete field specification.

**Request body (JSON):**

```json
{
  "items": [
    { "productId": "prod_black_hoodie_001", "variantId": "var_hoodie_m_black", "quantity": 1 },
    { "productId": "prod_top_blast_coffee", "quantity": 2 }
  ],
  "email": "customer@example.com",
  "payment": { "chain": "solana", "token": "USDC" },
  "shipping": {
    "name": "Customer Name",
    "address1": "123 Main St",
    "address2": "Apt 4B",
    "city": "San Francisco",
    "stateCode": "CA",
    "zip": "94102",
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
    "tier": "Gold",
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

Full order details including items, payment (with `txHash`), shipping, totals, and tracking. **Access:** session owner, admin, or `?ct=<confirmationToken>` for recent orders (&lt;1h). Without authorization, `email` and `shipping` are redacted or omitted.

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
    "zip": "94102",
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
    "help": "Contact support: weare@forthecult.store"
  }
}
```

**Note:** `email` and full `shipping` are only returned when the caller is the order owner (session or valid `ct`) or admin; otherwise they are redacted. Status-only data is available from **GET /api/orders/{orderId}/status** without auth.

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
