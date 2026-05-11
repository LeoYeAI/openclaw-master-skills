# Limit Order Placement (USDT → XAUT via UniswapX)

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
node swap.js balance   # ETH balance check + tokenIn (USDT) balance check
```

## 2. Parameter Confirmation (Preview)

Display at minimum:
- Pair: USDT → XAUT
- Limit price: `1 XAUT = X USDT` (i.e. amountIn / minAmountOut, human-readable)
- Amount: `amountIn` USDT → at least `minAmountOut` XAUT
- Expiry: `expiry` seconds / deadline in local time
- UniswapX Filler risk notice: XAUT is a low-liquidity token; if no Filler fills the order, it expires automatically after the deadline with no loss of funds

## 3. Large-Trade Double Confirmation

If amountIn (USDT converted to USD) > `risk.large_trade_usd`, double confirmation is required.

## 4. Approve Permit2 (if allowance is insufficient)

Check USDT allowance for Permit2:

```bash
node swap.js allowance --token USDT --spender 0x000000000022D473030F116dDEE9F6B43aC78BA3
```

If insufficient, approve (USDT requires reset-to-zero; swap.js handles this automatically via token_rules):

```bash
node swap.js approve --token USDT --amount <AMOUNT_IN> --spender 0x000000000022D473030F116dDEE9F6B43aC78BA3
```

## 5. Place Order

> **Important — raw units**: Unlike `swap.js` (which accepts human-readable amounts), `limit-order.js` requires **raw integer amounts in smallest token units**.
> Both USDT and XAUT have 6 decimals, so multiply by `10^6`:
> - 1 USDT → `1000000`
> - 0.0005 XAUT → `500`
> - Formula: `raw = human_amount * 1000000` (drop any fractional remainder)

Resolve contract addresses and wallet before placing:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
USDT=$(node -e "const c=require('js-yaml').load(require('fs').readFileSync(require('os').homedir()+'/.aurehub/config.yaml','utf8')); console.log(c.tokens.USDT.address)")
XAUT=$(node -e "const c=require('js-yaml').load(require('fs').readFileSync(require('os').homedir()+'/.aurehub/config.yaml','utf8')); console.log(c.tokens.XAUT.address)")
WALLET_ADDRESS=$(node swap.js address | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).address")
# Convert human-readable amounts to raw integers (6 decimals): raw = human_amount * 1000000
# AMOUNT_IN: user's USDT spend amount; MIN_AMOUNT_OUT: minimum XAUT to receive (from limit price)
AMOUNT_IN=$(node -e "console.log(Math.trunc(parseFloat('<USDT_AMOUNT>') * 1e6))")
MIN_AMOUNT_OUT=$(node -e "console.log(Math.trunc(parseFloat('<MIN_XAUT_AMOUNT>') * 1e6))")
```

```bash
# EXPIRY_SECONDS: use the user-specified expiry, or fall back to 86400 (1 day).
RESULT=$(node limit-order.js place \
  --token-in       "$USDT" \
  --token-out      "$XAUT" \
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
| UniswapX API returns 4xx | Hard-stop, note XAUT may not be in the supported list, suggest market order |
| Limit price deviates > 50% from current market | Warn + double confirmation (prevent price typos) |
| Approve failed | Return failure reason, suggest retry |
