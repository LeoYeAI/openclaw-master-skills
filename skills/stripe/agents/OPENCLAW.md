---
name: creditclaw-openclaw-checkout
version: 2.9.0
updated: 2026-03-18
description: "OpenClaw sub-agent checkout flow — spawn, execute, report, confirm, verify deletion."
companion_of: SKILL.md
api_base: https://creditclaw.com/api/v1
credentials: [CREDITCLAW_API_KEY]
---

# OpenClaw — Sub-Agent Checkout Flow

> **Companion to `SKILL.md`.**
> For registration, card setup, spending permissions, and the full API reference, see the main skill file.

On OpenClaw, every checkout is handled by an **ephemeral sub-agent**. Your main agent never
sees decrypted card data. The sub-agent is spawned for a single transaction, completes the
checkout, reports the result back to you, and is then deleted — decrypted card data never
persists in any agent's context.

**Security:** The sub-agent pattern ensures:
- Your main agent **never sees** decrypted card details
- Card data exists only in the sub-agent's memory for the duration of one transaction
- The sub-agent is deleted after checkout — no data leaks across sessions
- If the sub-agent crashes, the decryption key is already consumed and cannot be reused
- Server-side guardrails still enforce all spending limits regardless of what happens client-side

---

## Purchase Flow

```
Main Agent:
  1. Call POST /bot/rail5/checkout with merchant and amount details
  2. If pending_approval → wait for owner (webhook or poll)
  3. Once approved → spawn a sub-agent using spawn_payload

Sub-Agent:
  4. Call POST /bot/rail5/key for the one-time decryption key
  5. Decrypt card details using AES-256-GCM
  6. Navigate to the merchant checkout page
  7. Detect the platform → load the matching checkout guide
  8. Fill shipping/billing, then card fields
  9. Submit and capture confirmation
  10. Call POST /bot/rail5/confirm with success or failure
  11. Report result back to main agent
  12. Discard all decrypted card data — sub-agent is deleted

Main Agent:
  13. Verify the sub-agent was deleted
  14. Announce the result to your owner
```

---

## Step 1: Request Checkout (Main Agent)

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
  "checkout_steps": [
    "Call POST /api/v1/bot/rail5/key with { \"checkout_id\": \"r5chk_abc123\" } to get the decryption key.",
    "Run: node decrypt.js <key_hex> <iv_hex> <tag_hex> Card-ChaseD-9547.md",
    "Use the decrypted card details to complete checkout at DigitalOcean.",
    "Call POST /api/v1/bot/rail5/confirm with { \"checkout_id\": \"r5chk_abc123\", \"status\": \"success\" } when done.",
    "If checkout fails, call confirm with { \"status\": \"failed\" } instead.",
    "Announce the result."
  ],
  "spawn_payload": {
    "task": "You are a checkout agent...",
    "cleanup": "delete",
    "runTimeoutSeconds": 300,
    "label": "checkout-digitalocean"
  }
}
```

**`spawn_payload` fields:**

| Field | Description |
|-------|-------------|
| `task` | Full instructions for the sub-agent — what to buy, which API calls to make, how to decrypt |
| `cleanup` | Always `"delete"` — OpenClaw destroys the sub-agent after it finishes or times out |
| `runTimeoutSeconds` | Maximum time the sub-agent is allowed to run (300 seconds = 5 minutes) |
| `label` | Human-readable label for the sub-agent session (e.g. `"checkout-digitalocean"`) |

**Pending response (requires owner approval):**
```json
{
  "approved": false,
  "status": "pending_approval",
  "checkout_id": "r5chk_abc123",
  "message": "Amount exceeds auto-approve threshold. Your owner has been notified.",
  "expires_in_minutes": 15
}
```

---

## Step 2: Wait for Approval (Main Agent)

If the response status is `pending_approval`, your owner needs to approve the purchase.
Poll for the result:

```bash
curl "https://creditclaw.com/api/v1/bot/rail5/checkout/status?checkout_id=r5chk_abc123" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Poll every 30 seconds. Do not spawn a sub-agent until the status is `approved`.

| Status | Meaning |
|--------|---------|
| `pending_approval` | Owner hasn't responded — poll again in 30s |
| `approved` | Proceed with spawning a sub-agent |
| `rejected` | Do not proceed |
| `expired` | 15-min window passed — re-initiate if needed |
| `completed` | Checkout confirmed successful |
| `failed` | Checkout reported failure |

Your owner receives the approval request via their dashboard and email. Approvals expire
after 15 minutes.

---

## Step 3: Spawn Sub-Agent (Main Agent)

Once the checkout is approved, spawn an ephemeral sub-agent using the `spawn_payload`
from the response. **Save the returned `sub_agent_id`** — you will need it in Step 10
to verify the sub-agent was deleted.

```
const sub_agent_id = sessions_spawn({
  task: spawn_payload.task,
  cleanup: "delete",
  runTimeoutSeconds: 300,
  label: spawn_payload.label
})
// sub_agent_id → e.g. "sa_checkout_abc123"
```

The sub-agent receives the `task` string as its instructions. It will execute steps 4–11
autonomously. You (the main agent) wait for the sub-agent to complete.

**Do not pass your `CREDITCLAW_API_KEY` in the task.** The sub-agent inherits your
credentials through the OpenClaw session — it uses the same API key automatically.

**Do not interfere** with the sub-agent while it is running. Wait for it to finish or
time out.

---

## Step 4: Get Decryption Key (Sub-Agent)

The sub-agent calls this endpoint to retrieve the one-time decryption key:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/key \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "checkout_id": "r5chk_abc123" }'
```

Response: `{ "key_hex": "...", "iv_hex": "...", "tag_hex": "..." }`

**Single-use.** Cannot be retrieved again. If decryption fails, the checkout must be
re-initiated from Step 1.

---

## Step 5: Decrypt Card Details (Sub-Agent)

The sub-agent runs the deterministic decrypt script that was delivered with the card file:

```
node decrypt.js <key_hex> <iv_hex> <tag_hex> Card-ChaseD-9547.md
```

This outputs the card JSON (number, CVV, expiry, name, billing address).

Perform AES-256-GCM decryption using `key_hex`, `iv_hex`, and the encrypted card blob.
The GCM auth tag is already included in the encrypted blob — do NOT append `tag_hex`
separately.

**Critical:** The sub-agent must **never** store, log, or persist the decrypted card data.
It exists only in memory for this single transaction. After checkout, the sub-agent is deleted.

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

## Step 6: Detect Platform & Fill Checkout (Sub-Agent)

### 6a. Platform & Payment Form Detection

If you haven't already detected the platform via `SHOPPING-GUIDE.md`, do it now — see SHOPPING-GUIDE.md Step 2 (platform detection) and Step 6 (payment form identification).

If you already ran detection during the browsing phase, skip to 6b.

### 6b. Browser Interaction Rules (All Platforms)

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

## Step 7: After Submission (Sub-Agent)

After clicking the pay/submit button, wait for the confirmation page:

| Signal | Meaning |
|--------|---------|
| "Thank you", "Order confirmed", "Order #..." | **Success** — capture order number |
| "Payment successful", "Receipt" | **Success** |
| "Payment declined", "Card declined" | **Failed** |
| "Error", "try again" | **Failed** — do not retry automatically |
| Page unchanged after 30 seconds | **Failed** |

---

## Step 8: Confirm Checkout (Sub-Agent)

After completing (or failing) checkout at the merchant:

```bash
curl -X POST https://creditclaw.com/api/v1/bot/rail5/confirm \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "checkout_id": "r5chk_abc123",
    "status": "success"
  }'
```

Use `"status": "failed"` if checkout didn't work. On success, the transaction is recorded
in your owner's dashboard. After your first successful checkout, your card status moves
from `confirmed` to `active`.

---

## Step 9: Report Result to Main Agent (Sub-Agent)

Before the sub-agent is deleted, it must report the checkout result back to the main agent.
This is how the main agent learns what happened — it cannot see the sub-agent's context.

The sub-agent sends a structured result using the OpenClaw session return:

```
sessions_send({
  status: "success",
  checkout_id: "r5chk_abc123",
  merchant: "DigitalOcean",
  item: "Droplet hosting - 1 month",
  amount_usd: 12.00,
  order_id: "ORD-12345",
  message: "Purchase completed successfully."
})
```

For failures:

```
sessions_send({
  status: "failed",
  checkout_id: "r5chk_abc123",
  merchant: "DigitalOcean",
  item: "Droplet hosting - 1 month",
  amount_usd: 12.00,
  reason: "Card declined at checkout.",
  message: "Purchase failed — card was declined."
})
```

**After sending the report, the sub-agent discards all decrypted card data.** The sub-agent's
job is done — `cleanup: "delete"` ensures OpenClaw destroys it automatically.

---

## Step 10: Verify Sub-Agent Deletion (Main Agent)

After receiving the sub-agent's report (or after the timeout expires), use the `sub_agent_id`
you saved in Step 3 to verify the sub-agent was actually deleted:

```
sessions_status(sub_agent_id)
```

**Expected result:** The session should not exist or should show status `deleted`.

| Session Status | Action |
|----------------|--------|
| `deleted` or not found | Sub-agent was cleaned up successfully. Proceed to announce result. |
| `completed` | Sub-agent finished but hasn't been cleaned up yet. Wait 10 seconds, check again. |
| `running` | Sub-agent is still active. Wait for timeout or check again in 30 seconds. |
| Still `running` after timeout | Something went wrong. Log this and report the anomaly to your owner. The decryption key is already consumed, so card data cannot be re-accessed even if the sub-agent persists. |

**If the sub-agent persists beyond its timeout**, report this to your owner as an operational
anomaly. The card data is still protected — the key was single-use and the server-side
guardrails prevent duplicate spending — but the sub-agent should not remain active.

---

## Step 11: Announce Result (Main Agent)

Once you've confirmed the sub-agent was cleaned up, announce the result to your owner:

**On success:**
> "Purchased Droplet hosting - 1 month at DigitalOcean for $12.00. Order ID: ORD-12345."

**On failure:**
> "Purchase of Droplet hosting at DigitalOcean failed — card was declined. No charge was made."

**On timeout (sub-agent did not report back):**
> "The checkout sub-agent for DigitalOcean timed out after 5 minutes without reporting a result.
> The decryption key has been consumed. Please check your DigitalOcean account and CreditClaw
> dashboard to verify whether the purchase went through. If needed, I can re-initiate the checkout."

---

## Timeout & Failure Handling

The sub-agent has a hard time limit set by `runTimeoutSeconds` (default: 300 seconds / 5 minutes).

### What happens at timeout

| Scenario | What Happens |
|----------|-------------|
| Sub-agent finishes before timeout | Normal flow — result is reported, sub-agent is deleted |
| Sub-agent is still running at timeout | OpenClaw terminates and deletes the sub-agent automatically |
| Sub-agent crashes mid-checkout | OpenClaw detects the crash and deletes the sub-agent |

### What the main agent should do

| Scenario | Action |
|----------|--------|
| Sub-agent reports success | Announce success to owner |
| Sub-agent reports failure | Announce failure to owner — no charge was made |
| Sub-agent times out (no report received) | Check `GET /bot/rail5/checkout/status?checkout_id=...` to see if confirm was called before the timeout. If status is `completed`, the purchase went through. If status is `approved`, check `key_delivered` in the response: if `true`, the sub-agent retrieved the key and may have attempted checkout — advise owner to check the merchant account. If `key_delivered` is `false`, no card data was accessed and you can safely re-initiate. |
| Sub-agent crashes before getting the key | No card data was exposed. Re-initiate checkout from Step 1. |
| Sub-agent crashes after getting the key | The key is consumed and cannot be reused. Card data was in the sub-agent's memory and is destroyed with the crash. Check checkout status and advise owner. |

### Re-initiating after failure

If the checkout fails or times out, you can start a new checkout from Step 1. Each checkout
gets a fresh `checkout_id` and a fresh single-use decryption key. There is no limit on retry
attempts, but each attempt goes through the full guardrail and approval flow.

---

## Complete Example

Here's a full end-to-end example of an OpenClaw checkout:

```
# Step 1: Main agent requests checkout
POST /api/v1/bot/rail5/checkout
{ "merchant_name": "DigitalOcean", "merchant_url": "https://cloud.digitalocean.com/billing",
  "item_name": "Droplet hosting", "amount_cents": 1200, "category": "cloud_compute" }

# Response: approved with spawn_payload
# { "approved": true, "checkout_id": "r5chk_abc123", "spawn_payload": { ... } }

# Step 2: Main agent waits for approval (if pending) — skip if already approved

# Step 3: Main agent spawns sub-agent (save the ID)
sub_agent_id = sessions_spawn({ task: spawn_payload.task, cleanup: "delete", runTimeoutSeconds: 300 })

# Steps 4-9: Sub-agent runs autonomously:
#   → Gets decryption key
#   → Decrypts card file
#   → Navigates to DigitalOcean checkout
#   → Fills card details and submits
#   → Calls POST /bot/rail5/confirm with { status: "success" }
#   → Reports result: sessions_send({ status: "success", merchant: "DigitalOcean", ... })
#   → Sub-agent is automatically deleted

# Step 10: Main agent verifies sub-agent deletion
sessions_status(sub_agent_id)  # → deleted or not found

# Step 11: Main agent announces
"Purchased Droplet hosting at DigitalOcean for $12.00. Order ID: ORD-12345."
```
