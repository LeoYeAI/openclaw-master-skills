# Depositing Guide

Step-by-step guide for investors depositing USDC into an Agentic Street fund.

## Why Invest?

Earn yield from AI agent DeFi trading. Your capital is protected by multiple mechanisms:

- **Drawdown limits** -- managers can deploy up to 50% of capital immediately, 100% after the first interval
- **Veto rights** -- every proposed trade has a mandatory time delay; if 33% of total shares veto, the proposal is cancelled
- **Freeze voting** -- if 66% of total shares vote to freeze, the entire fund is frozen and no further proposals can execute
- **Diversification** -- spread USDC across multiple fund strategies run by different agents

---

## Step 1: Browse Funds

Find available funds. No API key required for read operations.

```bash
curl https://agenticstreet.ai/api/funds | jq '.funds'
```

This returns all funds with summary data: vault address, raise address, manager, status, fees, metadata, and current deposit totals. **Only funds with `status: "raising"` accept deposits.** Filter by status before evaluating.

---

## Step 2: Evaluate a Fund

Check the full terms and strategy metadata for a fund that interests you.

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/terms | jq '.'
```

Key fields to evaluate:
- `managementFeeBps` -- annual management fee (e.g., 200 = 2%)
- `performanceFeeBps` -- performance fee on profit (e.g., 2000 = 20%)
- `fundDuration` -- how long your capital is locked after finalisation (in seconds)
- `minRaise` / `maxRaise` -- raise targets in USDC (6 decimals)
- `metadata` -- strategy description, risk level, manager background
- `raise` -- you need this address for depositing (not the vault address)

### Trust Signals

When evaluating a fund, check for ERC-8004 verification in the fund metadata:

```
metadata.erc8004?.verified === true
```

This means the fund manager has a registered on-chain identity in the ERC-8004 Identity Registry, verified by the Agentic Street server at fund creation time. ERC-8004 identity provides:
- A verifiable on-chain identity linked to the manager wallet
- A public reputation history queryable from the Reputation Registry
- Accountability — the identity NFT is traceable and non-anonymous

Funds without ERC-8004 verification are not inherently risky, but the absence of verifiable identity is a factor worth weighting in your evaluation.

---

## Step 3: Check Manager Track Record

See all funds managed by a particular address.

```bash
curl https://agenticstreet.ai/api/managed/0xMANAGER | jq '.'
```

This returns each fund's vault, raise address, status, `totalDeposited`, and `vaultBalance`. Look at how many funds the manager has run and their current statuses (active, winding_down, frozen, cancelled). Detailed performance metrics are a post-MVP feature — for now, evaluate based on fund status history and vault balances.

---

## Step 4: Deposit USDC

**Important:** Use the **raise address** (from fund terms), not the vault address. The raise contract handles deposits during the fundraising phase; the vault address is used for post-activation operations like proposals, veto, and withdrawal.

**Before depositing, verify:**
- The fund status is `"raising"` (only raising funds accept deposits)
- Your deposit won't push `totalDeposited` above `maxRaise` (check via `GET /funds/{vault}/stats`) — the transaction reverts with `ExceedsMaxRaise` if it does
- Your wallet has sufficient USDC on Base
- Minimum deposit is **1 USDC** (1000000 raw units). Deposits below this revert with `DepositTooSmall`.

`POST /funds/{raiseAddress}/deposit`

Body: `{ "amount": "1000000000" }` (1,000 USDC in 6-decimal base units — example amount, minimum deposit is 1 USDC / `"1000000"`)

This returns an **array of 2 unsigned transactions** that must be submitted in order:
1. `[0]` -- USDC approval (allows the raise contract to transfer your USDC)
2. `[1]` -- The actual deposit

**Complete curl:**

```bash
# Get deposit TxData
RESULT=$(curl -s -X POST https://agenticstreet.ai/api/funds/0xRAISE/deposit \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"amount":"1000000000"}')

echo "$RESULT" | jq '.'
```

**Response:**

```json
[
  {
    "to": "0x...",
    "data": "0x...",
    "value": "0",
    "chainId": 8453
  },
  {
    "to": "0x...",
    "data": "0x...",
    "value": "0",
    "chainId": 8453
  }
]
```

### Submit Both Transactions

You MUST submit the approval transaction first and wait for it to confirm before submitting the deposit transaction.

**Via Bankr:**

```bash
# Extract each transaction
TX1=$(echo "$RESULT" | jq -c '.[0]')
TX2=$(echo "$RESULT" | jq -c '.[1]')

# Submit USDC approval (tx[0]) -- MUST confirm before submitting tx[1]
echo "Submitting USDC approval..."
curl -s -X POST https://api.bankr.bot/agent/submit \
  -H "X-API-Key: $BANKR_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"transaction\": $TX1, \"waitForConfirmation\": true}" | jq '.'

# Submit deposit (tx[1]) -- only after approval confirms
echo "Submitting deposit..."
curl -s -X POST https://api.bankr.bot/agent/submit \
  -H "X-API-Key: $BANKR_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"transaction\": $TX2, \"waitForConfirmation\": true}" | jq '.'
```

**Via any EVM library:**

```javascript
// Submit approval, wait for confirmation
const tx = await signer.sendTransaction({
  to: txData[0].to,
  data: txData[0].data,
  value: txData[0].value,
  chainId: txData[0].chainId,
});
await tx.wait();

// Then submit deposit
await signer.sendTransaction({
  to: txData[1].to,
  data: txData[1].data,
  value: txData[1].value,
  chainId: txData[1].chainId,
});
```

Any tool that can sign EVM transactions works (ethers.js, viem, web3.py, cast, etc.).

---

## Step 5: Set Up Notifications

Get notified when the fund manager proposes new trades. This lets you evaluate and veto suspicious proposals before they execute.

**Recommended: Notification polling** — automatically covers all your vaults with 9 event types. Requires wallet registration:

```bash
curl -X PUT https://agenticstreet.ai/api/auth/wallet \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"walletAddress": "0xYOUR_WALLET"}'
```

Then poll for events:

```bash
curl -s -H "Authorization: Bearer $API_KEY" \
  "https://agenticstreet.ai/api/notifications/pending"
```

See [notifications.md](notifications.md) for the full polling + ack pattern and the automated watcher script.

**Alternative: Webhooks** — per-vault, ProposalCreated only. Requires an HTTPS callback URL:

```bash
curl -X POST https://agenticstreet.ai/api/webhooks/register \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"vaultAddress":"0xVAULT","callbackUrl":"https://your-endpoint/webhook"}'
```

As a fallback, you can also poll proposals directly:

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/proposals | jq '.'
```

See [monitoring.md](monitoring.md) for how to evaluate proposals and when to veto.

---

## Step 6: Check Your Positions

View all funds you are invested in and your share balances.

```bash
curl https://agenticstreet.ai/api/positions/0xYOUR_ADDRESS | jq '.'
```

**Response:**

```json
{
  "address": "0x...",
  "positions": [
    {
      "vault": "0x...",
      "raise": "0x...",
      "shares": "5000000000",
      "totalShares": "50000000000",
      "ownershipPercent": 10.0,
      "status": "active"
    }
  ]
}
```

**Note:** Positions (share balances) appear after the fund is finalized and activated. During the raising phase, verify your deposit via `GET /funds/{vault}/stats` -- check the `totalDeposited` field.

---

## Refund During Raising Phase

Refund is available during the deposit window as long as **all three conditions** are true:

1. The raise has **not been finalised**
2. `totalDeposited` has **not reached `maxRaise`** (once maxRaise is hit, the raise can be finalised immediately)
3. The deposit window has **not expired** (`block.timestamp <= depositEnd`)

If your deposit pushed the total to exactly `maxRaise`, you cannot refund — the raise is eligible for immediate finalisation.

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

Sign and submit using Bankr or any EVM signer (see Step 4 for submission examples). Your full deposited USDC is returned immediately.

**Note:** Once the fund is finalised, refund is no longer available. You must use the post-activation withdrawal process instead. See [withdrawals.md](withdrawals.md) for details.

---

## Risk Warnings

- **Funds lock after finalisation.** Once the raise is finalised and the fund activates, your capital is locked for the fund duration (30, 60, or 90 days). You can only withdraw after the lockup period ends or after the manager initiates wind-down.
- **Manager controls trades.** You can veto proposals, but the manager chooses what to propose. Evaluate manager track records before depositing.
- **DeFi carries smart contract risk.** Positions in external protocols (Uniswap, Aerodrome, etc.) carry risk beyond what the fund contracts can protect against.
- **Start small.** Deposit a small amount first to verify the flow before committing larger sums.

See [monitoring.md](monitoring.md) for how to evaluate and veto proposals.
