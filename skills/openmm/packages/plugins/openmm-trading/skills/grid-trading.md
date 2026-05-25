---
name: openmm-grid-trading
version: 0.1.0
description: "Create and manage grid trading strategies with OpenMM. Automated buy/sell around center price."
tags: [openmm, grid, trading, strategy, automation]
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins: [openmm]
      env: [MEXC_API_KEY, GATEIO_API_KEY, BITGET_API_KEY, KRAKEN_API_KEY]
    install:
      - kind: node
        package: "@3rd-eye-labs/openmm"
        bins: [openmm]
---

# OpenMM Grid Trading

Create automated grid trading strategies that profit from market volatility.

## What is Grid Trading?

Grid trading places multiple buy and sell orders at preset price intervals around the current center price. As price oscillates, the bot automatically:
- **Buys low** -- places buy orders below the center price
- **Sells high** -- places sell orders above the center price
- **Profits from volatility** -- each complete cycle captures the spread

The grid uses **levels per side** and **spacing** to distribute orders. With 5 levels and 2% spacing (linear), orders are placed at 2%, 4%, 6%, 8%, 10% from center on both sides (10 total orders).

## When to Use

**Good for:**
- Sideways/ranging markets
- High volatility pairs
- Passive income generation
- 24/7 automated trading

**Avoid when:**
- Strong trending markets (risk of holding losing positions)
- Low liquidity pairs
- High fee environments

## Quick Start

### 1. Dry Run First (Always!)

```bash
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT --dry-run
```

### 2. Start Grid with Defaults

```bash
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT
```

### 3. Custom Configuration

```bash
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT \
  --levels 5 \
  --spacing 0.02 \
  --size 50 \
  --max-position 0.6 \
  --safety-reserve 0.3
```

### 4. Stop the Strategy

Press `Ctrl+C` to gracefully stop. The system will:
1. Cancel all open orders
2. Disconnect from exchange
3. Display final status

## Command Options

### Required Parameters
- `--strategy grid` -- Specifies grid trading strategy
- `--exchange <exchange>` -- Exchange to trade on (mexc, bitget, gateio, kraken)
- `--symbol <symbol>` -- Trading pair (e.g., INDY/USDT, SNEK/USDT, ADA/EUR)

### Grid Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `--levels <number>` | Grid levels each side (max: 10, total = levels x 2) | 5 |
| `--spacing <decimal>` | Base price spacing between levels (0.02 = 2%) | 0.02 |
| `--size <number>` | Base order size in quote currency | 50 |
| `--confidence <decimal>` | Minimum price confidence to trade | 0.6 |
| `--deviation <decimal>` | Price deviation to trigger grid recreation | 0.015 |
| `--debounce <ms>` | Delay between grid adjustments | 2000 |
| `--max-position <decimal>` | Max position size as % of balance | 0.8 |
| `--safety-reserve <decimal>` | Safety reserve as % of balance | 0.2 |
| `--dry-run` | Simulate without placing real orders | -- |

### Dynamic Grid Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `--spacing-model <model>` | linear, geometric, or custom | linear |
| `--spacing-factor <number>` | Geometric spacing multiplier per level | 1.3 |
| `--size-model <model>` | flat, pyramidal, or custom | flat |
| `--grid-profile <path>` | Load grid config from a JSON profile file | -- |

### Volatility Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `--volatility` | Enable volatility-based spread adjustment | off |
| `--volatility-low <decimal>` | Low volatility threshold | 0.02 |
| `--volatility-high <decimal>` | High volatility threshold | 0.05 |

## Spacing Models

**Linear (default):** Equal spacing between all levels.
```
With --spacing 0.02 and 5 levels:
Level 1:  2% from center
Level 2:  4% from center
Level 3:  6% from center
Level 4:  8% from center
Level 5: 10% from center
```

**Geometric:** Tighter spacing near center, wider gaps at outer levels.
```bash
openmm trade --strategy grid --exchange kraken --symbol BTC/USD \
  --levels 5 --spacing 0.005 --spacing-model geometric --spacing-factor 1.5
```
```
Level 1: 0.50% from center
Level 2: 1.25% from center
Level 3: 2.38% from center
Level 4: 4.06% from center
Level 5: 6.59% from center
```

**Custom:** Define exact spacing offsets per level using a grid profile JSON file.

## Size Models

**Flat (default):** All levels get equal order sizes.

**Pyramidal:** Larger orders near center price where fills are more likely, tapering at outer levels.
```bash
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT \
  --levels 5 --size 50 --size-model pyramidal
```

## Grid Profiles

JSON files for complete grid configuration:

```json
{
  "name": "balanced-geometric",
  "description": "Geometric spacing with pyramidal sizing",
  "levels": 10,
  "spacingModel": "geometric",
  "baseSpacing": 0.005,
  "spacingFactor": 1.3,
  "sizeModel": "pyramidal",
  "baseSize": 50
}
```

```bash
openmm trade --strategy grid --exchange gateio --symbol SNEK/USDT \
  --grid-profile ./profiles/balanced-geometric.json
```

## Volatility-Based Spread Adjustment

When enabled, the grid automatically widens during volatile conditions and tightens when the market calms. Tracks price changes over a 5-minute rolling window.

- Below low threshold (default 2%): Normal spacing (1.0x)
- Between thresholds: Elevated spacing (1.5x)
- Above high threshold (default 5%): Wide spacing (2.0x)

```bash
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT \
  --levels 10 \
  --spacing 0.005 \
  --spacing-model geometric \
  --spacing-factor 1.3 \
  --size-model pyramidal \
  --size 5 \
  --volatility
```

## Trading Examples

### Conservative
```bash
openmm trade --strategy grid --exchange bitget --symbol SNEK/USDT \
  --levels 2 \
  --spacing 0.02 \
  --size 20
```

### Active
```bash
openmm trade --strategy grid --exchange mexc --symbol BTC/USDT \
  --levels 7 \
  --spacing 0.005 \
  --size 25
```

### Dynamic (Geometric + Pyramidal)
```bash
openmm trade --strategy grid --exchange kraken --symbol SNEK/EUR \
  --levels 10 \
  --spacing 0.005 \
  --spacing-model geometric \
  --spacing-factor 1.5 \
  --size-model pyramidal \
  --size 5
```

## Risk Management

- `--max-position` -- Maximum % of balance used for trading (default: 80%)
- `--safety-reserve` -- % of balance kept as reserve (default: 20%)
- `--confidence` -- Minimum price confidence required (default: 60%)
- Grid is automatically recreated when orders are filled
- Adjusts to significant price movements (configurable via `--deviation`)

## Exchange-Specific Notes

**MEXC/Gate.io:** Minimum order value 1 USDT per order
**Bitget:** Minimum 1 USDT. Requires API key, secret, and passphrase. 6 decimal price precision for SNEK/NIGHT pairs.
**Kraken:** Minimum 5 EUR/USD per order. Supports major fiat pairs (EUR, USD, GBP).

## Tips for Agents

1. **Always dry-run first** -- show user the plan before executing
2. **Check balance** -- verify sufficient funds with `openmm balance --exchange <ex>`
3. **Check current price** -- use `openmm ticker --exchange <ex> --symbol <sym>`
4. **Respect minimum order values** -- ensure `--size` divided by `--levels` meets exchange minimums
5. **Use Ctrl+C to stop** -- graceful shutdown cancels all open orders
