# Protocol V1 — Subgraph Usage Guide

Companion to `protocol-v1-entities.graphql` and `protocol-v1-events.graphql`. Covers entity overview, token type detection, common queries, and filtering patterns.

---

## Entity Overview

### Higher-Order Entities

**Account** — Any address that interacts with Superfluid. Fields: `isSuperApp`, `inflows`, `outflows`, `pools`, `poolMemberships`

**Stream** — Lifetime of a CFA stream between sender and receiver. Fields: `currentFlowRate`, `deposit`, `streamedUntilUpdatedAt`, `sender`, `receiver`, `token`

**Pool** — GDA distribution pool. Fields: `totalUnits`, `totalMembers`, `flowRate`, `perUnitFlowRate`, `admin`, `token`

**PoolMember** — Membership in a GDA pool with allocated units. Fields: `units`, `isConnected`, `totalAmountClaimed`, `account`, `pool`

**PoolDistributor** — Account distributing tokens into a GDA pool. Fields: `totalBuffer`, `flowRate`, `totalAmountDistributedUntilUpdatedAt`, `account`, `pool`

**Index** — IDA index for distributing tokens (legacy). Fields: `indexId`, `indexValue`, `totalUnits`, `totalSubscriptionsWithUnits`, `publisher`, `token`

**IndexSubscription** — Subscription to an IDA index (legacy). Fields: `approved`, `units`, `totalAmountReceivedUntilUpdatedAt`, `subscriber`, `index`

**FlowOperator** — Flow operator permissions for an account-token pair. Fields: `permissions`, `flowRateAllowanceGranted`, `flowRateAllowanceRemaining`, `allowance`, `sender`, `token`

**StreamPeriod** — Period of constant flow rate within a stream. Fields: `flowRate`, `deposit`, `startedAtTimestamp`, `stoppedAtTimestamp`, `totalAmountStreamed`

**TokenGovernanceConfig** — Governance config for a Super Token. Fields: `rewardAddress`, `liquidationPeriod`, `patricianPeriod`, `minimumDeposit`, `isDefault`

### Helper Entities

**Token** — Super Token or underlying token. Fields: `symbol`, `name`, `decimals`, `isSuperToken`, `isNativeAssetSuperToken`, `isListed`, `underlyingAddress`

**StreamRevision** — Tracks revision index for sender-receiver streams. Fields: `revisionIndex`, `mostRecentStream`

**ResolverEntry** — Resolver registry mapping names to addresses. Fields: `targetAddress`, `isToken`, `isListed`

### Aggregate Entities

**AccountTokenSnapshot** — Per-account-per-token balance summary. Fields: `balanceUntilUpdatedAt`, `totalNetFlowRate`, `totalInflowRate`, `totalOutflowRate`, `totalDeposit`, `totalNumberOfActiveStreams`, `maybeCriticalAtTimestamp`

**AccountTokenSnapshotLog** — Historical snapshots of balance state changes. Fields: `balance`, `totalNetFlowRate`, `totalDeposit`, `triggeredByEventName`, `timestamp`

**TokenStatistic** — Aggregate stats for a token across all accounts. Fields: `totalNumberOfActiveStreams`, `totalOutflowRate`, `totalDeposit`, `totalAmountStreamedUntilUpdatedAt`, `totalSupply`

**TokenStatisticLog** — Historical log of TokenStatistic updates. _(deprecated — no longer indexed)_

### Events (by category)

**CFA:** FlowUpdatedEvent, FlowOperatorUpdatedEvent

**GDA/Pools:** PoolCreatedEvent, PoolConnectionUpdatedEvent, BufferAdjustedEvent, InstantDistributionUpdatedEvent, FlowDistributionUpdatedEvent, DistributionClaimedEvent, MemberUnitsUpdatedEvent

**IDA/Index (legacy):** IndexCreatedEvent, IndexDistributionClaimedEvent, IndexUpdatedEvent, IndexSubscribedEvent, IndexUnitsUpdatedEvent, IndexUnsubscribedEvent, SubscriptionApprovedEvent, SubscriptionDistributionClaimedEvent _(deprecated)_, SubscriptionRevokedEvent, SubscriptionUnitsUpdatedEvent

**Token:** TransferEvent, TokenUpgradedEvent, TokenDowngradedEvent, AgreementLiquidatedV2Event, BurnedEvent, MintedEvent, ApprovalEvent, CustomSuperTokenCreatedEvent, SuperTokenCreatedEvent, SuperTokenLogicCreatedEvent

**Governance:** ConfigChangedEvent, RewardAddressChangedEvent, PPPConfigurationChangedEvent, TrustedForwarderChangedEvent, GovernanceReplacedEvent, AgreementClassRegisteredEvent, AgreementClassUpdatedEvent, AppRegisteredEvent, JailEvent, SuperTokenFactoryUpdatedEvent, SuperTokenLogicUpdatedEvent, RoleAdminChangedEvent, RoleGrantedEvent, RoleRevokedEvent, SetEvent

**TOGA:** NewPICEvent, ExitRateChangedEvent, BondIncreasedEvent

---

## Token Type Detection

Determine a SuperToken's type from subgraph data:

**NativeAssetSuperToken** — Token address equals the network's native currency SuperToken address

**PureSuperToken** — `underlyingAddress` is `0x0000000000000000000000000000000000000000` or null

**WrapperSuperToken** — Has a non-zero `underlyingAddress` (wraps an underlying ERC-20)

---

## Example Query: Tokens an Account Has Interacted With

```graphql
query accountInteractedSuperTokens($account: String) {
  result: accountTokenSnapshots(where: { account: $account }) {
    token {
      id
    }
  }
}
```

---

## Example: Nested Entity Filtering — Streams by Operator

Check if a specific operator created a stream:

```graphql
query findStreamIdWhereOperatorMatches(
  $flowOperatorAddress: String
  $streamId: String
) {
  streams(
    where: {
      flowUpdatedEvents_: { flowOperator: $flowOperatorAddress }
      id: $streamId
    }
  ) {
    id
  }
}
```

The `flowUpdatedEvents_:` syntax is a **nested entity filter** — it filters parent entities (streams) based on properties of their related entities (flow events). The trailing underscore is the Graph Protocol syntax for relationship filters (see `query-patterns.md` § 9).
