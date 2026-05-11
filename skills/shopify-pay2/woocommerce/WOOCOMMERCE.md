---
name: merchant-woocommerce
platform: woocommerce
updated: 2026-03-18
---

# WooCommerce — Merchant Guide

WooCommerce is a WordPress plugin powering a large share of independent online stores. Guest checkout is generally available. Most WooCommerce stores use Stripe Elements for payment.

---

## Detection

```javascript
var isWooCommerce = !!document.querySelector('link[href*="woocommerce"], script[src*="woocommerce"], .woocommerce')
  || !!document.querySelector('script[src*="wp-content/plugins/woocommerce"]');
```

---

## Navigation

### URL Patterns

| Page type | URL pattern | Example |
|-----------|-------------|---------|
| Shop / All products | `/shop/` | `store.com/shop/` |
| Product | `/product/{slug}/` | `store.com/product/blue-widget/` |
| Cart | `/cart/` | `store.com/cart/` |
| Checkout | `/checkout/` | `store.com/checkout/` |
| Category | `/product-category/{slug}/` | `store.com/product-category/widgets/` |

---

## Product Selection

**Add to cart:** Button with class `.add_to_cart_button` or `.single_add_to_cart_button`.

Variants are typically `<select>` dropdowns or button swatches inside the product form. Select the desired options before clicking add to cart.

After adding to cart, navigate to `/cart/` to review, then click the checkout button to proceed to `/checkout/`.

---

## Checkout

WooCommerce checkout uses `form.checkout` as the main form.

```bash
openclaw browser snapshot --efficient --selector "form.checkout"
```

### Billing & Shipping Fields

Fill billing fields on the main page (name, address, email, phone). These are regular DOM inputs.

### Payment: Stripe Elements

WooCommerce usually uses Stripe Elements for card fields. If a payment method selector exists, click "Credit Card (Stripe)" if not already selected.

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

### Submit

Submit is typically a "Place order" button on the main page.

```bash
openclaw browser snapshot --efficient --selector "form.checkout"
openclaw browser click e<place_order_ref>
```

---

## Tips & Pitfalls

1. **Stripe iframe detection** — If card fields aren't visible, check for iframes: `snapshot --interactive --frame "iframe"`.
2. **Payment method tabs** — Some WooCommerce stores have multiple payment options. Make sure "Credit Card" or "Stripe" is selected before looking for card fields.
3. **Coupon fields** — WooCommerce often shows a coupon field above the form. Ignore it unless instructed.

---

## Snapshot Budget

| Phase | Target | Max |
|-------|--------|-----|
| Billing + shipping | 2 | 3 |
| Card fields (Stripe) | 2-3 | 4 |
| Submit + confirm | 1 | 2 |
| **Total** | **5** | **8** |
