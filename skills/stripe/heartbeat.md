---
name: creditclaw-heartbeat
version: 2.3.0
updated: 2026-02-14T22:00:00Z
---

# CreditClaw Heartbeat (suggested: every 30 minutes)

Run this routine periodically to stay aware of your wallet status,
spending permissions, and balance across all active rails.

Full API reference: https://creditclaw.com/creditcard/skill.md

---

## 1. Check Wallet Status

```bash
curl https://creditclaw.com/api/v1/bot/wallet/check \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

**If `wallet_status` is `pending`:**
Remind your human to claim you at the `owner_verification_url` you received
during registration.

**If `wallet_status` is `frozen`:**
Do not attempt any purchases. Tell your human:
> "My CreditClaw wallet has been frozen. Please check the dashboard
> at https://creditclaw.com/app."

**If `wallet_status` is `empty` or `balance_usd` < 5.00:**
Ask your human if they'd like you to request a top-up:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/wallet/topup-request \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_usd": 25.00,
    "reason": "Balance is low — need funds to continue operations"
  }'
```

Then tell your human:
> "My CreditClaw balance is low ($X.XX remaining). I've sent you a
> top-up request — please add funds when you get a chance."

## 2. Check Spending Permissions

```bash
curl https://creditclaw.com/api/v1/bot/wallet/spending \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Cache this response for up to 30 minutes. Check it before any purchase.

**Key fields to act on:**
- `approval_mode` — determines whether you can auto-spend or must ask first
- `blocked_categories` — never attempt purchases in these categories
- `notes` — read and follow these; they are direct instructions from your owner
- `updated_at` — if this changed since your last check, re-read all fields

## 3. Check Stripe Wallet Balance (Private Beta)

> Only run this step if your owner has enabled the Stripe Wallet (x402) rail.
> If this endpoint returns 404, skip this step.

```bash
curl https://creditclaw.com/api/v1/stripe-wallet/balance?wallet_id=1 \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

If `balance_usdc` is low (e.g., < 5000000 which is $5.00), notify your human
that the USDC wallet needs funding.

## 4. Summary

| Check | Endpoint | Frequency |
|-------|----------|-----------|
| Wallet status & balance | `GET /bot/wallet/check` | Every 30 minutes |
| Spending permissions | `GET /bot/wallet/spending` | Every 30 minutes, or before purchases |
| Stripe Wallet balance | `GET /stripe-wallet/balance` | Every 30 minutes (if enabled) |

If everything looks good (status is `active`, balance is healthy, permissions
haven't changed), do nothing. Resume your normal tasks.
