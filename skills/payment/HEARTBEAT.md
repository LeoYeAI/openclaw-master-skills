---
name: creditclaw-heartbeat
version: 2.8.0
---

# CreditClaw Heartbeat

Run this routine periodically to stay aware of your wallet status,
spending permissions, and pending messages.

Full API reference: `SKILL.md`

---

## 1. Check Messages (Every 30 Minutes)

```bash
curl https://creditclaw.com/api/v1/bot/messages \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Poll for pending messages from your owner or the system. Messages include
approval results, card delivery notifications, spending alerts, and other events.

If `messages` is non-empty, process each message and then acknowledge:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/messages/ack \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message_ids": [1, 2, 3]}'
```

Messages stay pending until you explicitly acknowledge them.

## 2. Check Full Status (Every 8 Hours)

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
Let your human know so they can take action from their dashboard at https://creditclaw.com/overview.

## 3. Check Spending Permissions (Every 24 Hours)

```bash
curl https://creditclaw.com/api/v1/bot/wallet/spending \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

**Key fields to act on:**
- `approval_mode` — determines whether you can auto-spend or must ask first
- `blocked_categories` — never attempt purchases in these categories
- `notes` — read and follow these; they are direct instructions from your owner
- `updated_at` — if this changed since your last check, re-read all fields

## Summary

| Check | Endpoint | Frequency |
|-------|----------|-----------|
| Messages | `GET /bot/messages` | Every 30 minutes |
| Full status (all rails) | `GET /bot/status` | Every 8 hours |
| Spending permissions | `GET /bot/wallet/spending` | Every 24 hours |

If everything looks good (status is `active`, balance is healthy, permissions
haven't changed, no pending messages), do nothing. Resume your normal tasks.
