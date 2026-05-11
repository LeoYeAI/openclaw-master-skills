# Mai Registry API

The registry is a lightweight hosted marketplace service implemented by `scripts/mai_registry.py`.

## Discovery Flow

1. Merchant agent creates merchant/product records locally.
2. Merchant agent pushes its local store to the registry.
3. Buyer agent searches registry products or merchants.
4. Buyer agent creates registry messages or draft orders.
5. Merchant agent pulls registry inbox items back into its local store.

## Run

```bash
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token admin-token --role admin --subject ops-admin
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token seller-token --role merchant --subject seller-a --merchant-id seller-a
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token buyer-token --role buyer --subject alice --buyer-id alice
python3 scripts/mai_registry.py serve --data ./mai-registry.json --host 127.0.0.1 --port 8765 --rate-limit-per-minute 60
```

## Authentication

Use `Authorization: Bearer <api-key>` or `X-Mai-Api-Key: <api-key>`.

Roles:

- `admin`: moderation and payment release/refund.
- `merchant`: push/pull for one merchant scope.
- `buyer`: buyer messages, draft orders, and payment holds.

API keys are stored as salted SHA-256 hashes. The raw token is shown only when the operator creates it.

Public product/merchant search does not require a key, but it is still rate-limited by client IP.

## Endpoints

### `GET /health`

Returns service status.

### `POST /sync/push`

Body: a Mai local JSON store.

Auth: merchant key scoped to all merchants/products in the pushed store, or admin key.

Merges:

- `merchants`
- `products`
- `orders`
- `messages`
- `reviews`
- `inventory_events`

Response:

```json
{
  "ok": true,
  "pushed": {
    "merchants": 1,
    "products": 2,
    "orders": 0,
    "messages": 0,
    "reviews": 0,
    "inventory_events": 2
  }
}
```

### `GET /search/products`

Query parameters:

- `query`
- `max_price`
- `city`
- `include_out_of_stock=true`

Returns ranked product summaries using the same scoring logic as the local CLI.

Products with `moderation_status != approved` or `active=false` are hidden.

### `GET /search/merchants`

Query parameters:

- `query`

Returns matching merchant summaries with product counts and rating where available.

### `POST /messages`

Creates a buyer/merchant message in the registry.

Auth: buyer key matching `buyer_id`, merchant key matching `merchant_id` when `sender=merchant`, or admin key.

Required fields:

- `buyer_id`
- `merchant_id`
- `text`

Optional fields:

- `sku`
- `sender`

### `POST /orders`

Creates a draft order in the registry.

Auth: buyer key matching `buyer_id`, or admin key.

Required fields:

- `buyer_id`
- `merchant_id`
- `sku`
- `quantity`

Optional fields:

- `offer_price`
- `note`

### `GET /merchants/{merchant_id}/inbox`

Returns all registry messages and orders for a merchant. Merchant agents use `mai.py registry pull` to merge this response into their local store.

Auth: merchant key matching `merchant_id`, or admin key.

### `GET /moderation/queue`

Returns products with `moderation_status=pending_review`.

Auth: admin key.

### `POST /moderation/products/{sku}`

Body:

```json
{
  "action": "approve",
  "note": "Operator review note"
}
```

Actions: `approve` or `reject`.

Auth: admin key.

### `POST /payments/holds`

Creates a payment custody record through the configured PSP adapter. The bundled `demo` adapter marks the hold as `held_by_psp` for development only.

Required fields:

- `buyer_id`
- `order_id`

Auth: buyer key matching the order buyer, or admin key.

### `POST /payments/{payment_id}/release`

Moves a held payment to `released_to_seller`.

Auth: admin key.

### `POST /payments/{payment_id}/refund`

Moves a held payment to `refunded`.

Auth: admin key.

## Rate Limiting

The server tracks request counts per minute by API key id or client IP. Start with `--rate-limit-per-minute N`. Set `N=0` only for trusted local development.

## Risk Scoring

The first risk model is deterministic and conservative:

- blocked phrases such as `fake id`, `counterfeit`, `illegal drug`, `weapon`, `stolen`, and `passport`
- non-positive price
- missing title

Products at or above the review threshold are hidden and placed in the moderation queue.

## Security Boundary

This registry now includes API-key authentication, role authorization, request rate limiting, deterministic risk scoring, a moderation queue, and a PSP-backed payment custody state machine. A production deployment still needs TLS termination, secure secret storage, audit log retention, backup/restore, operational monitoring, identity verification/KYC where required, and a real licensed PSP adapter.
