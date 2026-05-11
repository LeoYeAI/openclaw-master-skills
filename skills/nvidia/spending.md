# Spending Permissions

This file controls how your bot spends money. Edit any section below.
Your bot reads this file before every purchase to decide whether to
proceed, ask for approval, or decline.

---

## Approval Mode

Choose one:

- [x] **Ask me for everything** — Bot requests approval before any purchase
- [ ] **Auto-approve under threshold** — Bot spends freely up to the limit below
- [ ] **Auto-approve by category** — Bot spends freely on approved categories

---

## Spending Limits

| Limit | Amount |
|-------|--------|
| Per transaction max | $25.00 |
| Daily max | $50.00 |
| Monthly max | $500.00 |
| Ask approval above | $10.00 |

If a purchase exceeds the "ask approval above" amount, the bot must
send you a confirmation request before proceeding — even if auto-approve
is enabled.

---

## Approved Categories

If "auto-approve by category" is selected above, the bot may spend
freely (within limits) on checked categories. All others require approval.

- [x] API services & SaaS subscriptions
- [x] Cloud compute & hosting
- [x] Research & data access
- [ ] Physical goods & shipping
- [ ] Advertising & marketing
- [ ] Donations & tips
- [ ] Entertainment & media
- [ ] Other / uncategorized

---

## Blocked Categories

The bot must **never** spend on these, regardless of other settings:

- [x] Gambling
- [x] Adult content
- [x] Cryptocurrency purchases
- [x] Cash advances or money transfers
- [ ] _(add your own)_

---

## Recurring Payments

- [ ] **Allow recurring / subscription charges** — Bot can sign up for services that charge periodically
- [x] **One-time payments only** — Bot must ask before committing to recurring charges

If recurring is allowed:
| Limit | Amount |
|-------|--------|
| Max per subscription / month | $20.00 |
| Max total subscriptions | 3 |

---

## Notifications

When should the bot notify you?

- [x] Every purchase (with amount and merchant)
- [x] When balance drops below $10.00
- [x] When a purchase is declined
- [x] Weekly spending summary
- [ ] Only when approval is needed

---

## Notes to Your Bot

_Write any additional instructions in plain language here. Your bot
will read and follow these._

```
Example:
- Prefer free tiers of services before paying for premium
- Always check if there's a coupon or discount code before purchasing
- Don't sign up for annual plans without asking me first
- If you find a cheaper alternative for something, tell me before switching
```
