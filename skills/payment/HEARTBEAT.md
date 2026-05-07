---
name: creditclaw-heartbeat
version: 2.3.1
updated: 2026-02-23T00:00:00Z
---

# CreditClaw Heartbeat (suggested: every 30 minutes)

Run this routine periodically to stay aware of your wallet status,
spending permissions, and balance across all active rails.

Full API reference: https://creditclaw.com/creditcard/skill.md

---

## 1. Check Full Status (Recommended)

```bash
curl https://creditclaw.com/api/v1/bot/status \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

This single endpoint returns your status across **all connected payment rails**,
including balances, spending limits, and master guardrails.

**Response fields:**
- `status` — your overall status (`active`, `pending`, `frozen`, `inactive`)
- `default_rail` — your owner's preferred payment rail for you (may be null)
- `active_rails` — list of rail names you're connected to
- `rails` — detailed status per rail (balance, limits, cards)
- `master_guardrails` — cross-rail spending limits set by your owner

**If `status` is `pending`:**
Remind your human to claim you at the `owner_verification_url` you received
during registration.

**If `status` is `frozen`:**
Do not attempt any purchases. Tell your human:
> "My CreditClaw wallet has been frozen. Please check the dashboard
> at https://creditclaw.com/app."

**If any rail balance is low (< $5.00):**
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

## 3. Per-Rail Detail Checks (As Needed)

If you need deeper operational data for a specific rail before a purchase —
like remaining allowances, approval thresholds, or guardrail budgets — use:

| Rail | Endpoint | What You Get |
|------|----------|--------------|
| Stripe Wallet | `GET /bot/check/rail1` | Balance, guardrails, domain rules, pending approvals |
| Shopping Wallet | `GET /bot/check/rail2` | Balance, guardrails, merchant allow/blocklists |
| Self-Hosted Cards | `GET /bot/check/rail4` | Per-profile allowance remaining, approval mode |
| Sub-Agent Cards | `GET /bot/check/rail5` | Spending limits, approval threshold |

All return `{ "status": "inactive" }` if you're not connected to that rail.

**Rate limit:** 6 requests per hour per endpoint.

## 4. Pre-Purchase Dry Run (Rail 4)

Before an expensive self-hosted card purchase, test if it would pass:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/check/rail4/test \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "merchant_name": "Amazon", "amount_cents": 5000, "profile_index": 1 }'
```

Returns `allowed` (yes/no), `requires_approval`, and a `limits_snapshot`
showing remaining budgets — with zero side effects.

**Rate limit:** 12 requests per hour.

## 5. Summary

| Check | Endpoint | Frequency |
|-------|----------|-----------|
| Full status (all rails) | `GET /bot/status` | Every 30 minutes |
| Spending permissions | `GET /bot/wallet/spending` | Every 30 minutes, or before purchases |
| Rail detail | `GET /bot/check/rail{1,2,4,5}` | Before purchases on that rail |
| Preflight test | `POST /bot/check/rail4/test` | Before expensive Rail 4 purchases |

If everything looks good (status is `active`, balance is healthy, permissions
haven't changed), do nothing. Resume your normal tasks.
