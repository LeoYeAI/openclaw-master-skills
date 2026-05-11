---
name: merchant-bigcommerce
platform: bigcommerce
updated: 2026-03-18
---

# BigCommerce — Merchant Guide

BigCommerce is an e-commerce platform commonly used by mid-size retailers. Guest checkout is generally available. BigCommerce uses a **multi-step checkout** flow.

---

## Detection

```javascript
var isBigCommerce = !!document.querySelector('script[src*="cdn-bc.com"]')
  || typeof BCData !== 'undefined';
```

---

## Navigation

### URL Patterns

| Page type | URL pattern | Example |
|-----------|-------------|---------|
| Product | `/{slug}/` | `store.com/blue-widget/` (flat URLs) |
| Cart | `/cart.php` | `store.com/cart.php` |
| Checkout | `/checkout` | `store.com/checkout` |

BigCommerce uses flat product URLs (no `/product/` prefix). Categories and navigation vary by theme.

---

## Product Selection

- Add to cart buttons are typically standard form submits within the product page
- Variants appear as dropdowns or option selectors
- After adding to cart, navigate to `/cart.php` to review items
- Click the checkout button to proceed to `/checkout`

---

## Checkout

BigCommerce uses a **multi-step checkout** that splits the process across multiple pages or sections.

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
1. Customer info (email, name)
2. Shipping address
3. Shipping method
4. Payment
5. Review & place order

### Payment Fields

BigCommerce payment fields may be inline inputs or Stripe/Braintree iframes depending on the store's payment processor configuration.

**Inline card fields** (regular inputs):
```bash
openclaw browser type e<card_number_ref> "<decrypted card number>"
openclaw browser type e<expiry_ref> "<MM/YY>"
openclaw browser type e<cvv_ref> "<decrypted cvv>"
openclaw browser type e<name_ref> "<cardholder name>"
```

**Stripe Elements** (iframe):
```bash
openclaw browser snapshot --interactive --frame "iframe[src*='js.stripe.com']"
openclaw browser type e<card_ref> "<decrypted card number>"
openclaw browser type e<expiry_ref> "<MM/YY>"
openclaw browser type e<cvc_ref> "<decrypted cvv>"
```

**Important:** The submit button is always on the main page, not inside any iframe.

---

## Tips & Pitfalls

1. **Multi-step patience** — Each step requires a snapshot after clicking Continue. Don't rush — wait for `networkidle` between steps.
2. **Flat URLs** — Product URLs don't have a `/product/` prefix, which can make them harder to identify. Look for add-to-cart forms.
3. **Payment processor varies** — BigCommerce supports multiple processors. Check for iframes before assuming inline fields.

---

## Snapshot Budget

| Phase | Target | Max |
|-------|--------|-----|
| Multi-step (all steps) | 4-5 | 6 |
| Card fields | 1-2 | 3 |
| Submit + confirm | 1 | 2 |
| **Total** | **5-6** | **8** |
