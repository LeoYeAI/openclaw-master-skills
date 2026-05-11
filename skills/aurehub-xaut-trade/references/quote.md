# Quote & Slippage Protection

All commands below assume CWD is `$SCRIPTS_DIR` and env is sourced.

## 1. Fetch Quote

Example: buy with 100 USDT

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
RESULT=$(node swap.js quote --side buy --amount 100)
echo "$RESULT"
```

Output is JSON:

```json
{
  "side": "buy",
  "amountIn": "100",
  "amountOut": "0.033",
  "amountOutRaw": "33000",
  "sqrtPriceX96": "...",
  "gasEstimate": "150000"
}
```

For sell direction, use `--side sell --amount <XAUT_amount>`.

Extract values for downstream use:

```bash
AMOUNT_OUT=$(echo "$RESULT" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).amountOut")
AMOUNT_OUT_RAW=$(echo "$RESULT" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).amountOutRaw")
GAS_ESTIMATE=$(echo "$RESULT" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).gasEstimate")
```

## 2. Calculate minAmountOut

Read `default_slippage_bps` from config.yaml (e.g. 50 bps = 0.5%):

```bash
# Read slippage from config.yaml, default to 50 bps
DEFAULT_SLIPPAGE_BPS=$(node -e "const c=require('js-yaml').load(require('fs').readFileSync(require('os').homedir()+'/.aurehub/config.yaml','utf8')); console.log((c.risk||{}).default_slippage_bps||50)")
# Use node to avoid bash integer overflow on large trades
MIN_AMOUNT_OUT=$(node -p "Math.trunc($AMOUNT_OUT_RAW * (10000 - $DEFAULT_SLIPPAGE_BPS) / 10000)")
```

## 3. Preview Output

Must include at minimum:
- Input amount (human-readable)
- Estimated output received (`amountOut`)
- Slippage setting and `minAmountOut`
- Risk indicators (large trade / slippage / gas)

## 4. Execution Confirmation Gate

Determine confirmation level by USD notional and risk:

- `< risk.confirm_trade_usd`: show full preview, then execute without blocking confirmation
- `>= risk.confirm_trade_usd` and `< risk.large_trade_usd`: single confirmation
- `>= risk.large_trade_usd` or estimated slippage exceeds `risk.max_slippage_bps_warn`: double confirmation

Accepted confirmation phrases:
- "confirm approve"
- "confirm swap"
