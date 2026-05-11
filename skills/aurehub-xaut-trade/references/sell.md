# Sell Execution (XAUT -> USDT)

All commands below assume CWD is `$SCRIPTS_DIR` and env is sourced. Each Bash block must begin with `source ~/.aurehub/.env` and `cd "$SCRIPTS_DIR"`.

## 0. Pre-execution Declaration

- Current stage must be `Ready to Execute`
- Quote and explicit user confirmation must already be complete
- Full command must be displayed before execution

## 1. Input Validation

User provides XAUT amount (e.g. `0.01`).

**Precision check**: if the input has more than 6 decimal places (e.g. `0.0000001`), hard-stop:

> XAUT supports a maximum of 6 decimal places. The minimum tradeable unit is 0.000001 XAUT. Please adjust the input amount.

## 2. Quote

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
RESULT=$(node swap.js quote --side sell --amount <XAUT_AMOUNT>)
echo "$RESULT"
```

Output:

```json
{
  "side": "sell",
  "amountIn": "<XAUT_AMOUNT>",
  "amountOut": "30.5",
  "amountOutRaw": "30500000",
  "sqrtPriceX96": "...",
  "gasEstimate": "150000"
}
```

Extract values:

```bash
AMOUNT_OUT=$(echo "$RESULT" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).amountOut")
AMOUNT_OUT_RAW=$(echo "$RESULT" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).amountOutRaw")
```

Calculate `minAmountOut` using `risk.default_slippage_bps` from config.yaml:

```bash
DEFAULT_SLIPPAGE_BPS=$(node -e "const c=require('js-yaml').load(require('fs').readFileSync(require('os').homedir()+'/.aurehub/config.yaml','utf8')); console.log((c.risk||{}).default_slippage_bps||50)")
MIN_AMOUNT_OUT=$(node -p "Math.trunc($AMOUNT_OUT_RAW * (10000 - $DEFAULT_SLIPPAGE_BPS) / 10000)")
```

Reference rate (for Preview display; both tokens have 6 decimals so divide directly):

```
Reference rate = amountOut / amountIn  (USDT/XAUT, human-readable)
```

## 3. Preview Output

Must include at minimum:

- Input amount (user-provided form)
- Estimated USDT received (`amountOut`, human-readable)
- Reference rate: `1 XAUT ~ X USDT`
- Slippage setting and `minAmountOut`
- Risk indicators (large trade / slippage / gas)

**Large-trade check**: convert `amountOut` (USDT) to USD value; if it exceeds `risk.large_trade_usd`, require double confirmation.

## 4. Confirmation Gate

Trade execution confirmation follows the threshold-based policy (see Section 9 — Mandatory Rules):

- `< risk.confirm_trade_usd`: show full preview, then execute without blocking confirmation
- `>= risk.confirm_trade_usd` and `< risk.large_trade_usd`: single confirmation
- `>= risk.large_trade_usd` or estimated slippage exceeds `risk.max_slippage_bps_warn`: double confirmation

Accepted confirmation phrases: "confirm approve", "confirm swap"

## 5. Allowance Check

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
node swap.js allowance --token XAUT
```

Output:

```json
{
  "address": "0x...",
  "token": "XAUT",
  "allowance": "0.0",
  "spender": "0x..."
}
```

If allowance < `AMOUNT_IN`, approve first.

## 6. Approve (XAUT is standard ERC-20)

**XAUT does not require a prior reset** — approve directly:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
APPROVE_RESULT=$(node swap.js approve --token XAUT --amount <XAUT_AMOUNT>)
echo "$APPROVE_RESULT"
```

Output:

```json
{
  "address": "0x...",
  "token": "XAUT",
  "amount": "<XAUT_AMOUNT>",
  "spender": "0x...",
  "txHash": "0x..."
}
```

Report: `Approve tx: https://etherscan.io/tx/<txHash>`

> Note: Unlike USDT, XAUT does not require `approve(0)` to reset before approving.

## 7. Swap Execution

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
SWAP_RESULT=$(node swap.js swap --side sell --amount <XAUT_AMOUNT> --min-out <MIN_AMOUNT_OUT>)
echo "$SWAP_RESULT"
```

Output:

```json
{
  "address": "0x...",
  "side": "sell",
  "amountIn": "<XAUT_AMOUNT>",
  "minAmountOut": "<MIN_AMOUNT_OUT>",
  "txHash": "0x...",
  "status": "success",
  "gasUsed": "180000"
}
```

Report: `Swap tx: https://etherscan.io/tx/<txHash>`

> On failure (`"status": "failed"`), report retry suggestions.

## 7a. Swap Error Recovery

**CRITICAL**: If the swap command returns an error, exits with a non-zero code, or returns `"status": "unconfirmed"`:

1. **Do NOT retry immediately.** The transaction may have been broadcast and mined despite the RPC error.
2. Check the current balance:
   ```bash
   source ~/.aurehub/.env
   cd "$SCRIPTS_DIR"
   node swap.js balance
   ```
3. Compare the XAUT balance against the pre-swap balance (from pre-flight):
   - **If XAUT balance decreased by the trade amount** → the swap **succeeded**. Proceed to Result Verification (Step 8). Do NOT re-approve or re-swap.
   - **If XAUT balance is unchanged** → the swap did **not** execute. Safe to retry from Step 5 (Allowance Check).
4. If a `txHash` was returned (including in the `"unconfirmed"` response), verify on Etherscan: `https://etherscan.io/tx/<txHash>`

> **Why this matters**: RPC nodes can return errors (e.g. 400, 504, "Unknown block") even when the transaction was successfully broadcast and mined. Retrying without checking balance will execute a **duplicate trade**, costing the user double.

## 8. Result Verification

Post-swap balance:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
node swap.js balance
```

Return:
- tx hash
- Post-trade balances (XAUT, USDT, ETH)
- on failure, return retry suggestions (reduce sell amount / increase slippage tolerance / check nonce and gas)

## 9. Mandatory Rules

- Before every on-chain write (approve, swap), remind the user: "About to execute an on-chain write"
- Trade execution confirmation follows:
  - `< risk.confirm_trade_usd`: show full preview, then execute without blocking confirmation
  - `>= risk.confirm_trade_usd` and `< risk.large_trade_usd`: single confirmation
  - `>= risk.large_trade_usd` or estimated slippage exceeds `risk.max_slippage_bps_warn`: double confirmation
- Approval confirmation follows `risk.approve_confirmation_mode` with force override:
  - If approve amount `> risk.approve_force_confirm_multiple * AMOUNT_IN`, require explicit approval confirmation
- Hard-stop if input precision exceeds 6 decimal places
