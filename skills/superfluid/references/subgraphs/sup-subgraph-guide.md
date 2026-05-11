# SUP (Locker / Reserve) — Subgraph Usage Guide

Companion to `sup-subgraph.graphql`. Covers entity overview, endpoints, filter patterns, and example queries for the SUP token staking and reserve system.

---

## Availability

Base Mainnet and Base Sepolia **only**. These are Goldsky-hosted endpoints (not the standard `subgraph-endpoints.superfluid.dev` pattern):

- Base Mainnet (8453): `https://api.goldsky.com/api/public/project_clsnd6xsoma5j012qepvucfpp/subgraphs/sup/v2/gn`
- Base Sepolia (84532): `https://api.goldsky.com/api/public/project_clsnd6xsoma5j012qepvucfpp/subgraphs/sup_test/latest/gn`

---

## Entity Overview

**Locker** — Deployed FluidLocker contract instance. One per user. Derived fields link to all locker activity: `fontaines`, `instantUnlocks`, `stakingData`, `liquidityPositions`. Fields: `lockerOwner`, `blockNumber`, `blockTimestamp`, `transactionHash`

**Program** — Emission program for distributing SUP via a GDA distribution pool. Fields: `programAdmin`, `signer`, `token`, `distributionPool`, `fundingAmount`, `subsidyAmount`, `earlyEndDate`, `endDate`, `stoppedDate`, `cancellationDate`, `returnedDeposit`, `fundingCompensationAmount`, `subsidyCompensationAmount`

**FluidStreamClaimEvent** — Claim event triggered when a locker claims from emission programs. Links to `ClaimEventUnit` entries via derived `units` field. Fields: `locker`, `claimer`

**ClaimEventUnit** — Per-program claim detail within a FluidStreamClaimEvent. Fields: `programId`, `amount`, `event`

**StakingStats** — Global singleton (ID = `"global"`). Tracks aggregate staking metrics and dynamic config. Fields: `totalStaked`, `activeStakerCount`, `totalStakerCount`, `stakingEventCount`, `taxDistributionPool`, `stakerAllocationBP`, `currentStakerFlowRate`

**LockerStaking** — Per-locker staking state. Fields: `locker`, `currentStakedBalance`, `stakingEventCount`, `firstStakedTimestamp`, `lastStakedTimestamp`, `lastUnstakedTimestamp`, `rewardUnits`

**StakingEvent** — Immutable STAKE or UNSTAKE event. Fields: `lockerStaking`, `type` (STAKE | UNSTAKE), `amount`, `newStakedBalance`

**LiquidityPosition** — Uniswap V3 position NFT (ETHx/SUP pair) owned by a locker. Fields: `locker`, `tokenId`, `liquidityAmount`, `token0AmountProvided` (ETHx), `token1AmountProvided` (SUP), `token0AmountCollected`, `token1AmountCollected`, `createdAt`, `burnedAt` (null if active)

**Fontaine** — Time-delayed vesting unlock. A separate contract is deployed per unlock. Fields: `locker`, `recipient`, `unlockPeriod`, `unlockAmount`, `unlockFlowRate`, `endDate`

**InstantUnlock** — Immediate unlock with 80% penalty. The penalty is distributed to stakers; the recipient receives 20%. Fields: `locker`, `recipient`, `unlockAmount`, `penaltyAmount`, `netAmount`

---

## Filter Patterns

```graphql
# Lockers by owner
{
  lockerOwner: "0x...lowercase..."
}

# Active stakers (have staked balance)
{
  currentStakedBalance_gt: "0"
}

# Active liquidity positions (not burned)
{
  burnedAt: null
}

# Burned liquidity positions
{
  burnedAt_not: null
}

# Staking events for a specific locker
{
  lockerStaking_: { locker: "0x...locker-address..." }
}

# Only STAKE events (no unstakes)
{
  type: STAKE
}

# Fontaines by locker
{
  locker: "0x...locker-address..."
}

# Instant unlocks by locker
{
  locker: "0x...locker-address..."
}
```

---

## Example Queries

### Locker overview with all activity

```graphql
query lockerOverview($locker: Bytes!) {
  locker(id: $locker) {
    id
    lockerOwner
    stakingData {
      currentStakedBalance
      firstStakedTimestamp
      lastStakedTimestamp
      rewardUnits
    }
    fontaines(orderBy: blockTimestamp, orderDirection: desc) {
      id
      recipient
      unlockPeriod
      unlockAmount
      unlockFlowRate
      endDate
    }
    instantUnlocks(orderBy: blockTimestamp, orderDirection: desc) {
      id
      recipient
      unlockAmount
      penaltyAmount
      netAmount
    }
    liquidityPositions(orderBy: createdAt, orderDirection: desc) {
      tokenId
      liquidityAmount
      token0AmountProvided
      token1AmountProvided
      createdAt
      burnedAt
    }
  }
}
```

### Global staking stats

```graphql
{
  stakingStats(id: "global") {
    totalStaked
    activeStakerCount
    totalStakerCount
    stakingEventCount
    taxDistributionPool
    stakerAllocationBP
    currentStakerFlowRate
  }
}
```

### Staking event history for a locker

```graphql
query stakingHistory($locker: Bytes!, $first: Int = 100) {
  stakingEvents(
    where: { lockerStaking_: { locker: $locker } }
    orderBy: blockTimestamp
    orderDirection: desc
    first: $first
  ) {
    type
    amount
    newStakedBalance
    blockTimestamp
    transactionHash
  }
}
```
