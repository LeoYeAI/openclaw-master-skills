---
name: openmm-order-management
version: 0.1.0
description: "Place, list, and cancel limit/market orders on supported exchanges with OpenMM."
tags: [openmm, orders, trading, limit, market]
metadata:
  openclaw:
    emoji: "📋"
    requires:
      bins: [openmm]
      env: [MEXC_API_KEY, GATEIO_API_KEY, BITGET_API_KEY, KRAKEN_API_KEY]
    install:
      - kind: node
        package: "@3rd-eye-labs/openmm"
        bins: [openmm]
---

# OpenMM Order Management

Place, list, and cancel limit and market orders on MEXC, Gate.io, Kraken, and Bitget.

## When to Use

Use this skill when:
- Placing a manual buy or sell order
- Listing open orders on an exchange
- Looking up an order by ID
- Cancelling a single order or all orders for a pair

## CLI Commands

### Create an Order

```bash
openmm orders create --exchange <ex> --symbol <sym> --side <buy|sell> --type <limit|market> --amount <n> [--price <n>]
```

**Examples:**

```bash
# Limit buy on MEXC
openmm orders create --exchange mexc --symbol BTC/USDT --side buy --type limit --price 50000 --amount 0.001

# Limit buy on Bitget (SNEK with 6-decimal price)
openmm orders create --exchange bitget --symbol SNEK/USDT --side buy --type limit --price 0.000010 --amount 10000

# Limit buy on Kraken
openmm orders create --exchange kraken --symbol ADA/EUR --side buy --type limit --price 0.45 --amount 50

# Market sell on MEXC
openmm orders create --exchange mexc --symbol BTC/USDT --side sell --type market --amount 0.001

# Market sell on Bitget
openmm orders create --exchange bitget --symbol SNEK/USDT --side sell --type market --amount 5000
```

**Parameters:**
| Flag | Required | Description |
|------|----------|-------------|
| `--exchange <ex>` | Yes | Exchange: mexc, gateio, kraken, bitget |
| `--symbol <sym>` | Yes | Trading pair (e.g. BTC/USDT, ADA/EUR) |
| `--side <side>` | Yes | `buy` or `sell` |
| `--type <type>` | Yes | `limit` or `market` |
| `--amount <n>` | Yes | Amount in base currency |
| `--price <n>` | Limit only | Price in quote currency (required for limit, ignored for market) |

### List Open Orders

```bash
openmm orders list --exchange <ex> [--symbol <sym>] [--limit <n>]
```

**Examples:**

```bash
# All open orders on MEXC
openmm orders list --exchange mexc

# Orders for a specific pair on Bitget
openmm orders list --exchange bitget --symbol SNEK/USDT

# Limited results on Kraken
openmm orders list --exchange kraken --symbol ADA/EUR --limit 5
```

### Get Order by ID

```bash
openmm orders get --exchange <ex> --id <id> --symbol <sym>
```

**Examples:**

```bash
openmm orders get --exchange mexc --id 123456 --symbol BTC/USDT
openmm orders get --exchange bitget --id 1385288398060044291 --symbol SNEK/USDT
openmm orders get --exchange kraken --id OQN3UE-LRH6U-MPLZ5I --symbol ADA/EUR
```

### Cancel an Order

```bash
openmm orders cancel --exchange <ex> --id <id> --symbol <sym>
```

**Examples:**

```bash
openmm orders cancel --exchange mexc --id C02__626091255599874048060 --symbol INDY/USDT
openmm orders cancel --exchange bitget --id 1385288398060044291 --symbol SNEK/USDT
openmm orders cancel --exchange kraken --id OQN3UE-LRH6U-MPLZ5I --symbol ADA/EUR
```

### Cancel All Orders for a Pair

```bash
openmm orders cancel-all --exchange <ex> [--symbol <sym>]
```

**Examples:**

```bash
# Cancel all orders for a specific pair
openmm orders cancel-all --exchange mexc --symbol INDY/USDT

# Cancel all open orders on an exchange
openmm orders cancel-all --exchange gateio
```

## MCP Tools

When using OpenMM as an MCP server, the following tools are available for order management:

| Tool | Parameters | Description |
|------|-----------|-------------|
| `create_order` | `exchange`, `symbol`, `type`, `side`, `amount`, `price?` | Place a limit or market order |
| `cancel_order` | `exchange`, `orderId`, `symbol` | Cancel a specific order by ID |
| `cancel_all_orders` | `exchange`, `symbol` | Cancel all open orders for a pair |
| `list_orders` | `exchange`, `symbol?` | List open orders |

## Safety Guidelines

1. **Always confirm with the user before placing orders.** Show the order details (exchange, symbol, side, type, amount, price) and get explicit approval.
2. **Check balance first.** Run `openmm balance --exchange <ex>` to verify sufficient funds before placing an order.
3. **Check current price.** Run `openmm ticker --exchange <ex> --symbol <sym>` to verify the market price before placing limit orders.
4. **Respect minimum order values:**
   - MEXC / Gate.io / Bitget: 1 USDT minimum per order
   - Kraken: 5 EUR/USD minimum per order
5. **Bitget requires passphrase.** Ensure `BITGET_PASSPHRASE` is set alongside `BITGET_API_KEY` and `BITGET_SECRET`.
6. **Double-check symbol format.** Always use `BASE/QUOTE` format (e.g. `BTC/USDT`, `ADA/EUR`).
7. **For limit orders, verify price is reasonable.** Compare the limit price against the current ticker price to avoid placing orders far from market.

## Exchange-Specific Notes

**MEXC:**
- Minimum order value: 1 USDT
- Env vars: `MEXC_API_KEY`, `MEXC_SECRET`

**Gate.io:**
- Minimum order value: 1 USDT
- Env vars: `GATEIO_API_KEY`, `GATEIO_SECRET`

**Bitget:**
- Minimum order value: 1 USDT
- 6-decimal price precision for SNEK/NIGHT pairs
- 2-decimal quantity precision
- Requires passphrase
- Env vars: `BITGET_API_KEY`, `BITGET_SECRET`, `BITGET_PASSPHRASE`

**Kraken:**
- Minimum order value: 5 EUR/USD
- Supports fiat pairs (EUR, USD, GBP)
- Env vars: `KRAKEN_API_KEY`, `KRAKEN_SECRET`
