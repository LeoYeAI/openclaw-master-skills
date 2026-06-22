# Fund Manager Operations Guide

Operational reference for fund managers after the fund is activated. Covers proposing trades, drawdown limits, fee claiming, and wind-down.

---

## Prerequisites

Your fund must be finalised (deposits met `minRaise`, `finalise()` called, fund activated). Verify status:

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/stats | jq '.status'
# Should return "active"
```

If the status is `"raising"`, the deposit window is still open or finalisation has not been called. If `"winding_down"`, the fund is already closing.

All write endpoints below require an API key:
```
Authorization: Bearer $API_KEY
```

All write endpoints return unsigned TxData:
```json
{
  "to": "0x...",
  "data": "0x...",
  "value": "0",
  "chainId": 8453
}
```

Sign and submit using Bankr or any EVM signer (see [Submitting Transactions](#submitting-transactions) at the bottom).

---

## Proposing DeFi Trades

There are two ways to propose trades. Use the **adapter path** for supported protocols — it handles encoding and executes instantly. Use the **raw call path** for everything else — you provide calldata directly, and it goes through a time delay with LP veto.

| Path | Input | Delay | Veto | Use when |
|------|-------|-------|------|----------|
| Adapter | `adapter` + `action` + `params` | None (instant) | No | Uniswap V3, Aave V3 |
| Raw call | `target` + `calldata` + `value` | 7200s | Yes | Any other protocol |

### Adapter Path (Recommended)

One proposal. No approval step. The server encodes the calldata for you.

**Supported adapters and actions:**

| Adapter | Actions |
|---------|---------|
| `uniswap_v3` | `swapExactInputSingle`, `swapExactInput` |
| `aave_v3` | `supply`, `withdraw`, `borrow`, `repay` |

**Example: Uniswap swap (1000 USDC → WETH)**

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/propose \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "adapter": "uniswap_v3",
    "action": "swapExactInputSingle",
    "params": {
      "tokenIn": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "tokenOut": "0x4200000000000000000000000000000000000006",
      "fee": 3000,
      "amountIn": "1000000000",
      "amountOutMin": "0"
    }
  }'
```

Returns TxData. Sign and submit. The vault transfers USDC to the adapter, the adapter executes the swap, and the output token is sent back to the vault — all in one transaction.

**Example: Aave supply (5000 USDC)**

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/propose \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "adapter": "aave_v3",
    "action": "supply",
    "params": {
      "token": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "amount": "5000000000"
    }
  }'
```

### Raw Call Path

For protocols without an adapter. You construct the calldata yourself. Each proposal enters a time-delayed queue where LPs can veto.

DeFi operations via raw call typically require **two proposals** (approve + action):

**Step 1 -- Propose USDC approval:**

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/propose \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "calldata": "0x095ea7b3000000000000000000000000ROUTER_ADDRESS000000000000000000000000000000000000000000000000000000003B9ACA00",
    "value": "0"
  }'
```

**Step 2 -- Propose the operation:**

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/propose \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "0xROUTER_ADDRESS",
    "calldata": "0x<encoded function call>",
    "value": "0"
  }'
```

You must encode the calldata using the target protocol's ABI.

**Step 3 -- Wait for delays, then execute:**

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/proposals | jq '.'
```

Each proposal shows `executableAt` and `vetoPercent`. Once the delay passes without veto reaching 33%, execute in order:

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/proposals/0/execute \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Execute the approval first, then the operation.

### Important Notes on Proposals

- **Adapter proposals execute instantly** — no delay, no veto window, no separate approval step.
- **Raw call proposals are time-delayed** — LPs can veto during the delay window.
- **Target must be a contract** — the vault blocks proposals targeting EOAs.
- **USDC target restrictions** — only `approve()` is allowed when targeting the USDC contract. `transfer()` and `transferFrom()` are blocked.
- **Proposals cannot be submitted when the fund is frozen or winding down.**

---

## Drawdown Schedule

The drawdown limit controls how much USDC can leave the vault. It is cumulative and does **NOT** refill when capital is returned.

### How It Works

The drawdown has two phases:

- **At activation:** 50% of `initialDeposits` is available immediately.
- **After first interval** (`fundDuration / 10`): 100% is available.

| Fund Duration | First Interval | Example (100k USDC fund) |
|---------------|---------------|--------------------------|
| 30 days | 3 days | 50k immediately, 100k after day 3 |
| 60 days | 6 days | 50k immediately, 100k after day 6 |
| 90 days | 9 days | 50k immediately, 100k after day 9 |

### Formula

```
if elapsed >= drawdownIntervalSeconds:
  allowance = initialDeposits
else:
  allowance = initialDeposits / 2
```

`initialDeposits` is the USDC the vault actually received — after any protocol fee deduction at finalisation. It is less than `totalDeposited`. Use `GET /funds/{vault}/stats` to get the exact value; do not calculate it from `totalDeposited`.

The contract tracks `cumulativeDrawn` -- the total USDC that has left the vault across all executed proposals. When a proposal executes and the vault's USDC balance decreases, `cumulativeDrawn` increases by the difference. If `cumulativeDrawn > allowance`, the proposal execution **reverts**.

### Cumulative Means Cumulative

The drawdown limit is a lifetime cap on outflows, not a current-balance check. Plan your trades within the current allowance.

### Checking Drawdown Status

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/stats \
  | jq '{cumulativeDrawn, drawdownAllowance}'
```

Example response:
```json
{
  "cumulativeDrawn": "15000000000",
  "drawdownAllowance": "50000000000"
}
```

This means: 15k USDC drawn out of 50k allowed (50% of a 100k fund, before the first interval passes).

---

## Claiming Management Fees

Management fees accrue on capital that has left the vault via proposals. If no capital has been deployed, fees are zero.

### Formula

```
deployedCapital = initialDeposits - USDC.balanceOf(vault)
fee = deployedCapital * managementFeeBps * timeElapsed / (10000 * 365 days)
```

- `deployedCapital` is clamped to 0 if the vault balance exceeds `initialDeposits`.
- `timeElapsed` is seconds since the last fee claim (or fund activation if first claim).
- A `managementFeeBps` of 200 = 2% annual fee on deployed capital.

### Claiming

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/fees/claim \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Returns TxData. Sign and submit.

The fee is transferred directly to the manager's address in USDC. Claim periodically -- fees are computed at claim time based on elapsed duration, so waiting longer claims a larger amount but does not compound.

### Fee Claiming Restrictions

- Only the manager can claim fees.
- Cannot claim while the fund is winding down (fees are settled at wind-down).
- The fund must be activated.

---

## Wind-Down

Wind-down closes the fund. It can be initiated by the manager at any time after activation. You can wind down immediately after activation, but winding down before deploying capital means zero performance fees and wasted LP trust.

### Before Wind-Down

1. **Unwind all DeFi positions.** Return all USDC to the vault first. Any capital still deployed in DeFi protocols will be inaccessible to LPs after wind-down (the vault cannot execute new proposals once winding down).
2. **Claim all remaining management fees.** You **MUST** claim management fees before initiating wind-down. The contract blocks fee claims once wind-down begins (`FundWindingDown` revert). Any unclaimed fees are forfeited.

### Initiating Wind-Down

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/wind-down \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Returns TxData. Sign and submit.

### What Wind-Down Does

1. **Cancels all pending proposals.** No further trades can be proposed or executed.
2. **Calculates performance fee (carry):**
   ```
   adjustedBase = initialDeposits - totalManagementFeesClaimed
   profit = max(0, USDC.balanceOf(vault) - adjustedBase)
   carry = profit * performanceFeeBps / 10000
   ```
   The performance fee is transferred to your wallet in the same transaction as the wind-down call. No separate claim step needed.
3. **Opens immediate LP withdrawals.** LPs can request and claim withdrawals with no delay (the `claimableAt` is set to the current timestamp).

### After Wind-Down

- The fund status changes to `"winding_down"`.
- LPs withdraw their pro-rata share of remaining vault USDC.
- No new proposals, no fee claims, no further manager operations.

---

## Monitoring Your Fund

| What | Endpoint | Auth |
|------|----------|------|
| Fund status and capital | `GET /funds/{vault}/stats` | None |
| Fund terms and metadata | `GET /funds/{vault}/terms` | None |
| Active proposals | `GET /funds/{vault}/proposals` | None |
| Event history | `GET /funds/{vault}/events` | None |
| All your managed funds | `GET /managed/{yourAddress}` | None |

### Checking Fund Stats

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/stats | jq '.'
```

Response:
```json
{
  "vault": "0x...",
  "status": "active",
  "totalDeposited": "50000000000",
  "vaultBalance": "35000000000",
  "deployedCapital": "15000000000",
  "depositorCount": 12,
  "totalManagementFeesClaimed": "150000000",
  "cumulativeDrawn": "15000000000",
  "drawdownAllowance": "20000000000",
  "elapsedIntervals": 4,
  "activated": true,
  "fundFrozen": false,
  "fundWindingDown": false
}
```

### Checking Proposals

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/proposals | jq '.proposals[]'
```

Each proposal includes `vetoPercent`, `countdown`, and `status` fields so you can track whether LPs are vetoing your proposals.

Post-MVP: periodic NAV reporting will allow managers to publish position valuations via `POST /funds/{vault}/nav`, building transparency and on-chain reputation (see ERC-8004).

---

## Submitting Transactions

See [api-reference.md — Submitting Transactions](api-reference.md#submitting-transactions) for TxData format, Bankr submit example, and generic EVM signer patterns.

---

## Freeze Risk

If **66% of total LP shares** vote to freeze, the fund is frozen and you are replaced by the platform liquidator. No further proposals can be submitted or executed. Maintain LP trust by proposing transparent, well-reasoned trades that align with your stated strategy. Monitor `fundFrozen` in fund stats.

---

## Fund Manager Lifecycle Summary

1. **Pin metadata** -- `POST /metadata/pin` -- Upload fund name, strategy, and description to IPFS.
2. **Create fund** -- `POST /funds/create` -- Submit the creation transaction.
3. **Wait for deposits** -- LPs deposit during the deposit window.
4. **Finalise** -- `POST /funds/{raise}/finalise` -- Anyone can call once `minRaise` is met and the deposit window closes (or `maxRaise` is reached).
5. **Propose DeFi trades** -- Use adapters for supported protocols (single proposal, instant). Use raw calls for others (two proposals, time-delayed).
6. **Claim management fees** -- Periodically claim fees accrued on deployed capital.
7. **Wind down** -- Close the fund. Performance fees are deducted automatically. LPs can withdraw immediately.

### Common Mistakes

- **Using raw calls for supported protocols.** Adapter proposals are simpler and execute instantly. Use `uniswap_v3` or `aave_v3` adapters instead of constructing calldata manually.
- **Forgetting the approval proposal (raw call path).** Raw call DeFi interactions need USDC approval first. Adapter proposals handle this automatically.
- **Exceeding drawdown limits.** Plan your trades within the current allowance. Check `drawdownAllowance` before proposing.
- **Winding down with capital still deployed.** Any USDC in external DeFi protocols at wind-down time is not included in the final distribution. Unwind all positions first.
