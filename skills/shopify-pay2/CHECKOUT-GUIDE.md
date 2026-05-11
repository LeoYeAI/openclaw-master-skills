---
name: creditclaw-checkout-guide
version: 2.9.0
updated: 2026-03-16
description: "My Card — complete purchase flow, browser checkout, and confirmation."
companion_of: SKILL.md
api_base: https://creditclaw.com/api/v1
credentials: [CREDITCLAW_API_KEY]
---

# My Card — Checkout Guide

> **Companion to `SKILL.md`.**
> For registration, card setup, spending permissions, and the full API reference, see the main skill file.

This guide covers the complete purchase flow — from requesting checkout approval through filling the merchant's payment form to confirming the result.

**Security:** Never store, log, or persist decrypted card data. It exists only in memory for the duration of a single checkout. Discard it immediately after.

---

## Purchase Flow

```
1. Call POST /bot/rail5/checkout with merchant and amount details
2. If pending_approval → wait for owner (webhook or poll)
3. Once approved → call POST /bot/rail5/key for the one-time decryption key
4. Decrypt card details using AES-256-GCM
5. Navigate to the merchant checkout page
6. Detect the platform → load the matching checkout guide
7. Fill shipping/billing, then card fields
8. Submit and capture confirmation
9. Call POST /bot/rail5/confirm with success or failure
10. Discard all decrypted card data
```

---

## Step 1: Request Checkout

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/checkout \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_name": "DigitalOcean",
    "merchant_url": "https://cloud.digitalocean.com/billing",
    "item_name": "Droplet hosting - 1 month",
    "amount_cents": 1200,
    "category": "cloud_compute"
  }'
```

| Field | Required | Description |
|-------|----------|-------------|
| `merchant_name` | Yes | Merchant name (1-200 chars) |
| `merchant_url` | Yes | Merchant website URL |
| `item_name` | Yes | What you're buying |
| `amount_cents` | Yes | Amount in cents (integer) |
| `category` | No | Spending category |

**Approved response:**
```json
{
  "approved": true,
  "checkout_id": "r5chk_abc123",
  "checkout_steps": ["..."],
  "spawn_payload": { "task": "...", "cleanup": "delete", "runTimeoutSeconds": 300 }
}
```

**Pending response:**
```json
{
  "approved": false,
  "status": "pending_approval",
  "checkout_id": "r5chk_abc123",
  "message": "Amount exceeds auto-approve threshold. Your owner has been notified.",
  "expires_in_minutes": 15
}
```

### Waiting for Approval

If `pending_approval`:
- **Webhook:** You'll receive `wallet.spend.authorized` or `wallet.spend.declined` automatically.
- **Polling:** Call every 30 seconds:

```bash
curl "https://creditclaw.com/api/v1/bot/rail5/checkout/status?checkout_id=r5chk_abc123" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

| Status | Meaning |
|--------|---------|
| `pending_approval` | Owner hasn't responded — poll again in 30s |
| `approved` | Proceed with checkout |
| `rejected` | Do not proceed |
| `expired` | 15-min window passed — re-initiate if needed |
| `completed` | Checkout confirmed successful |
| `failed` | Checkout reported failure |

---

## Step 2: Get Decryption Key

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/key \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "checkout_id": "r5chk_abc123" }'
```

Response: `{ "key_hex": "...", "iv_hex": "...", "tag_hex": "..." }`

**Single-use.** Cannot be retrieved again. If decryption fails, re-initiate checkout.

---

## Step 3: Decrypt Card Details

Perform AES-256-GCM decryption using `key_hex`, `iv_hex`, and the encrypted card blob. The GCM auth tag is already included in the encrypted blob — do NOT append `tag_hex` separately.

**Never store, log, or persist decrypted card data.**

### Card Data → Form Fields

| Decrypted Field | Form Field | Notes |
|-----------------|------------|-------|
| `number` | Card number | Enter as-is |
| `exp_month` + `exp_year` | Expiration | Combine as MM/YY. Some forms have separate fields. |
| `cvv` | Security code / CVV | 3 or 4 digits |
| `name` | Name on card | Enter as-is |
| `address` | Billing address | Optional — some forms pre-fill from shipping |
| `city`, `state`, `zip`, `country` | Billing fields | Optional — use defaults if not in card data |

---

## Step 4: Detect Platform & Fill Checkout

### 4a. Platform & Payment Form Detection

If you haven't already detected the platform via `SHOPPING-GUIDE.md`, do it now — see SHOPPING-GUIDE.md Step 2 (platform detection) and Step 6 (payment form identification).

If you already ran detection during the browsing phase, skip to 4b.

### 4b. Browser Interaction Rules (All Platforms)

These rules apply regardless of which platform guide you're following:

**Snapshots:**
- Always use `--efficient` flag
- Budget: **5 snapshots target, 8 max**. Fail if exceeded.
- Use `--selector "form"` to scope when possible
- After any navigation or button click, wait for network idle before snapshotting

**Interacting with elements:**
```bash
openclaw browser click e12                    # click element
openclaw browser type e13 "value"             # type into field
openclaw browser select e14 "Option"          # native <select>
openclaw browser press Enter                  # press key
openclaw browser press Tab                    # move focus
```

**Custom/React dropdowns** (no native `<select>`):
```bash
openclaw browser click e14                    # open dropdown
openclaw browser type e14 "United"            # filter
openclaw browser press Enter                  # select
```

**If click/type fails:**
```bash
openclaw browser highlight e12                # debug — verify ref is correct
openclaw browser press Tab                    # try keyboard navigation
```

**Iframe card fields:**
```bash
openclaw browser snapshot --interactive --frame "iframe[src*='stripe']"
```
Fill fields using refs from the iframe snapshot. Switch back to main page to click submit.

**Hard stops:**
- CAPTCHA / 3DS / OTP → fail immediately
- Max 2 retries per field. Then try Tab + type. If still failing → fail checkout.

---

## Step 5: After Submission

After clicking the pay/submit button, wait for the confirmation page:

| Signal | Meaning |
|--------|---------|
| "Thank you", "Order confirmed", "Order #..." | **Success** — capture order number |
| "Payment successful", "Receipt" | **Success** |
| "Payment declined", "Card declined" | **Failed** |
| "Error", "try again" | **Failed** — do not retry automatically |
| Page unchanged after 30 seconds | **Failed** |

---

## Step 6: Confirm Checkout

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/confirm \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "checkout_id": "r5chk_abc123", "status": "success" }'
```

Use `"status": "failed"` if checkout didn't work. Discard all decrypted card data immediately.
