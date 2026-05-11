---
name: merchant-wix
platform: wix
updated: 2026-03-18
maturity: experimental
---

# Wix — Merchant Guide

> **Experimental.** Wix checkout behavior varies heavily by template and needs further research. Detection is reliable but navigation and checkout patterns are not yet fully documented.

---

## Detection

```javascript
var isWix = !!document.querySelector('meta[name="generator"][content*="Wix"]')
  || !!document.querySelector('script[src*="wixstatic.com"]');
```

---

## Navigation

Wix sites vary significantly by template. Common patterns:

| Page type | Typical URL | Notes |
|-----------|-------------|-------|
| Shop | `/shop` or `/store` | Template-dependent |
| Product | `/product-page/{slug}` | Common pattern but not universal |
| Cart | Cart overlay or `/cart` | Often a slide-out panel |

- Wix uses a proprietary rendering engine — DOM structure can differ significantly from standard HTML patterns
- Product pages generally have a title, price, image gallery, and add-to-cart button
- Look for standard e-commerce patterns: "Add to Cart", "Buy Now", cart icons in the header

---

## Product Selection

- Add-to-cart buttons vary by template — use scoped snapshots to identify them
- Variants may appear as dropdowns, color swatches, or size selectors
- After adding to cart, look for a cart icon or checkout link

---

## Checkout

> **Needs research.** Wix checkout flow details are not yet fully documented.

Wix may use its own built-in checkout or third-party payment processors. General approach:

1. Take a scoped snapshot of the checkout form
2. Fill billing and shipping fields (regular DOM inputs)
3. Identify the payment form type (see `generic/GENERIC.md` for iframe detection and identification patterns)
4. Fill card fields accordingly
5. Submit and check for confirmation

For dropdown handling, troubleshooting, and general checkout mechanics, see `generic/GENERIC.md`.

---

## Tips & Pitfalls

1. **Template variation** — Wix templates vary more than most platforms. Always use snapshots scoped to forms.
2. **Proprietary DOM** — Wix renders pages differently from standard HTML. Selectors may be non-standard.
3. **CAPTCHA** — Wix may present CAPTCHA challenges. Escalate to user if encountered.
