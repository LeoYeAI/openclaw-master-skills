# Size-Aware OTC Pricing Parameters

Use these defaults when creating or negotiating outbound offers.

## Core pricing inputs
- `spotPrice`: current mid price from liquid route
- `ammExecPrice`: estimated effective onchain execution price at target size
- `impactBps`: `((ammExecPrice / spotPrice) - 1) * 10000` for buy-side impact
- `sizeUsd`: notional size in USD
- `depthUsd`: estimated executable liquidity depth near current price
- `sizeDepthRatio`: `sizeUsd / depthUsd`

## Quote construction
- `impactCaptureRatio`: `0.55` default
  - capture 55% of estimated impact as maker edge
  - leave 45% as taker savings versus AMM execution
- `basePremiumBps`: `8`
  - minimum premium when impact is tiny
- `maxPremiumBps`: `350`
  - hard cap unless explicitly overridden
- `volatilityHaircutBps`: `20` to `120`
  - add for volatile/illiquid assets before final safety checks

### Suggested premium formula
- `rawPremiumBps = max(basePremiumBps, impactBps * impactCaptureRatio)`
- `adjustedPremiumBps = rawPremiumBps + volatilityHaircutBps`
- `finalPremiumBps = min(adjustedPremiumBps, maxPremiumBps)`

## Size-to-liquidity ladder
- `sizeDepthRatio < 0.5` → premium band `10–40 bps`
- `0.5–1.0` → `40–90 bps`
- `1.0–2.0` → `90–180 bps`
- `2.0–4.0` → `180–300 bps`
- `> 4.0` → `300–500 bps` only with explicit confirmation

## Negotiation step rules
- `maxRounds`: `3`
- `stepBpsSmall`: `10` bps per round when ratio `< 1.0`
- `stepBpsLarge`: `25` bps per round when ratio `>= 1.0`
- `maxTotalConcessionBps`: `60` bps from initial quote

## Execution safety limits
- `minEdgeAfterFeesBps`: `15`
  - do not quote if edge after protocol fee and gas is below this
- `maxGasCostPctNotional`: `0.35%`
  - avoid tiny notionals with disproportionate gas drag
- `minExpirySec`: `1800`
- `maxExpirySec`: `86400`

## Decision policy
- If `impactBps` is low and `sizeDepthRatio < 0.5`, stay near fair and prioritize fill speed.
- If `impactBps` is high and `sizeDepthRatio >= 1.0`, apply the ladder and capture meaningful edge.
- Always ensure taker still gets a better expected fill than onchain AMM execution for that size.
