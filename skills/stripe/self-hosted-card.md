# Self-Hosted Cards — Day-to-Day Guide

Companion to [skill.md](https://creditclaw.com/creditcard/skill.md). Covers how to make purchases using your owner's self-hosted cards (Rail 4).

**Prerequisite:** Your owner must have set up at least one self-hosted card and linked it to your account. Check `GET /bot/wallet/check` first.

---

## How It Works

Self-hosted cards use a split-knowledge privacy model. Your owner provides their own card details through CreditClaw's secure setup wizard — you never see the actual card numbers. When you need to make a purchase at any online merchant, you submit a checkout request. CreditClaw evaluates it against your card's permissions and either auto-approves (if within your allowance) or sends your owner an approval request via email.

**Use this rail for:** Any online store — SaaS subscriptions, cloud hosting, domain registrations, digital services, or any merchant not covered by the Pre-paid Wallet.

**Endpoint:** `POST /bot/merchant/checkout`

---

## Checkout Flow

1. You submit a checkout request with merchant and amount details
2. CreditClaw evaluates the request against your card's permissions
3. If the amount is within your auto-approved allowance, it processes immediately
4. If the amount exceeds the threshold, your owner receives an approval request (email with secure link)
5. You poll for the result
6. Once approved, the transaction is recorded

### Checkout Request

```bash
curl -X POST https://creditclaw.com/api/v1/bot/merchant/checkout \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_index": 1,
    "merchant_name": "DigitalOcean",
    "merchant_url": "https://cloud.digitalocean.com",
    "item_name": "Droplet hosting - 1 month",
    "amount_cents": 1200,
    "category": "cloud_compute"
  }'
```

### Request Fields

| Field | Required | Description |
|-------|----------|-------------|
| `profile_index` | Yes | The payment profile index assigned to you |
| `merchant_name` | Yes | Merchant name (1-200 chars) |
| `merchant_url` | Yes | Merchant website URL |
| `item_name` | Yes | What you're buying |
| `amount_cents` | Yes | Amount in cents (integer) |
| `card_id` | No | Required if you have multiple cards; auto-selects if only one |
| `category` | No | Spending category |
| `task_id` | No | Your internal task reference |

### Response (Auto-Approved — Within Allowance)

```json
{
  "status": "approved",
  "transaction_id": "txn_abc123",
  "amount_usd": 12.00,
  "message": "Transaction approved within allowance."
}
```

### Response (Requires Human Approval)

```json
{
  "status": "pending_approval",
  "confirmation_id": "conf_xyz789",
  "message": "Your owner has been sent an approval request. Poll /bot/merchant/checkout/status to check the result.",
  "expires_in_minutes": 15
}
```

---

## Polling for Approval

If you received `pending_approval`, poll for the result:

```bash
curl "https://creditclaw.com/api/v1/bot/merchant/checkout/status?confirmation_id=conf_xyz789" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

| Status | Meaning |
|--------|---------|
| `pending` | Owner hasn't responded yet — poll again in 30 seconds |
| `approved` | Owner approved — proceed with your task |
| `rejected` | Owner declined — do not proceed |
| `expired` | 15-minute approval window passed — try again if needed |

**Poll interval:** Every 30 seconds until resolved or expired.

---

## Multi-Card Handling

If your owner has linked you to multiple self-hosted cards, you **must** include `card_id` in your checkout request. If you only have one active card, `card_id` is optional and will auto-select.

To find your available cards, check the response from `GET /bot/wallet/check` — it includes your linked card IDs and their status.

---

## Allowance Thresholds

Your owner sets a per-profile allowance threshold for each card. Purchases within this threshold are auto-approved — no email confirmation needed. Purchases above it require human approval via a secure email link (15-minute TTL).

Your owner can view and adjust these thresholds from their dashboard at `https://creditclaw.com/app/self-hosted`.

---

## Common Errors

| Error | What to Do |
|-------|-----------|
| 403 — `category_blocked` | This spending category is blocked by your owner |
| 403 — `exceeds_per_transaction_limit` | Amount exceeds per-transaction cap |
| 403 — `wallet_frozen` | Owner has frozen your wallet. Wait for them to unfreeze. |
| 410 — approval expired | Owner didn't approve within 15 minutes. Resubmit the checkout request. |
| 400 — `card_id required` | You have multiple cards — include `card_id` in your request |
| 404 — `rail not enabled` | Self-hosted cards not set up for your account |

---

## Quick Reference

| Item | Value |
|------|-------|
| Checkout endpoint | `POST /bot/merchant/checkout` |
| Status polling | `GET /bot/merchant/checkout/status?confirmation_id=X` |
| Amount format | Cents (integer, e.g. 1200 = $12.00) |
| Approval window | 15 minutes |
| Poll interval | ~30 seconds |
| Rate limit (checkout) | 30/hr |
| Rate limit (polling) | 30/hr |
