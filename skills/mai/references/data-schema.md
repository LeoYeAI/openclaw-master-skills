# Mai Data Schema

Mai stores a JSON document at `~/.local/share/mai/mai.json` by default. Use `--data` to point at another file.

## Top Level

```json
{
  "version": "1.1.2",
  "sync": {
    "mode": "local-first",
    "schema_version": "1.1.2",
    "remote_marketplace_url": "",
    "pending_events": []
  },
  "merchants": {},
  "products": {},
  "orders": {},
  "messages": [],
  "reviews": [],
  "inventory_events": []
}
```

## Merchant

Keyed by merchant id:

```json
{
  "id": "seller-a",
  "name": "West Lake Tea",
  "city": "Hangzhou",
  "contact": "wechat:westlake",
  "tags": ["tea", "gift"],
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## Product

Keyed by SKU:

```json
{
  "sku": "tea-a",
  "merchant_id": "seller-a",
  "title": "Longjing Gift Box",
  "description": "Fresh spring tea gift box",
  "category": "tea",
  "tags": ["longjing", "gift"],
  "price": 88.0,
  "currency": "CNY",
  "stock": 5,
  "shipping": "same-city courier",
  "active": true
}
```

## Order

Keyed by order id:

```json
{
  "id": "ORD-0001",
  "buyer_id": "alice",
  "merchant_id": "seller-a",
  "sku": "tea-a",
  "quantity": 2,
  "requested_unit_price": 86.0,
  "quoted_unit_price": 86.0,
  "currency": "CNY",
  "status": "paid_external",
  "payment_url": "https://pay.example/orders/ORD-0001",
  "payment_reference": "wx-20260503-1",
  "terms": "External payment; seller ships after payment reference is recorded.",
  "tracking": "SF123",
  "stock_reserved": true,
  "history": []
}
```

## Sync Contract

`sync.pending_events` is an append-only local outbox. A future hosted marketplace can upload these events and clear them after acknowledgement. Consumers should treat the JSON file as the source of truth for the local agent and events as a replay/sync aid, not as a complete event-sourced ledger.

## Registry Store

The registry uses the same top-level schema as local stores, plus:

```json
{
  "registry": {
    "service": "mai-registry",
    "version": "1.1.2",
    "created_at": "ISO-8601"
  }
}
```

Merchant agents push local snapshots into the registry. Buyer agents create registry messages and draft orders. Merchant agents pull inbox data and merge it back into local `messages` and `orders`.

## Public Registry Extensions

```json
{
  "auth": {
    "api_keys": [
      {
        "id": "KEY-0001",
        "role": "merchant",
        "subject": "seller-a",
        "merchant_id": "seller-a",
        "buyer_id": "",
        "salt": "hex",
        "token_hash": "sha256",
        "active": true
      }
    ]
  },
  "rate_limits": {
    "KEY-0001:29629744": {
      "count": 3,
      "minute": 29629744
    }
  },
  "moderation": {
    "decisions": []
  },
  "payments": {
    "PAY-0001": {
      "id": "PAY-0001",
      "order_id": "ORD-0001",
      "buyer_id": "alice",
      "merchant_id": "seller-a",
      "amount": 176.0,
      "currency": "CNY",
      "provider": "demo",
      "provider_reference": "demo-hold-PAY-0001",
      "checkout_url": "demo://mai/payments/PAY-0001",
      "status": "held_by_psp",
      "history": []
    }
  }
}
```

API key raw tokens must not be stored. Payment records track PSP state only; they are not evidence that Mai itself holds funds.
