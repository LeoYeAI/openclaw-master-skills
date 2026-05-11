---
name: merchant-magento
platform: magento
updated: 2026-03-18
maturity: experimental
---

# Magento — Merchant Guide

> **Experimental.** Magento checkout patterns are documented at a high level. Detection is reliable but checkout processor configuration varies by store. Magento 2 uses a **multi-step checkout**.

---

## Detection

```javascript
var isMagento = !!document.querySelector('script[src*="mage/"]')
  || !!document.querySelector('script[src*="varien"]')
  || !!document.querySelector('script[src*="requirejs/require"]');
```

**Note:** The `requirejs/require` signal can produce false positives on non-Magento sites that use RequireJS. Combine with other signals when possible.

---

## Navigation

### URL Patterns

| Page type | Typical URL | Notes |
|-----------|-------------|-------|
| Product | `/{slug}.html` | Magento uses `.html` suffix by default |
| Category | `/{category-slug}.html` | |
| Cart | `/checkout/cart/` | |
| Checkout | `/checkout/` | Multi-step |
| Search | `/catalogsearch/result/?q={query}` | |

---

## Product Selection

- Add to cart: typically `#product-addtocart-button` or `button.tocart`
- Variants (configurable products): dropdowns or swatches inside `.product-options-wrapper`
- After adding to cart, navigate to `/checkout/cart/` to review
- Click "Proceed to Checkout" to enter the multi-step checkout flow

---

## Checkout

Magento 2 uses a **multi-step checkout** that splits the process across sections.

### Multi-Step Flow

After filling each section, click Continue, wait for the next section to load, then snapshot again:

```bash
openclaw browser snapshot --efficient --selector "form"
```

Fill visible fields → click Continue → repeat until the payment step.

```bash
openclaw browser click e<continue_ref>
openclaw browser wait --load networkidle
openclaw browser snapshot --efficient --selector "form"
```

**Typical steps:**
1. Shipping address
2. Shipping method
3. Payment
4. Review & place order

### Payment Fields

Magento's payment step varies by store configuration. Common setups:

**Inline card fields** (regular inputs):
```bash
openclaw browser type e<card_number_ref> "<decrypted card number>"
openclaw browser type e<expiry_ref> "<MM/YY>"
openclaw browser type e<cvv_ref> "<decrypted cvv>"
openclaw browser type e<name_ref> "<cardholder name>"
```

**Braintree** (iframe):
```bash
openclaw browser snapshot --interactive --frame "iframe[name*='braintree']"
```

**Stripe Elements** (iframe):
```bash
openclaw browser snapshot --interactive --frame "iframe[src*='js.stripe.com']"
```

Fill fields using refs from the iframe snapshot. Submit button is on the main page.

For general iframe handling, dropdown mechanics, and troubleshooting, see `generic/GENERIC.md`.

---

## Tips & Pitfalls

1. **Multi-step patience** — Each step requires a snapshot after clicking Continue. Wait for `networkidle` between steps.
2. **Payment processor varies** — Magento supports many processors (Braintree, Stripe, Adyen, PayPal, etc.). Check for iframes before assuming inline fields.
3. **RequireJS false positive** — The `requirejs/require` detection signal can match non-Magento sites. Combine with other signals.
4. **Separate month/year** — Magento often uses separate month and year dropdowns for expiry instead of a single field.

---

## Snapshot Budget

| Phase | Target | Max |
|-------|--------|-----|
| Multi-step (all steps) | 4-5 | 6 |
| Card fields | 1-2 | 3 |
| Submit + confirm | 1 | 2 |
| **Total** | **5-6** | **8** |
