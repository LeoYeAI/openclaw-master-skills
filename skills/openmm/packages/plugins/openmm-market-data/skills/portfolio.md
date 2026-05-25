---
name: openmm-portfolio
version: 0.1.0
description: "Balance tracking, order overview, and market data across exchanges using OpenMM."
tags: [openmm, portfolio, balance, orders, market-data]
metadata:
  openclaw:
    emoji: "💼"
    requires:
      bins: [openmm]
      env: [MEXC_API_KEY, GATEIO_API_KEY, BITGET_API_KEY, KRAKEN_API_KEY]
    install:
      - kind: node
        package: "@3rd-eye-labs/openmm"
        bins: [openmm]
---

# OpenMM Portfolio Management

Track balances, review open orders, and monitor market data across exchanges.

## Required Credentials

At least one exchange must be configured via environment variables. Set the credentials for each exchange you want to query:

```bash
# MEXC
MEXC_API_KEY=your-mexc-api-key
MEXC_SECRET=your-mexc-secret
MEXC_UID=your-mexc-uid-for-whitelisted-access

# Gate.io
GATEIO_API_KEY=your-gateio-api-key
GATEIO_SECRET=your-gateio-secret

# Bitget (requires passphrase)
BITGET_API_KEY=your-bitget-api-key
BITGET_SECRET=your-bitget-secret
BITGET_PASSPHRASE=your-bitget-passphrase

# Kraken
KRAKEN_API_KEY=your-kraken-api-key
KRAKEN_SECRET=your-kraken-secret
```

See the [exchange-setup](../../skills/exchange-setup/SKILL.md) skill for detailed configuration instructions.

## View Balances

```bash
# All assets on an exchange
openmm balance --exchange mexc
openmm balance --exchange kraken

# Specific asset
openmm balance --exchange mexc --asset BTC
openmm balance --exchange kraken --asset ADA
openmm balance --exchange bitget --asset USDT

# JSON output
openmm balance --exchange mexc --json
```

To see balances across all exchanges, query each one:

```bash
openmm balance --exchange mexc
openmm balance --exchange gateio
openmm balance --exchange bitget
openmm balance --exchange kraken
```

## Review Open Orders

```bash
# All open orders on an exchange
openmm orders list --exchange mexc

# Filter by trading pair
openmm orders list --exchange bitget --symbol SNEK/USDT

# Limit results
openmm orders list --exchange kraken --limit 5
```

## Check Market Prices

```bash
# Current price
openmm ticker --exchange mexc --symbol BTC/USDT
openmm ticker --exchange kraken --symbol ADA/EUR

# Order book depth
openmm orderbook --exchange bitget --symbol SNEK/USDT --limit 10

# Recent trades
openmm trades --exchange mexc --symbol ETH/USDT --limit 50
```

## Compare Prices Across Exchanges

```bash
# Compare DEX and CEX prices for Cardano tokens
openmm price-comparison --symbol SNEK
openmm price-comparison --symbol INDY
```

## Cardano Token Prices

```bash
# Aggregated price from DEX pools
openmm pool-discovery prices NIGHT
openmm pool-discovery prices SNEK

# Discover liquidity pools
openmm pool-discovery discover INDY
openmm pool-discovery discover SNEK --min-liquidity 50000
```

## MCP Tools for Portfolio Overview

When using the MCP server, these tools are relevant for portfolio management:

| Tool | Description |
|------|-------------|
| `get_balance` | Get balances for an exchange (all or specific asset) |
| `list_orders` | List open orders on an exchange |
| `get_ticker` | Current price for a trading pair |
| `get_orderbook` | Order book depth (bids/asks) |
| `get_trades` | Recent trades with buy/sell summary |
| `get_cardano_price` | Aggregated Cardano token price |
| `discover_pools` | Discover Cardano DEX liquidity pools |

## Tips for Agents

1. **Check balances before trading** — always verify available funds
2. **Query each exchange separately** — there is no cross-exchange aggregate command
3. **Use `--json` for parsing** — structured output for programmatic use
4. **Use `BASE/QUOTE` format** — e.g. `BTC/USDT`, `ADA/EUR`, `SNEK/USDT`
5. **Respect minimum order values** — MEXC/Gate.io/Bitget: 1 USDT, Kraken: 5 EUR/USD
