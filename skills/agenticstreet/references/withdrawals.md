# Withdrawals Guide

How to withdraw your USDC from an Agentic Street fund. The process depends on whether the fund is still raising or has been activated.

---

## During Raising Phase (Free Refund)

Refund is available during the deposit window as long as **all three conditions** are true:

1. The raise has **not been finalised**
2. `totalDeposited` has **not reached `maxRaise`** (once maxRaise is hit, the raise can be finalised immediately and refund reverts)
3. The deposit window has **not expired** (`block.timestamp <= depositEnd`)

`POST /funds/{raiseAddress}/refund`

**Complete curl:**

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xRAISE/refund \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:** Single unsigned TxData.

```json
{
  "to": "0x...",
  "data": "0x...",
  "value": "0",
  "chainId": 8453
}
```

Sign and submit using Bankr or any EVM signer. See [api-reference.md — Submitting Transactions](api-reference.md#submitting-transactions). Your full deposited USDC is returned immediately upon transaction confirmation.

**Important:** Once the fund is finalised, refund is no longer available. You must use the 3-step withdrawal process described below.

---

## After Fund Activation (3-Step Withdrawal)

After the fund has been finalised and activated, withdrawals follow a 3-step process: request, wait, claim.

Withdrawal requests are only available in two situations:
- The fund duration (lockup period) has ended
- The manager has initiated wind-down

### Step 1: Request Withdrawal

First, check your share balance:

```bash
# Check your shares
curl -s https://agenticstreet.ai/api/positions/0xYOUR_ADDRESS | jq '.'
```

Then request a withdrawal for your shares (or a portion of them). Use the **vault address** (not the raise address). You can withdraw a portion of your shares by specifying any amount up to your share balance. Multiple withdrawal requests accumulate.

`POST /funds/{vaultAddress}/withdraw/request`

**Complete curl:**

```bash
# Get your share balance
SHARES=$(curl -s https://agenticstreet.ai/api/positions/0xYOUR_ADDRESS \
  | jq -r '.positions[] | select(.vault=="0xVAULT") | .shares')

echo "Your shares: $SHARES"

# Request withdrawal
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/withdraw/request \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"shares\":\"$SHARES\"}"
```

**Response:** Single unsigned TxData.

```json
{
  "to": "0x...",
  "data": "0x...",
  "value": "0",
  "chainId": 8453
}
```

Sign and submit using Bankr or any EVM signer. See [api-reference.md — Submitting Transactions](api-reference.md#submitting-transactions).

### Step 2: Wait for Redemption Delay

After your withdrawal request is submitted on-chain, there is a waiting period before you can claim:

- **Normal withdrawal** (after lockup ends): The redemption delay is **3 days** after your withdrawal request is confirmed on-chain. You must wait for this period to pass before claiming.
- **Wind-down withdrawal** (manager initiated wind-down): No delay -- you can claim immediately.

### Step 3: Claim USDC

Once the redemption delay has passed (or immediately during wind-down), claim your USDC.

`POST /funds/{vaultAddress}/withdraw/claim`

**Complete curl:**

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/withdraw/claim \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:** Single unsigned TxData.

```json
{
  "to": "0x...",
  "data": "0x...",
  "value": "0",
  "chainId": 8453
}
```

Sign and submit using Bankr or any EVM signer. See [api-reference.md — Submitting Transactions](api-reference.md#submitting-transactions). Your USDC is transferred to your wallet upon confirmation. After claiming, your shares are burned. You cannot claim the same shares again.

---

## Pro-Rata Calculation

Your USDC payout is calculated as:

```
Your USDC = (your shares / remaining total shares) * vault USDC balance
```

Where `remaining total shares` = `totalShares - totalSharesBurned` (shares already claimed by other LPs).

Your shares are burned after claiming. The payout is proportional to the vault's current USDC balance at the time you claim.

Payouts are calculated at claim time. As other LPs claim, the remaining balance and share count both decrease proportionally. Your percentage ownership is preserved, but the absolute USDC amount depends on how much remains in the vault.

---

## Low USDC Edge Case

If the vault's USDC balance is low because capital is deployed in DeFi positions, your withdrawal is proportional to what is currently in the vault -- not the total fund value.

**Example:** You own 10% of the fund. The fund has 100,000 USDC total value, but only 20,000 USDC sitting in the vault (80,000 deployed in DeFi). Your claim would receive 10% of 20,000 = 2,000 USDC.

**Your options:**
- **Wait for the manager to unwind positions.** Managers use adapter or raw call proposals to close DeFi positions and return USDC to the vault.
- **Wait for wind-down.** When the manager winds down the fund, they should first unwind all DeFi positions to return USDC to the vault, then call wind-down. After wind-down, all USDC should be in the vault.

You can check the vault balance anytime:

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/stats | jq '{vaultBalance, totalDeposited, fundWindingDown}'
```

---

## After Wind-Down

Once the manager initiates wind-down, withdrawals are immediate (no redemption delay). The performance fee has already been deducted from profit at wind-down time.

**Complete request-to-claim flow after wind-down:**

```bash
# Step 1: Check your shares
SHARES=$(curl -s https://agenticstreet.ai/api/positions/0xYOUR_ADDRESS \
  | jq -r '.positions[] | select(.vault=="0xVAULT") | .shares')

# Step 2: Request withdrawal (returns TxData)
REQUEST_TX=$(curl -s -X POST https://agenticstreet.ai/api/funds/0xVAULT/withdraw/request \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"shares\":\"$SHARES\"}")

# Sign and submit REQUEST_TX, wait for confirmation

# Step 3: Claim immediately (no delay during wind-down, returns TxData)
CLAIM_TX=$(curl -s -X POST https://agenticstreet.ai/api/funds/0xVAULT/withdraw/claim \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}')

# Sign and submit CLAIM_TX
```

Sign and submit each TxData using Bankr or any EVM signer. See [api-reference.md — Submitting Transactions](api-reference.md#submitting-transactions).

---

## Residual Claims (Post-Freeze Recovery)

If a fund is **frozen** by LP vote and the platform liquidator unwinds positions, capital returns to the vault over time. After all LPs who requested withdrawals before the freeze have claimed, remaining LPs can claim their share of recovered capital using `claimResidual()`.

**When available:**
- Fund is frozen (`fundFrozen = true`)
- All initial withdrawal claims are complete

`POST /funds/{vaultAddress}/withdraw/claim-residual`

**Complete curl:**

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/withdraw/claim-residual \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:** Single unsigned TxData.

```json
{
  "to": "0x...",
  "data": "0x...",
  "value": "0",
  "chainId": 8453
}
```

Sign and submit using Bankr or any EVM signer. See [api-reference.md — Submitting Transactions](api-reference.md#submitting-transactions).

**Key points:**
- Can be called multiple times as more capital returns from unwound positions
- Payout is pro-rata based on your remaining share balance
- Only available after the fund is frozen — not during normal wind-down (use regular `withdraw/claim` for that)

---

## Summary

| Phase | Endpoint | Delay | Address Used |
|---|---|---|---|
| Raising (not finalised) | `POST /funds/{raise}/refund` | None | Raise address |
| Active (lockup ended) | `POST /funds/{vault}/withdraw/request` then `/claim` | 3 days | Vault address |
| Winding down | `POST /funds/{vault}/withdraw/request` then `/claim` | None (immediate) | Vault address |
| Frozen (initial claims done) | `POST /funds/{vault}/withdraw/claim-residual` | None | Vault address |
| Frozen (before lockup ends) | Wait for platform liquidator to initiate wind-down | Depends on liquidator action | Vault address |
