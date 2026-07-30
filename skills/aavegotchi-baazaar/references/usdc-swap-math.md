# USDC swapAmount Math (Matches Dapp Defaults)

This file defines how to compute the `swapAmount` argument (USDC base units, 6 decimals) for:
- `swapAndBuyERC721(...)`
- `swapAndBuyERC1155(...)`

Constants/defaults:
- `PAYMENT_FEE_PCT_USDC=1` (1%)
- `SLIPPAGE_PCT=1` (1%)

Given a listing's price in GHST wei:
- ERC721: `totalCostGhstWei = priceInWei`
- ERC1155: `totalCostGhstWei = priceInWei * quantity`

The contract args must be:
- `minGhstOut = totalCostGhstWei` (exactly)
- `swapAmount = ceil( baseUsdc * (1 + feePct/100) * (1 + slippagePct/100) )`

Where:
1. Convert GHST wei to GHST:
   - `totalGhst = totalCostGhstWei / 1e18`
2. Convert to USD:
   - `usd = totalGhst * ghstUsdPrice`
3. Convert to USDC base units (6 decimals):
   - `baseUsdc = usd * 1e6`
4. Apply payment fee:
   - `baseUsdc *= (1 + PAYMENT_FEE_PCT_USDC/100)`
5. Apply slippage:
   - `baseUsdc *= (1 + SLIPPAGE_PCT/100)`
6. Round up to the next integer:
   - `swapAmount = ceil(baseUsdc)`

## Python Reference Snippet (Ceiling)

```bash
python3 - <<'PY'
from decimal import Decimal, getcontext, ROUND_CEILING

getcontext().prec = 80

total_cost_ghst_wei = Decimal("1000000000000000000")  # replace
ghst_usd_price = Decimal("0.10")                      # replace
payment_fee_pct = Decimal("1")                        # default 1
slippage_pct = Decimal("1")                           # default 1

total_ghst = total_cost_ghst_wei / (Decimal(10) ** 18)
usd = total_ghst * ghst_usd_price
base_usdc = usd * (Decimal(10) ** 6)

swap_amount = (
    base_usdc
    * (Decimal(1) + payment_fee_pct / Decimal(100))
    * (Decimal(1) + slippage_pct / Decimal(100))
).to_integral_value(rounding=ROUND_CEILING)

print("swapAmount (USDC 6dp):", int(swap_amount))
PY
```

## Price Source (CoinGecko)

If `GHST_USD_PRICE` is unset, fetch it:
```bash
curl -s 'https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi&vs_currencies=usd' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["aavegotchi"]["usd"])'
```
