# Swap Amount Math (USDC / ETH -> GHST)

This file defines how to estimate the `swapAmount` argument for:
- `swapAndCommitBid((...))`
- `swapAndBuyNow((...))`

Important notes:
- `swapAmount` is the amount of `tokenIn` you will spend (USDC 6dp or ETH wei).
- `minGhstOut` is a GHST wei minimum output (slippage protection). For bidding and buy-now, set it to the exact required GHST amount:
  - bid: `minGhstOut = bidAmount`
  - buy-now: `minGhstOut = buyNowPrice`
- Swaps can still fail due to price impact or route conditions (`LibTokenSwap: Insufficient output amount`). If that happens, increase `swapAmount` and/or `SLIPPAGE_PCT`.

Defaults:
- `SLIPPAGE_PCT=1` (1%)

## Price Sources (CoinGecko)

If `GHST_USD_PRICE` / `ETH_USD_PRICE` are unset, fetch them:
```bash
curl -s 'https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi,ethereum&vs_currencies=usd' \
  | python3 -c 'import json,sys; j=json.load(sys.stdin); print(\"GHST_USD\", j[\"aavegotchi\"][\"usd\"]); print(\"ETH_USD\", j[\"ethereum\"][\"usd\"])'
```

## USDC swapAmount (6 decimals)

Given:
- `min_ghst_out_wei` (bidAmount or buyNowPrice)
- `ghst_usd_price`

Compute:
1. `ghst = min_ghst_out_wei / 1e18`
2. `usd = ghst * ghst_usd_price`
3. `base_usdc_6dp = usd * 1e6`
4. `swapAmount = ceil(base_usdc_6dp * (1 + SLIPPAGE_PCT/100))`

Python reference:
```bash
python3 - <<'PY'
from decimal import Decimal, getcontext, ROUND_CEILING

getcontext().prec = 80

min_ghst_out_wei = Decimal("<MIN_GHST_OUT_GHST_WEI>")  # replace
ghst_usd_price = Decimal("<GHST_USD_PRICE>")           # replace
slippage_pct = Decimal("<SLIPPAGE_PCT>")               # default 1

ghst = min_ghst_out_wei / (Decimal(10) ** 18)
usd = ghst * ghst_usd_price
base_usdc = usd * (Decimal(10) ** 6)

swap_amount = (base_usdc * (Decimal(1) + slippage_pct / Decimal(100))).to_integral_value(rounding=ROUND_CEILING)
print("swapAmount (USDC 6dp):", int(swap_amount))
PY
```

## ETH swapAmount (wei)

Given:
- `min_ghst_out_wei`
- `ghst_usd_price`
- `eth_usd_price`

Compute:
1. `ghst = min_ghst_out_wei / 1e18`
2. `usd = ghst * ghst_usd_price`
3. `eth = usd / eth_usd_price`
4. `base_eth_wei = eth * 1e18`
5. `swapAmountWei = ceil(base_eth_wei * (1 + SLIPPAGE_PCT/100))`

Python reference:
```bash
python3 - <<'PY'
from decimal import Decimal, getcontext, ROUND_CEILING

getcontext().prec = 80

min_ghst_out_wei = Decimal("<MIN_GHST_OUT_GHST_WEI>")  # replace
ghst_usd_price = Decimal("<GHST_USD_PRICE>")           # replace
eth_usd_price = Decimal("<ETH_USD_PRICE>")             # replace
slippage_pct = Decimal("<SLIPPAGE_PCT>")               # default 1

ghst = min_ghst_out_wei / (Decimal(10) ** 18)
usd = ghst * ghst_usd_price
eth = usd / eth_usd_price
base_eth_wei = eth * (Decimal(10) ** 18)

swap_amount = (base_eth_wei * (Decimal(1) + slippage_pct / Decimal(100))).to_integral_value(rounding=ROUND_CEILING)
print("swapAmount (ETH wei):", int(swap_amount))
PY
```
