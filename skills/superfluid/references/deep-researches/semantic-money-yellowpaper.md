---
title: Semantic Money — Formal Foundations
date: 2026-03-23
tags: [superfluid, formal-spec, yellowpaper, haskell, payment-primitives, BasicParticle, agreement-framework]
sources:
  - https://semantic.money/assets/semantic-money-yellowpaper1.pdf
  - https://github.com/superfluid-finance/protocol-monorepo/tree/dev/packages/spec-haskell
  - https://semantic.money
---

# Semantic Money — Formal Foundations

The formal theory underlying the Superfluid Protocol. Two artifacts define it:
a yellowpaper and a Haskell reference implementation that together specify how
continuous real-time payments work.

## Introduction

[semantic.money](https://semantic.money) is the home of the Semantic Money
research and specification project. It hosts two core artifacts:

1. **Yellowpaper**: "Denotational Semantics of General Payment Primitives, and
   Its Payment System" by Miao ZhiCheng (co-founder / CTO of Superfluid),
   v1.0 dated 2022-10-31. Available at
   [semantic-money-yellowpaper1.pdf](https://semantic.money/assets/semantic-money-yellowpaper1.pdf).

2. **Haskell reference implementation**: The spec-haskell package in the
   Superfluid protocol monorepo. This is not a translation of a spec written
   elsewhere — the Haskell code **is** the specification. Types, laws, and
   property tests constitute the formal definition of Superfluid's on-chain
   behavior.

The yellowpaper gives the mathematical foundations (denotational semantics,
conservation proofs, FRP connection). The Haskell code gives the executable
specification that the Solidity contracts implement. Together they answer:
"What does it mean for money to flow continuously, and how do you implement
that on a blockchain?"

## Payment System Model

The yellowpaper defines a **payment system** as four components:

- **Money distribution** — how monetary value is assigned to parties
- **Payment primitives** — operations that update money distribution
- **Execution environment** — the runtime that sequences operations
- **Money medium (token model)** — the unit of account

Traditional money distribution is **discrete**: a bearer holds a fixed value,
updated only by explicit transfers. The key innovation of semantic money is
adding **context** to the distribution:

```
γ = t × ctx
```

where `t` is time and `ctx` is shared state. This allows monetary value to
**vary continuously over time** — a balance is no longer a stored number but a
function evaluated at the current moment.

| Formal Concept | On-Chain Equivalent |
|---|---|
| Money distribution | SuperToken `realtimeBalanceOf` across all accounts |
| Payment primitive | Agreement operation (CFA, GDA) |
| Execution environment | Superfluid Host |
| Money medium (token model) | Super Token |
| Context γ | Block timestamp + agreement contract state |

## Conservation of Value

The fundamental law: **the sum of all monetary values across all parties
equals zero at all times**. This is the conservation invariant.

The yellowpaper proves conservation via restricted money distributions:

- **Axiom A**: Each payment primitive individually preserves zero-sum. That
  is, the sum of value changes across all affected parties is zero.
- **Axiom B**: The money distribution is defined solely as the composition of
  payment primitives — no value is created or destroyed outside primitives.
- **Proof**: Payment primitives form a monoid under composition. Conservation
  follows by monoid homomorphism and induction over the sequence of applied
  operations.

Practical consequences of monoidality:

- **Constant gas cost**: Applying an operation touches only the parties
  involved, regardless of how many prior operations have occurred. Updates are
  incremental and associative — no replay of history needed.
- **Auditable total supply**: The sum of all balances is zero by construction.
  No iteration over accounts is required to verify this.
- **Parallel composition**: Independent payment primitives can be modeled and
  reasoned about in isolation, then composed. This underpins the agreement
  framework's modularity.

## Implemented Payment Primitives

*Haskell snippets below are simplified for readability. The actual spec uses prefixed field names (`bp_`, `pdidx_`, `pdpm_`) and an `mt` type parameter for generic monetary types. See the [spec source](https://github.com/superfluid-finance/protocol-monorepo/tree/dev/packages/spec-haskell) for exact definitions.*

### Transfer (Instant)

A fixed amount `x` moved from sender `ua` to receiver `ub` at a single point
in time.

Denotational semantics:

```
⟦transfer ua ub x⟧ = λu → λt →
    -x   if u = ua
     x   if u = ub
     0   otherwise
```

On-chain mapping: ERC-20 `transfer` / Instant Transfer Agreement (ITA).

### Constant Flow

A continuous stream at rate `r` starting at time `t'`, from sender `ua` to
receiver `ub`.

Denotational semantics:

```
⟦flow ua ub r t'⟧ = λu → λt →
    -r · (t - t')   if u = ua
     r · (t - t')   if u = ub
     0              otherwise
```

On-chain mapping: CFA `createFlow` / `updateFlow` / `deleteFlow`.

### BasicParticle — The Building Block

The Haskell spec's fundamental type that captures both transfers and flows in
a single structure:

```haskell
-- The fundamental building block for all real-time balances.
-- On-chain, this is how SuperToken computes realtimeBalanceOfNow.
data BasicParticle = BasicParticle
  { settled_at    :: Timestamp  -- last time state was materialized (t')
  , settled_value :: Value      -- accumulated value at settled_at (s)
  , flow_rate     :: Value      -- continuous rate of change (r); same type as value
  }

-- Real-time balance at any time t:
--   rtb(t) = settled_value + flow_rate * (t - settled_at)
--
-- This is THE formula. It appears everywhere in Superfluid —
-- in the Haskell spec, the Solidity contracts, and the subgraph.
balanceAt :: BasicParticle -> Timestamp -> Value
balanceAt particle t =
  settled_value particle + flow_rate particle * (t - settled_at particle)
```

A transfer sets `settled_value`; a flow sets `flow_rate`. The linear
interpolation handles continuous time natively — no per-block updates.

BasicParticle is a **Monoid**. Two particles can be combined by settling both
to the later timestamp, then adding their components:

```haskell
-- Combining two particles: settle both to the later time, then sum.
-- This is what makes agreement composition work — each agreement
-- contributes a BasicParticle, and they combine via mappend.
combine :: BasicParticle -> BasicParticle -> BasicParticle
combine a b = BasicParticle
  { settled_at    = t'
  , settled_value = balanceAt a t' + balanceAt b t'
  , flow_rate     = flow_rate a + flow_rate b
  }
  where t' = max (settled_at a) (settled_at b)

-- The identity element: zero value, zero flow, at time zero.
mempty :: BasicParticle
mempty = BasicParticle { settled_at = 0, settled_value = 0, flow_rate = 0 }
```

Monoidality means:

- Multiple agreements' contributions to an account can be summed in any order.
- Incremental updates compose: new delta `<>` existing state = updated state.
- The zero particle is the identity — accounts with no activity have zero balance.

### Decaying Flow (Not Implemented)

The yellowpaper also specifies an exponential decay primitive where value
decreases over time at rate `e^(-λt)`. This is mathematically well-defined
and preserves conservation but is **not implemented on-chain** in the current
Superfluid protocol. It remains a theoretical contribution for potential future
use.

## Index Abstraction

To generalize beyond 1:1 payments, the yellowpaper introduces the **index
abstraction**. An index `k` has a **proportion function** `ρ`:

```
ρ k :: u → ℝ      with constraint: Σ(ρ k u) = 1 for all u
```

The proportion function determines what fraction of a payment each party
receives. This enables multi-party payment primitives:

**Indexed Transfer**:
```
⟦transfer_I ka kb x⟧ = λu → λt → -x · ρ(ka, u) + x · ρ(kb, u)
```

**Indexed Flow**:
```
⟦flow_I ka kb r t'⟧ = λu → λt → -r · (t - t') · ρ(ka, u) + r · (t - t') · ρ(kb, u)
```

The index type determines the payment topology:

| Index Type | ρ Definition | Constraint | On-Chain Mapping |
|---|---|---|---|
| Universal Index | ρ = 1 for exactly one party, 0 for all others | Σρ = 1 (trivially) | CFA (1:1 streams) |
| Proportional Distribution | Sender side: universal; receiver side: proportional by unit weights | Σρ = 1 via normalized units | GDA (1:N pools) |
| Network (general) | Arbitrary weights across all parties | Σρ = 0 | Not implemented |

**Universal index** recovers standard 1:1 payments — each index identifies
exactly one party. This is what CFA uses.

**Proportional distribution** fixes the sender side to a universal index
(one sender) and distributes the receiver side proportionally across pool
members weighted by their units. This is exactly what GDA pools do on-chain:
the pool has members with units, and the flow (or distribution) is split
proportionally.

In the Haskell spec, the proportional distribution is modeled via
`PDPoolIndex` and `PDPoolMember`:

```haskell
-- Pool-level index: tracks total units and per-unit accumulation.
-- On-chain: this is SuperfluidPool's storage.
data PDPoolIndex = PDPoolIndex
  { total_units          :: Units         -- sum of all member units
  , wrapped_particle     :: BasicParticle -- per-unit accumulation
  }

-- Per-member state: tracks each member's units and sync point.
-- On-chain: each member's position in the pool.
data PDPoolMember = PDPoolMember
  { owned_units          :: Units         -- this member's weight
  , settled_value        :: Value         -- accumulated value at last sync
  , synced_particle      :: BasicParticle -- pool's particle snapshot at last sync
  }

-- Member's real-time balance (via the MonetaryUnit typeclass's rtb method
-- on the (PDPoolIndex, PDPoolMember) tuple):
--   balance = settled_value + (pool_rtb(t) - synced_rtb(t_sync)) * owned_units
-- The subtraction gives the per-unit delta since last sync, multiplied by units.
memberRtb pool member t =
  let poolVal  = balanceAt (wrapped_particle pool) t
      syncVal  = balanceAt (synced_particle member) (settledAt (synced_particle member))
      delta    = poolVal - syncVal
  in delta * owned_units member + settled_value member
```

The **network abstraction** (Σρ = 0 rather than Σρ = 1) is even more general
— it would allow arbitrary weighted graphs of payments — but is not currently
implemented on-chain.

## Agreement Framework

Part III of the yellowpaper describes the optimization and implementation
layer — how the mathematical primitives become practical on-chain contracts.

### Monetary Unit Data (MUD)

Each monetary unit (account) has a set of MUD entries — one per agreement it
participates in. The **π function** computes real-time balance from stored
parameters:

```haskell
-- π function: compute balance from stored MUD at time t.
-- No iteration over transaction history — just current parameters.
class MonetaryUnitData mud where
  balanceProvided :: mud -> Timestamp -> RealTimeBalance
```

MUD must be a **Semigroup** (combinable via `<>`) for scalability. When a new
operation occurs, its delta merges onto existing state in constant time rather
than rebuilding from scratch.

An account's total balance is the monoidal sum of π applied to each of its
MUD entries — one from CFA data, one from GDA data, one from the token's own
settled balance, etc.

### Agreement Contracts and the ω Function

The **ω (omega) function** is the core of agreement execution:

```haskell
-- ω function: apply an operation to agreement contract state.
-- Returns: updated contract state + MUD deltas for affected parties.
-- The MUD deltas are applied to accounts' stored data.
applyAgreementOperation
  :: AgreementContract ac
  => ac                -- current contract state
  -> Operation         -- the operation (create/update/delete flow, etc.)
  -> Timestamp         -- current time
  -> (ac, MUD_Deltas)  -- new contract state + per-account deltas
```

Key properties of agreements:

- **Agreements are stateless in themselves** — they store data on the token
  contract, not in the agreement contract. The agreement contract is logic;
  the token is storage. This is why `ISuperfluid` (the Host) mediates all
  calls.
- **ω preserves conservation** — the sum of all MUD deltas from any single ω
  invocation is zero. This is the per-operation zero-sum guarantee.
- **Agreement contracts are MUD** (they provide balance via π) but are **not**
  Semigroups — they replace state rather than merging. Only per-account MUD is
  a Semigroup.

### Lens Accessors

To support the index abstraction generically, MUD fields are accessed through
**lenses** (getter/setter pairs). This allows the same agreement logic to work
with both:

- **Universal index** — direct record field access (one sender, one receiver)
- **Proportional distribution index** — computed from pool state (one sender,
  many receivers via pool)

The lens pattern means CFA and GDA share the same underlying flow logic,
differing only in how they access and distribute the flow's effect across
parties.

### Agreement Hierarchy

| Agreement | Index Type | MUD Contains | On-Chain Contract |
|---|---|---|---|
| ITA (Instant Transfer) | Universal | settled_value | ERC-20 `transfer` on SuperToken |
| CFA (Constant Flow) | Universal | settled_at, settled_value, net_flow_rate | `ConstantFlowAgreementV1` |
| IDA (Instant Distribution) | Proportional | value_per_unit, synced state | `InstantDistributionAgreementV1` (deprecated) |
| CFDA (Constant Flow Distribution) | Proportional | flow_rate_per_unit, synced state | `GeneralDistributionAgreementV1` |

The IDA is the predecessor of GDA — it supported only instant (discrete)
distributions to pool members. The CFDA (exposed as GDA on-chain) adds
continuous streaming to pools, unifying instant and continuous distribution
under the proportional distribution index.

A **Minter agreement** (for mint/burn of Super Tokens) is also specified in
the Haskell code and used internally, but is not exposed as a user-facing
agreement contract.

## FRP Connection

The yellowpaper draws explicitly on **Functional Reactive Programming** (FRP),
as formalized by Elliott & Hudak (1997). This is not a loose analogy — it is
the mathematical framework that makes continuous-time money possible.

### Behaviors

Values that vary continuously over time:

```
at :: Behavior α → Time → α
```

A SuperToken balance is a behavior. At any moment `t`, evaluating the behavior
yields the current balance — no state change, no transaction, just a function
of time.

### Events

Discrete occurrences at specific times:

```
occ :: Event α → Time × α
```

Agreement operations (createFlow, updateFlow, deleteFlow, distribute) are
events. They happen at discrete block timestamps and change the parameters of
the behavior.

### Reactivity (untilB)

The bridge between continuous behavior and discrete events:

```
b untilB e
```

Exhibits behavior `b` until event `e` occurs at time `t_e`, then switches to a
new behavior `b'`:

```
at ⟦b untilB e⟧ t =
    if t ≤ t_e  then at ⟦b⟧ t      -- formula governs
    else             at ⟦b'⟧ t      -- new formula after event
```

This is exactly the **settle-on-write** pattern used everywhere in Superfluid:

1. **Between events**: Balance computed purely from the formula
   `settled_value + flow_rate * (t - settled_at)`. No storage writes, no
   per-block updates. The behavior handles continuous time natively.
2. **At event time (write)**: Settle the current behavior's value at `now`,
   store new parameters (new flow rate, new settled value), and the formula
   takes over again with the updated parameters.
3. **After the event**: A new behavior governs, with its own linear formula.

The yellowpaper notes that while FRP in software typically handles discrete
event semantics with conceptually continuous behaviors, Superfluid's use case
genuinely requires **continuous-time semantics for money flow**. The balance
between two events is not "the same value stored repeatedly" — it is a
continuously varying quantity that the formula evaluates at read time.

## Real-Time Balance

The protocol introduces **Real-Time Balance (RTB)** as a "functorful" of
monetary values. Rather than a single number, RTB separates:

- **Untapped value** — what the bearer can freely use (available balance)
- **Typed set-asides** — value reserved for specific financial purposes
  (deposits, owed deposits)

```haskell
-- Real-time balance: a typed container of monetary values.
-- Each component has a distinct financial meaning.
class RealTimeBalance rtb value where
  valueToRTB    :: value -> rtb    -- promote a single value into RTB
  netValueOfRTB :: rtb -> value    -- collapse RTB to net monetary value
  -- Invariant: netValueOfRTB (valueToRTB v) = v
```

RTB is itself a **Monoid** — RTBs from different agreements are summed to get
the account's total real-time balance. This is why `realtimeBalanceOfNow`
returns multiple components (`availableBalance`, `deposit`, `owedDeposit`)
rather than collapsing to a single number. The components serve distinct
purposes in solvency accounting.

## Buffer-Based Solvency

In a non-deterministic execution environment like a blockchain, the system
cannot predict when financial contracts will actually execute. A sender's
balance could go negative between the last on-chain event and the next — the
stream keeps "flowing" according to the formula even when no one is transacting.

The yellowpaper introduces **buffers**: monetary value set aside in a
conditional financial contract. The buffer is:

- **Locked** when a stream is created — a deposit proportional to the flow
  rate is reserved.
- **Released** when the stream is closed normally (sender still solvent).
- **Consumed** if insolvency arises — the buffer covers the loss caused by
  timing uncertainty between when the sender ran out and when a liquidation
  transaction actually executes.

This is exactly the **deposit mechanism** in Superfluid:

- Creating a CFA stream locks a deposit (typically 4 hours of flow).
- If the sender's balance hits zero and no one liquidates immediately, the
  deposit covers the gap.
- Sentinels (liquidation bots) monitor for critical balances and trigger
  liquidation, receiving a reward from the deposit.

The buffer model is what makes streaming payments safe in a blockchain
environment where "check balance and stop stream" cannot happen atomically or
instantaneously.

## Future Investigations

The yellowpaper's concluding section identifies several directions:

- **Agda restatement**: The Haskell spec relies on QuickCheck property tests
  for assurance. Restating in Agda (a dependently-typed language) would enable
  machine-checked formal proofs of conservation and other invariants.
- **Compositional financial contracts**: A planned next yellowpaper exploring
  combinator library patterns inspired by Peyton Jones et al.'s "Composing
  Contracts" (2000). This would allow complex financial instruments to be built
  by composing simpler payment primitives.
- **General accounting domains**: Extending "real-time finance" beyond token
  streaming. The yellowpaper defines real-time finance as: a financial system
  where payments are continuous, contracts are compositional, and accounting
  is automated in real time.

## Key Haskell Modules

Reference table for exploring the spec-haskell source:

| Module | Purpose | On-Chain Equivalent |
|---|---|---|
| `Money.Theory.SemanticMoney` | Core math: BasicParticle, PDPoolIndex, PDPoolMember, shift/flow primitives | Foundation for all agreements |
| `Money.Systems.Superfluid.CoreTypes` | Type families for values, timestamps, real-time balance | SuperToken type system |
| `Money.Systems.Superfluid.Concepts.Agreement` | AgreementContract typeclass, ω function | Agreement framework (Host + agreements) |
| `Money.Systems.Superfluid.Concepts.MonetaryUnitData` | MUD typeclass, π function, semigroup constraint | Per-account agreement data storage |
| `Money.Systems.Superfluid.Agreements.Universal.ConstantFlowAgreement` | CFA spec | `ConstantFlowAgreementV1.sol` |
| `Money.Systems.Superfluid.Agreements.ProportionalDistribution.ConstantFlowDistributionAgreement` | CFDA spec | `GeneralDistributionAgreementV1.sol` |
| `Money.Systems.Superfluid.Agreements.ProportionalDistributionIndex` | PDPool distribution contracts | `SuperfluidPool.sol` |
| `Money.Systems.Superfluid.Token` | Token typeclass with all agreement operations | `SuperToken.sol` |
| `Money.Systems.Superfluid.SubSystems.BufferBasedSolvency` | Deposit/liquidation model | Sentinel system + deposits |
| `Money.Systems.Superfluid.MonetaryUnit` | Balance aggregation across all MUDs | `realtimeBalanceOf` computation |

## Links

- **Yellowpaper PDF**: https://semantic.money/assets/semantic-money-yellowpaper1.pdf
- **semantic.money**: https://semantic.money
- **Haskell spec source**: https://github.com/superfluid-finance/protocol-monorepo/tree/dev/packages/spec-haskell
- See also: `references/deep-researches/gda-scalability.md` for how the proportional distribution index achieves O(1) streaming
