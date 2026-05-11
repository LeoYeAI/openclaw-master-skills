# Limit Sell Order Placement (XAUT → USDT via UniswapX)

## 0. Pre-execution Declaration

- Current stage must be `Ready to Execute`
- Parameters must be confirmed and user must have explicitly confirmed
- Full command must be displayed before execution

## 1. Pre-flight Checks

All commands below assume CWD is `$SCRIPTS_DIR` and env is sourced. Each Bash block must begin with:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
```

> `--api-url` and `--chain-id` are omitted from `limit-order.js` calls — the script reads defaults from `limit_order.uniswapx_api` and `networks.ethereum_mainnet.chain_id` in `~/.aurehub/config.yaml`.

```bash
node --version     # If not found, hard-stop and prompt to install https://nodejs.org (Node is required for all script commands)
node swap.js balance   # ETH balance check + XAUT balance check (hard-stop if insufficient)
```

## 2. Parameter Confirmation (Preview)

Display at minimum:
- Pair: XAUT → USDT
- Limit price: `1 XAUT = X USDT` (i.e. minAmountOut / amountIn, human-readable)
- Amount: sell `amountIn` XAUT → receive at least `minAmountOut` USDT
- Expiry: `expiry` seconds / deadline in local time
- UniswapX Filler risk notice: XAUT is a low-liquidity token; if no Filler fills the order, it expires automatically after the deadline with no loss of funds

## 3. Large-Trade Double Confirmation

If `minAmountOut` (USDT) > `risk.large_trade_usd`, double confirmation is required.

## 4. Approve Permit2 (if allowance is insufficient)

XAUT is a standard ERC-20 — **approve directly, no reset needed**:

```bash
node swap.js allowance --token XAUT --spender 0x000000000022D473030F116dDEE9F6B43aC78BA3
```

If insufficient, approve directly:

```bash
node swap.js approve --token XAUT --amount <AMOUNT_IN> --spender 0x000000000022D473030F116dDEE9F6B43aC78BA3
```

## 5. Place Order

> **Important — raw units**: Unlike `swap.js` (which accepts human-readable amounts), `limit-order.js` requires **raw integer amounts in smallest token units**.
> Both XAUT and USDT have 6 decimals, so multiply by `10^6`:
> - 0.001 XAUT → `1000`
> - 5000 USDT → `5000000000`
> - Formula: `raw = human_amount * 1000000` (drop any fractional remainder)

Resolve contract addresses and wallet before placing:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
XAUT=$(node -e "const c=require('js-yaml').load(require('fs').readFileSync(require('os').homedir()+'/.aurehub/config.yaml','utf8')); console.log(c.tokens.XAUT.address)")
USDT=$(node -e "const c=require('js-yaml').load(require('fs').readFileSync(require('os').homedir()+'/.aurehub/config.yaml','utf8')); console.log(c.tokens.USDT.address)")
WALLET_ADDRESS=$(node swap.js address | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).address")
# Convert human-readable amounts to raw integers (6 decimals): raw = human_amount * 1000000
# AMOUNT_IN: user's XAUT sell amount; MIN_AMOUNT_OUT: minimum USDT to receive (from limit price)
AMOUNT_IN=$(node -e "console.log(Math.trunc(parseFloat('<XAUT_AMOUNT>') * 1e6))")
MIN_AMOUNT_OUT=$(node -e "console.log(Math.trunc(parseFloat('<MIN_USDT_AMOUNT>') * 1e6))")
```

```bash
# EXPIRY_SECONDS: use the user-specified expiry, or fall back to 86400 (1 day).
RESULT=$(node limit-order.js place \
  --token-in       "$XAUT" \
  --token-out      "$USDT" \
  --amount-in      "$AMOUNT_IN" \
  --min-amount-out "$MIN_AMOUNT_OUT" \
  --expiry         "$EXPIRY_SECONDS" \
  --wallet         "$WALLET_ADDRESS")
```

Parse result:

```bash
ORDER_HASH=$(echo "$RESULT" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).orderHash")
DEADLINE=$(echo "$RESULT"   | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).deadline")
NONCE=$(echo "$RESULT"      | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).nonce")
```

## 6. Output

Return to user:
- `orderHash`: for querying / cancelling the order
- `deadline`: order expiry in local time
- Note: order details (including nonce) have been auto-saved to `~/.aurehub/orders/`. Cancellation can be done via `--order-hash` without needing to record the nonce manually.
- Reminder: order has been submitted to UniswapX; the computer does not need to stay online — the Filler network fills automatically when the price is reached

## 7. Error Handling

| Error | Action |
|-------|--------|
| `node` not found | Hard-stop, prompt to install Node.js >= 18 (required for all script commands) |
| XAUT precision > 6 decimals | Script-level hard-stop (exit 1), report minimum precision of 0.000001 |
| USDT minAmountOut precision > 6 decimals | Script-level hard-stop (exit 1), report maximum precision |
| XAUT balance insufficient | Hard-stop, report shortfall |
| Limit price deviates > 50% from current market | Warn + double confirmation (prevent price typos) |
| UniswapX API returns 4xx | Hard-stop, note XAUT may not be in the supported list, suggest market order |
| Approve failed | Return failure reason, suggest retry |
