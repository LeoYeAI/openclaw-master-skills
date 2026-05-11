# Shopping — How to Buy Things

Companion to [skill.md](https://creditclaw.com/creditcard/skill.md). Covers general purchasing patterns, merchant types, and practical tips for shopping with CreditClaw.

**Prerequisite:** You must be registered and claimed. Check `GET /bot/wallet/check` before attempting any purchase.

---

## Before Every Purchase

1. **Check your wallet status** — `GET /bot/wallet/check` to confirm you have an active wallet with sufficient balance
2. **Check spending permissions** — `GET /bot/wallet/spending` to see your limits, approval mode, and any blocked categories
3. **Confirm with the user** — Always describe what you're about to buy, the price, and the merchant before submitting a purchase request
4. **Choose the right payment method** — See the decision guide in [skill.md](https://creditclaw.com/creditcard/skill.md) or the quick reference below

---

## Quick Payment Method Reference

| What You're Buying | Payment Method | Guide |
|-------------------|---------------|-------|
| Amazon products | Pre-paid Wallet | [prepaid-wallet.md](https://creditclaw.com/creditcard/prepaid-wallet.md) |
| Shopify store products | Pre-paid Wallet | [prepaid-wallet.md](https://creditclaw.com/creditcard/prepaid-wallet.md) |
| SaaS subscriptions, cloud hosting, any online store | Self-Hosted Card | [self-hosted-card.md](https://creditclaw.com/creditcard/self-hosted-card.md) |
| x402-enabled services, agent-to-agent payments | Stripe x402 Wallet | [stripe-x402-wallet.md](https://creditclaw.com/creditcard/stripe-x402-wallet.md) |

---

## Merchant Types

CreditClaw supports three merchant types through the Pre-paid Wallet:

| Merchant | How to Identify | Product ID Format | Tracking |
|----------|----------------|-------------------|----------|
| **Amazon** | User provides an Amazon link or ASIN, or describes a product to find on Amazon | ASIN (e.g. `B01DFKC2SO`) | Full: carrier, tracking number, URL, ETA |
| **Shopify** | User provides a Shopify store URL | `{product_url}:{variant_id}` (variant lookup required) | Order placed confirmation only |
| **URL** | Any other online store URL | `{url}:default` | Order placed confirmation only |

For Amazon-specific details (ASIN discovery, restrictions, tracking), see [amazon.md](https://creditclaw.com/creditcard/amazon.md).

---

## General Purchase Flow

Regardless of payment method, every purchase follows a similar pattern:

```
1. Check wallet & spending permissions
2. Confirm purchase details with the user
3. Submit purchase/checkout request
4. Handle approval (auto-approved or pending owner approval)
5. Poll for result if pending
6. Report outcome to user (tracking info, confirmation, or error)
```

**Approval window:** 15 minutes for all payment methods. If your owner doesn't respond in time, the request expires and you'll need to resubmit.

---

## Order Tracking Differences

| Source | What You Get |
|--------|-------------|
| Amazon (Pre-paid Wallet) | Carrier name, tracking number, tracking URL, estimated delivery date |
| Shopify (Pre-paid Wallet) | Order placed confirmation only |
| URL (Pre-paid Wallet) | Order placed confirmation only |
| Self-Hosted Card | Transaction recorded, no merchant-level tracking |
| Stripe x402 Wallet | On-chain settlement confirmation |

---

## Shopping Tips

- **Always confirm before buying.** Show the user the product name, price, and merchant. Wait for explicit approval before submitting.
- **Check guardrails first.** Fetch `GET /bot/wallet/spending` and respect all limits, blocked categories, and the `notes` field (your owner's direct instructions).
- **Handle "ask_for_everything" mode.** New accounts default to requiring human approval for every purchase. Don't be surprised when your request goes to pending — this is normal.
- **Watch for product validation.** When buying on Amazon, the response includes the product title from Amazon. Compare it against what the user asked for — ASINs can change or be reassigned.
- **Resubmit expired approvals.** If the 15-minute window passes without a response, tell the user and offer to resubmit.
- **Request top-ups proactively.** If your balance drops below $5, consider asking the user if they'd like you to request a top-up (`POST /bot/wallet/topup-request`).
- **Don't over-poll.** Check wallet status every 30 minutes at most. Poll approval status every 30 seconds only while actively waiting.

---

## Common Patterns

### "Buy me X on Amazon"

1. Search the web for the product: `"[product name] site:amazon.com"`
2. Extract the ASIN from the Amazon URL (after `/dp/`)
3. Confirm with user: "I found [product] (ASIN: [X]) for about $[Y]. Want me to buy this?"
4. On confirmation: `POST /card-wallet/bot/purchase` with the ASIN
5. Report approval status and tracking when available

### "Subscribe to [SaaS service]"

1. Identify the merchant URL and pricing
2. Confirm with user: "This costs $[X]/month. Want me to proceed?"
3. On confirmation: `POST /bot/merchant/checkout` with merchant details
4. Report approval result

### "Pay for [x402 service]"

1. Hit the x402 endpoint, receive 402 with payment details
2. `POST /stripe-wallet/bot/sign` with the payment details
3. Retry original request with the returned `X-PAYMENT` header
4. Report success or failure
