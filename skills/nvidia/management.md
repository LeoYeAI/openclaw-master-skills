---
name: creditclaw-management
parent: skill.md
description: Cross-rail wallet management — top-ups, transaction history
---

# CreditClaw — Wallet Management

> **Companion file.** This document covers cross-rail wallet operations.
> For the full API reference and registration instructions, see [SKILL.md](https://creditclaw.com/skill.md).

**Base URL:** `https://creditclaw.com/api/v1`

**All requests require:** `Authorization: Bearer <your-api-key>`

---

## Request a Top-Up From Your Owner

When your balance is low, ask your human if they'd like you to request a top-up:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/wallet/topup-request \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_usd": 25.00,
    "reason": "Need funds to purchase API access for research task"
  }'
```

Response:
```json
{
  "topup_request_id": 7,
  "status": "sent",
  "amount_usd": 25.00,
  "owner_notified": true,
  "message": "Your owner has been emailed a top-up request."
}
```

**What happens:**
- Your owner gets an email notification with the requested amount and reason.
- They log in to their dashboard and fund your wallet using their saved card.
- Once payment completes, your balance updates automatically.

Poll `GET /bot/status` to see when the balance increases across any rail.

**Rate limit:** 3 requests per hour.

---

## View Transaction History

```bash
curl "https://creditclaw.com/api/v1/bot/wallet/transactions?limit=10" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Response:
```json
{
  "transactions": [
    {
      "id": 1,
      "type": "topup",
      "amount_usd": 25.00,
      "description": "Owner top-up",
      "created_at": "2026-02-06T14:30:00Z"
    },
    {
      "id": 2,
      "type": "purchase",
      "amount_usd": 5.99,
      "description": "OpenAI API: GPT-4 API credits",
      "created_at": "2026-02-06T15:12:00Z"
    },
    {
      "id": 3,
      "type": "payment_received",
      "amount_usd": 10.00,
      "description": "Research report: Q4 market analysis",
      "created_at": "2026-02-06T16:45:00Z"
    }
  ]
}
```

**Transaction types:**
| Type | Meaning |
|------|---------|
| `topup` | Owner funded your wallet |
| `purchase` | You spent from your wallet |
| `payment_received` | Someone paid your payment link |

Default limit is 50, max is 100.

**Rate limit:** 12 requests per hour.

---

## Approval Flows

Approval flows are rail-specific. Each payment rail has its own approval mechanism and status progression. See the relevant rail documentation for details:

- **Encrypted Card (Rail 5):** [encrypted-card.md](https://creditclaw.com/encrypted-card.md)
- **Stripe Wallet (x402):** [stripe-x402-wallet.md](https://creditclaw.com/stripe-x402-wallet.md)
