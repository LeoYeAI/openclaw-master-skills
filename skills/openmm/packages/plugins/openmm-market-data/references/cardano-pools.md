# Cardano Pool Reference

Reference for Cardano DEX liquidity pool data accessed through OpenMM.

## Iris Protocol Overview

OpenMM uses the **Iris Protocol** to aggregate liquidity pool data from Cardano decentralized exchanges. Iris indexes on-chain pool state across multiple DEXes, providing a unified interface for discovering pools, fetching reserves, and calculating prices.

No API keys are required — all Cardano DEX data is public on-chain data aggregated by Iris.

## Supported DEXes

| DEX | Description |
|-----|-------------|
| **SundaeSwap** | One of the earliest AMM DEXes on Cardano. Constant-product pools. |
| **Minswap** | Largest Cardano DEX by total value locked. Multiple pool types including constant-product and stableswap. |
| **WingRiders** | Cardano DEX featuring concentrated liquidity and efficient routing. |

## Supported Tokens

| Token | Symbol | Description |
|-------|--------|-------------|
| SNEK | `SNEK` | Snek Token — Cardano meme/community token |
| INDY | `INDY` | Indigo Protocol — synthetic assets on Cardano |
| NIGHT | `NIGHT` | Midnight — privacy-focused Cardano sidechain token |
| MIN | `MIN` | Minswap — governance token for Minswap DEX |

## Pool Structure

When discovering pools via `openmm pool-discovery discover <TOKEN>`, each pool entry includes:

| Field | Description |
|-------|-------------|
| **Pool address** | On-chain identifier for the liquidity pool |
| **DEX** | Which decentralized exchange hosts the pool (SundaeSwap, Minswap, WingRiders) |
| **Token pair** | The two tokens in the pool (e.g., SNEK/ADA) |
| **Reserve A** | Amount of the first token locked in the pool |
| **Reserve B** | Amount of the second token locked in the pool |
| **TVL** | Total value locked, denominated in ADA |
| **Implied price** | Price derived from the ratio of reserves |

## Price Calculation

Aggregated prices are computed in two steps:

1. **TOKEN/ADA** — Calculated from DEX pool reserves across all discovered pools, weighted by TVL. Pools with higher TVL contribute more to the final price.
2. **ADA/USDT** — Fetched from CEX price feeds (e.g., MEXC).
3. **TOKEN/USDT** = TOKEN/ADA x ADA/USDT

This bridging approach produces a USD-denominated price for tokens that may not have direct USDT pairs on centralized exchanges.

## Liquidity Thresholds and Filtering

Use the `--min-liquidity` flag to filter out low-TVL pools that may have unreliable pricing due to thin liquidity:

```bash
# Only show pools with at least 50,000 ADA in TVL
openmm pool-discovery discover SNEK --min-liquidity 50000

# Lower threshold for less liquid tokens
openmm pool-discovery discover NIGHT --min-liquidity 10000
```

**Guidelines:**
- Pools with TVL below 10,000 ADA may have wide implied spreads and unreliable prices
- For price comparison purposes, filter to pools with at least 25,000-50,000 ADA TVL
- The aggregated price (`pool-discovery prices`) already weights by TVL, so low-liquidity pools have minimal impact on the final price

## Token Discovery Flow

1. **Discover pools** — `openmm pool-discovery discover <TOKEN>` to find all liquidity pools for a token across supported DEXes
2. **Check prices** — `openmm pool-discovery prices <TOKEN>` to get the TVL-weighted aggregated price
3. **Compare with CEX** — `openmm price-comparison --symbol <TOKEN>` to see DEX vs CEX price spread
4. **Filter by liquidity** — Use `--min-liquidity` to focus on pools with meaningful TVL for more reliable pricing

## CLI Commands

```bash
# Aggregated price
openmm pool-discovery prices <TOKEN>

# Discover pools
openmm pool-discovery discover <TOKEN> [--min-liquidity <n>]

# DEX vs CEX comparison
openmm price-comparison --symbol <TOKEN>
```

## MCP Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_cardano_price` | `symbol` | Aggregated token price (TOKEN/USDT via ADA bridge) |
| `discover_pools` | `symbol`, `minLiquidity?` | Discover liquidity pools for a Cardano token |
