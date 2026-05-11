---
name: merchant-squarespace
platform: squarespace
updated: 2026-03-18
---

# Squarespace — Merchant Guide

Squarespace is a website builder with built-in commerce. Sites vary heavily by template. Payment is typically handled via Stripe Elements or Squarespace's built-in checkout.

---

## Detection

```javascript
var isSquarespace = !!document.querySelector('script[src*="squarespace.com"]')
  || typeof Static !== 'undefined';
```

---

## Navigation

Squarespace sites vary heavily by template. Common patterns:

| Page type | Typical URL | Notes |
|-----------|-------------|-------|
| Shop / Products | `/shop` or `/store` | Template-dependent |
| Product | `/shop/{slug}` | |
| Cart | Cart overlay or `/cart` | Often a slide-out panel |

**Add to cart:** Button with class `.sqs-add-to-cart-button`.

Product pages are generally straightforward — title, price, variant selector (if applicable), and add-to-cart button.

---

## Product Selection

- Look for `.sqs-add-to-cart-button` to add items
- Variants may appear as dropdowns or option selectors within the product form
- After adding to cart, look for a cart icon or "Checkout" link — Squarespace often uses a cart overlay rather than a separate cart page

---

## Checkout

Squarespace typically uses Stripe Elements or its own built-in checkout for payment.

### Billing & Shipping Fields

Fill billing and shipping fields on the main checkout page. These are regular DOM inputs.

### Payment: Stripe Elements

Card fields are inside iframes sourced from `js.stripe.com`. There are two layouts:

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

## Tips & Pitfalls

1. **Template variation** — Squarespace templates vary significantly in layout. Use snapshots scoped to forms rather than relying on fixed selectors.
2. **Cart overlay** — Many Squarespace sites use a slide-out cart panel instead of a separate cart page. Look for the cart icon in the header.
3. **Stripe iframe detection** — If card fields aren't visible, check for iframes: `snapshot --interactive --frame "iframe"`.

---

## Snapshot Budget

| Phase | Target | Max |
|-------|--------|-----|
| Billing + shipping | 2 | 3 |
| Card fields (Stripe) | 2-3 | 4 |
| Submit + confirm | 1 | 2 |
| **Total** | **5** | **8** |
