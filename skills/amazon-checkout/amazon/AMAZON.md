---
name: merchant-amazon
platform: amazon
updated: 2026-03-18
---

# Amazon — Merchant Guide

Amazon requires **account authentication** — no guest checkout. Uses saved payment methods and addresses from the account. No raw card entry at checkout.

> **Future:** CreditClaw will add Amazon API support (SP-API) once approved. For now, use browser control.

---

## Detection

```javascript
var isAmazon = (typeof ue !== 'undefined' && typeof AmazonUIPageJS !== 'undefined');
```

Other signals: `P` global, CDN hosts `images-na.ssl-images-amazon.com` and `m.media-amazon.com`, DOM elements `#twotabsearchtextbox`, `#nav-search-bar-form`, `#nav-logo-sprites`.

---

## Navigation

### URL Patterns

| Page | Pattern |
|------|---------|
| Search | `/s?k=<query>` |
| Product | `/dp/{ASIN}` (slug before `/dp/` is decorative) |
| Cart | `/gp/cart/view.html` |
| Sign-in | `/ap/signin` |
| Checkout | `/checkout/entry/cart` |

### Search Results (`/s?k=...`)

- Container: `[data-component-type="s-search-results"]`
- Each card: `[data-component-type="s-search-result"]` with `data-asin`
- Product link: `a[href*="/dp/"]` — **sponsored results may lack this** (use tracking redirects)
- Title: `h2 a span` | Price: `.a-price-whole` + `.a-price-fraction` | Prime: `.a-icon-prime`
- **No "Add to Cart" on search results** — must click into product page first

---

## Product Selection

### Product Page (`/dp/{ASIN}`)

| Element | Selector |
|---------|----------|
| ASIN | `#ASIN` (hidden input) or from URL |
| Title | `#productTitle` |
| Price | `#corePrice_feature_div` |
| Availability | `#availability` |
| Add to Cart | `#add-to-cart-button` |
| Buy Now | `#buy-now-button` (skips cart, goes to checkout) |
| Quantity | `#quantity` |

**Variants** live inside `#twister`. Common IDs: `#variation_color_name`, `#variation_size_name`, `#variation_style_name`. Not all products use these — some use button-style selectors. Snapshot the variant area rather than relying on fixed IDs.

**Add to Cart flow:** select variants → set quantity → click `#add-to-cart-button` → confirmation page at `/cart/smart-wagon?newItems=...` → navigate to `/gp/cart/view.html`.

### Cart (`/gp/cart/view.html`)

| Element | Selector |
|---------|----------|
| Cart items | `[data-asin][data-itemtype="active"]` |
| Subtotal | `#sc-subtotal-label-activecart` |
| Proceed to checkout | `[name="proceedToRetailCheckout"]` |
| Item quantity | `.sc-quantity-textfield` per item |
| Delete item | `[value="Delete"]` per item |

---

## Checkout

### Authentication

Amazon **always requires sign-in** before checkout.

**Sign-in flow:**
1. Email/phone field at `/ap/signin` → form posts to `/ax/claim` → click `#continue`
2. Password field on next page → `#ap_password` → click `#signInSubmit`

**Possible challenges:** CAPTCHA (`#auth-captcha-image`), OTP/2FA prompt, or "Approve sign-in" push notification to Amazon app. If any of these appear, escalate to the user.

**Session:** If already logged in, "Proceed to checkout" goes directly to checkout. Amazon sessions persist if "Keep me signed in" is checked. Check sign-in state via the nav bar text ("Hello, Sign in" vs "Hello, {Name}").

### Payment (Post-Authentication)

Amazon checkout uses **saved payment methods and addresses** — no raw card entry.

**Flow:** select shipping address → shipping speed → payment method → review → place order.

| Step | Selector |
|------|----------|
| Place order | `#submitOrderButtonId` or `[name="placeYourOrder1"]` |

The CreditClaw card must be **already added to the Amazon account**. The agent selects it at checkout by last 4 digits, confirms address and shipping speed, then clicks "Place your order".

---

## Tips & Pitfalls

1. **Don't scan full pages** — Amazon pages are massive. Use targeted selectors (`#add-to-cart-button`, `#productTitle`) instead of full snapshots.
2. **ASIN is king** — use `/dp/{ASIN}` for direct product navigation.
3. **Skip sponsored results** — they use tracking redirects instead of clean `/dp/` links.
4. **Watch for CAPTCHA** — Amazon may challenge automation. Escalate to user if it appears.
