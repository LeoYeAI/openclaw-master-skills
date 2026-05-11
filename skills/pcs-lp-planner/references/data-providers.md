# Data Providers Reference

This guide documents the data sources and APIs used by the liquidity-planner skill to gather pool information, yields, and liquidity metrics across PancakeSwap.

## DexScreener API

DexScreener provides real-time pool discovery and detailed trading pair information across multiple DEXs and chains.

### Filtering PancakeSwap Pools

DexScreener aggregates data from multiple DEXs. To filter for PancakeSwap pools only, use:

```bash
jq 'select(.dexId == "pancakeswap")'
```

### Supported Networks

PancakeSwap operates across multiple networks via DexScreener:

| Network | DexScreener ID | Primary Use |
|---------|---|---|
| BSC | `bsc` | Main liquidity, lowest fees |
| Ethereum | `ethereum` | Cross-chain assets |
| Arbitrum | `arbitrum` | Layer 2 scaling |
| Base | `base` | Coinbase ecosystem |
| zkSync | `zksync` | Low-cost transactions |
| Linea | `linea` | Ethereum compatibility |
| opBNB | `opbnb` | BSC Layer 2 |

### Pool Discovery by Token Address

To find all PancakeSwap pools containing a specific token:

```bash
curl -s "https://api.dexscreener.com/latest/dex/tokens/{tokenAddress}" | \
  jq '.pairs[] | select(.dexId == "pancakeswap")'
```

**Example: USDT pools on BSC**

```bash
curl -s "https://api.dexscreener.com/latest/dex/tokens/0x55d398326f99059ff775485246999027b3197955" | \
  jq '.pairs[] | select(.dexId == "pancakeswap") | {pairAddress, tokenA: .baseToken.symbol, tokenB: .quoteToken.symbol, volume24h, liquidity}'
```

### Pool Search by Name

To find pools by token name or symbol:

```bash
curl -s "https://api.dexscreener.com/latest/dex/search?q={searchQuery}" | \
  jq '.pairs[] | select(.dexId == "pancakeswap")'
```

**Example: Search for CAKE/BUSD**

```bash
curl -s "https://api.dexscreener.com/latest/dex/search?q=CAKE%20BUSD" | \
  jq '.pairs[] | select(.dexId == "pancakeswap" and .chainId == "bsc") | {pairAddress, priceUsd, liquidity, volume24h}'
```

### Pool Detail by Pair Address

To retrieve detailed information for a specific pair:

```bash
curl -s "https://api.dexscreener.com/latest/dex/pairs/{chainId}/{pairAddress}" | \
  jq '.pairs[0]'
```

**Example: Get details for CAKE/WBNB pool**

```bash
curl -s "https://api.dexscreener.com/latest/dex/pairs/bsc/0x0ed7e52944161450261c02fcc3d6855decdbda83" | \
  jq '.pairs[0] | {pairAddress, version: (if .labels | contains("v3") then "V3" elif .labels | contains("v2") then "V2" else "StableSwap" end), liquidity, volume24h, priceNative, priceUsd}'
```

### Response Field Reference

| Field | Type | Description |
|-------|------|---|
| `pairAddress` | string | Smart contract address of the pool |
| `dexId` | string | DEX identifier (always "pancakeswap" for this guide) |
| `chainId` | string | Blockchain network identifier |
| `baseToken` | object | Primary token in the pair |
| `quoteToken` | object | Secondary token in the pair |
| `priceNative` | string | Price in native blockchain currency |
| `priceUsd` | string | Price in USD (when available) |
| `liquidity` | string | Total liquidity in USD |
| `volume24h` | string | 24-hour trading volume in USD |
| `txns` | object | Transaction count (buys, sells, total) over time periods |
| `labels` | array | Pool metadata ("v2", "v3", "verified", etc.) |

### Important Notes on StableSwap Pools

DexScreener treats PancakeSwap StableSwap pools specially:

- **Labeling**: Some StableSwap pools appear with `dexId == "pancakeswap-stableswap"` instead of `"pancakeswap"`
- **Discovery**: To find all StableSwap pools, filter for both:
  ```bash
  jq '.pairs[] | select(.dexId == "pancakeswap" or .dexId == "pancakeswap-stableswap")'
  ```
- **Version identifier**: Not explicitly shown in `labels` for StableSwap (unlike "v2"/"v3")
- **Recommendation**: Cross-reference with DefiLlama or PancakeSwap API to confirm pool type

---

## DefiLlama Yields API

DefiLlama aggregates yield farming data across DeFi protocols. Use it to find APY/APR information for PancakeSwap positions.

### Project Identifiers

PancakeSwap projects are identified by version:

| Version | Project ID | Supported Chains |
|---------|---|---|
| V3 | `pancakeswap-amm-v3` | BSC, Ethereum, Arbitrum, Base, zkSync, Linea, opBNB, Monad |
| V2 | `pancakeswap-amm` | BSC, Ethereum, Arbitrum, Base, opBNB |
| StableSwap | `pancakeswap-stableswap` | BSC only |

### Chain Identifiers in DefiLlama

| Network | DefiLlama Name |
|---------|---|
| BSC | `BSC` |
| Ethereum | `Ethereum` |
| Arbitrum | `Arbitrum` |
| Base | `Base` |
| zkSync | `zkSync` |
| Linea | `Linea` |
| opBNB | `opBNB` |

### Fetching APY Data

```bash
curl -s "https://yields.llama.fi/pools" | \
  jq '.data[] | select(.project == "pancakeswap-amm-v3" and .chain == "BSC")'
```

**Example: Find top CAKE/WBNB yield pools on BSC**

```bash
curl -s "https://yields.llama.fi/pools" | \
  jq '.data[] |
    select(.project == "pancakeswap-amm-v3" and .chain == "BSC") |
    select((.symbol | contains("CAKE")) and (.symbol | contains("WBNB"))) |
    {symbol, apy, tvlUsd, poolMeta}'
```

### Response Field Reference

| Field | Type | Description |
|-------|------|---|
| `pool` | string | Unique pool identifier |
| `project` | string | Protocol name (pancakeswap-amm-v3, etc.) |
| `chain` | string | Blockchain network |
| `symbol` | string | Token pair symbol (e.g., "CAKE-WBNB") |
| `tvlUsd` | number | Total Value Locked in USD |
| `apy` | number | Annual Percentage Yield (percentage) |
| `apyBase` | number | Base APY from swap fees |
| `apyReward` | number | Additional reward APY (if any) |
| `rewardTokens` | array | Tokens used for rewards |
| `poolMeta` | string | Additional metadata (fee tier, etc.) |

### Coverage Limitations

- **Lag time**: DefiLlama updates may lag 5-15 minutes behind real-time conditions
- **StableSwap**: Limited coverage; some StableSwap pools may not be indexed
- **New pools**: Newly created pools may take time to appear in results
- **Fee information**: Not always provided; V3 pools may need separate lookup for fee tier

---

## PancakeSwap Token List API

Use the official PancakeSwap token list as a fallback when DexScreener lacks token information or for token metadata validation.

### Endpoint

```
https://tokens.pancakeswap.finance/pancakeswap-extended.json
```

### Token List Structure

The endpoint returns a JSON object with token arrays organized by chain. Each token includes metadata useful for position setup.

### Finding a Token by Symbol

```bash
curl -s "https://tokens.pancakeswap.finance/pancakeswap-extended.json" | \
  jq '.tokens[] | select(.symbol == "CAKE")'
```

**Example: Find USDT on multiple chains**

```bash
curl -s "https://tokens.pancakeswap.finance/pancakeswap-extended.json" | \
  jq '.tokens[] | select(.symbol == "USDT") | {chainId, address, name, decimals}'
```

### Token Object Fields

| Field | Type | Description |
|-------|------|---|
| `chainId` | number | Blockchain network (56 = BSC, 1 = Ethereum, etc.) |
| `address` | string | Token contract address |
| `name` | string | Full token name |
| `symbol` | string | Token ticker symbol |
| `decimals` | number | Number of decimal places |
| `logoURI` | string | URL to token icon (optional) |

### When to Use This API

- **Token validation**: Confirm token addresses before creating positions
- **Decimals lookup**: Get correct decimal places for calculations
- **Metadata filling**: Retrieve token names and logos for UI display
- **Fallback**: When DexScreener doesn't return token information

---

## Recommended Workflow

Follow this sequence to gather complete pool and position data:

### Step 1: Discover Pools

Use DexScreener to find candidate pools matching your criteria:

```bash
curl -s "https://api.dexscreener.com/latest/dex/search?q={searchQuery}" | \
  jq '.pairs[] | select(.dexId == "pancakeswap" or .dexId == "pancakeswap-stableswap")'
```

**Output needed**:
- Pair address
- Token addresses and symbols
- Current liquidity (USD)
- 24h volume

### Step 2: Check Yields (APY)

Query DefiLlama for farming returns on promising pools:

```bash
curl -s "https://yields.llama.fi/pools" | \
  jq '.data[] | select(.pool == "{pairAddress}")'
```

**Output needed**:
- APY (base + rewards)
- TVL in USD
- Pool metadata (fee tier for V3)

### Step 3: Assess Liquidity Depth

Evaluate if liquidity is sufficient for your position size:

| TVL (USD) | Assessment | Risk Level |
|-----------|---|---|
| > $10M | Deep, excellent for large positions | Low |
| $1M - $10M | Moderate-to-good depth | Low to Medium |
| $100K - $1M | Moderate, suitable for medium positions | Medium |
| $10K - $100K | Shallow, large positions cause slippage | Medium to High |
| < $10K | Very shallow, high slippage risk | High |

### Step 4: Calculate Price Range (for V3)

Use the collected price data to determine appropriate tick ranges:

```python
import math

# Current price and target range (e.g., ±10%)
current_price = float(price_usd)
range_percent = 0.10  # 10% buffer
lower_bound = current_price * (1 - range_percent)
upper_bound = current_price * (1 + range_percent)

# V3 uses ticks with basis points spacing
# Tick formula: log_1.0001(price) for 1 basis point ticks
tick_lower = math.floor(math.log(lower_bound) / math.log(1.0001))
tick_upper = math.ceil(math.log(upper_bound) / math.log(1.0001))

print(f"Tick range: {tick_lower} to {tick_upper}")
print(f"Price range: ${lower_bound:.4f} to ${upper_bound:.4f}")
```

### Error Handling

| Error | Cause | Resolution |
|-------|---|---|
| Pool not found | DexScreener doesn't index this pool yet | Try token search instead; verify pair address manually |
| No APY data | Pool too new or not tracked by DefiLlama | Monitor pool directly; estimate from volume |
| Stale price | API lag or low volume | Cross-check with multiple sources; add buffer to ranges |
| Token not found | Token list outdated or not supported | Verify token address on blockchain explorer |
| Network mismatch | Querying wrong chainId for pool | Check pool address format; confirm network in dexId |

---

## Rate Limits & Best Practices

- **DexScreener**: 2 requests/second (generous for research)
- **DefiLlama**: 10 requests/second (no API key required)
- **PancakeSwap Token List**: No stated limit; cache locally when possible
- **Caching**: Store results for 5-15 minutes to reduce unnecessary requests
- **Error handling**: Implement exponential backoff for failed requests
