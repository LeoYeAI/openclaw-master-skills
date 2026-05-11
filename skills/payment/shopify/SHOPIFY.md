---
name: merchant-shopify
platform: shopify
updated: 2026-03-18
---

# Shopify — Merchant Guide

Shopify is the most common e-commerce platform. Guest checkout is always available. Card fields use cross-origin iframes (one per field).

---

## Detection

### Tier 1 — Definitive (any one = Shopify)

| Signal | How to check |
|--------|-------------|
| `window.Shopify` global | `typeof Shopify !== 'undefined'` — always present on every Shopify page |
| `Shopify.shop` | Returns the `.myshopify.com` domain |
| `Shopify.theme` | Returns `{ name, id }` of the active theme |
| `cdn.shopify.com` in scripts | Any `<script src="...cdn.shopify.com...">` |
| `monorail-edge.shopifysvc.com` | In `<link rel="preconnect">` — Shopify's analytics edge |

### Tier 2 — Structural DOM patterns

| Signal | How to check |
|--------|-------------|
| Section IDs | `document.querySelectorAll('[id^="shopify-section"]')` — template sections |
| Payment button | `[data-shopify="payment-button"]` or `.shopify-payment-button` — "Buy it now" |
| Add to cart form | `form[action*="/cart/add"]` |
| Cart form | `form[action="/cart"]` |
| `ShopifyAnalytics` global | `typeof ShopifyAnalytics !== 'undefined'` |

### Detection Script

```javascript
var isShopify = (typeof Shopify !== 'undefined' && !!Shopify.shop)
  || !!document.querySelector('script[src*="cdn.shopify.com"]')
  || !!document.querySelector('link[href*="monorail-edge.shopifysvc.com"]');
```

One line. No snapshots needed.

---

## Useful Globals

Once confirmed Shopify, these are available:

| Global | Value |
|--------|-------|
| `Shopify.shop` | Store domain (e.g. `legoclaw.myshopify.com`) |
| `Shopify.locale` | Language (e.g. `en`) |
| `Shopify.currency.active` | Currency code (e.g. `USD`) |
| `Shopify.routes.root` | Store root path |
| `Shopify.theme.name` | Theme name (e.g. `Horizon`, `Dawn`) |

---

## Navigation

### URL Patterns

Shopify stores follow a consistent URL structure regardless of theme:

| Page type | URL pattern | Example |
|-----------|-------------|---------|
| Homepage | `/` | `store.com/` |
| All products | `/collections/all` | `store.com/collections/all` |
| Collection | `/collections/{handle}` | `store.com/collections/shirts` |
| Product | `/products/{handle}` | `store.com/products/short-sleeve-shirt` |
| Cart | `/cart` | `store.com/cart` |
| Search | `/search?q={query}` | `store.com/search?q=shirt` |
| Checkout | `/checkouts/cn/...` | Redirects to Shopify-hosted checkout |

### Browsing Products

Don't snapshot the full page — Shopify pages can be large. Target specific sections:

**On collection/catalog pages:**
- Products are in a grid. Each product links to `/products/{handle}`.
- Look for product cards with price and title.

**On product pages:**
- Product info is structured: title, price, variant selectors, add-to-cart.
- Target the product form: `form[action*="/cart/add"]`

---

## Product Selection

### Variant Selection

Shopify products can have variants (size, color, etc.). These appear as:
- **Buttons/swatches** — click to select (most common in modern themes)
- **Dropdowns** — `<select>` elements inside the product form

Selecting a variant updates the URL with `?variant={id}` and may change the price.

### Adding to Cart

Two paths:

1. **"Add to cart"** → adds item, stays on page (or opens cart drawer)
   - Form: `form[action*="/cart/add"]`
   - Button: `button[type="submit"]` inside that form

2. **"Buy it now"** → skips cart, goes straight to checkout
   - Button: `[data-shopify="payment-button"]` or `.shopify-payment-button`
   - This triggers Shopify's dynamic checkout — redirects to `/checkouts/cn/...`

**Recommendation:** Use "Buy it now" when purchasing a single item. It saves a step (skips the cart page entirely).

### Cart Page

If items were added to cart:
- Navigate to `/cart`
- The checkout button is typically `button[name="checkout"]` or a link to `/checkout`
- Some stores use cart drawers (slide-out panels) instead of a separate cart page

---

## Checkout

Shopify uses a **single-page checkout** with shipping and payment together. Card fields live in **cross-origin iframes** — one iframe per field.

### Shopify Card Iframe Layout

| Field | Iframe name pattern |
|-------|-------------------|
| Card number | `card-fields-number-*` |
| Expiry | `card-fields-expiry-*` |
| CVV | `card-fields-verification_value-*` |
| Name on card | `card-fields-name-*` |

These iframes are cross-origin. You **cannot** use `evaluate` to run JavaScript inside them. You must use `--frame` targeting with snapshot + click/type.

### Phase 1: Shipping Info

Shipping fields are regular DOM elements — fill them normally.

```bash
openclaw browser snapshot --efficient --selector "form"
```

Fill in order:
1. **Email** — `type` on the email field
2. **Country** — custom dropdown: `click` → `type` first letters → `press Enter`
3. **First name, Last name** — `type` on each
4. **Address** — `type` the street address. **Wait 1-2 seconds** for autocomplete suggestions to appear, then `click` the matching suggestion. This **may** auto-fill city, state, and ZIP — but not always. After clicking, snapshot and verify those three fields. Fill manually any that are still empty.
5. **State** — treat as a React combobox: `click` to open → `type` the first letters → `press Enter` on the match. Some stores use a simpler native `<select>` instead — the same approach still works.
6. **Phone** — `type` the phone number. **Shopify often requires this.** Missing phone is a common cause of submit failure.
7. **Shipping method** — usually auto-selected (Free Shipping or cheapest). Verify with a snapshot if unsure.

Budget: **2 snapshots** for shipping.

### Phase 2: Card Fields

Card fields are inside cross-origin iframes. Use `--frame` to target each one.

#### Card Number

```bash
openclaw browser snapshot --interactive --frame "iframe[name^='card-fields-number']"
openclaw browser click e<ref>
openclaw browser type e<ref> "<decrypted card number>"
```

#### Expiry Date — CRITICAL

Shopify's expiry field auto-formats input (inserting " / " between month and year). Typing all digits at once will garble the field.

**You must type digit-by-digit with pauses:**

```bash
openclaw browser snapshot --interactive --frame "iframe[name^='card-fields-expiry']"
openclaw browser click e<ref>
openclaw browser press 1
# wait 1 second
openclaw browser press 2
# Shopify auto-formats to "12 / " — wait 2 seconds
openclaw browser press 2
# wait 1 second
openclaw browser press 9
# Field now shows "12 / 29"
```

**Rules for expiry:**
- Type each digit as a separate `press` command
- Wait **2 seconds** after the second month digit (the auto-formatter needs time)
- Wait **1 second** between other digits
- **Never** use `type` to enter all digits at once
- If the field shows the wrong value: `press End` → `press Backspace` ×10 to clear → retype

#### CVV

```bash
openclaw browser snapshot --interactive --frame "iframe[name^='card-fields-verification']"
openclaw browser click e<ref>
openclaw browser type e<ref> "<decrypted cvv>"
```

#### Name on Card

Often auto-filled from shipping info. Check before filling.

```bash
openclaw browser snapshot --interactive --frame "iframe[name^='card-fields-name']"
```

If the name field is empty:
```bash
openclaw browser click e<ref>
openclaw browser type e<ref> "<cardholder name>"
```

Budget: **3-4 snapshots** for card fields (one per iframe you need to fill).

### Phase 3: Submit

```bash
openclaw browser snapshot --efficient --selector "form"
openclaw browser click e<pay_now_ref>
```

Wait **8-10 seconds** for processing. Then check for confirmation:

```bash
openclaw browser snapshot --efficient
```

Look for "Thank you for your purchase" or "Order confirmed" with an order number.

**If validation errors appear:**

| Error | Fix |
|-------|-----|
| "Enter a phone number" | Go back, fill phone field, resubmit |
| "Enter a valid card number" | Re-fill card number iframe |
| "Enter a valid expiry date" | Clear and retype expiry digit-by-digit |
| "Enter a security code" | Re-fill CVV iframe |

---

## Tips & Pitfalls

1. **Expiry garbling** — The #1 issue. Always type digit-by-digit with pauses. Never use `type` for the full expiry string.
2. **Missing phone number** — Shopify requires it on most stores. Fill it during shipping.
3. **Address autocomplete** — Don't manually fill city/state/zip if autocomplete is available. Click the suggestion instead.
4. **Name on card auto-fill** — Check before typing. Overwriting the auto-filled name can cause issues.
5. **Iframe ref scoping** — Refs from `--frame` snapshots are scoped to that frame. You need a new snapshot when switching to a different iframe or back to the main page.

---

## Themes

Themes change the visual layout but not the underlying structure. Common themes:
- **Dawn** (default) — clean, grid-based
- **Horizon** — editorial style
- **Refresh**, **Taste**, **Sense** — various Shopify 2.0 themes

The detection signals, URL patterns, and form structures are the same across all themes.

---

## Snapshot Budget

| Phase | Snapshots |
|-------|-----------|
| Shipping | 2 |
| Card fields | 3-4 |
| Submit + confirm | 1-2 |
| **Total** | **6-8** |
