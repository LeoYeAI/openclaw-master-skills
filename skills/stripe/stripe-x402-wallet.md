# Stripe x402 Wallet — Day-to-Day Guide

Companion to [skill.md](https://creditclaw.com/creditcard/skill.md). Covers how to make payments using the Stripe Wallet rail (Rail 1) with the x402 payment protocol.

> **This rail is currently in private beta and not yet available for general use.**
> If your owner has been granted access, the following endpoints will be active.
> Otherwise, these endpoints will return `404`.

**Prerequisite:** Your owner must have a Stripe Wallet set up with USDC balance. Check `GET /stripe-wallet/balance` to verify.

---

## How It Works

The Stripe Wallet rail provides USDC-based wallets on the Base blockchain. Your owner funds the wallet using Stripe's fiat-to-crypto onramp (credit card to USDC), and you spend by requesting cryptographic payment signatures that are settled on-chain.

**Use this rail for:** x402-enabled services, agent-to-agent payments, and any service that returns HTTP `402 Payment Required` with x402 payment details.

**Endpoint:** `POST /stripe-wallet/bot/sign`

---

## x402 Signing Flow

When you encounter a service that returns HTTP `402 Payment Required` with x402 payment details:

1. You send the payment details to `POST /stripe-wallet/bot/sign`
2. CreditClaw enforces your owner's guardrails (per-tx limit, daily budget, monthly budget, domain allow/blocklist, approval threshold)
3. If approved, CreditClaw signs an EIP-712 `TransferWithAuthorization` message and returns an `X-PAYMENT` header
4. You retry your original request with the `X-PAYMENT` header attached
5. The facilitator verifies the signature and settles USDC on-chain

### Request x402 Payment Signature

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

### Request Fields

| Field | Required | Description |
|-------|----------|-------------|
| `resource_url` | Yes | The x402 endpoint URL you're paying for |
| `amount_usdc` | Yes | Amount in micro-USDC (6 decimals). 1000000 = $1.00 |
| `recipient_address` | Yes | The merchant's 0x wallet address from the 402 response |
| `valid_before` | No | Unix timestamp for signature expiry |

### Response (Approved — HTTP 200)

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

### Response (Requires Approval — HTTP 202)

```json
{
  "status": "awaiting_approval",
  "approval_id": 15
}
```

When you receive a 202, your owner has been notified. Poll the approvals endpoint or wait approximately 5 minutes before retrying.

### Response (Declined — HTTP 403)

```json
{
  "error": "Amount exceeds per-transaction limit",
  "max": 10.00
}
```

---

## Guardrail Checks

CreditClaw evaluates these checks in order before signing:

1. Wallet active? (not paused/frozen)
2. Amount ≤ per-transaction limit?
3. Daily cumulative + amount ≤ daily budget?
4. Monthly cumulative + amount ≤ monthly budget?
5. Domain on allowlist? (if allowlist is set)
6. Domain not on blocklist?
7. Amount below approval threshold? (if set)
8. Sufficient USDC balance?

---

## Check Balance

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

## View Transactions

```bash
curl "https://creditclaw.com/api/v1/stripe-wallet/transactions?wallet_id=1&limit=10" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

| Type | Meaning |
|------|---------|
| `deposit` | Owner funded the wallet via Stripe onramp (fiat to USDC) |
| `x402_payment` | You made an x402 payment |
| `refund` | A payment was refunded |

---

## Common Errors

| Error | What to Do |
|-------|-----------|
| 403 — `Wallet is not active` | Wallet paused or frozen by owner |
| 403 — `Amount exceeds per-transaction limit` | Reduce the payment amount or ask owner to raise the limit |
| 403 — `Would exceed daily budget` | Daily spending limit reached. Wait until tomorrow or ask owner to adjust. |
| 403 — `Would exceed monthly budget` | Monthly cap reached. Ask owner to adjust. |
| 403 — `Domain not on allowlist` | The service URL isn't in your owner's allowed domains |
| 403 — `Domain is blocklisted` | The service URL is explicitly blocked |
| 402 — `Insufficient USDC balance` | Not enough funds. Ask owner to fund via Stripe onramp. |
| 404 — endpoints return 404 | This rail is in private beta and not enabled for your account |

---

## Quick Reference

| Item | Value |
|------|-------|
| Signing endpoint | `POST /stripe-wallet/bot/sign` |
| Balance check | `GET /stripe-wallet/balance?wallet_id=X` |
| Transactions | `GET /stripe-wallet/transactions?wallet_id=X` |
| Amount format | Micro-USDC (6 decimals, e.g. 1000000 = $1.00) |
| Chain | Base |
| Rate limit (signing) | 30/hr |
| Rate limit (balance/tx) | 12/hr |
| Status | Private Beta |
