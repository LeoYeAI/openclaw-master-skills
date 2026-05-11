# Superfluid Protocol Architecture

## Contract Hierarchy

```
                        ┌──────────────┐
                        │   Superfluid │  (Host — central router)
                        │    (Host)    │
                        └──────┬───────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼───────┐ ┌─────▼──────┐ ┌───────▼──────────┐
     │      CFA       │ │    GDA     │ │       IDA        │
     │ (Money Streams) │ │(Distribute)│ │  (Deprecated)    │
     └────────┬───────┘ └─────┬──────┘ └──────────────────┘
              │               │
     ┌────────▼───────┐ ┌────▼───────────┐
     │ CFAv1Forwarder │ │ GDAv1Forwarder │
     │  (convenience) │ │  (convenience) │
     └────────────────┘ └────┬───────────┘
                             │
                        ┌────▼───────────┐
                        │ SuperfluidPool │
                        │ (GDA members)  │
                        └────────────────┘

     ┌────────────────┐     ┌──────┐
     │   SuperToken    │     │ TOGA │
     │ (ERC20+ERC777  │     │(PIC  │
     │  +realtime bal) │     │auction)
     └────────────────┘     └──────┘
```

## The Host as Central Router

The Superfluid contract (commonly called "the Host") is the protocol's
orchestrator.  Almost nothing happens by calling agreement contracts directly.
Instead:

1. User calls `Host.callAgreement(agreement, callData, userData)`
2. Host creates a **context** (`ctx`) encoding the original `msg.sender`
3. Host delegates to the target agreement with the context
4. During execution, the Host invokes **Super App callbacks** (before/after
   hooks) if any involved account is a registered Super App
5. After execution, the Host validates that Super Apps didn't violate any
   rules (the `APP_RULE` error codes)

For convenience, `batchCall` bundles multiple operations (agreement calls,
ERC-20 approvals, token upgrades/downgrades) into a single transaction.
`forwardBatchCall` does the same but preserves the original sender via
EIP-2771 — this is what the forwarder contracts use internally.

### Key Host responsibilities
- Agreement class whitelisting (`registerAgreementClass`)
- Super App registry (`registerApp`, `registerAppWithKey`)
- SuperTokenFactory and pool beacon management
- Governance configuration
- ERC-2771 trusted forwarder support

## Agreements — Financial Primitives

Agreements are **stateless singletons**. They don't store data in their own
contract storage. Instead, they write state to the Super Token itself using:
- `token.createAgreement(id, data)` / `updateAgreementData` / `terminateAgreement`
- `token.updateAgreementStateSlot(account, slotId, slotData)`
- `token.settleBalance(account, delta)`

This design means all financial state for a token lives on that token contract.

### CFA — Constant Flow Agreement

Creates continuous money streams: one sender, one receiver, constant flow rate.

**Terminology: flow vs stream** — The protocol uses "flow" everywhere:
`createFlow`, `updateFlow`, `deleteFlow`, `getFlow`, `FlowUpdated`. A flow
always exists between two accounts for a given token (rate 0 when inactive).
"Stream" is a higher-level concept introduced by the subgraph — a stream
represents one continuous period of non-zero flow (rate 0→non-zero = stream
created, back to 0 = stream closed). Prefer "flow" in code and variable names;
"stream" is acceptable in user-facing text and event labels (`StreamCreated`,
`StreamUpdated`, `StreamClosed`).

- Flow rate is `int96` in wei/second
- Sender must maintain a **buffer deposit** = flowRate * liquidationPeriod
- When a sender's available balance goes negative ("critical"), anyone can
  liquidate (delete) the flow and earn a reward
- Supports **ACL** (Access Control List): operators can manage flows on behalf
  of senders via `flowOperatorDefinitions`
- All CFA state changes go through the Host's `callAgreement`

#### App Credit

When a Super App receives a stream, it can open outgoing streams using
**app credit** — a temporary deposit allowance backed by the sender as
**owed deposit**. See `guides/super-apps.md` for the full explanation
(callback lifecycle, credit rules, jailing, app levels).

### GDA — General Distribution Agreement

Many-to-many distribution via **pools**:

- An admin creates a `SuperfluidPool` and assigns **units** to members
- **Instant distribution**: `distribute(token, from, pool, amount)` — splits
  `amount` proportionally among members based on their units
- **Streaming distribution**: `distributeFlow(token, from, pool, flowRate)` —
  creates a continuous flow that splits proportionally
- Members must **connect** to receive distributions automatically; unconnected
  members can still **claim** accumulated distributions
- Pool `distributionFromAnyAddress` setting controls whether only the admin can
  distribute or anyone can — enabling many-to-many patterns

#### GDA Rounding & Adjustment Flow

Flow distributions use integer math: `perUnitRate = requestedFlowRate / totalUnits`
(truncated). The small remainder becomes the **adjustment flow** directed to the pool
admin. When `updateMemberUnits` changes the unit count, the adjustment flow is
recalculated but can only increase (sticky behavior) — it never decreases until
`distributeFlow` is called again. In the extreme case where `totalUnits` exceeds
`requestedFlowRate` (even transiently), the per-unit rate truncates to 0 and the
entire distribution becomes adjustment flow. Re-calling `distributeFlow` resets
the per-unit rate and adjustment flow from scratch.

### IDA — Instant Distribution Agreement (Deprecated)

The original distribution mechanism (1-to-many only), superseded by GDA. Notable differences:
- Uses "index" / "subscription" terminology instead of "pool" / "member"
- Dual event pattern: every operation emits both an Index* variant (indexed by
  publisher) and a Subscription* variant (indexed by subscriber)
- No streaming distribution — instant only
- Still deployed on all networks for backward compatibility

## Super Token — The Token Layer

SuperToken is a standard ERC-20/ERC-777/ERC-2612 token with real-time balance
capabilities. Key design points:

### Real-time Balance
`balanceOf(account)` returns `max(0, availableBalance)` — it clamps negative
balances to zero for ERC-20 compatibility. For the full picture, use:

```
(availableBalance, deposit, owedDeposit, timestamp) = token.realtimeBalanceOfNow(account)
```

The available balance is computed dynamically:
```
availableBalance = settledBalance + sum(agreement_dynamics) - max(0, deposit - owedDeposit)
```

### Three Variants
- **Wrapper**: Backed by an ERC-20. `upgrade(amount)` wraps, `downgrade(amount)` unwraps.
- **Native Asset (SETH)**: Backed by ETH/MATIC/etc. `upgradeByETH()` wraps,
  `downgradeToETH(wad)` unwraps. Also mints on plain ETH transfer via `receive()`.
- **Pure**: Pre-minted supply, no underlying token. `upgrade`/`downgrade` revert.

All three share the same logic contract (UUPS proxy). Each Super Token is an
individual proxy deployed by the SuperTokenFactory.

### Agreement Hosting
The token stores agreement data directly:
- `createAgreement` / `updateAgreementData` / `terminateAgreement` — agreement-level data
- `updateAgreementStateSlot` / `getAgreementStateSlot` — per-account state
- `settleBalance` — adjust settled balance (only listed agreements)
- `makeLiquidationPayoutsV2` — execute liquidation rewards/penalties

### Access Control Modifiers
- `onlyHost` — only the Superfluid Host contract
- `onlyAgreement` — only whitelisted agreement contracts (via Host)
- `onlySelf` — only the token contract itself (for custom proxy logic)
- `onlyAdmin` — the explicit admin, or the Host if no admin is set

## SuperfluidPool — GDA Building Block

Each GDA pool is a separate contract deployed as a beacon proxy. Key mechanics:

- **Units**: Members receive distribution shares proportional to their units
- **Connect/Disconnect**: Connected members get distributions automatically;
  disconnected members accumulate claimable balances
- **Admin**: Manages unit assignments, pool configuration
- **Transfer restrictions**: `poolConfig.transferabilityForUnitsOwner` controls
  whether members can transfer pool units via ERC-20 transfer

## Forwarders — Developer-Friendly Layer

CFAv1Forwarder and GDAv1Forwarder exist because calling
`Host.callAgreement(cfa, abi.encode(cfa.createFlow.selector, ...))` is verbose.

They internally use `ForwarderBase._forwardBatchCall()` which:
1. Encodes the operation as a batch call
2. Calls `Host.forwardBatchCall` with EIP-2771 sender preservation
3. The Host unpacks the original sender, so the flow/distribution is attributed correctly

Forwarders have almost no logic of their own — no events, minimal errors.
They are the recommended entry point for most integrations.

### MacroForwarder — Extensible Batch Executor

MacroForwarder extends the forwarder pattern for **user-defined** operations.
Instead of hardcoding specific agreement calls, it delegates to a **macro
contract** implementing `IUserDefinedMacro`. The macro's `buildBatchOperations`
returns an array of operations that MacroForwarder forwards to the Host via
`forwardBatchCall`, preserving the original sender via EIP-2771.

This enables developers to encapsulate complex multi-step batch operations
(wrap tokens + approve + create stream + connect pool) in a reusable,
permissionless contract. See `guides/macro-forwarders.md` for the full
pattern, interface, and examples.

## TOGA — Sentinel Incentive Layer

Liquidation requires someone to call `deleteFlow` on critical accounts. TOGA
incentivizes this via a continuous bond auction per Super Token:

1. Anyone can become PIC by sending a bond (via ERC-777 `send()`) exceeding
   the current PIC's bond
2. The PIC receives all liquidation rewards for that token
3. The bond streams back to the PIC at a configurable exit rate
4. When outbid, the previous PIC gets their remaining bond via ERC-20 transfer

TOGA is the only contract that uses `require()` with string messages rather
than custom errors — it predates the protocol's migration to custom error types.

## Cross-Contract Call Patterns

### Direct calls (user → contract)
- ERC-20 operations on SuperToken: `transfer`, `approve`, `balanceOf`
- Forwarder operations: `cfaForwarder.createFlow(...)`, `gdaForwarder.distribute(...)`
- Pool operations: `pool.claimAll()`, `pool.getUnits(member)`
- TOGA operations: `toga.changeExitRate(token, newRate)`

### Host-routed calls (user → Host → agreement → token)
- CFA/GDA/IDA operations via `Host.callAgreement` or `Host.batchCall`
- Forwarders use this pattern internally via `Host.forwardBatchCall`
- The `ctx: bytes` parameter on agreement functions indicates Host routing

### Self calls (token proxy → token logic)
- SETH's `upgradeByETH()` calls `selfMint` on the logic contract
- PureSuperToken's `initialize()` calls `selfMint`
- These use the `onlySelf` modifier

### Agreement → token storage
- Agreements write state via `token.createAgreement`, `token.settleBalance`, etc.
- These use the `onlyAgreement` modifier (checked against Host's whitelist)

## Formal Foundations

The protocol's formal mathematical foundations are specified in the [Semantic Money yellowpaper](https://semantic.money) — see `references/deep-researches/semantic-money-yellowpaper.md` for a detailed walkthrough.
