---
name: citrea-claw-skill
description: A CLI tool and OpenClaw skill for monitoring the Citrea Bitcoin L2 ecosystem
tags: [citrea, bitcoin, defi, arbitrage, openclaw, cli, web3, cbtc]
requires:
  bins:
    - node
  env:
    - TELEGRAM_BOT_TOKEN
    - TELEGRAM_CHAT_ID
    - ARB_ALERT_THRESHOLD_BPS
    - ARB_MONITOR_INTERVAL_SEC
primaryEnv: TELEGRAM_BOT_TOKEN
---

# citrea-claw-skill

Monitor the Citrea Bitcoin L2 ecosystem. Track DEX pools, liquidity, arbitrage opportunities, token prices, and wallet balances — all sourced directly from Citrea mainnet with no third-party APIs.

## Commands

### balance
Check cBTC and token balances for a wallet address with USD values.
- **Usage:** `balance <address>`
- **Example:** `balance 0xYourAddress`

### price
Get the current USD price for a token from RedStone on-chain oracles.
- **Usage:** `price <token>`
- **Example:** `price wcBTC`
- **Tokens:** wcBTC, ctUSD, USDC.e, USDT.e, WBTC.e, JUSD

### pool:price
Show the implied price of a token pair from each DEX side by side, with oracle deviation.
- **Usage:** `pool:price <tokenA> <tokenB>`
- **Example:** `pool:price wcBTC USDC.e`

### pools:recent
List all new pools created in the last N hours across JuiceSwap and Satsuma.
- **Usage:** `pools:recent [hours]`
- **Example:** `pools:recent 24`

### pools:latest
Show the most recently created pool on each DEX.
- **Usage:** `pools:latest`

### pools:monitor
Watch for new pools in real time. Sends a Telegram alert whenever a new pool is created on any supported DEX.
- **Usage:** `pools:monitor`

### pool:liquidity
Show TVL and token reserves for a pool. Accepts a pool address, token pair, or single token.
- **Usage:** `pool:liquidity <poolAddr|tokenA tokenB|token>`
- **Examples:**
  - `pool:liquidity wcBTC USDC.e`
  - `pool:liquidity 0xPoolAddress`
  - `pool:liquidity wcBTC`

### arb:check
Check a specific token pair for arbitrage opportunities across JuiceSwap and Satsuma.
- **Usage:** `arb:check <tokenA> <tokenB>`
- **Example:** `arb:check wcBTC USDC.e`

### arb:scan
Scan all token pairs for arbitrage opportunities in a single pass. Shows price spread, estimated profit, gas cost, and net profit after fees.
- **Usage:** `arb:scan`

### arb:monitor
Continuously monitor all token pairs for arbitrage opportunities. Sends a Telegram alert when a profitable opportunity is detected above the configured threshold.
- **Usage:** `arb:monitor`

### txns
Show recent token transfer activity for a wallet address.
- **Usage:** `txns <address> [hours]`
- **Example:** `txns 0xYourAddress 24`

## Supported Tokens

| Symbol  | Description                         |
|---------|-------------------------------------|
| wcBTC   | Wrapped Citrea Bitcoin              |
| ctUSD   | Citrea USD stablecoin               |
| USDC.e  | Bridged USDC (LayerZero)            |
| USDT.e  | Bridged USDT (LayerZero)            |
| WBTC.e  | Bridged Wrapped Bitcoin (LayerZero) |
| JUSD    | BTC-backed stablecoin (JuiceDollar) |

## Supported DEXes

| DEX       | Type         | Fee Tiers              |
|-----------|--------------|------------------------|
| JuiceSwap | Uniswap V3   | 0.05%, 0.30%, 1.00%    |
| Satsuma   | Algebra      | Dynamic per pool       |

## Configuration

Set these in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | — |
| `TELEGRAM_CHAT_ID` | Your chat ID from @userinfobot | — |
| `ARB_ALERT_THRESHOLD_BPS` | Minimum profit to trigger arb alert (basis points) | 50 |
| `ARB_MONITOR_INTERVAL_SEC` | Seconds between arb scans | 15 |

## Notes

- All data sourced directly from Citrea mainnet — no third-party APIs
- Prices from RedStone push oracles deployed on Citrea
- Arb detection is indicative only — always verify on-chain before executing
- JuiceSwap JUSD pairs use svJUSD internally — handled transparently
- RPC: `https://rpc.mainnet.citrea.xyz`
