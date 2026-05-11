# Buy Execution (USDT -> XAUT)

All commands below assume CWD is `$SCRIPTS_DIR` and env is sourced. Each Bash block must begin with `source ~/.aurehub/.env` and `cd "$SCRIPTS_DIR"`.

## 0. Pre-execution Declaration

- Current stage must be `Ready to Execute`
- Quote and explicit user confirmation must already be complete
- Full command must be displayed before execution

## 1. Allowance Check

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
node swap.js allowance --token USDT
```

Output:

```json
{
  "address": "0x...",
  "token": "USDT",
  "allowance": "0.0",
  "spender": "0x..."
}
```

If allowance < intended `AMOUNT_IN`, approve first.

## 2. Approve (USDT)

USDT requires a reset-to-zero before approving (handled internally by swap.js when `token_rules.USDT.requires_reset_approve: true` in config):

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
APPROVE_RESULT=$(node swap.js approve --token USDT --amount <AMOUNT_IN>)
echo "$APPROVE_RESULT"
```

Output:

```json
{
  "address": "0x...",
  "token": "USDT",
  "amount": "<AMOUNT_IN>",
  "spender": "0x...",
  "txHash": "0x..."
}
```

The reset-to-zero step is handled automatically — no separate call needed.

Report: `Approve tx: https://etherscan.io/tx/<txHash>`

## 3. Swap Execution

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
SWAP_RESULT=$(node swap.js swap --side buy --amount <AMOUNT_IN> --min-out <MIN_AMOUNT_OUT>)
echo "$SWAP_RESULT"
```

Output:

```json
{
  "address": "0x...",
  "side": "buy",
  "amountIn": "<AMOUNT_IN>",
  "minAmountOut": "<MIN_AMOUNT_OUT>",
  "txHash": "0x...",
  "status": "success",
  "gasUsed": "180000"
}
```

Report: `Swap tx: https://etherscan.io/tx/<txHash>`

> On failure (`"status": "failed"`), report retry suggestions (reduce trade amount / increase slippage tolerance / check nonce and gas).

## 3a. Swap Error Recovery

**CRITICAL**: If the swap command returns an error, exits with a non-zero code, or returns `"status": "unconfirmed"`:

1. **Do NOT retry immediately.** The transaction may have been broadcast and mined despite the RPC error.
2. Check the current balance:
   ```bash
   source ~/.aurehub/.env
   cd "$SCRIPTS_DIR"
   node swap.js balance
   ```
3. Compare the USDT balance against the pre-swap balance (from pre-flight Step 1):
   - **If USDT balance decreased by the trade amount** → the swap **succeeded**. Proceed to Result Verification (Step 4). Do NOT re-approve or re-swap.
   - **If USDT balance is unchanged** → the swap did **not** execute. Safe to retry from Step 1 (Allowance Check).
4. If a `txHash` was returned (including in the `"unconfirmed"` response), verify on Etherscan: `https://etherscan.io/tx/<txHash>`

> **Why this matters**: RPC nodes can return errors (e.g. 400, 504, "Unknown block") even when the transaction was successfully broadcast and mined. Retrying without checking balance will execute a **duplicate trade**, costing the user double.

## 4. Result Verification

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
node swap.js balance
```

Return:
- tx hash
- post-trade XAUT balance (from balance output)
- on failure, return retry suggestions

## 5. Mandatory Rules

- Before every on-chain write (approve, swap), remind the user: "About to execute an on-chain write"
- Trade execution confirmation follows:
  - `< risk.confirm_trade_usd`: show full preview, then execute without blocking confirmation
  - `>= risk.confirm_trade_usd` and `< risk.large_trade_usd`: single confirmation
  - `>= risk.large_trade_usd` or estimated slippage exceeds `risk.max_slippage_bps_warn`: double confirmation
- Approval confirmation follows `risk.approve_confirmation_mode` with force override:
  - If approve amount `> risk.approve_force_confirm_multiple * AMOUNT_IN`, require explicit approval confirmation
- Accepted confirmation phrases: "confirm approve", "confirm swap"
