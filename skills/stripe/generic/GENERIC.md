---
name: merchant-generic
platform: generic
updated: 2026-03-18
---

# Generic — Universal Checkout Reference

This is **not** a platform guide. It is the universal browser-control shopping reference for when no specific merchant guide applies, or when a merchant guide references shared mechanics.

> **For platform detection and routing,** see `SHOPPING-GUIDE.md`. It will tell you which merchant file to read.

---

## Unknown Sites — Browsing Strategy

If no platform is detected:

1. **Look for product/cart patterns:**
   - Forms with add-to-cart actions
   - Cart icons or links in the header
   - Price elements near product images

2. **Navigate cautiously:**
   - Use `--efficient` snapshots scoped to forms
   - Don't snapshot entire pages on unknown sites — they may be very large
   - Look for standard e-commerce patterns: "Add to cart", "Buy now", "Checkout"

---

## Inline Card Fields (No Iframes)

Card fields are regular inputs — fill them like any form field.

```bash
openclaw browser type e<card_number_ref> "<decrypted card number>"
openclaw browser type e<expiry_ref> "<MM/YY>"
openclaw browser type e<cvv_ref> "<decrypted cvv>"
openclaw browser type e<name_ref> "<cardholder name>"
```

Some forms have separate month/year dropdowns:
```bash
openclaw browser select e<month_ref> "12"
openclaw browser select e<year_ref> "2029"
```

---

## Stripe Elements (Iframe Card Fields)

Stripe puts card fields inside iframes sourced from `js.stripe.com`. There are two layouts:

**Single iframe** (all card fields in one frame):
```bash
openclaw browser snapshot --interactive --frame "iframe[src*='js.stripe.com']"
openclaw browser type e<card_ref> "<decrypted card number>"
openclaw browser type e<expiry_ref> "<MM/YY>"
openclaw browser type e<cvc_ref> "<decrypted cvv>"
```

**Split iframes** (one iframe per field):
```bash
openclaw browser snapshot --interactive --frame "iframe[name*='number']"
openclaw browser type e<ref> "<decrypted card number>"

openclaw browser snapshot --interactive --frame "iframe[name*='expiry']"
openclaw browser type e<ref> "<MM/YY>"

openclaw browser snapshot --interactive --frame "iframe[name*='cvc']"
openclaw browser type e<ref> "<decrypted cvv>"
```

**Important:** The submit button is always on the main page, not inside the iframe. Take a new main-page snapshot to find and click it.

---

## Braintree / Adyen (Iframe Card Fields)

Same approach as Stripe — card fields are in iframes.

**Braintree:**
```bash
openclaw browser snapshot --interactive --frame "iframe[name*='braintree']"
```

**Adyen:**
```bash
openclaw browser snapshot --interactive --frame "iframe[src*='adyen']"
```

Fill fields using refs from the iframe snapshot. Submit button is on the main page.

---

## Multi-Step Checkout

Some sites (BigCommerce, Magento, custom) split checkout across multiple pages or sections.

After filling each section:
```bash
openclaw browser click e<continue_ref>
openclaw browser wait --load networkidle
openclaw browser snapshot --efficient --selector "form"
```

Fill visible fields → click Continue → repeat until the payment step. Then use the appropriate card fill approach (inline or iframe).

Budget: **5-6 snapshots** for multi-step flows.

---

## Dropdowns

**Native `<select>` elements:**
```bash
openclaw browser select e<ref> "United States"
```

**Custom/React dropdowns** (no `<select>` in the DOM):
```bash
openclaw browser click e<ref>              # open
openclaw browser type e<ref> "United"      # filter
openclaw browser press Enter               # select
```

If typing doesn't filter:
```bash
openclaw browser click e<ref>              # open
openclaw browser press ArrowDown           # navigate
openclaw browser press ArrowDown
openclaw browser press Enter               # select
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Card fields not visible | Check for iframes: `snapshot --interactive --frame "iframe"` |
| `click`/`type` fails | `highlight e<ref>` to verify ref, then retry. Try `press Tab` to focus. |
| Field covered by overlay | Wait 2 seconds, retake snapshot, try again |
| Dropdown won't open | Try `click` then `press ArrowDown` then `press Enter` |
| Submit button not found | Take full page snapshot: `snapshot --efficient --depth 4` |
| Page unchanged after submit | Wait for network idle: `wait --load networkidle --timeout-ms 15000` |

---

## Snapshot Budget

| Checkout type | Target | Max |
|---------------|--------|-----|
| Single-page, inline fields | 3 | 5 |
| Single-page, iframe fields | 5 | 8 |
| Multi-step | 5 | 8 |

**CAPTCHA / 3DS / OTP → fail immediately.** Do not attempt to solve these.
