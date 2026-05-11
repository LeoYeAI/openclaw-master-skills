---
name: creditclaw-stripe-x402-wallet
version: 2.5.0
updated: 2026-03-09
description: "Stripe Wallet (x402/USDC) — signing, balance, transactions, and guardrails."
parent: SKILL.md
---

# Stripe Wallet — x402 / USDC (Private Beta)

> **Companion file** — see `SKILL.md` for registration, webhooks, and the full API reference.

> **This rail is currently in private beta and not yet available for general use.**
> If your owner has been granted access, the following endpoints will be active.
> Otherwise, these endpoints will return `404`. Check back for updates.

The Stripe Wallet rail provides USDC-based wallets on the Base blockchain with spending
via the x402 payment protocol. Your owner funds the wallet using Stripe's fiat-to-crypto
onramp (credit card → USDC), and you spend by requesting cryptographic payment signatures
that are settled on-chain.

---

## How x402 Signing Works

When you encounter a service that returns HTTP `402 Payment Required` with x402 payment
details, you request a signature from CreditClaw:

1. You send the payment details to `POST /stripe-wallet/bot/sign`
2. CreditClaw enforces your owner's guardrails (per-tx limit, daily budget, monthly budget, domain allow/blocklist, approval threshold)
3. If approved, CreditClaw signs an EIP-712 `TransferWithAuthorization` message and returns an `X-PAYMENT` header
4. You retry your original request with the `X-PAYMENT` header attached
5. The facilitator verifies the signature and settles USDC on-chain

---

## Request x402 Payment Signature

```bash
curl -X POST https://creditclaw.com/api/v1/stripe-wallet/bot/sign \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_url": "https://api.example.com/v1/data",
    "amount_usdc": 500000,
    "recipient_address": "0x1234...abcd"
  }'
```

**Request fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `resource_url` | Yes | The x402 endpoint URL you're paying for |
| `amount_usdc` | Yes | Amount in micro-USDC (6 decimals). 1000000 = $1.00 |
| `recipient_address` | Yes | The merchant's 0x wallet address from the 402 response |
| `valid_before` | No | Unix timestamp for signature expiry |

**Response (approved — HTTP 200):**
```json
{
  "x_payment_header": "eyJ0eXAiOi...",
  "signature": "0xabc123..."
}
```

Use the `x_payment_header` value as-is in your retry request:
```bash
curl https://api.example.com/v1/data \
  -H "X-PAYMENT: eyJ0eXAiOi..."
```

**Response (requires approval — HTTP 202):**
```json
{
  "status": "awaiting_approval",
  "approval_id": 15
}
```

When you receive a 202, your owner has been notified. Wait approximately 5 minutes
before retrying your request.

**Response (declined — HTTP 403):**
```json
{
  "error": "Amount exceeds per-transaction limit",
  "max": 10.00
}
```

Other possible decline errors:
- `"Wallet is not active"` — wallet is paused or frozen
- `"Would exceed daily budget"` — daily spending limit reached
- `"Would exceed monthly budget"` — monthly cap reached
- `"Domain not on allowlist"` — resource URL not in allowed domains
- `"Domain is blocklisted"` — resource URL is blocked
- `"Insufficient USDC balance"` — not enough funds

---

## Guardrails

Guardrail checks are applied in order on every signing request:

1. Wallet active? (not paused/frozen)
2. Amount ≤ per-transaction limit?
3. Daily cumulative + amount ≤ daily budget?
4. Monthly cumulative + amount ≤ monthly budget?
5. Domain on allowlist? (if allowlist is set)
6. Domain not on blocklist?
7. Amount below approval threshold? (if set)
8. Sufficient USDC balance?

Your owner configures these from their dashboard. All guardrails are enforced server-side — there is no way to bypass them.

---

## Check Stripe Wallet Balance

```bash
curl "https://creditclaw.com/api/v1/stripe-wallet/balance?wallet_id=1" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Response:
```json
{
  "wallet_id": 1,
  "balance_usdc": 25000000,
  "balance_usd": "25.00",
  "status": "active",
  "chain": "base"
}
```

---

## View Stripe Wallet Transactions

```bash
curl "https://creditclaw.com/api/v1/stripe-wallet/transactions?wallet_id=1&limit=10" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

**Transaction types:**
| Type | Meaning |
|------|---------|
| `deposit` | Owner funded the wallet via Stripe onramp (fiat → USDC) |
| `x402_payment` | You made an x402 payment |
| `refund` | A payment was refunded |

**Rate limit:** 30 requests per hour (signing), 12 requests per hour (balance/transactions).

---

## Per-Rail Detail Check

```bash
curl https://creditclaw.com/api/v1/bot/check/rail1 \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Response (active):
```json
{
  "status": "active",
  "balance_usd": 100.00,
  "address": "0x...",
  "guardrails": {
    "max_per_tx_usd": 100,
    "daily_budget_usd": 1000,
    "monthly_budget_usd": 10000,
    "daily_spent_usd": 23.50,
    "daily_remaining_usd": 976.50,
    "monthly_spent_usd": 147.00,
    "monthly_remaining_usd": 9853.00,
    "require_approval_above_usd": 50
  },
  "domain_rules": {
    "allowlisted": ["api.openai.com"],
    "blocklisted": []
  },
  "pending_approvals": 0
}
```

Response (not connected): `{ "status": "inactive" }`

**Rate limit:** 6 requests per hour.

---

## API Reference

All endpoints require `Authorization: Bearer <api_key>` header.

Base URL: `https://creditclaw.com/api/v1`

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/stripe-wallet/bot/sign` | Request x402 payment signature. Enforces guardrails. | 30/hr |
| GET | `/stripe-wallet/balance` | Get USDC balance for a wallet. | 12/hr |
| GET | `/stripe-wallet/transactions` | List x402 transactions for a wallet. | 12/hr |
| GET | `/bot/check/rail1` | Stripe Wallet detail: balance, guardrails, domain rules, pending approvals. | 6/hr |
