---
name: creditclaw-shopping-guide
version: 2.9.0
updated: 2026-03-18
description: "Merchant detection, routing, and vendor discovery — the single decision point before checkout."
parent: SKILL.md
api_base: https://creditclaw.com/api/v1
credentials: [CREDITCLAW_API_KEY]
---

# CreditClaw — Procurement

> **Companion file.** For registration, spending permissions, and the full API reference, see `SKILL.md`.

This is the single decision point when you need to buy something. It answers three questions:
1. Does CreditClaw have a verified skill for this merchant?
2. What platform is the merchant using?
3. What kind of payment form does the checkout use?

---

## Step 1: Check for a Known Vendor Skill

Before navigating manually, check if CreditClaw has a verified skill for this merchant:

```bash
curl "https://creditclaw.com/api/v1/bot/skills?search=MERCHANT_NAME" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

If a vendor skill exists → use it. It contains merchant-specific instructions that are faster and more reliable than generic navigation.

If no vendor skill exists → continue to Step 2.

---

## Step 2: Identify the Platform

Land on the merchant's site and run platform detection. This determines how to navigate, browse, and check out.

**Run this via `evaluate` (OpenClaw) or `javascript_tool` (Claude) on any page:**

```javascript
var p = 'unknown';

// Shopify
if ((typeof Shopify !== 'undefined' && Shopify.shop)
  || document.querySelector('script[src*="cdn.shopify.com"]')
  || document.querySelector('link[href*="monorail-edge.shopifysvc.com"]')
  || document.querySelector('[id^="shopify-section"]')) p = 'shopify';

// Amazon
else if ((typeof ue !== 'undefined' && typeof AmazonUIPageJS !== 'undefined')
  || (document.querySelector('#nav-logo-sprites') && document.querySelector('#twotabsearchtextbox'))
  || document.querySelector('script[src*="images-na.ssl-images-amazon.com"]')) p = 'amazon';

// WooCommerce
else if (document.querySelector('link[href*="woocommerce"], script[src*="woocommerce"], .woocommerce')
  || document.querySelector('script[src*="wp-content/plugins/woocommerce"]')) p = 'woocommerce';

// Squarespace
else if (document.querySelector('script[src*="squarespace.com"]')
  || typeof Static !== 'undefined') p = 'squarespace';

// BigCommerce
else if (document.querySelector('script[src*="cdn-bc.com"]')
  || typeof BCData !== 'undefined') p = 'bigcommerce';

// Wix
else if (document.querySelector('meta[name="generator"][content*="Wix"]')
  || document.querySelector('script[src*="wixstatic.com"]')) p = 'wix';

// Magento
else if (document.querySelector('script[src*="mage/"]')
  || document.querySelector('script[src*="varien"]')
  || document.querySelector('script[src*="requirejs/require"]')) p = 'magento';

p;
```

> **Why this order matters:** Shopify and Amazon are checked first because they have the most reliable signals and are the most common purchase targets. Generic platforms (WooCommerce, etc.) are checked after to avoid false positives from third-party scripts loaded on major platforms.

---

## Step 3: Route to the Right Guide

Use your detection result to load the merchant guide. Each guide covers the full flow — detection, navigation, product selection, and checkout — in a single file.

| Platform | Guide |
|----------|-------|
| `shopify` | `shopify/SHOPIFY.md` |
| `amazon` | `amazon/AMAZON.md` |
| `woocommerce` | `woocommerce/WOOCOMMERCE.md` |
| `squarespace` | `squarespace/SQUARESPACE.md` |
| `bigcommerce` | `bigcommerce/BIGCOMMERCE.md` |
| `wix` | `wix/WIX.md` |
| `magento` | `magento/MAGENTO.md` |
| `unknown` | `generic/GENERIC.md` |

Read the guide for your detected platform. It contains everything you need from browsing through checkout.

---

## Step 4: Browse & Select Products

Follow the navigation guide to:
1. Navigate to the product or collection page
2. Select the correct variant (size, color, quantity)
3. Add to cart or use "Buy it now"

**General tips (all platforms):**
- Don't snapshot full pages — scope to product forms or specific sections
- Use URL patterns when possible (faster than clicking through navigation)
- Confirm price and item name before proceeding to checkout

---

## Step 5: Proceed to Checkout

When ready to purchase:
1. Navigate to or trigger checkout (navigation guide explains how)
2. For the full purchase API flow (approval, decryption, confirmation), see your agent platform's guide in the Secure Card Handoff table in `SKILL.md`

---

## Step 6: Identify the Payment Form

Once you're on the checkout page (after approval and decryption), determine what kind of payment form you're dealing with before filling any fields.

**If you already know it's Shopify** → go directly to `shopify/SHOPIFY.md` → Checkout section. Shopify checkout always uses cross-origin iframes (`card-fields-*` pattern).

**If you already know it's Amazon** → skip this step. Amazon uses saved payment methods, not card form entry.

**For all other platforms**, take a scoped snapshot:

```bash
openclaw browser snapshot --efficient --selector "form"
```

If no form found:
```bash
openclaw browser snapshot --efficient --depth 4
```

From the snapshot, determine:

| What you see | Payment type | Guide |
|-------------|-------------|-------|
| Card fields as regular `<input>` elements | **Inline** | `generic/GENERIC.md` → Inline Card Fields |
| `iframe[src*="js.stripe.com"]` | **Stripe Elements** | `generic/GENERIC.md` → Stripe Elements |
| `iframe[name*="braintree"]` | **Braintree** | `generic/GENERIC.md` → Braintree / Adyen |
| `iframe[src*="adyen"]` | **Adyen** | `generic/GENERIC.md` → Braintree / Adyen |
| `iframe[name^="card-fields-"]` on Shopify | **Shopify iframes** | `shopify/SHOPIFY.md` → Checkout |
| Multiple pages/sections with "Continue" buttons | **Multi-step** | `generic/GENERIC.md` → Multi-Step Checkout |
| No card fields visible, payment method tabs/radios | Select "Credit Card" first, then re-check |

Follow the matched guide section to fill the payment form.

---

## Vendor Discovery API

Find vendors and merchants that CreditClaw has verified checkout skills for:

```bash
curl "https://creditclaw.com/api/v1/bot/skills" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

**Query parameters** (all optional):

| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Search by name or slug | `?search=amazon` |
| `category` | Filter by category | `?category=saas` |
| `checkout` | Filter by checkout method | `?checkout=guest,api` |
| `capability` | Filter by capability (all must match) | `?capability=returns,tracking` |
| `maturity` | Filter by skill maturity | `?maturity=verified,stable` |

Response:
```json
{
  "vendors": [
    {
      "slug": "cloudserve-pro",
      "name": "CloudServe Pro",
      "category": "saas",
      "url": "https://cloudserve.example.com",
      "checkout_methods": ["guest", "api"],
      "capabilities": ["returns", "tracking"],
      "maturity": "verified",
      "agent_friendliness": 0.85,
      "guest_checkout": true,
      "success_rate": 0.92,
      "skill_url": "https://creditclaw.com/api/v1/bot/skills/cloudserve-pro"
    }
  ],
  "total": 1,
  "categories": ["saas", "retail", "marketplace", "food", "software", "payments"]
}
```

## Get a Vendor Skill

```bash
curl "https://creditclaw.com/api/v1/bot/skills/cloudserve-pro" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Returns the vendor's complete checkout instructions as Markdown.

| Field | Meaning |
|-------|---------|
| `agent_friendliness` | 0–1 score of how easy the checkout is for an agent |
| `guest_checkout` | Whether the vendor supports checkout without an account |
| `maturity` | Skill reliability: `verified`, `stable`, `beta`, `experimental` |
| `success_rate` | Historical success rate for agent checkouts |
