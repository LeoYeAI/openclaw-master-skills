# Position Types Reference

This guide documents the different liquidity position types available on PancakeSwap, their characteristics, fee structures, and when to use each.

## Version Comparison

PancakeSwap offers multiple liquidity mechanisms, each optimized for different use cases:

| Feature | V2 | V3 | StableSwap | Infinity (v4) |
|---------|----|----|-----------|---|
| **Range Type** | Full range | Concentrated | Full range (optimized) | Concentrated (CL) or Bin |
| **Fee Structure** | Fixed 0.25% | Tiered (4 options) | Fixed, varies by pair | Dynamic (hooks) |
| **LP Token** | ERC-20 token | NFT (ERC-721) | ERC-20 token | Managed by PoolManager |
| **Networks** | Multi-chain | Multi-chain | BSC, Ethereum, Arbitrum | BSC, Base |
| **Liquidity Efficiency** | Low | High | Very High (for stables) | Highest |
| **Farming Flow** | 2 steps (add LP → stake) | 2 steps (add LP → stake NFT) | 2 steps (add LP → stake) | **1 step (add LP = auto-farmed)** |
| **Best For** | Long-term passive | Active management | Stablecoin pairs | Simplest farming UX + advanced strategies |
| **Status** | Mature | Production | Production | Production |

---

## V2 Positions

V2 uses the constant product formula (x * y = k) with liquidity across the entire price range.

### Characteristics

- **Full range**: Liquidity available at all possible prices
- **Fixed fee**: 0.25% of all swaps (unique to PancakeSwap V2)
- **LP token**: Fungible ERC-20 token representing your share
- **Network**: Multi-chain (BSC, Ethereum, Arbitrum, Base, zkSync, Linea, opBNB, Monad)
- **Emissions**: May qualify for CAKE rewards (subject to farm selection)

### When to Use V2

- Long-term passive liquidity provision
- Pairs with low volatility (established stablecoin pairs on BSC)
- Simple implementation without active management
- Maximum simplicity for newer LPs

### Key Formula

```
Constant Product: x * y = k

Where:
  x = reserve of tokenA
  y = reserve of tokenB
  k = constant (invariant)

Price = y / x

When you add liquidity at price P:
  Your LP tokens = sqrt(x * y) = k
```

### Creating V2 Positions

**Deep link format**:
```
https://pancakeswap.finance/v2/add/{tokenA}/{tokenB}?chain=bsc
```

**Parameter explanations**:
- `{tokenA}`: Contract address of first token (or "BNB" for native)
- `{tokenB}`: Contract address of second token
- `chain=bsc`: Chain identifier

**Example: CAKE/WBNB on BSC**
```
https://pancakeswap.finance/v2/add/0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82/0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c?chain=bsc
```

### Fee Details

| Feature | V2 |
|---------|---|
| **Swap fee** | 0.25% |
| **LP creator share** | 0.25% |
| **Burn/Treasury** | 0.00% (all to LPs) |
| **Tier** | Single tier (no variation) |

---

## V3 Positions

V3 introduces concentrated liquidity, allowing capital efficiency gains through custom price ranges.

### Characteristics

- **Concentrated ranges**: Deploy liquidity in custom price bands
- **Multiple fee tiers**: Choose based on expected volatility
- **NFT positions**: Each position is a unique NFT (ERC-721)
- **Multi-chain**: Available on BSC, Ethereum, Arbitrum, Base, zkSync, Linea, opBNB, Monad
- **Capital efficiency**: 4000x more capital-efficient at full range than V2

### Fee Tiers

| Fee Tier | Percentage | Tick Spacing | Best For |
|----------|-----------|---|---|
| **0.01%** | 100 bps (0.01%) | 1 | Stablecoin pairs, tight ranges |
| **0.05%** | 500 bps (0.05%) | 10 | Stablecoins, low volatility |
| **0.25%** | 2500 bps (0.25%) | 50 | Most pairs, standard volatility |
| **1%** | 10000 bps (1%) | 200 | Exotic pairs, very high volatility |

### Tick Math Reference

V3 uses logarithmic price spacing in "ticks":

```
Tick to Price conversion:
  Price = 1.0001 ^ tick

Price to Tick conversion:
  tick = log(price) / log(1.0001)

Example:
  Tick 0 = Price 1.0000
  Tick 1 = Price 1.0001
  Tick 100 = Price 1.01005
  Tick 1000 = Price 1.1052
  Tick 10000 = Price 2.7183
```

### Price Range Strategies

Choose your range based on expected volatility and capital efficiency goals:

#### Full Range (Conservative)
- **Range**: -887200 to +887200 ticks (covers virtually all prices)
- **Capital efficiency**: 1x (same as V2)
- **When to use**: Maximum safety, no monitoring required
- **Fee tier recommendation**: 0.25% or 1% (volatility-dependent)

#### Tight Range (Aggressive)
- **Range**: Current price ±5% (~±50 ticks for 0.25% tier)
- **Capital efficiency**: 20x
- **When to use**: Stablecoins, confident direction, active monitoring
- **Fee tier recommendation**: 0.01% or 0.05%
- **Risk**: High impermanent loss if price moves beyond range

#### Medium Range (Balanced)
- **Range**: Current price ±20% (~±400 ticks for 0.25% tier)
- **Capital efficiency**: 3-5x
- **When to use**: Most pairs, reasonable volatility assumptions
- **Fee tier recommendation**: 0.25%
- **Risk**: Moderate impermanent loss outside range

#### Wide Range (Passive)
- **Range**: Current price ±50% (~±1500 ticks for 0.25% tier)
- **Capital efficiency**: 1.5-2x
- **When to use**: Volatile pairs, minimal monitoring
- **Fee tier recommendation**: 0.25% or 1%
- **Risk**: Lower IL, but capital inefficiency similar to V2

### Creating V3 Positions

**Deep link format**:
```
https://pancakeswap.finance/add/{tokenA}/{tokenB}/{feeAmount}?chain={chainKey}
```

**Parameter explanations**:
- `{tokenA}`: Contract address of first token (or "BNB" for native)
- `{tokenB}`: Contract address of second token
- `{feeAmount}`: Fee in basis points: 100, 500, 2500, or 10000
- `{chainKey}`: Chain identifier (see table below)

**Example: CAKE/WBNB 0.25% on BSC**
```
https://pancakeswap.finance/add/0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82/0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c/2500?chain=bsc
```

**Example: USDC/USDT 0.01% on Ethereum**
```
https://pancakeswap.finance/add/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48/0xdac17f958d2ee523a2206206994597c13d831ec7/100?chain=eth
```

### Fee Tier Selection Decision Tree

```
Is this a stablecoin pair (USDT/USDC, etc.)?
├─ Yes: Use 0.01% or 0.05% tier
│   └─ Will you actively rebalance? Use 0.01%
│   └─ Long-term hold? Use 0.05%
└─ No: Estimate volatility
    ├─ Low (established pair, <5% daily swings): Use 0.05% or 0.25%
    ├─ Medium (most pairs, 5-15% daily swings): Use 0.25%
    └─ High (new tokens, >15% daily swings): Use 1%
```

### V3 Fee Accumulation

```
Fee structure (varies by pair maturity):
  Base fee tier to LPs: Majority of the tier (e.g., 0.24% of 0.25%)
  Protocol fee: Small portion to PancakeSwap (e.g., 0.01% of 0.25%)

Fees are collected as the swapped tokens and must be manually claimed.
```

---

## StableSwap Positions

StableSwap is PancakeSwap's specialized pool type for stablecoin pairs, optimized for minimal slippage and tight pricing near 1:1.

### Characteristics

- **Optimized for stables**: Uses an amplification coefficient (A parameter) for better pricing
- **Tight effective range**: Prices gravitate around 1:1 (0.99-1.01 for typical stablecoins)
- **Lower slippage**: Superior pricing compared to V3's 0.01% tier for stable pairs
- **Fixed fees**: Protocol-determined, typically 0.04% or lower
- **ERC-20 LP tokens**: Fungible tokens (unlike V3 NFTs)
- **BSC, Ethereum, Arbitrum**: Available on these three chains
- **No impermanent loss**: IL is negligible for actual stablecoin pairs

### Amplification Coefficient (A parameter)

The A parameter controls how "tight" the curve is around 1:1:

- **Typical values**: A = 100-5000
- **Higher A**: Tighter curve, better pricing near peg, but more slippage outside peg
- **Lower A**: Wider curve, more slippage at peg, but more forgiving of off-peg scenarios
- **Example**: A=100 means 100:1 leverage at equilibrium for price drift

### Best Pairs for StableSwap

| Pair | Status | A Parameter |
|------|--------|---|
| USDT/USDC | Active | 100 |
| USDT/BUSD | Active | 100 |
| USDC/BUSD | Active | 100 |
| USDT/DAI | Active | 50-100 |
| USDC/DAI | Active | 50-100 |
| Other stables | Less common | Varies |

### When to Use StableSwap

- Trading stablecoin pairs with minimal slippage
- Providing stable liquidity with low IL risk
- Pairs where slight off-peg scenarios are expected but still considered "stable"
- Maximum yield on stable pairs relative to V3 0.01% tier

### Creating StableSwap Positions

**Deep link format**:
```
https://pancakeswap.finance/stable/add/{tokenA}/{tokenB}?chain={chainKey}
```

**Parameter explanations**:
- `{tokenA}`: Contract address of first token
- `{tokenB}`: Contract address of second token
- `{chainKey}`: Chain identifier (`bsc`, `eth`, or `arb`)

**Example: USDT/USDC StableSwap on BSC**
```
https://pancakeswap.finance/stable/add/0x55d398326f99059ff775485246999027b3197955/0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d?chain=bsc
```

### Fee Structure

| Aspect | StableSwap |
|--------|---|
| **Swap fee** | 0.04% typical (protocol-set per pool) |
| **LP share** | Typically 0.04% (varies) |
| **Burn/Treasury** | Minimal |

---

## Infinity (v4)

PancakeSwap Infinity introduces singleton architecture, hooks, and dynamic fee mechanisms.

### Key Features

- **Singleton contract**: Single contract for all liquidity (gas efficiency)
- **Hooks framework**: Extensible position logic (take fees, trigger rebalancing, etc.)
- **Dynamic fees**: Fees can adjust based on conditions (volatility, time, custom logic)
- **Concentrated liquidity (CL) and Bin pools**: Two pool types for different strategies
- **Automatic farming**: Adding liquidity to an Infinity pool automatically enrolls the position in farming — **no separate staking step required**. CAKE rewards are distributed every 8 hours via Merkle proofs.
- **Multi-chain**: Available on BSC and Base

### Farming UX Advantage

Unlike V2/V3 farms which require two steps (add liquidity → stake in MasterChef), Infinity farms combine both into a single step. When a user adds liquidity via the Infinity deep link, their position is automatically eligible for CAKE farming rewards without any additional transaction.

---

## Chain Availability Matrix

| Chain | V2 | V3 | Infinity | Infinity Stable | StableSwap |
|-------|----|----|----------|-----------------|------------|
| BSC | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ethereum | ✅ | ✅ | — | — | ✅ |
| Arbitrum | ✅ | ✅ | — | — | ✅ |
| Base | ✅ | ✅ | ✅ | — | — |
| zkSync | ✅ | ✅ | — | — | — |
| Linea | ✅ | ✅ | — | — | — |
| opBNB | ✅ | ✅ | — | — | — |
| Monad | ✅ | ✅ | — | — | — |

---

## Impermanent Loss Reference

Impermanent loss occurs when the price ratio of your LP tokens drifts from the entry point.

### IL Formula

```
IL(%) = (2 * sqrt(price_ratio)) / (1 + price_ratio) - 1) * 100

Where:
  price_ratio = final_price / entry_price
```

### IL Examples at Different Price Changes

| Price Change | IL (V2 full range) | IL (V3 ±10% range) | IL (StableSwap 1% change) |
|---|---|---|---|
| ±1% | -0.00% | -0.005% | ~0% |
| ±5% | -0.01% | -0.13% | ~0% |
| ±10% | -0.06% | -0.50% | ~0% |
| ±25% | -0.38% | -3.12% | ~0% |
| ±50% | -1.64% | out of range | N/A |
| ±100% | -5.72% | out of range | N/A |

### Managing Impermanent Loss

| Strategy | Mechanism |
|----------|---|
| **Wider V3 ranges** | Reduce IL but lower capital efficiency |
| **StableSwap** | Eliminates IL for pegged pairs |
| **Fee collection** | Offset IL with swap fees on active pairs |
| **Rebalancing** | Narrow V3 ranges, monitor actively |
| **Pair selection** | Choose pairs with lower expected volatility |

---

## Deep Link Parameter Reference

### V2 Deep Link

**Format**:
```
https://pancakeswap.finance/v2/add/{tokenA}/{tokenB}?chain={chainKey}
```

**Token Identifiers**:
- Regular token: Contract address (0x-prefixed, checksum address)
- Native currency: Use "BNB" for BSC, "ETH" for Ethereum, etc.

**Chain Keys**:
| Network | Chain Key |
|---------|---|
| BSC | `bsc` |
| Ethereum | `eth` |
| Arbitrum | `arb` |
| Base | `base` |
| zkSync | `zksync` |
| Linea | `linea` |
| opBNB | `opbnb` |
| Monad | `monad` |

**Example**:
```
https://pancakeswap.finance/v2/add/0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82/BNB?chain=bsc
```

### V3 Deep Link

**Format**:
```
https://pancakeswap.finance/add/{tokenA}/{tokenB}/{feeAmount}?chain={chainKey}
```

**Fee Amount Values**:
- 0.01% tier: `100`
- 0.05% tier: `500`
- 0.25% tier: `2500`
- 1% tier: `10000`

**Example**:
```
https://pancakeswap.finance/add/0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82/0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c/2500?chain=bsc
```

### StableSwap Deep Link

**Format**:
```
https://pancakeswap.finance/stable/add/{tokenA}/{tokenB}?chain=bsc
```

**Note**: StableSwap is available on BSC, Ethereum, and Arbitrum.

**Example**:
```
https://pancakeswap.finance/stable/add/0x55d398326f99059ff775485246999027b3197955/0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d?chain=bsc
```

### Optional Parameters (All Versions)

| Parameter | Purpose | Example |
|-----------|---------|---|
| `inputCurrency` | Pre-fill amount input | `&inputCurrency=0.5` |
| `outputCurrency` | Pre-fill output amount | `&outputCurrency=1000` |
| `pMin` | Slippage tolerance | `&pMin=0.95` |
| `pMax` | Price impact cap | `&pMax=1.05` |

---

## Position Selection Decision Tree

```
Start: "I want to provide liquidity on PancakeSwap"
│
├─> What blockchain?
│   ├─ BSC: Can use V2, V3, StableSwap, or Infinity
│   ├─ Base: Can use V2, V3, or Infinity
│   ├─ Ethereum/Arbitrum: Can use V2, V3, or StableSwap
│   └─ Other chain: V2 or V3
│
├─> Do you also want to farm CAKE rewards?
│   ├─ Yes, simplest UX (1 step): Use Infinity farm if available
│   │   (adding liquidity = auto-staked, no extra step)
│   ├─ Yes, willing to do 2 steps: Use V2/V3 farm
│   │   (add liquidity → then stake in MasterChef)
│   └─ No, just LP fees: Any pool type
│
├─> What token pair?
│   ├─ Stablecoin pair (USDT/USDC, etc.)?
│   │   ├─ Yes, BSC/Ethereum/Arbitrum: Consider StableSwap first (lowest slippage)
│   │   ├─ Yes, other chain: Use V3 0.01% tier
│   │   └─ No: Continue...
│   │
│   ├─ Established pair (CAKE/WBNB, etc.)?
│   │   ├─ Yes, want passive: Use V2 (BSC) or V3 full range
│   │   ├─ Yes, can monitor: Use V3 medium range (±20%)
│   │   └─ No (new/volatile token): Use V3 wide range (±50%) or 1% tier
│
├─> How much monitoring can you do?
│   ├─ None (passive): V2 or V3 full range
│   ├─ Occasional checks: V3 medium range (±20%)
│   └─ Active management: V3 tight range (±5%)
│
└─> [Select position type and fee tier]
```

---

## Position Management After Creation

### V2 Positions
- Monitor capital distribution over time
- Harvest rewards if applicable (CAKE emissions)
- Exit and reposition if pair becomes illiquid

### V3 Positions
- **Monitor price vs. range**: If price drifts, you'll stop earning fees
- **Rebalance**: Create new position, migrate liquidity
- **Collect fees**: Claim accumulated swap fees periodically
- **Exit strategy**: Burn position and retrieve tokens

### StableSwap Positions
- Monitor A parameter adjustments (rare)
- Harvest rewards if applicable
- Consider IL risk negligible for true stable pairs

---

## Fee Tier Reference Summary

| Tier | Pair Type | Volatility | Monitoring | Capital Efficiency |
|------|-----------|-----------|-----------|---|
| **0.01%** | Stablecoins | Very Low | Medium | Medium |
| **0.05%** | Low-vol pairs | Low | Low | Medium |
| **0.25%** | Most pairs | Medium | Low-Medium | High |
| **1%** | Volatile pairs | High | Low-Medium | Very High |
| **StableSwap** | Stablecoins (BSC, ETH, ARB) | Minimal | Minimal | Very High |
