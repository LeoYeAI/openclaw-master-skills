# Amazon Shopping — Purchase Guide

Companion to [skill.md](https://creditclaw.com/creditcard/skill.md). Covers how to buy products on Amazon using CreditClaw's Pre-paid Wallet.

**Prerequisite:** Your owner must have set up a Pre-paid Wallet for you. Check `GET /bot/wallet/check` first.

---

## How It Works

You request a purchase → CreditClaw checks your owner's guardrails → your owner approves → CreditClaw places the order on Amazon → you get tracking updates.

All Amazon purchases go through the **Pre-paid Wallet**. Your wallet holds USDC. CreditClaw handles the conversion to fiat and places a real Amazon order on your behalf.

**Endpoint:** `POST /card-wallet/bot/purchase`

---

## Purchase Flow

1. Find the product's ASIN (see "Finding Products" below)
2. `POST /card-wallet/bot/purchase` with ASIN + shipping address
3. CreditClaw checks guardrails (spending limits, merchant allowlist)
4. If approved automatically or below threshold: order proceeds immediately
5. If above threshold: owner has **15 minutes** to approve or reject
6. Poll `GET /card-wallet/bot/purchase/status?approval_id=X` every ~30s
7. On approval: order is placed on Amazon, status becomes `processing`
8. Order progresses: `processing` → `shipped` → `delivered`

### Purchase Request

```bash
curl -X POST https://creditclaw.com/api/v1/card-wallet/bot/purchase \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant": "amazon",
    "product_id": "B01DFKC2SO",
    "quantity": 1,
    "product_name": "AmazonBasics USB Cable",
    "estimated_price_usd": 7.99,
    "shipping_address": {
      "name": "Jane Smith",
      "line1": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94105",
      "country": "US"
    }
  }'
```

### Request Fields

| Field | Required | Notes |
|-------|----------|-------|
| `merchant` | Yes | Always `"amazon"` |
| `product_id` | Yes | Amazon ASIN — 10-character alphanumeric code (e.g. `B01DFKC2SO`) |
| `quantity` | Yes | 1–100 |
| `product_name` | Yes | Human-readable name shown on your owner's approval screen |
| `estimated_price_usd` | Yes | Your best estimate of the price. Actual charge may differ slightly. |
| `shipping_address` | Yes | US addresses only. See address format below. |

### Shipping Address Format

| Field | Required | Example |
|-------|----------|---------|
| `name` | Yes | `"Jane Smith"` |
| `line1` | Yes | `"123 Main St"` |
| `line2` | No | `"Apt 4B"` |
| `city` | Yes | `"San Francisco"` |
| `state` | Yes | `"CA"` |
| `zip` | Yes | `"94105"` |
| `country` | Yes | `"US"` (only US is supported) |

---

## Finding Products (ASIN Discovery)

Every Amazon product has an ASIN — a 10-character code that usually starts with `B0`. You need the ASIN to make a purchase.

### If the user provides a link

Extract the ASIN from the URL. It appears after `/dp/`:
```
https://www.amazon.com/dp/B01DFKC2SO → ASIN is B01DFKC2SO
https://www.amazon.com/AmazonBasics-Cable/dp/B01DFKC2SO/ref=sr_1_1 → ASIN is B01DFKC2SO
```

### If the user provides an ASIN directly

Use it as-is:
```
product_id: "B01DFKC2SO"
```

### If the user describes a product

1. Search the web for the product: `"[product name] site:amazon.com"`
2. Find the ASIN in the Amazon URL
3. **Confirm with the user before purchasing** — show them the product name and estimated price
4. Only proceed after confirmation

**Example:**
```
User: "Buy me some Celsius energy drinks"
You: Search "Celsius energy drink site:amazon.com"
You: "I found CELSIUS Sparkling Orange 12-pack (ASIN: B08P5H1FLX) for about $25. Want me to buy this?"
User: "Yes"
You: POST /card-wallet/bot/purchase with product_id "B08P5H1FLX"
```

### Product Validation

After your purchase request is processed, the response includes the product title from Amazon. **Always compare this against what the user asked for.** ASINs can change or be reassigned. If the returned product name doesn't match, tell the user immediately and ask if they want to proceed.

---

## Order Tracking

Amazon orders provide full delivery tracking. When polling status, the response includes tracking info as it becomes available:

```json
{
  "status": "approved",
  "order_status": "shipped",
  "tracking_info": {
    "carrier": "UPS",
    "tracking_number": "1Z999AA10123456784",
    "tracking_url": "https://www.ups.com/track?tracknum=1Z999AA10123456784",
    "estimated_delivery": "2026-02-18"
  }
}
```

| Field | Availability |
|-------|-------------|
| `carrier` | When shipped (UPS, USPS, FedEx, etc.) |
| `tracking_number` | When shipped |
| `tracking_url` | When shipped |
| `estimated_delivery` | When shipped (may update) |

---

## Order Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Awaiting owner approval |
| `quote` | Pricing the order |
| `processing` | Payment succeeded, Amazon is preparing the order |
| `shipped` | In transit — tracking info available |
| `delivered` | Successfully delivered |
| `payment_failed` | Payment could not be processed |
| `delivery_failed` | Delivery unsuccessful |

---

## What You Can and Cannot Buy

### Can buy:
- Physical products sold by Amazon or verified third-party sellers
- Most standard Prime-eligible items
- Products with standard shipping to US addresses

### Cannot buy:
- Digital products (Kindle books, software, music, video, apps)
- Amazon Fresh, Pantry, or Pharmacy items
- Subscribe & Save items
- Gift cards
- Hazardous materials (batteries, chemicals, flammables)
- Oversized or freight-only items
- Products requiring age verification
- Items unavailable for shipping to the provided US address

If you attempt to purchase a restricted item, the order will fail with a `product_restricted` error after the approval step.

---

## Common Errors

| Error | What to Do |
|-------|-----------|
| 403 — merchant blocked | Your owner has Amazon on their blocklist. Ask them to update merchant settings. |
| 403 — budget exceeded | Purchase exceeds per-transaction, daily, or monthly spending limit. Ask your owner to adjust guardrails if needed. |
| 410 — approval expired | Owner didn't approve within 15 minutes. Resubmit the purchase request. |
| `product_restricted` | Item is digital, hazmat, gift card, or otherwise restricted. Choose a different product. |
| `payment_failed` | Wallet balance insufficient or payment processing failed. Check balance with `GET /card-wallet/balance`. |
| `delivery_failed` | Amazon couldn't deliver. Check tracking info for details. May need a different shipping address. |
| `product_not_found` | Invalid ASIN or product no longer available on Amazon. Verify the ASIN. |

---

## Webhook Events

If you registered with a `callback_url`, you'll receive these events instead of needing to poll:

| Event | Trigger |
|-------|---------|
| `purchase.approved` | Owner approved your purchase |
| `purchase.rejected` | Owner rejected your purchase |
| `purchase.expired` | 15-minute approval window passed |
| `order.shipped` | Order shipped — tracking info included in payload |
| `order.delivered` | Order delivered |
| `order.failed` | Payment or delivery failed |

---

## Quick Reference

| Item | Value |
|------|-------|
| Endpoint | `POST /card-wallet/bot/purchase` |
| Status polling | `GET /card-wallet/bot/purchase/status?approval_id=X` |
| Merchant value | `"amazon"` |
| Product ID format | ASIN (10-char alphanumeric, e.g. `B01DFKC2SO`) |
| Shipping | US only |
| Approval window | 15 minutes |
| Order tracking | Full (carrier, tracking number, URL, ETA) |
| Poll interval | ~30 seconds |
