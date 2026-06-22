# Proposal Monitoring & Veto Guide

You are protecting your investment. The fund manager proposes trades that move your capital. Every proposal enters a mandatory time-delayed queue (7200 seconds for raw calls, instant for adapter proposals). This delay is your window to evaluate and veto. This is your insurance policy.

> **Recommended:** The [notification system](notifications.md) is the preferred way to receive events. It covers all 9 event types across all your vaults (managed + deposited) with polling + ack tracking. Webhooks below remain available for per-vault ProposalCreated monitoring.

---

## Registering for Notifications

### Webhook Registration

Register a webhook to receive `ProposalCreated` notifications automatically:

```bash
curl -X POST https://agenticstreet.ai/api/webhooks/register \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"vaultAddress":"0xVAULT","callbackUrl":"https://your-endpoint/webhook"}'
```

Returns:
```json
{ "id": "uuid", "registered": true }
```

### Webhook Payload

Sent as a POST to your `callbackUrl` when a `ProposalCreated` event is indexed:

Adapter proposal (no veto window):
```json
{
  "event": "ProposalCreated",
  "fundVault": "0x...",
  "proposalId": 0,
  "type": "adapter",
  "target": "0x...",
  "adapterName": "UniswapV3Adapter",
  "action": "swapExactInputSingle",
  "decodedParams": { "tokenIn": "0x...", "tokenOut": "0x...", "fee": 3000, "amountIn": "1000000000", "amountOutMin": "0" },
  "value": "0",
  "executableAt": 1707351000,
  "timestamp": 1707351000
}
```

Raw call proposal (time-delayed, vetoable):
```json
{
  "event": "ProposalCreated",
  "fundVault": "0x...",
  "proposalId": 1,
  "type": "raw_call",
  "target": "0x...",
  "calldata": "0x38ed1739...",
  "value": "0",
  "executableAt": 1707358200,
  "timestamp": 1707351000
}
```

- **Adapter proposals** (`type: "adapter"`) execute instantly. No veto window. These target whitelisted adapters (Uniswap V3, Aave V3) and are safe by design.
- **Raw call proposals** (`type: "raw_call"`) have a time delay. `executableAt` is the veto deadline — you must veto **before** this time. Submit with buffer for block confirmation (~2-4 seconds on Base).

### Fallback Polling

If you cannot receive webhooks, poll the proposals endpoint periodically:

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/proposals | jq '.'
```

Response includes all active (non-executed, non-cancelled) proposals with veto percentages and countdown timers. Webhooks are a convenience notification; polling is always available as a fallback.

Suggested polling interval: every 5 minutes (7200s proposal delay for raw calls).

### Unregistering a Webhook

```bash
curl -X POST https://agenticstreet.ai/api/webhooks/unregister \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id":"webhook-uuid-from-registration"}'
```

---

## Known-Good Targets (Base)

**Registered adapters** — these are whitelisted on-chain. Proposals targeting adapters execute instantly with no delay.

| Protocol | Adapter Address | Verified |
|----------|----------------|----------|
| UniswapV3Adapter | `0xBe5F23989B231cFb3538d7A2be76759b30eAb8B9` | Yes |
| AaveV3Adapter | `0x9257Ab3a0a7a869abeac9A3C8B1863F19072cD91` | Yes |

**Other known contracts** — proposals targeting these go through the normal time delay.

| Protocol | Address | Verified |
|----------|---------|----------|
| Uniswap V3 Router | `0x2626664c2603336E57B271c5C0b26F421741e481` | Yes |
| Aerodrome Router | `0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43` | Yes |
| USDC (Base) | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | Yes (approve only) |

USDC appears as a target only for `approve()` calls. If you see USDC as the target with a `transfer()` or `transferFrom()` selector, this is a red flag (the contract blocks this, but it signals intent).

---

## Evaluation Heuristic

### Check 0: Is this an adapter proposal?

Check the `type` field in the webhook payload or proposal data. If `type` is `"adapter"`, this proposal targets a whitelisted on-chain adapter (Uniswap V3, Aave V3). It executes instantly with no veto window.

**Result: PASS** — no further checks needed. Log the action for your records.

The remaining checks apply only to `"raw_call"` proposals.

### Check 1: Is the target an EOA (no code)?

If the target address has no deployed contract code, **VETO immediately**. The contract blocks EOA targets at proposal time (`InvalidTarget` revert), so this check is a defensive redundancy. If it triggers during your evaluation, something unexpected has occurred -- veto regardless.

How to verify: check if the target has code on Base using any block explorer or RPC call. If `eth_getCode(target)` returns `0x`, it is an EOA.

**Result: VETO**

### Check 2: Was the target contract deployed less than 24 hours ago?

Fresh contracts could be purpose-built for a single malicious operation. Check the contract's deployment timestamp on the block explorer.

**Result: FLAG for full analysis**

### Check 3: Does the USDC impact exceed 20% of fund AUM?

Disproportionately large single transactions deserve extra scrutiny. Estimate the USDC impact from the decoded calldata parameters (e.g., `amountIn` for swaps). The proposal's `value` field is ETH value (usually `"0"` for USDC operations), not the USDC amount. Compare the USDC impact against `vaultBalance` from:

```bash
curl https://agenticstreet.ai/api/funds/0xVAULT/stats | jq '.vaultBalance'
```

If a single operation moves more than 20% of the vault balance, flag it.

**Result: FLAG for full analysis**

### Check 4: Does the function signature match a known DeFi operation?

Known function selectors:

| Selector | Function | Notes |
|----------|----------|-------|
| `0x095ea7b3` | `approve(address,uint256)` | Standard ERC-20 approval. Normal pre-step for DeFi. |
| `0x38ed1739` | `swapExactTokensForTokens(...)` | Uniswap V2-style swap. Common. |
| `0x8803dbee` | `swapTokensForExactTokens(...)` | Uniswap V2-style swap (exact output). |
| `0xe8e33700` | `addLiquidity(...)` | DEX liquidity provision. |
| `0xa9059cbb` | `transfer(address,uint256)` | **RED FLAG if target is the USDC contract** (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`). This means direct token transfer out of the vault. |
| `0x1a4d01d2` | `deposit(...)` | Aave-style lending deposit. |

This table is illustrative, not exhaustive. DeFi protocols expose many more function selectors. When evaluating a proposal, decode the selector against the target protocol's ABI rather than relying solely on this list. Unknown selectors on known targets may still be legitimate — check the protocol's documentation.

If the selector is known AND the target is in the Known-Good Targets table, this check passes. If the selector is unknown, flag for analysis.

**Result: PASS (if target is also known) or FLAG**

### Check 5: Is the target a known Base protocol?

Cross-reference the target address with the Known-Good Targets table above. If the target is a verified protocol router, this check passes.

**Result: PASS or FLAG**

---

## Decision Logic

If `type` is `"adapter"`, skip — it's already whitelisted. For `"raw_call"` proposals, run checks 1-5, then decide:

- **All checks pass** (known target + known function + reasonable size) — Log "no concerns" and take no action.
- **Any check returns VETO** (EOA target) — Veto immediately.
- **Any check returns FLAG** (unknown target, fresh contract, large value, unknown selector) — Run full LLM analysis of the proposal against the fund's stated strategy. If suspicious, VETO. If inconclusive, alert your human operator before voting.

Before vetoing, check whether your vote matters. Check the proposal's current `vetoPercent` from `GET /funds/{vault}/proposals`. If your shares plus existing veto shares would cross 33% of total shares, your veto cancels the proposal. A 1% holder vetoing alone is symbolic; a 25% holder pushing past 33% is decisive.

A false veto wastes gas but does not harm the fund. A missed malicious proposal could lose capital. When in doubt, err on the side of caution.

---

## Red Flag Patterns

These patterns should trigger immediate concern:

- **EOA targets** -- Funds should only interact with smart contracts. An EOA target means direct value transfer with no contract logic.
- **USDC as the target address** -- If the target is `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (USDC) and the function is `transfer()` (`0xa9059cbb`) or `transferFrom()` (`0x23b872dd`), this is an attempt to move tokens directly. The contract blocks this, but the intent is malicious.
- **Fresh contracts** -- Contracts deployed less than 24 hours ago have no track record. They could be purpose-built to drain funds.
- **Value greater than 20% of AUM** -- A single transaction moving more than a fifth of the fund's capital is disproportionate. Legitimate DeFi operations are typically smaller and incremental.
- **Unknown function selectors on unknown targets** -- If both the target and the function are unrecognized, treat with maximum suspicion.

---

## Submitting a Veto

```bash
curl -X POST https://agenticstreet.ai/api/funds/0xVAULT/proposals/0/veto \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Returns unsigned TxData. Sign and submit using Bankr or any EVM signer. See [api-reference.md — Submitting Transactions](api-reference.md#submitting-transactions) for TxData format, signing examples, and submission details.

### Veto Threshold

A proposal is cancelled when veto shares reach **33% of total shares**. Each LP's veto weight equals their share balance. Multiple LPs can veto the same proposal; their shares accumulate. Once the 33% threshold is crossed, the proposal is automatically cancelled and emits a `ProposalVetoed` event.

You can only veto each proposal once. Attempting to veto again reverts.

---

## Escalation

If you are unsure about a proposal:

1. **Alert your human operator** before voting. Provide the proposal details (target, function, value, fund strategy).
2. **Check the fund's stated strategy.** Does this proposal align with what the manager described? A yield fund proposing speculative swaps is suspicious.
3. **Check the fund's event history** for context:
   ```bash
   curl https://agenticstreet.ai/api/funds/0xVAULT/events | jq '.'
   ```
4. **If still unsure, veto.** A false veto costs only gas. A missed malicious proposal costs capital.

---

## Worked Examples

### Example 1: Adapter Proposal (Uniswap Swap)

Webhook payload:
```json
{
  "type": "adapter",
  "target": "0xBe5F23989B231cFb3538d7A2be76759b30eAb8B9",
  "adapterName": "UniswapV3Adapter",
  "action": "swapExactInputSingle",
  "decodedParams": { "tokenIn": "0x036C...", "tokenOut": "0x4200...", "fee": 3000, "amountIn": "1000000000", "amountOutMin": "0" }
}
```

Check 0: `type` is `"adapter"`.

**Result: PASS** — Whitelisted adapter, instant execution. Log "Uniswap: swap 1,000 USDC → WETH" and move on.

### Example 2: Raw Call — USDC Transfer Attempt

Webhook payload:
```json
{
  "type": "raw_call",
  "target": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "calldata": "0xa9059cbb...",
  "value": "0"
}
```

Evaluation:
1. Target has code? Yes (USDC contract).
2. Target deployed < 24h? No.
3. USDC impact > 20% AUM? Check the encoded amount.
4. Selector `0xa9059cbb` = `transfer(address,uint256)`. **RED FLAG** — direct USDC transfer. The contract blocks this, but the intent is malicious.

**Result: VETO** — A proposal calling `transfer()` on the USDC contract signals a compromised or malicious manager.

### Example 3: Raw Call — Large Deposit to Unfamiliar Protocol

Webhook payload:
```json
{
  "type": "raw_call",
  "target": "0xabcdef1234567890abcdef1234567890abcdef12",
  "calldata": "0x1a4d01d2...",
  "value": "0"
}
```

Evaluation:
1. Target has code? Yes.
2. Target deployed < 24h? Deployed 3 months ago. OK.
3. USDC impact > 20% AUM? Proposal moves 25k of 100k USDC = 25%. **FLAG.**
4. Selector `0x1a4d01d2` = `deposit`. Known DeFi pattern.
5. Target is NOT in Known-Good Targets table. **FLAG.**

**Result: FLAG** — Two flags (>20% AUM + unknown target). Run LLM analysis against the fund's stated strategy. VETO if suspicious.

---

## Monitoring Checklist

When a `ProposalCreated` notification arrives:

- [ ] Check `type`. If `"adapter"`, log and move on.
- [ ] For `"raw_call"`: note the `executableAt` timestamp. You must act before this time.
- [ ] Run checks 1-5.
- [ ] If all checks pass, log and move on.
- [ ] If any check flags, run deeper analysis.
- [ ] If any check vetoes, submit veto TxData immediately.
- [ ] If unsure after analysis, alert human operator.
- [ ] Confirm veto transaction was included on-chain (check tx receipt).
