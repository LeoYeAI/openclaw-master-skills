# openmm-market-data

> Market data, portfolio tracking, and Cardano DEX integration for OpenMM

[![npm](https://img.shields.io/npm/v/@qbtlabs/openmm-market-data)](https://www.npmjs.com/package/@qbtlabs/openmm-market-data)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../../LICENSE)

A self-contained plugin for [OpenMM](https://github.com/3rd-Eye-Labs/OpenMM) that provides read-only market data, portfolio tracking, and Cardano DEX integration. No trading, no order placement — just data.

---

## Install

### npm

```bash
npm install @3rd-eye-labs/openmm
```

### ClawHub

```bash
clawhub install openmm-portfolio
clawhub install openmm-cardano-dex
```

### OpenClaw

```bash
openclaw plugins install @qbtlabs/openmm-market-data
```

---

## Skills

| Skill | Description |
|-------|-------------|
| **[portfolio](skills/portfolio.md)** | Balance tracking, open orders, market prices, and DEX/CEX price comparison |
| **[cardano-dex](skills/cardano-dex.md)** | Cardano DEX pool discovery, aggregated pricing via Iris Protocol |

## References

| Reference | Description |
|-----------|-------------|
| **[exchange-data](references/exchange-data.md)** | Exchange-specific data notes (min orders, precision, fiat pairs) |
| **[cardano-pools](references/cardano-pools.md)** | Cardano pool reference (Iris Protocol, DEXes, filtering) |

---

## Quick Start

### 1. Install OpenMM

```bash
npm install -g @3rd-eye-labs/openmm
```

### 2. Set Credentials

```bash
export MEXC_API_KEY="your_key"
export MEXC_SECRET="your_secret"
```

### 3. Check Balances

```bash
openmm balance --exchange mexc
```

### 4. Get Market Data

```bash
openmm ticker --exchange mexc --symbol BTC/USDT
openmm orderbook --exchange kraken --symbol ADA/EUR --limit 10
openmm trades --exchange bitget --symbol SNEK/USDT --limit 20
```

### 5. Cardano DEX Prices

```bash
openmm pool-discovery prices SNEK
openmm pool-discovery discover INDY --min-liquidity 50000
openmm price-comparison --symbol SNEK
```

---

## MCP Tools

When using the MCP server, these tools are available for market data:

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_balance` | Account balances (all or specific asset) | `exchange`, `asset?` |
| `get_ticker` | Real-time price, bid/ask, spread, volume | `exchange`, `symbol` |
| `get_orderbook` | Order book depth (bids/asks) | `exchange`, `symbol`, `limit?` |
| `get_trades` | Recent trades with buy/sell summary | `exchange`, `symbol`, `limit?` |
| `list_orders` | Open orders (all or by symbol) | `exchange`, `symbol?`, `limit?` |
| `get_cardano_price` | Aggregated Cardano token price from DEX pools | `symbol` |
| `discover_pools` | Discover Cardano DEX liquidity pools | `symbol`, `minLiquidity?` |

---

## Supported Exchanges

| Exchange | Env Vars | Min Order | Notes |
|----------|----------|-----------|-------|
| MEXC | `MEXC_API_KEY`, `MEXC_SECRET` | 1 USDT | SNEK/USDT, INDY/USDT, NIGHT/USDT |
| Gate.io | `GATEIO_API_KEY`, `GATEIO_SECRET` | 1 USDT | |
| Kraken | `KRAKEN_API_KEY`, `KRAKEN_SECRET` | 5 EUR/USD | Fiat pairs (EUR, USD, GBP), ADA/EUR |
| Bitget | `BITGET_API_KEY`, `BITGET_SECRET`, `BITGET_PASSPHRASE` | 1 USDT | 6 decimal price precision for SNEK/NIGHT |

---

## Links

- **OpenMM Core:** https://github.com/3rd-Eye-Labs/OpenMM
- **MCP Server:** https://github.com/QBT-Labs/OpenMM-MCP
- **npm:** https://www.npmjs.com/package/@3rd-eye-labs/openmm
- **Documentation:** https://deepwiki.com/3rd-Eye-Labs/OpenMM

## License

MIT
