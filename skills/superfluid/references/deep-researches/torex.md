---
title: TOREX (TWAP Oracle Exchange)
date: 2026-03-24
tags: [superfluid, torex, twap, dex, streaming, liquidity, uniswap, CFA, GDA, super-app]
sources:
  - https://app.superboring.xyz/torexpaper
  - https://github.com/superfluid-finance/averagex-contracts-cloned
  - https://github.com/superfluid-finance/torex-basic-liquidity-mover
  - https://github.com/superfluid-finance/liquidity-mover
  - https://audits.sherlock.xyz/contests/360
---

# TOREX (TWAP Oracle Exchange)

A reactive exchange mechanism that swaps one Super Token for another time-continuously at fair TWAP prices by combining Uniswap V3 TWAP oracles with Superfluid CFA streams and GDA distributions. Name: **T**(WAP) **OR**(acle) **EX**(change).

---

## Architecture Overview

Each TOREX contract is a [CFASuperApp](https://app.superboring.xyz/torexpaper) that accepts CFA streams of an **in-token** and distributes an **out-token** back to streamers via GDA. Two independent event loops drive the system:

| Event Loop | Trigger | Actor | Effect |
|---|---|---|---|
| Money Flow Event | CFA stream create/update/delete | Trader | Updates trader's share of the in-token pool and GDA distribution units |
| Liquidity Moving Event (LME) | `moveLiquidity()` call | Liquidity mover | Swaps accumulated in-tokens for out-tokens, distributes via GDA |

The loops are decoupled: money flows happen at trader discretion; LMEs happen when movers find it profitable.

---

## Contract Structure

| Contract | Role |
|---|---|
| `Torex.sol` (v1.1.0) | Main implementation, inherits `TorexCore` and `CFASuperApp` |
| `TorexCore.sol` | Abstract base with core swap logic, back-adjustment math, discount model |
| `TorexFactory.sol` | Deterministic deployment of TOREX instances with TWAP observers |
| `ITorex.sol` | Core interface for traders and movers |
| `ITorexController.sol` | Hook interface for fee/permission customization |
| `ILiquidityMover.sol` | Callback interface movers must implement |
| `ITwapObserver.sol` | TWAP oracle abstraction |
| `UniswapV3PoolTwapHoppableObserver.sol` | Multi-hop Uniswap V3 TWAP (up to 4 pool hops) |
| `ManualLiquidityMover.sol` | Reference mover with 5% max discount cap |

Source: [averagex-contracts-cloned](https://github.com/superfluid-finance/averagex-contracts-cloned)

---

## TWAP Observer

### Interface (`ITwapObserver`)

```solidity
function createCheckpoint() external;
function getDurationSinceLastCheckpoint() external view returns (uint256);
function getTwapSinceLastCheckpoint() external view returns (uint256);
```

### Uniswap V3 Implementation

- Stores its **own** checkpoint (`lastCheckPointAt`, `lastTickCumulative`) independently of Uniswap's observation array (which starts with 1 slot, max 65,536)
- Computes geometric mean TWAP: `P(t1,t2) = 1.0001^((a_t2 - a_t1) / (t2 - t1))`
- A new checkpoint is created at the end of each LME

### Hoppable Observer

`UniswapV3PoolTwapHoppableObserver` chains up to **4 Uniswap V3 pools** for token pairs that lack a direct pool. Each hop's TWAP is composed to derive the final price.

---

## Liquidity Moving Event (LME) Flow

Step-by-step execution when a liquidity mover calls `moveLiquidity()`:

1. TOREX reads the accumulated **in-token balance** (`inAmount`) in its temporary pool
2. Calls `getBenchmarkQuote(inAmount)` -- applies TWAP price then time-based discount
3. Transfers `inAmount` of in-tokens to the liquidity mover
4. Calls `moveLiquidityCallback()` on the mover -- mover must return at least `minOutAmount` of out-tokens to the TOREX
5. TOREX validates that `minOutAmount` was deposited; **reverts** if not
6. Distributes received out-tokens to all current traders via **GDA instant distribution**
7. Creates a new TWAP checkpoint

### Mover Callback Interface

```solidity
function moveLiquidityCallback(
    ISuperToken inToken,
    ISuperToken outToken,
    uint256 inAmount,
    uint256 minOutAmount,
    bytes calldata moverData
) external returns (bool);
```

The mover receives in-tokens, must execute the swap (on any venue), and deposit at least `minOutAmount` of out-tokens back. The `moverData` parameter allows passing arbitrary routing hints.

---

## Discount Model

A shifted reciprocal function ensures the TOREX **never stalls** -- as time passes without an LME, the discount grows, eventually making any swap profitable:

```
f(v, t) = v * F / (F + t)
```

| Symbol | Meaning |
|---|---|
| `v` | Full TWAP value of accumulated in-tokens |
| `t` | Seconds since last LME |
| `F` | Discount factor (computed from intuitive params) |

### Intuitive Parameterization

`F = tau * (1 - epsilon) / epsilon`

| Parameter | Meaning | Example |
|---|---|---|
| `tau` | Reference time in seconds | 3600 (1 hour) |
| `epsilon` | Discount at time `tau` | 0.10 (10%) |

With `tau=3600, epsilon=0.10`: at 1 hour since last LME, 90% of TWAP value remains. At `t=0`, zero discount. As `t -> infinity`, discount approaches 100%.

### TWAP Scaler

`getBenchmarkQuote` also applies a configurable `_twapScaler` multiplier to the raw TWAP value before applying the discount. This allows systematic adjustment of the benchmark price.

---

## Back Adjustments

Because money flow events and LMEs are independent, traders who join or leave between LMEs need fair treatment to prevent gaming:

### Back Charge (new streamer)

When a trader starts streaming between LMEs, they would receive a share of the next distribution without having contributed proportionally to the accumulated in-token pool. The TOREX **charges them back** the missing contribution since the last LME.

- Prevents free-riding on in-tokens about to be swapped
- Charged at flow creation time

### Back Refund (departing streamer)

When a trader stops streaming between LMEs, they contributed in-tokens since the last LME but will not receive the next distribution. The TOREX **refunds** their contribution since the last LME.

- Prevents loss from contributing without receiving distribution
- Refunded at flow deletion time

This design is **computationally scalable**: LMEs process all traders simultaneously via GDA; back adjustments handle individual edge cases at flow event time.

---

## Controller / Hooks

The optional `ITorexController` provides hooks at both money flow events and LMEs:

```solidity
interface ITorexController {
    function getTypeId() external view returns (bytes32);

    function onInFlowChanged(
        address flowUpdater,
        int96 prevFlowRate,
        int96 preFeeFlowRate,
        uint256 lastUpdated,
        int96 newFlowRate,
        uint256 now,
        bytes calldata userData
    ) external returns (int96 newFeeFlowRate);

    function onLiquidityMoved(LiquidityMoveResult calldata result)
        external returns (bool);
}
```

### Capabilities

| Use Case | Mechanism |
|---|---|
| Fee extraction | `onInFlowChanged` returns `newFeeFlowRate`; fee portion streams to a fee GDA pool |
| Permission control | Controller can revert on disallowed traders or movers |
| Staking integration | Controller can require staking as condition for streaming |
| Front-end fees | Different fee rates based on `userData` identifying the front-end |

### Fee Safety

Production TOREX contracts have an **immutable max-fee setting** that caps the fee flow rate. This prevents a rogue controller from extracting excessive fees. The controller is also the admin of the TOREX's fee distribution pool, controlling how collected fees are allocated.

SuperBoring.sol is the primary ITorexController implementation — see `superboring.md` for product details (BORING token, staking, emissions, deployments).

---

## MEV Properties

### Trader Protection

- Contributions are paid **over time** via continuous streams, not lump-sum
- Swaps happen on pooled contributions at **TWAP prices**, not spot
- TWAP manipulation within the same block is **impossible by definition** (TWAP requires time)
- Multi-block manipulation requires capital at risk proportional to the manipulation duration

### Liquidity Mover Exposure

- LME swaps are **instant** and visible in the mempool -- vulnerable to frontrunning
- Core TOREX does **not** protect movers natively
- Controller hooks can implement access control (e.g., prior commitment schemes, whitelisted movers)

---

## Liquidity Mover Implementations

### Basic: SwapRouter02LiquidityMover

[torex-basic-liquidity-mover](https://github.com/superfluid-finance/torex-basic-liquidity-mover) -- a straightforward mover using Uniswap SwapRouter02.

| Feature | Detail |
|---|---|
| DEX | Uniswap V3 via SwapRouter02 |
| Routing | Custom swap paths or auto-detection from UniswapV3PoolTwapObserver |
| Token handling | Unwraps Super Tokens to ERC-20, swaps underlying, wraps result |
| Automation | Gelato-based time intervals |

**Deployment addresses:**

| Chain | Address |
|---|---|
| Base | `0x1e77916e3fed4a24dc4e37968587e2b71d3a9c06` |
| Optimism | `0xb32d94537591a899b13f7923a0f2cd0200a1ca84` |
| Celo | `0x8B25D8a48d1FB17C9aF7765c797CA38B78614729` |
| Arbitrum | `0x5D0acD0864Ad07ba4E1E0474AE69Da87482e14A9` |

### Advanced: TwinTorexLiquidityMover

[liquidity-mover](https://github.com/superfluid-finance/liquidity-mover) -- optimized mover that exploits inverse TOREX pairs.

#### Twin TOREX Concept

For a token pair (e.g., ETHx/USDCx), two inverse TOREX contracts exist:
- TOREX A: ETHx -> USDCx
- TOREX B: USDCx -> ETHx

The TwinTorexLiquidityMover **nets** the two sides:

1. Identifies which TOREX is "Rich" (more accumulated liquidity) and which is "Poor"
2. Moves liquidity from Rich TOREX first -- its out-tokens feed the Poor TOREX
3. Calculates the **shortfall** (Rich needs minus Poor provides)
4. Only executes an **external DEX swap for the shortfall**

This dramatically reduces capital requirements and DEX interaction costs.

#### Modular Swapper Architecture

All swappers inherit `BaseTokenSwapper` and handle SuperToken unwrap/swap/wrap:

| Swapper | DEX | Notes |
|---|---|---|
| `OneInchTokenSwapper` | 1inch aggregation | Optimal cross-DEX routing |
| `UniswapV3TokenSwapper` | Uniswap V3 | Direct pool routing |
| `UniswapV4TokenSwapper` | Uniswap V4 | Latest Uniswap version |
| `BalancerV3TokenSwapper` | Balancer V3 | Alternative DEX |

**Automation:** Trigger.dev (cron-based scheduling) with USD-denominated profitability checks -- only executes when profit exceeds gas cost threshold.

**Deployment addresses:**

| Chain | Contract | Address |
|---|---|---|
| Base | TwinTorexLM | `0x4D5E390992f88eD613387b929c1dbB1804a55fBA` |
| Base | 1InchSwapper | `0x98358c0c599CD5590a8D87eA97F5664d63dE7206` |
| Arbitrum | TwinTorexLM | `0xF62bf574aAaB3C6AC9d6FF6a2C765668e2e2a9B4` |
| Arbitrum | 1InchSwapper | `0x16d6e47Ae89c8C5BBF88De76B33f180C5b689F6e` |

---

## Factory and Deployment

`TorexFactory.sol` creates TOREX instances deterministically. Each deployment specifies:

| Parameter | Purpose |
|---|---|
| `inToken` | The Super Token traders stream in |
| `outToken` | The Super Token traders receive |
| `observer` | TWAP observer address (Uniswap V3 pool or hoppable chain) |
| `discountFactor` | `F` value for the shifted reciprocal discount model |
| `twapScaler` | Multiplier applied to raw TWAP before discounting |
| `controller` | Optional ITorexController address for hooks |
| `maxFeeRate` | Immutable cap on fee extraction (basis points) |

The factory emits deployment events and allows enumeration of all TOREX instances created through it.

---

## Security

The TOREX contracts were [audited via Sherlock](https://audits.sherlock.xyz/contests/360) as part of the averageX / SuperBoring audit contest.

Key trust assumptions:
- **TWAP oracle integrity**: relies on Uniswap V3 pool observations being non-manipulable over the checkpoint duration
- **Controller trust**: controller can set fees up to the immutable max-fee cap; cannot exceed it
- **Liquidity mover atomicity**: the `moveLiquidityCallback` pattern enforces atomic settlement -- mover must deposit out-tokens in the same transaction or the entire LME reverts

---

## Repositories

| Repository | Contents |
|---|---|
| [averagex-contracts-cloned](https://github.com/superfluid-finance/averagex-contracts-cloned) | Core TOREX + SuperBoring contracts (Solidity, MIT) |
| [torex-basic-liquidity-mover](https://github.com/superfluid-finance/torex-basic-liquidity-mover) | Basic Uniswap V3 liquidity mover + Gelato automation |
| [liquidity-mover](https://github.com/superfluid-finance/liquidity-mover) | Twin TOREX mover + multi-DEX swappers + Trigger.dev automation |
