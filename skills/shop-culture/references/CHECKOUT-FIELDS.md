# Checkout Request Body — POST `/checkout`

Complete field specification for creating an order. This is the core Agentic Commerce endpoint — where an agent converts product discovery into a real purchase.

---

## Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items` | array | **Yes** | Line items to purchase |
| `email` | string | **Yes** | Customer email for order confirmation |
| `payment` | object | **Yes** | Cryptocurrency, credit, or debit card for payment |
| `shipping` | object | **Yes** | Delivery address |
| `wallet` / `walletAddress` | string | No | Solana wallet for CULT tier discount (ownership verified) |
| `walletMessage` | string | No | Message from `GET /api/checkout/wallet-verify-message` (signed-message verification) |
| `walletSignature` | string | No | Base64 signature of `walletMessage` by the wallet |
| `walletSignatureBase58` | string | No | Base58 signature of `walletMessage` (alternative to `walletSignature`) |

---

## `items[]`

An array of one or more products to order.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `productId` | string | **Yes** | Product `id` from `GET /products/search` or `GET /products/{slug}`. **Never use placeholder or example IDs.** |
| `variantId` | string | No | Variant `id` from product detail `variants[]`. Required when the product has size/color variants. |
| `quantity` | integer | **Yes** | Number of units. Minimum: 1. |

**Multi-item example:**

```json
"items": [
  { "productId": "prod_black_hoodie_001", "variantId": "var_hoodie_m_black", "quantity": 1 },
  { "productId": "prod_top_blast_coffee", "quantity": 2 }
]
```

---

## `payment`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `chain` | string | **Yes** | Blockchain network ID |
| `token` | string | **Yes** | Token symbol on that chain |

**Supported values** (verify with `GET /payment-methods` response `chains` before checkout):

| Chain | Tokens |
|-------|--------|
| `solana` | `SOL`, `USDC`, `USDT`, `CULT` |
| `ethereum` | `ETH`, `USDC`, `USDT` |
| `base` | `ETH`, `USDC` |
| `polygon` | `MATIC`, `USDC` |
| `arbitrum` | `ETH`, `USDC` |
| `bitcoin` | `BTC` |
| `dogecoin` | `DOGE` |
| `monero` | `XMR` |

**Recommendation:** Use `USDC` or `USDT` for stable pricing. Volatile payment methods (SOL, ETH, BTC) are priced at the moment of order creation.

---

## `shipping`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | **Yes** | Recipient full name |
| `address1` | string | **Yes** | Street address |
| `address2` | string | No | Apartment, suite, unit, etc. |
| `city` | string | **Yes** | City |
| `stateCode` | string | **Yes** | State or region code (e.g. `CA`, `NY`, `ON`) |
| `postalCode` | string | **Yes** | Postal / ZIP code |
| `countryCode` | string | **Yes** | 2-letter ISO 3166-1 alpha-2 code (e.g. `US`, `CA`, `GB`) |

**Important field names:** Use `address1` (not `line1`), `stateCode` (not `state`), `postalCode` (not `zip`), `countryCode` (not `country`). Using incorrect field names will result in a validation error.

---

## `wallet` / `walletAddress` (optional)

Solana wallet address for CULT member tier discounts. **Ownership is verified** in one of two ways:

1. **Linked account** — The requester is authenticated and this wallet is linked to their account.
2. **Signed message** — Send `walletMessage` (from `GET /api/checkout/wallet-verify-message`) and `walletSignature` or `walletSignatureBase58` (the wallet’s signature of that message). Message is valid for 5 minutes.

If you send a wallet without verification, the API returns `400` with `code: "WALLET_VERIFICATION_REQUIRED"`. The response `discount` object shows the applied tier, percentage, and amount saved.

---

## Complete single-item example

```json
{
  "items": [
    { "productId": "prod_top_blast_coffee", "quantity": 1 }
  ],
  "email": "customer@example.com",
  "payment": { "chain": "solana", "token": "USDC" },
  "shipping": {
    "name": "Satoshi Nakamoto",
    "address1": "123 Main St",
    "city": "San Francisco",
    "stateCode": "CA",
    "postalCode": "94102",
    "countryCode": "US"
  }
}
```

## Complete multi-item example with wallet discount

CULT tier discounts use a **Solana** wallet (CULT is on Solana); the wallet must be **verified** (linked to the user’s account or signed via `GET /api/checkout/wallet-verify-message`). Customer payment can be on any supported chain (e.g. Ethereum). Example with signed-message verification:

```json
{
  "items": [
    { "productId": "prod_black_hoodie_001", "variantId": "var_hoodie_l_black", "quantity": 1 },
    { "productId": "prod_top_blast_coffee", "quantity": 3 }
  ],
  "email": "holder@example.com",
  "payment": { "chain": "ethereum", "token": "USDC" },
  "shipping": {
    "name": "Ada Lovelace",
    "address1": "456 Oak Avenue",
    "address2": "Suite 200",
    "city": "Los Angeles",
    "stateCode": "CA",
    "postalCode": "90001",
    "countryCode": "US"
  },
  "wallet": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "walletMessage": "FortheCult tier verification\n2026-02-10T14:30:00Z",
  "walletSignatureBase58": "<signature from wallet of walletMessage>"
}
```

If the wallet is **linked** to the user’s account (authenticated), you can omit `walletMessage` and `walletSignatureBase58`.

---

## Checkout response

```json
{
  "orderId": "order_abc123xyz",
  "payment": {
    "chain": "solana",
    "token": "USDC",
    "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "amount": "29.99",
    "reference": "FortheCult_order_abc123xyz",
    "qrCode": "data:image/png;base64,iVBOR..."
  },
  "discount": null,
  "expiresAt": "2026-02-10T15:00:00Z",
  "statusUrl": "/api/orders/order_abc123xyz/status",
  "_actions": {
    "next": "Send 29.99 USDC to the payment address within 15 minutes",
    "cancel": "/api/orders/order_abc123xyz/cancel",
    "status": "/api/orders/order_abc123xyz/status"
  }
}
```

**After creating an order:**

1. Tell the user to send exactly `payment.amount` of `payment.token` to `payment.address` on `payment.chain`.
2. Display the QR code (`payment.qrCode`) if the client supports images.
3. Warn that the payment window expires at `expiresAt` (~15 minutes).
4. Begin polling `GET /orders/{orderId}/status` — every 5 seconds while `awaiting_payment`.
5. If the order expires, inform the user and offer to create a new order.

**Never use placeholder product IDs.** Always obtain `productId` from a prior `GET /products/search` or `GET /products/{slug}` response.
