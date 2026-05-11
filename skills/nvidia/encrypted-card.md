---
name: creditclaw-encrypted-card
version: 2.5.0
updated: 2026-03-09
description: "My Card (Rail 5) — secure checkout flow for CreditClaw bots."
companion_of: https://creditclaw.com/skill.md
api_base: https://creditclaw.com/api/v1
credentials: [CREDITCLAW_API_KEY]
---

# My Card (Rail 5)

> **This file is a companion to [skill.md](https://creditclaw.com/skill.md).**
> For registration, security details, webhooks, spending permissions, and the full API reference, see the main skill file.

Rail 5 lets your owner securely share their card details with you. Card details are protected
with AES-256-GCM encryption. You decrypt the card details for a single transaction using a
one-time key from the API, and the decrypted data is discarded immediately after checkout.

**Base URL:** `https://creditclaw.com/api/v1`

---

## Making a Purchase

This is the core transaction flow. When you need to buy something, follow the checkout steps
below. Decrypted card details should only exist in memory for the duration of the checkout
and must be discarded immediately after.

### How It Works

```
1. You decide a purchase is needed (and it's within your spending rules)
2. You call POST /bot/rail5/checkout with the merchant and amount details
3. CreditClaw checks guardrails — if within limits, it approves immediately
   If above threshold, your owner gets an approval request (via dashboard or email)
4. Once approved, follow the checkout_steps returned by the API
5. Call POST /bot/rail5/key to get the one-time decryption key
6. Decrypt the card details using AES-256-GCM and complete checkout at the merchant
7. Call POST /bot/rail5/confirm with success or failure
8. Discard decrypted card data — it must not persist beyond this checkout
9. Announce the result to your human
```

### Step 1: Request Checkout

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/checkout \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_name": "DigitalOcean",
    "merchant_url": "https://cloud.digitalocean.com/billing",
    "item_name": "Droplet hosting - 1 month",
    "amount_cents": 1200,
    "category": "cloud_compute"
  }'
```

**Request fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `merchant_name` | Yes | Merchant name (1-200 chars) |
| `merchant_url` | Yes | Merchant website URL |
| `item_name` | Yes | What you're buying |
| `amount_cents` | Yes | Amount in cents (integer) |
| `category` | No | Spending category |

**Response (approved):**
```json
{
  "approved": true,
  "checkout_id": "r5chk_abc123",
  "checkout_steps": [
    "Call POST /api/v1/bot/rail5/key with { \"checkout_id\": \"r5chk_abc123\" } to get the decryption key.",
    "Decrypt the encrypted card data using AES-256-GCM with the key, IV, and tag from the API response.",
    "Use the decrypted card details to complete checkout at DigitalOcean.",
    "Call POST /api/v1/bot/rail5/confirm with { \"checkout_id\": \"r5chk_abc123\", \"status\": \"success\" } when done.",
    "If checkout fails, call confirm with { \"status\": \"failed\" } instead.",
    "Discard all decrypted card data. Announce the result."
  ],
  "spawn_payload": {
    "task": "You are a checkout agent...",
    "cleanup": "delete",
    "runTimeoutSeconds": 300,
    "label": "checkout-digitalocean"
  }
}
```

**Response (requires owner approval):**
```json
{
  "approved": false,
  "status": "pending_approval",
  "checkout_id": "r5chk_abc123",
  "message": "Amount exceeds auto-approve threshold. Your owner has been notified.",
  "expires_in_minutes": 15
}
```

### Checkout Status Polling

If you receive `pending_approval`, poll for the result:

```bash
curl "https://creditclaw.com/api/v1/bot/rail5/checkout/status?checkout_id=r5chk_abc123" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Response:
```json
{
  "checkout_id": "r5chk_abc123",
  "status": "pending_approval",
  "merchant_name": "DigitalOcean",
  "item_name": "Droplet hosting - 1 month",
  "amount_cents": 1200,
  "key_delivered": false,
  "confirmed_at": null,
  "created_at": "2026-03-09T12:00:00.000Z"
}
```

**Status values:**
| Status | Meaning |
|--------|---------|
| `pending_approval` | Owner hasn't responded yet — poll again in 30 seconds |
| `approved` | Owner approved — proceed with checkout |
| `rejected` | Owner declined — do not proceed |
| `expired` | 15-minute approval window passed — try again if needed |
| `completed` | Checkout confirmed successful |
| `failed` | Checkout reported failure |

Your owner receives the approval request via their dashboard and email. Approvals expire after 15 minutes.

### Step 2: Get Decryption Key

Once the checkout is approved, call this endpoint to retrieve the one-time decryption key:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/key \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "checkout_id": "r5chk_abc123" }'
```

**Response:** `{ "key_hex": "...", "iv_hex": "...", "tag_hex": "..." }`

**This key is single-use.** It cannot be retrieved again for this checkout. If decryption
fails after retrieving the key, the checkout must be re-initiated.

### Step 3: Decrypt Card Details

Using the `key_hex`, `iv_hex`, and `tag_hex` from the API response, perform AES-256-GCM
decryption on the encrypted card data you received from your owner. This produces the
card details (number, CVV, expiry, name, billing address).

**Critical:** Never store, log, or persist the decrypted card data.
It should exist only in memory for the duration of this single checkout.

### Step 4: Confirm

After completing (or failing) checkout at the merchant:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/confirm \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "checkout_id": "r5chk_abc123", "status": "success" }'
```

Use `"status": "failed"` if checkout didn't work. On success, the transaction is recorded
in your owner's dashboard. After your first successful checkout, your card status moves
from `confirmed` to `active`.

---

## Receiving Card Details

When your owner sets up a card for you, CreditClaw delivers the encrypted card details
via the `rail5.card.delivered` event.

**Via webhook:** If you have a `callback_url`, the card details are delivered automatically:
```json
{
  "event": "rail5.card.delivered",
  "bot_id": "bot_abc123",
  "data": {
    "card_id": "r5card_...",
    "card_name": "ChaseD",
    "card_last4": "9547",
    "encrypted_data": "<encrypted card details>",
    "instructions": "Accept the encrypted card details and confirm delivery via POST /bot/rail5/confirm-delivery"
  }
}
```

**Via bot messages (fallback):** If you don't have a webhook, check `GET /bot/messages` for
messages with `event_type: "rail5.card.delivered"`. The payload is identical. After accepting
the card details, acknowledge the message via `POST /bot/messages/ack`.

Store the encrypted card data securely using your platform's secrets manager or keep it
in memory. Follow the `instructions` field in the message payload for next steps.

### Confirm Delivery

**After receiving the card details**, confirm delivery so your card status advances from `pending_delivery`
to `confirmed`:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/confirm-delivery \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Response:
```json
{
  "status": "confirmed",
  "card_id": "r5card_...",
  "card_name": "ChaseD",
  "message": "Card confirmed. Complete a test purchase to verify your card works end-to-end.",
  "test_checkout_url": "https://creditclaw.com/pay/test_...",
  "test_instructions": "Navigate to the test checkout URL to complete a sandbox purchase.\nThis is a sandbox checkout — no real payment will be processed.\nDecrypt the card details and enter them at the checkout page.\nFill in all fields: card number, expiry, CVV, cardholder name, and billing address.\nSubmit the payment. The system will verify that the card details were decrypted correctly.\nThis proves your card works end-to-end before any real purchase."
}
```

After confirming delivery, you will also receive a `rail5.test.required` event (via webhook or
pending message) with the `test_checkout_url` and full instructions. This ensures you are notified
even if you don't parse the `confirm-delivery` response.

**Complete the test purchase** at the `test_checkout_url` to advance your card from `confirmed`
to `active`. This is a sandbox checkout — no real payment is processed. It verifies that your
card details decrypt correctly end-to-end before any real purchase.

**Pending messages for card deliveries expire after 24 hours.** If the message expires before
you retrieve it, your owner can re-stage the delivery from their dashboard.

**Recovery:** If you lose the card data, your owner deletes the card and creates a new one
through the setup wizard. The card details are re-delivered automatically.

---

## Card Status Progression

| Status | Meaning |
|--------|---------|
| `pending_delivery` | Key submitted, waiting for bot to confirm card details received |
| `confirmed` | Bot confirmed card details received — ready for checkout |
| `active` | First successful checkout completed — proven working |
| `frozen` | Owner manually paused the card |

> Cards begin in `pending_setup` during owner configuration. Your bot first sees the card
> at `pending_delivery` when the encrypted card details are delivered.

---

## Per-Rail Detail Check

For deeper operational info about your encrypted card — limits, approval threshold, and status:

```bash
curl https://creditclaw.com/api/v1/bot/check/rail5 \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Response:
```json
{
  "status": "active",
  "card_id": "r5_abc123",
  "card_name": "Shopping Card",
  "card_brand": "visa",
  "last4": "4532",
  "limits": {
    "per_transaction_usd": 50.00,
    "daily_usd": 100.00,
    "monthly_usd": 500.00,
    "human_approval_above_usd": 25.00
  }
}
```

Response (not connected): `{ "status": "inactive" }`

**Rate limit:** 6 requests per hour.
