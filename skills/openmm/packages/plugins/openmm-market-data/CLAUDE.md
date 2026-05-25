# openmm-market-data — Agent Instructions

## What This Plugin Does

This plugin provides **read-only** market data, portfolio tracking, and Cardano DEX integration for OpenMM. It covers two skills:

- **portfolio** — Balance checks, open order listing, ticker prices, orderbook depth, recent trades, and DEX/CEX price comparison.
- **cardano-dex** — Aggregated Cardano token pricing from on-chain DEX pools via Iris Protocol, pool discovery, and DEX vs CEX arbitrage analysis.

## Important: Read-Only Operations Only

This plugin does **not** perform any trading actions. There is no risk of placing orders, cancelling orders, or modifying positions. All operations are read-only data queries.

The following actions are **in scope**:
- Checking account balances
- Listing open orders (read-only)
- Fetching ticker prices, orderbooks, and recent trades
- Querying Cardano DEX pool prices and discovering liquidity pools
- Comparing DEX and CEX prices

The following actions are **out of scope** for this plugin:
- Creating or cancelling orders
- Starting or stopping grid strategies
- Any operation that modifies exchange state

## Skills

| Skill | File | Description |
|-------|------|-------------|
| `openmm-portfolio` | `skills/portfolio.md` | Balance tracking, order overview, market data |
| `openmm-cardano-dex` | `skills/cardano-dex.md` | Cardano DEX pricing and pool discovery |

## Reference Files

| Reference | File | Description |
|-----------|------|-------------|
| Exchange Data | `references/exchange-data.md` | Exchange-specific notes (min orders, precision, fiat pairs) |
| Cardano Pools | `references/cardano-pools.md` | Iris Protocol, DEX pool structure, liquidity thresholds |

## MCP Tools

These MCP tools are relevant for this plugin:

- `get_balance` — Account balances (exchange, asset?)
- `get_ticker` — Real-time price data (exchange, symbol)
- `get_orderbook` — Order book depth (exchange, symbol, limit?)
- `get_trades` — Recent trades (exchange, symbol, limit?)
- `list_orders` — Open orders (exchange, symbol?, limit?)
- `get_cardano_price` — Aggregated Cardano token price (symbol)
- `discover_pools` — Discover Cardano DEX liquidity pools (symbol, minLiquidity?)

## CLI Commands

```bash
openmm balance --exchange <ex> [--asset <asset>] [--json]
openmm ticker --exchange <ex> --symbol <sym>
openmm orderbook --exchange <ex> --symbol <sym> [--limit <n>]
openmm trades --exchange <ex> --symbol <sym> [--limit <n>]
openmm orders list --exchange <ex> [--symbol <sym>] [--limit <n>]
openmm pool-discovery prices <TOKEN>
openmm pool-discovery discover <TOKEN> [--min-liquidity <n>]
openmm price-comparison --symbol <TOKEN>
```

## Supported Exchanges

MEXC, Gate.io, Kraken, Bitget. Each exchange requires its own API credentials set via environment variables. Query each exchange separately — there is no cross-exchange aggregate command.
