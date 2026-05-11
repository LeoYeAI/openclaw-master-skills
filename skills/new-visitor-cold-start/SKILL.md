---
name: new-visitor-cold-start
description: Convert first-time store visitors with behavior-based personalization — browse path → preference segment → matched first-order incentive → popup timing including exit intent. Use when the user wants cold-start offers for new visitors, first-purchase coupons tied to what they viewed, exit-intent or timed modals, or onboarding for anonymous traffic before email capture. Steps baked in: monitor path, classify preference, match first-order voucher or gift, set trigger (exit intent and alternatives). Do NOT use for loyalty win-back of existing customers only, post-purchase flows with no first-visit lens, or legal-only coupon policy with no behavioral targeting ask.
compatibility:
  required: []
---

# New visitor cold-start conversion

You turn **first session behavior** into a **single high-fit first-order offer** and **clear modal timing** so new visitors convert without generic blasts.

## Core workflow (always in order)

1. **Monitor browse path** — Pages viewed, sequence, time on category/PDP, scroll depth proxy (if described), cart add without checkout.
2. **Classify user preference** — Segment from path (e.g. category A explorer, price-sensitive browser, single-SKU deep dive, bouncer on shipping page).
3. **Match first-order offer** — Code or auto-apply; type (%, fixed, gift, free ship) aligned to segment; guardrails (min order, exclusions).
4. **Set popup / push timing** — **Exit intent** primary; backups (seconds on PDP, second category view, cart abandon on first visit).

## Gather context

1. Catalog categories and margin-safe discount bands.
2. Stack rules with other promos.
3. Compliance: new-customer definition, consent for popup/email.

Read `references/cold_start_playbook.md` for segment → offer → trigger map.

## Mandatory outputs (full run)

### A) Path → segment table

| Observed path pattern | Preference label | Rationale |
|----------------------|------------------|-----------|
| e.g. 3 PDPs same category | Category intent | … |
| e.g. cart + shipping page | Shipping sensitivity | … |

### B) Segment → first-order offer

| Segment | First-order offer | Min order / notes |
|---------|-------------------|-------------------|
| … | … | … |

### C) Trigger spec

| Trigger | When | Copy role |
|---------|------|-----------|
| **Exit intent** | Mouse leave viewport / mobile back intent proxy | Save offer + urgency light |
| Backup 1 | e.g. 25s on PDP | Deep interest |
| Backup 2 | e.g. second collection view | Broad interest |

Include **one modal headline + subline + CTA** per primary segment (or one adaptive template with dynamic category name).

## Pushy when vague

If user only says "better first-time conversion," still deliver **one full row chain**: path example → segment → offer → exit-intent line.

## When NOT to use

- Repeat-customer-only campaigns.
- No first-visit or anonymous context.

## Split with other skills

- **LTV win-back** — lapsed buyers; this skill is **first session**.
- **Cart bundle AOV** — add-ons; this skill is **cold start + first order**.
