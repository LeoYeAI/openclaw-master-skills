# citrea-claw-skill 🦞

A CLI tool and [OpenClaw](https://openclaw.ai) skill for monitoring the [Citrea](https://citrea.xyz) Bitcoin L2 ecosystem. Track DEX pools, liquidity, arbitrage opportunities, token prices, and wallet balances — all sourced directly from Citrea mainnet with no third-party APIs.

Built for traders, liquidity providers, and developers active on Citrea.

## Features

- 🔍 **Arbitrage detection** — scan all token pairs across JuiceSwap and Satsuma, with gas-adjusted profit estimates and Telegram alerts
- 🏊 **Pool monitoring** — watch for new pools in real time with instant Telegram notifications
- 💰 **Price feeds** — on-chain prices via RedStone push oracles, pool-implied prices with oracle deviation
- 💼 **Wallet balances** — full token balances with USD values
- 📊 **Liquidity TVL** — pool reserves and total value locked
- 📋 **Transaction history** — recent swap activity for any wallet

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

| DEX       | Type       | Fee Tiers           |
|-----------|------------|---------------------|
| JuiceSwap | Uniswap V3 | 0.05%, 0.30%, 1.00% |
| Satsuma   | Algebra    | Dynamic per pool    |

## Quick Start
```bash
git clone https://github.com/jason-chew/citrea-claw-skill.git
cd citrea-claw-skill
npm install
cp .env.example .env
# edit .env with your Telegram bot token and chat ID
node index.js
```

See [SETUP.md](SETUP.md) for full configuration and deployment instructions.

## Commands
```bash
# Wallet
node index.js balance <address>                  # cBTC + token balances

# Prices
node index.js price <token>                      # USD price from RedStone oracle
node index.js pool:price <tokenA> <tokenB>       # implied price from each DEX

# Pools
node index.js pools:recent [hours]               # new pools in last N hours
node index.js pools:latest                       # most recent pool per DEX
node index.js pools:monitor                      # live watcher with Telegram alerts

# Liquidity
node index.js pool:liquidity <poolAddr>          # TVL by pool address
node index.js pool:liquidity <tokenA> <tokenB>   # TVL by pair
node index.js pool:liquidity <token>             # all pools for a token

# Arbitrage
node index.js arb:check <tokenA> <tokenB>        # check a specific pair
node index.js arb:scan                           # scan all pairs once
node index.js arb:monitor                        # live monitor with Telegram alerts

# Transactions
node index.js txns <address> [hours]             # recent swap activity
```

## Telegram Alerts

Set up a Telegram bot to receive alerts for:
- **Arb opportunities** — when a profitable spread is detected above your threshold
- **New pools** — whenever a new pool is created on any supported DEX

See [SETUP.md](SETUP.md) for setup instructions.

## Running 24/7

Use PM2 on any VPS to keep the monitors running continuously:
```bash
npm install -g pm2
pm2 start index.js --name "arb-monitor" -- arb:monitor
pm2 start index.js --name "pool-monitor" -- pools:monitor
pm2 save
```

See [SETUP.md](SETUP.md) for full deployment instructions.

## Tech Stack

- **Node.js** v18+ with ES modules
- **viem** — Ethereum/EVM client for on-chain reads
- **RedStone** — push oracle price feeds on Citrea
- **Telegram Bot API** — free, no usage limits

## Notes

- All data sourced directly from Citrea mainnet — no third-party APIs
- Arb detection is indicative only — always verify on-chain before executing
- RPC: `https://rpc.mainnet.citrea.xyz` (public, no API key required)

## License

MIT
