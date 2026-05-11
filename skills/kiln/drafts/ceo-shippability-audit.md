# CEO Shippability Audit — February 12, 2026

> 10 concerns a wise experienced CEO would raise about Kiln's readiness to ship and generate revenue.

---

## Summary

**The code is 90% ready. What's blocking revenue is ~15 hours of Adam's work on non-code things.** The engineering is ahead of the business ops.

---

## 1. "How does a customer actually pay us?"

**Status: 🔴 Not ready**

- Stripe integration exists (PaymentIntent, SetupIntent, card storage) but never tested live
- No subscription product for Pro ($29/mo) — only one-shot per-order charges exist
- No web signup flow — user must run `kiln billing setup --rail stripe` from CLI
- Stripe webhook handler is a stub (receives events but doesn't process them)
- **No recurring billing infrastructure at all**

**Action needed:** Either build Stripe Subscriptions, or simplify — use Stripe Payment Links / Lemon Squeezy to sell license keys externally, keep Kiln focused on validating them.

---

## 2. "Who is our customer and can they find us?"

**Status: 🔴 Not ready**

- Landing page exists but is "Coming Soon" with `noindex` — Google can't see it
- Full landing page is built (Astro site with pricing, install, docs) but not deployed
- No email capture, no newsletter, no waitlist
- No analytics — zero visibility into visits or installs
- No social media presence, no Discord
- PyPI package is live (`pip install kiln3d`) but nobody knows about it

**Action needed (Adam):** Deploy full landing page, remove noindex, add email capture, create Discord.

---

## 3. "Does the thing that makes us money actually work?"

**Status: 🟡 Architecturally sound, operationally unverified**

- Fulfillment brokering (5% fee) is the primary revenue path
- Craftcloud/Sculpteo API field names are **guessed** with defensive fallbacks
- Zero live API testing — all 260+ fulfillment tests use mocked HTTP responses
- If any field name is wrong, quotes silently return $0.00 instead of erroring

**Action needed (Adam, 2 hours):** Get Craftcloud API key, make one real call, validate field names.

---

## 4. "What stops someone from using Pro features for free?"

**Status: 🟢 Implemented, with a caveat**

- Free tier: max 2 printers, 10 queued jobs — enforced in code
- Pro/Business features gated behind `@requires_tier()` decorators
- License key validation works (`kiln_pro_*` → PRO, `kiln_biz_*` → BUSINESS)
- **Caveat:** No way to purchase a license key. Upgrade URL is a dead link.

**Action needed:** License key generation + distribution system. Simplest: Stripe Payment Link → webhook → auto-generate key → email.

---

## 5. "If I gave this to 100 people today, would it work?"

**Status: 🟢 Yes, for local printing**

- Install script works, `kiln setup` is guided with mDNS discovery
- Clear error messages with exact fix commands
- 3,451 tests all passing
- Zero-to-first-print works if printer is reachable + user has API key

**Minor friction:** Bambu users need manual IP/access code, OctoPrint users need API key from web UI.

---

## 6. "What's our competitive moat?"

**Status: 🟡 Real but fragile**

- AI agent control via MCP — nobody else does this
- Multi-printer fleet management across firmware ecosystems
- Fulfillment brokering — OctoPrint has no outsourced manufacturing
- 26 printer safety profiles

**Fragile because:** MCP agent control is a feature, not a category. Moat gets real with multi-device expansion (laser, CNC, SLA).

---

## 7. "What's the time-to-value for a new user?"

**Status: 🟢 Technical users / 🔴 Everyone else**

- OctoPrint user: 5-10 min install-to-print
- Bambu user: 10-15 min (manual config)
- "I don't own a printer" user: **dead end** — consumer workflow exists in code but isn't surfaced

**Action needed:** Surface the no-printer fulfillment path as a first-class flow.

---

## 8. "Are we legally ready to take money?"

**Status: 🔴 Not addressed**

- No Terms of Service
- No Privacy Policy
- No refund policy for fulfillment orders
- No manufacturing liability disclaimer
- Stripe requires TOS + privacy policy links during onboarding

**Action needed (Adam + legal template):** TOS, Privacy Policy, refund policy, liability disclaimer. Required before Stripe goes live.

---

## 9. "What happens when something breaks?"

**Status: 🟡 Partial**

- Structured error format, HMAC audit logs, event bus, log rotation all good
- **Missing:** No Sentry/error monitoring, no uptime monitoring, no alerting, no customer support channel besides GitHub Issues

---

## 10. "What's the minimum viable path to first dollar?"

**Two revenue streams that can work without building a SaaS platform:**

### Stream A: Fulfillment brokering (5% fee)
1. Validate Craftcloud API field names (2 hours)
2. Set up Stripe live mode (1 hour)
3. Deploy full landing page (1 hour — already built)
4. Legal pages (2-4 hours with templates)

### Stream B: Pro license sales ($29/mo)
1. Create Stripe Payment Link for Pro tier
2. Build webhook → generate `kiln_pro_*` key → email
3. User pastes key into `~/.kiln/license`

### Stream C: Donations (already live)
- `kiln3d.sol` and `kiln3d.eth` configured

**Total to first dollar: ~10-15 hours of Adam's time.**

---

## What's NOT needed to launch

- ❌ Web dashboard / control panel — CLI + MCP is the product
- ❌ User accounts / SaaS platform — license key validation works offline
- ❌ Cloud hosting — self-hosted is the model
- ❌ Recurring Stripe Subscriptions — Stripe Payment Links + license keys is simpler
- ❌ Multi-device support (laser, CNC, SLA) — that's the longterm play, not the MVP
