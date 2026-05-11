---
name: creditclaw-management
version: 2.6.0
updated: 2026-03-13
description: "Bot self-management — transaction history, profile updates."
parent: SKILL.md
api_base: https://creditclaw.com/api/v1
credentials: [CREDITCLAW_API_KEY]
---

# CreditClaw — Management

> **Companion file.** This document covers bot self-management operations.
> For the full API reference and registration instructions, see `SKILL.md`.

**Base URL:** `https://creditclaw.com/api/v1`

**All requests require:** `Authorization: Bearer <your-api-key>`

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
| `purchase` | You spent from your wallet |
| `payment_received` | Someone paid your payment link |

Default limit is 50, max is 100.

**Rate limit:** 12 requests per hour.

---

## View & Update Your Profile

Check your current profile:

```bash
curl https://creditclaw.com/api/v1/bot/profile \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Response:
```json
{
  "bot_name": "ShopperBot",
  "description": "Performs web research tasks for hire",
  "callback_url": "https://my-gateway.com/hooks/creditclaw",
  "webhook_status": "active",
  "webhook_fail_count": 0,
  "default_rail": "sub_agent_cards",
  "created_at": "2026-02-01T10:00:00Z",
  "claimed_at": "2026-02-01T12:00:00Z"
}
```

Update your name, description, or webhook URL:

```bash
curl -X PATCH https://creditclaw.com/api/v1/bot/profile \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_name": "ResearchBot",
    "description": "AI research assistant",
    "callback_url": "https://new-endpoint.com/hooks/creditclaw"
  }'
```

All fields are optional — include only the ones you want to change. If you set a new `callback_url`, the response includes a one-time `webhook_secret` for verifying webhook signatures. Save it immediately in your platform's secure secrets manager. Never log, expose, or share your webhook secret.
