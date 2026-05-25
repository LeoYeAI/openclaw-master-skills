# OpenMM CLI Reference -- Trading Commands

Full flag reference for trading-related CLI commands in OpenMM.

## balance

Get account balances for a connected exchange.

```bash
openmm balance --exchange <ex> [--asset <asset>] [--json]
```

| Flag | Required | Description |
|------|----------|-------------|
| `-e, --exchange <exchange>` | Yes | Exchange to query: mexc, gateio, kraken, bitget |
| `-a, --asset <asset>` | No | Filter by specific asset (e.g. BTC, USDT, EUR) |
| `--json` | No | Output in JSON format |

**Examples:**

```bash
# All balances on MEXC
openmm balance --exchange mexc

# Specific asset
openmm balance --exchange mexc --asset USDT
openmm balance --exchange kraken --asset EUR

# JSON output
openmm balance --exchange bitget --json
```

---

## orders list

List open orders on an exchange.

```bash
openmm orders list --exchange <ex> [--symbol <sym>] [--limit <n>]
```

| Flag | Required | Description |
|------|----------|-------------|
| `-e, --exchange <exchange>` | Yes | Exchange to query |
| `-s, --symbol <symbol>` | No | Filter by trading pair (e.g. BTC/USDT) |
| `-l, --limit <limit>` | No | Maximum number of orders to return |

**Examples:**

```bash
openmm orders list --exchange mexc
openmm orders list --exchange bitget --symbol SNEK/USDT
openmm orders list --exchange kraken --symbol ADA/EUR --limit 5
```

---

## orders get

Get details for a specific order by ID.

```bash
openmm orders get --exchange <ex> --id <id> --symbol <sym>
```

| Flag | Required | Description |
|------|----------|-------------|
| `-e, --exchange <exchange>` | Yes | Exchange to query |
| `--id <id>` | Yes | Order ID |
| `-s, --symbol <symbol>` | Yes | Trading pair the order belongs to |

**Examples:**

```bash
openmm orders get --exchange mexc --id 123456 --symbol BTC/USDT
openmm orders get --exchange bitget --id 1385288398060044291 --symbol SNEK/USDT
openmm orders get --exchange kraken --id OQN3UE-LRH6U-MPLZ5I --symbol ADA/EUR
```

---

## orders create

Place a limit or market order.

```bash
openmm orders create --exchange <ex> --symbol <sym> --side <buy|sell> --type <limit|market> --amount <n> [--price <n>]
```

| Flag | Required | Description |
|------|----------|-------------|
| `-e, --exchange <exchange>` | Yes | Exchange to trade on |
| `-s, --symbol <symbol>` | Yes | Trading pair (e.g. BTC/USDT, ADA/EUR) |
| `--side <side>` | Yes | Order side: `buy` or `sell` |
| `--type <type>` | Yes | Order type: `limit` or `market` |
| `--amount <amount>` | Yes | Amount in base currency |
| `--price <price>` | Limit only | Price in quote currency (required for limit, ignored for market) |

**Examples:**

```bash
# Limit buy
openmm orders create --exchange mexc --symbol BTC/USDT --side buy --type limit --price 50000 --amount 0.001

# Market sell
openmm orders create --exchange mexc --symbol BTC/USDT --side sell --type market --amount 0.001

# Limit buy on Kraken (fiat pair)
openmm orders create --exchange kraken --symbol ADA/EUR --side buy --type limit --price 0.45 --amount 50
```

---

## orders cancel

Cancel an order by ID.

```bash
openmm orders cancel --exchange <ex> --id <id> --symbol <sym>
```

| Flag | Required | Description |
|------|----------|-------------|
| `-e, --exchange <exchange>` | Yes | Exchange |
| `--id <id>` | Yes | Order ID to cancel |
| `-s, --symbol <symbol>` | Yes | Trading pair the order belongs to |

**Examples:**

```bash
openmm orders cancel --exchange mexc --id C02__626091255599874048060 --symbol INDY/USDT
openmm orders cancel --exchange bitget --id 1385288398060044291 --symbol SNEK/USDT
openmm orders cancel --exchange kraken --id OQN3UE-LRH6U-MPLZ5I --symbol ADA/EUR
```

---

## orders cancel-all

Cancel all open orders for a pair (or all orders on the exchange).

```bash
openmm orders cancel-all --exchange <ex> [--symbol <sym>]
```

| Flag | Required | Description |
|------|----------|-------------|
| `-e, --exchange <exchange>` | Yes | Exchange |
| `-s, --symbol <symbol>` | No | Trading pair (if omitted, cancels all orders on the exchange) |

**Examples:**

```bash
openmm orders cancel-all --exchange mexc --symbol INDY/USDT
openmm orders cancel-all --exchange gateio
```

---

## trade --strategy grid

Start an automated grid trading strategy.

```bash
openmm trade --strategy grid --exchange <ex> --symbol <sym> [options]
```

### Required Flags

| Flag | Description |
|------|-------------|
| `--strategy grid` | Specifies grid trading strategy |
| `--exchange <exchange>` | Exchange: mexc, gateio, kraken, bitget |
| `--symbol <symbol>` | Trading pair (e.g. INDY/USDT, ADA/EUR) |

### Grid Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--levels <number>` | 5 | Grid levels per side (max: 10, total orders = levels x 2) |
| `--spacing <decimal>` | 0.02 | Base price spacing between levels (0.02 = 2%) |
| `--size <number>` | 50 | Base order size in quote currency |
| `--confidence <decimal>` | 0.6 | Minimum price confidence to trade |
| `--deviation <decimal>` | 0.015 | Price deviation to trigger grid recreation |
| `--debounce <ms>` | 2000 | Delay between grid adjustments |
| `--max-position <decimal>` | 0.8 | Max position size as % of balance |
| `--safety-reserve <decimal>` | 0.2 | Safety reserve as % of balance |
| `--dry-run` | -- | Simulate without placing real orders |

### Dynamic Grid Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--spacing-model <model>` | linear | Spacing model: linear, geometric, or custom |
| `--spacing-factor <number>` | 1.3 | Geometric spacing multiplier per level |
| `--size-model <model>` | flat | Size model: flat, pyramidal, or custom |
| `--grid-profile <path>` | -- | Load complete grid config from a JSON profile |

### Volatility Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--volatility` | off | Enable volatility-based dynamic spread adjustment |
| `--volatility-low <decimal>` | 0.02 | Low volatility threshold |
| `--volatility-high <decimal>` | 0.05 | High volatility threshold |

**Examples:**

```bash
# Dry run
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT --dry-run

# Default grid
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT

# Custom configuration
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT \
  --levels 5 --spacing 0.02 --size 50 --max-position 0.6 --safety-reserve 0.3

# Geometric spacing with pyramidal sizing
openmm trade --strategy grid --exchange kraken --symbol BTC/USD \
  --levels 10 --spacing 0.005 --spacing-model geometric --spacing-factor 1.5 \
  --size-model pyramidal --size 50

# Volatility-based adjustment
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT \
  --levels 10 --spacing 0.005 --spacing-model geometric --spacing-factor 1.3 \
  --size-model pyramidal --size 5 --volatility

# From a profile
openmm trade --strategy grid --exchange gateio --symbol SNEK/USDT \
  --grid-profile ./profiles/balanced-geometric.json
```

---

## Exchange Minimum Order Values

| Exchange | Minimum | Notes |
|----------|---------|-------|
| MEXC | 1 USDT | -- |
| Gate.io | 1 USDT | -- |
| Bitget | 1 USDT | Requires passphrase, 6-decimal precision for SNEK/NIGHT |
| Kraken | 5 EUR/USD | Supports fiat pairs (EUR, USD, GBP) |
