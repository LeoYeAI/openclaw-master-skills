---
title: How GDA Achieves Infinite Scalability
date: 2026-03-23
tags: [superfluid, GDA, scalability, PDPool, streaming, proportional-distribution, pool]
sources:
  - https://semantic.money/assets/semantic-money-yellowpaper1.pdf
  - https://github.com/superfluid-finance/protocol-monorepo/tree/dev/packages/spec-haskell
  - https://github.com/superfluid-finance/protocol-monorepo/tree/dev/packages/ethereum-contracts/contracts/agreements/gdav1
---

# How GDA Achieves Infinite Scalability

The General Distribution Agreement (GDA) is Superfluid's mechanism for streaming tokens from one sender to an unlimited number of receivers at constant gas cost. This document explains exactly how that works at the data-structure, formula, and rounding level, drawing from the formal Haskell specification.

## The Problem

With the Constant Flow Agreement (CFA), every 1:1 stream is O(1) — creating or updating a single flow between Alice and Bob is a single state update. But distributing to N receivers requires N separate CFA streams: N transactions to create, N transactions to update, N transactions to delete.

For real-world use cases this breaks down fast:

- **Payroll**: A company paying 500 employees needs 500 stream-creation transactions.
- **Revenue sharing**: Splitting protocol fees among 10,000 stakers means 10,000 CFA operations per rate change.
- **Reward distribution**: Airdropping to all token holders means one transaction per holder.

Every time the distribution rate changes, every stream must be individually updated. The cost scales linearly with member count. This is O(N) for setup and O(N) for updates — unusable at scale.

GDA solves this completely. A single `distributeFlow` call streams to unlimited pool members at O(1) gas. A single `distribute` call splits a lump sum among unlimited members at O(1) gas. Member count does not affect gas cost of distributions.

## The Key Insight: Pool-Level State

*Haskell snippets below are simplified for readability. The actual spec uses prefixed field names (`bp_`, `pdidx_`, `pdpm_`) and an `mt` type parameter for generic monetary types. See the [spec source](https://github.com/superfluid-finance/protocol-monorepo/tree/dev/packages/spec-haskell) for exact definitions.*

The trick: instead of storing a flow rate per member, store a single **flow-rate-per-unit** at the pool level. Each member holds some number of "units" (their proportional share). Their balance is computed lazily from the pool's aggregate state.

### Data Structures

The pool index stores two things — total units and a wrapped particle (a BasicParticle that tracks per-unit value):

```haskell
-- Pool-level index: total units + per-unit accounting particle
data PDPoolIndex = PDPoolIndex
  { total_units :: Units        -- sum of all member units
  , wrapped     :: BasicParticle -- per-unit settled_value, flow_rate, settled_at
  }
```

Each member stores their unit count, a settled value (accumulated distributions already accounted for), and a snapshot of the pool's wrapped particle at the time of last sync:

```haskell
-- Per-member state
data PDPoolMember = PDPoolMember
  { owned_units     :: Units          -- this member's share weight
  , settled_value   :: Value          -- accumulated value already synced
  , synced_particle :: BasicParticle  -- pool's wrapped particle at last sync
  }
```

The underlying `BasicParticle` is the same structure used everywhere in Superfluid — a linear function of time:

```haskell
-- The fundamental accounting primitive
data BasicParticle = BasicParticle
  { settled_at    :: Time   -- last settlement timestamp
  , settled_value :: Value  -- value accumulated up to settled_at
  , flow_rate     :: Value  -- per-second rate of change
  }

-- Real-time balance: linear interpolation from last settlement
rtb particle t = settled_value particle
               + flow_rate particle * (t - settled_at particle)
```

### The Member Balance Formula

A member's real-time balance is derived entirely from the pool's current state and the member's last-synced state:

```
member_balance(t) = settled_value
                  + (pool_rtb(t) - synced_rtb_at_sync) * owned_units
```

In Haskell:

```haskell
-- Member balance = settled + (current_per_unit - synced_per_unit) * units
rtb (poolIndex, member) t =
    settled_value member
  + (rtb (wrapped poolIndex) t
     - rtb (synced_particle member) (settledAt (synced_particle member)))
    * owned_units member
```

The key insight is the delta: `pool_rtb(t) - synced_rtb_at_sync`. This captures **all** distributions (both instant and streaming) that occurred since the member last interacted with the pool. It does not matter whether there were 0 or 10,000 distribution events in between — the delta covers them all in one subtraction.

This is why the pool is O(1) for distributions: the pool's wrapped particle accumulates per-unit value over time, and each member's balance is a function of that accumulated value times their units.

## How Each Operation Works

### `distributeFlow(flowRate)` — Start or Update a Stream into the Pool

Sets the pool's per-unit flow rate. One state update, all members affected lazily.

```haskell
-- flow1: set the pool's per-unit flow rate
-- Returns (updated pool, actual per-unit rate)
flow1 requestedRate pool@(PDPoolIndex tu particle) =
  if tu == 0
    then (pool { wrapped = setFlowRate 0 particle }, 0)
    else let perUnitRate = requestedRate `div` tu  -- integer division
             particle'   = setFlowRate perUnitRate particle
         in  (pool { wrapped = particle' }, perUnitRate)
```

The actual distributed rate is `perUnitRate * total_units`, which may be less than `requestedRate` due to integer division. The remainder becomes the **adjustment flow** directed to the pool admin (see Rounding Model below).

**Gas cost**: O(1). Updates one `BasicParticle` and one `total_units` field. No per-member writes.

### `distribute(amount)` — Instant Lump-Sum Distribution

Adds a per-unit amount to the pool's settled value. All members receive their share lazily.

```haskell
-- shift1: add per-unit value to the pool's settled_value
-- Returns (updated pool, actual per-unit amount)
shift1 amount pool@(PDPoolIndex tu particle) =
  if tu == 0
    then (pool, 0)
    else let perUnit     = amount `div` tu  -- integer division
             particle'   = addSettled perUnit particle
         in  (pool { wrapped = particle' }, perUnit)
```

The actual distributed amount is `perUnit * total_units`. The remainder (the fractional dust) simply stays with the distributor — it is never debited.

**Gas cost**: O(1). Single settled_value update on the pool's particle.

### `updateMemberUnits(member, newUnits)` — Change a Member's Share

This is the only operation that touches per-member state. It must settle the member first (capture accrued value), then update units and adjust the pool's totals.

```haskell
-- pdpUpdateMember2: settle member, update units, handle rounding
pdpUpdateMember2 newUnits t (senderAcct, (poolIndex, member)) =
  let
    -- Step 1: Settle the member (capture accrued distributions)
    (PDPoolIndex tu particle, member') = settle t (poolIndex, member)
    oldUnits = owned_units member'

    -- Step 2: Compute new total units
    newTotalUnits = tu + newUnits - oldUnits

    -- Step 3: Adjust pool flow rate for new total (rounding correction)
    (particle', senderAcct') = align2 tu newTotalUnits (particle, settle t senderAcct)

    -- Step 4: Update pool and member
    poolIndex' = PDPoolIndex newTotalUnits particle'
    member''   = member' { owned_units = newUnits, synced_particle = particle' }
  in
    (senderAcct', (poolIndex', member''))
```

**Gas cost**: O(1) per member updated. Does not touch other members' state.

### `connectPool` — Subscribe to Real-Time Balance

A member "connects" to a pool so that their `balanceOf` call automatically includes the pool's real-time balance. This registers the pool in the member's connected-pools list.

**Gas cost**: O(1). Adds an entry to the member's connection registry.

**Limit**: Maximum 256 connected pools per account per token.

### `claimAll` — Claim Accumulated Distributions

For disconnected members, distributions accumulate in the pool's accounting but do not reflect in `balanceOf`. Calling `claimAll` settles the member and transfers the accrued amount.

**Gas cost**: O(1). Settles one member, transfers one amount.

## The Rounding Model (Right-Side-Biased Error Terms)

Integer division on the EVM means `flowRate / totalUnits` truncates. The formal spec handles this with a precise pattern: the **right side** (pool) computes with integer division, and the **left side** (sender) is debited only the actual amount, not the requested amount.

### How shift2/flow2 Preserve Conservation of Value

```haskell
-- flow2: right-side-biased error term for streaming
flow2 requestedRate (sender, pool) =
  let (pool', actualPerUnit) = flow1 requestedRate pool  -- pool gets truncated rate
      actualTotal            = actualPerUnit * total_units pool'
      (sender', _)           = flow1 (-actualTotal) sender  -- sender debited ACTUAL, not requested
  in  (sender', pool')

-- shift2: right-side-biased error term for instant distribution
shift2 amount (sender, pool) =
  let (pool', actualPerUnit) = shift1 amount pool     -- pool gets truncated amount
      actualTotal            = actualPerUnit * total_units pool'
      (sender', _)           = shift1 (-actualTotal) sender  -- sender debited ACTUAL, not requested
  in  (sender', pool')
```

The pattern is the same for both operations: compute on the pool side with integer division, then debit the sender only for what was actually distributed. The difference between requested and actual is the remainder.

### Where the Remainder Goes

| Operation | Remainder | Destination |
|---|---|---|
| `distributeFlow` | `requestedRate - (perUnitRate * totalUnits)` | Adjustment flow to pool admin |
| `distribute` | `amount - (perUnit * totalUnits)` | Stays with distributor (never debited) |
| `updateMemberUnits` (via `align2`) | Rounding error from `rate * oldUnits / newUnits` | Adjustment flow to pool admin |

### The Adjustment Flow

For `distributeFlow`, the adjustment flow is the stream of tokens that accounts for the rounding remainder. It flows continuously to the pool admin. If the requested flow rate is 100 tokens/sec and totalUnits is 7:

- `perUnitRate = 100 / 7 = 14` (integer division)
- `actualTotal = 14 * 7 = 98` tokens/sec
- `adjustmentFlow = 100 - 98 = 2` tokens/sec to admin

The admin always receives the dust. This is by design — the pool admin is the party that controls the pool's configuration.

### Common Gotcha: flowRate < totalUnits

If the requested flow rate is less than totalUnits, integer division truncates perUnitRate to 0. The **entire** flow becomes the adjustment flow — all tokens stream to the admin, members receive nothing.

Example: `flowRate = 5`, `totalUnits = 100` -> `perUnitRate = 5 / 100 = 0` -> admin gets 5 tokens/sec, members get 0.

To avoid this, ensure `flowRate >= totalUnits`, or use large unit values to minimize the relative remainder.

### The align2 Function: Rounding on Unit Changes

When total units change (via `updateMemberUnits`), the pool's per-unit flow rate must be adjusted. The `align2` function handles this:

```haskell
-- align2: adjust flow rates when total units change
align2 oldTotalUnits newTotalUnits (particle, senderAcct) =
  let currentRate = flowRate particle
      -- Recompute per-unit rate for new total, with integer division
      (newRate, errorRate) =
        if newTotalUnits == 0
          then (0, currentRate * oldTotalUnits)  -- all flow -> admin
          else divWithRemainder (currentRate * oldTotalUnits) newTotalUnits
      -- Update pool particle with new per-unit rate
      particle'   = setFlowRate newRate particle
      -- Error term added to sender's (admin's) flow rate
      senderAcct' = adjustFlowRate (errorRate + flowRate senderAcct) senderAcct
  in  (particle', senderAcct')
```

The computation is: `newPerUnitRate = (currentPerUnitRate * oldTotalUnits) / newTotalUnits`. This preserves the total flow as closely as possible, with the remainder going to the admin.

**Important**: `updateMemberUnits` does NOT re-derive the per-unit rate from the distributor's originally requested rate. It only adjusts based on the current per-unit rate and the unit change. After changing units, the distributor should re-call `distributeFlow` with their desired rate to reset the rounding to be optimal.

## Universal Index Inside GDA

GDA does not exist in isolation. It is embedded in Superfluid's **Universal Index** — the same accounting framework that handles all 1:1 flows. The architecture composes two layers:

1. **Sender -> Pool**: A standard 1:1 flow in the universal index. The pool is just another account. The sender's particle tracks the outflow, the pool's particle tracks the inflow. This is the same mechanism as CFA.

2. **Pool -> Members**: The proportional distribution index (PDPoolIndex). The pool splits its inflow among members by units.

```
Sender Account                Pool Account                  Members
+----------------+   flow2   +--------------------+  lazy  +---------+
| BasicParticle  | --------> | PDPoolIndex        | -----> | Member1 |
| (universal     |           |   total_units      |        | Member2 |
|  index)        |           |   BasicParticle    |        | Member3 |
+----------------+           |   (per-unit)       |        | ...     |
                              +--------------------+        +---------+
```

The pool contract is a first-class account in the token's universal index. It receives flows from distributors (potentially multiple) just like any account receives CFA streams. The per-member splitting is a separate, inner layer that is entirely lazy.

This composability is why GDA replaced both the old Instant Distribution Agreement (IDA) and CFA-for-distributions in a single agreement. IDA could only do one-shot distributions. CFA could stream but only 1:1. GDA does both — instant and streaming distributions to unlimited members — because it layers proportional distribution on top of the universal index.

Multiple distributors can stream into the same pool. Each distributor has their own flow in the universal index; the pool aggregates all inflows and splits the total among members proportionally. The pool's per-unit flow rate reflects the sum of all distributor flows (divided by total units).

## Settle-on-Write Pattern

Members do not receive per-block updates. No cron job writes to storage every second. The system uses a **settle-on-write** pattern derived from functional reactive programming (FRP):

### Between Events: Pure Formula

Between any two state-changing events, every balance in the system is a pure function of time:

```
balance(t) = settled_value + flow_rate * (t - settled_at)
```

This applies at every level — sender accounts, pool particles, member balances. The `balanceOf` function evaluates this formula at the current block timestamp. No storage reads beyond the formula parameters.

### At Event Time: Settle, Then Update

When a state-changing event occurs (unit change, claim, disconnect, new distribution), the system:

1. **Settles** — evaluates the formula at the current timestamp, collapses the accrued value into `settled_value`, resets `settled_at` to now.
2. **Updates** — applies the new parameters (new units, new flow rate, etc.).
3. **New formula takes over** — subsequent reads use the updated parameters.

For members specifically, settlement means:

```haskell
-- Settle a member: capture accrued distributions, sync to current pool state
settleMember t (poolIndex, member) =
  let delta = rtb (wrapped poolIndex) t
            - rtb (synced_particle member) (settledAt (synced_particle member))
      newSettled = settled_value member + delta * owned_units member
  in  member { settled_value   = newSettled
             , synced_particle = wrapped poolIndex  -- sync to current pool state
             }
```

The delta `(current_per_unit_value - synced_per_unit_value)` captures **all** distributions since last sync in a single subtraction. If 1,000 `distribute` calls and 50 `distributeFlow` rate changes happened since the member's last interaction, the delta covers them all. This is the core of the O(1) scalability.

### FRP Connection

The yellowpaper calls this the "untilB" reactivity pattern from Conal Elliott's FRP framework. A behavior (balance as a function of time) holds until an event occurs, at which point it is replaced by a new behavior. The system materializes (settles) the old behavior and installs the new one. Between events, the behavior is a pure, closed-form function — no iteration, no accumulation loops.

## Connected vs. Disconnected Members

Pool members can be in one of two states, with different tradeoffs:

### Connected Members

- `balanceOf` automatically includes the member's real-time pool balance.
- Good for UX: dashboards, wallets, and apps show the streaming balance in real time.
- Cost: `balanceOf` iterates over all connected pools for that account/token pair. If an account is connected to K pools, `balanceOf` is O(K).
- **Maximum 256 connected pools per account per token**. This is the only scaling limit in the entire GDA system.

### Disconnected Members

- Distributions accumulate in the pool's accounting but do NOT reflect in `balanceOf`.
- Must call `claimAll` to receive accumulated distributions.
- Good for gas-sensitive use cases: no `balanceOf` overhead from pool iteration.
- Useful when the member is a contract that cannot handle real-time balance fluctuations (e.g., a vault that expects discrete deposits).
- Default state for new members — they must explicitly connect or be auto-connected.

### Autoconnect Slots

Pool admins can configure up to **4 autoconnect slots**. When a member's units are updated and they have not explicitly connected/disconnected, the pool can auto-connect them using one of these slots. This is a convenience feature for pools where all members should be connected by default, but the limit of 4 prevents abuse (auto-connecting on behalf of a member costs the member a connected-pool slot out of their 256 limit).

### Choosing Connected vs. Disconnected

| Factor | Connected | Disconnected |
|---|---|---|
| Real-time balance in `balanceOf` | Yes | No |
| Gas cost of `balanceOf` | O(connected pools) | Unaffected |
| Requires `claimAll` | No | Yes |
| Pool slot usage | 1 of 256 per account/token | None |
| Best for | User-facing wallets, dashboards | Contracts, gas-sensitive flows |

## Scalability Summary

| Operation | Gas Cost | Members Affected | Notes |
|---|---|---|---|
| `distributeFlow` | O(1) | All (lazily) | Single pool-level state update |
| `distribute` | O(1) | All (lazily) | Single pool-level state update |
| `updateMemberUnits` | O(1) per call | 1 member | Settles member, updates pool total |
| `connectPool` | O(1) | 1 member | Registers for real-time balance |
| `claimAll` | O(1) | 1 member | Settles disconnected member |
| `balanceOf` (member) | O(connected pools) | 1 read | Up to 256 pool iterations |

All distribution operations — both instant and streaming — are constant-time regardless of member count. A pool with 10 members and a pool with 10 million members cost the same gas for `distributeFlow` and `distribute`.

The only operation that scales with anything is `balanceOf`, which is O(K) where K is the number of connected pools (max 256). This is a read-side cost borne by the member, not the distributor.

## Why This Matters for Builders

### Use Cases Unlocked

- **Payroll to 10,000 employees**: 1 `distributeFlow` call, not 10,000 CFA stream creations. Change the rate for everyone with 1 transaction.
- **Reward distribution**: `distribute` splits any amount proportionally in 1 tx. Works for airdrops, yield distribution, cashback.
- **Revenue sharing**: Stream protocol revenue to a pool. Members (stakers, LPs, token holders) get proportional real-time share. Adding/removing members does not require touching the distribution flow.
- **Salary adjustments**: Change one member's units without affecting others. Only the changed member's state is written. Then optionally re-call `distributeFlow` to reset rounding.

### Practical Advice

**Rounding awareness**: Always account for the adjustment flow going to the pool admin. The admin receives the integer division remainder as a continuous stream. Design your admin address accordingly (it should be able to receive and handle these tokens).

**Minimize rounding**: Use large unit values relative to flow rates. If every member has 1 unit and the flow rate is 100 wei/sec with 7 members, the admin gets 2 wei/sec as adjustment. If units are 1000x larger and the flow rate is scaled to match, the absolute remainder is the same but the relative waste is smaller.

**flowRate < totalUnits**: If the per-second flow rate is smaller than the total units, per-unit rate truncates to 0 and the entire flow goes to admin. For very small flow rates or very large member counts, verify that `flowRate / totalUnits > 0`.

**Re-call distributeFlow after unit changes**: `updateMemberUnits` adjusts the per-unit rate based on the old rate and the unit change via `align2`. It does not re-derive from the distributor's original intended rate. After significant unit changes, the distributor should re-call `distributeFlow` with their desired rate to reset the rounding to be optimal.

**Connected vs. disconnected**: Use connected for user-facing applications where real-time balances matter (dashboards, wallets). Use disconnected for contracts, gas-sensitive flows, or accounts that interact with many pools (to conserve the 256-pool limit).

**The 256-pool limit**: This is per account per token. An account can be connected to 256 pools for USDCx and 256 pools for ETHx independently. If an account needs to receive from more than 256 pools of the same token, some must be disconnected (requiring `claimAll` to access funds).

**Multiple distributors**: Multiple accounts can stream into the same pool. The pool aggregates all inflows. This is useful for multi-source revenue sharing (e.g., a pool that receives fees from several DeFi protocols and splits them among stakers).

## Links

- **Yellowpaper PDF**: https://semantic.money/assets/semantic-money-yellowpaper1.pdf
- **semantic.money**: https://semantic.money
- **Haskell spec source**: https://github.com/superfluid-finance/protocol-monorepo/tree/dev/packages/spec-haskell
- **GDA Solidity source**: https://github.com/superfluid-finance/protocol-monorepo/tree/dev/packages/ethereum-contracts/contracts/agreements/gdav1
- See also: `references/deep-researches/semantic-money-yellowpaper.md` for the broader formal foundations (payment system model, conservation of value, agreement framework, FRP connection)
