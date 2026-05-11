# Auto-Wrap — Subgraph Usage Guide

Companion to `auto-wrap.graphql`. Covers entity overview, example queries, and filter patterns.

---

## Entity Overview

### Entities

**WrapSchedule** — Automated wrapping schedule for a strategy-token-account combination. Fields: `account`, `superToken`, `liquidityToken`, `strategy`, `manager`, `lowerLimit`, `upperLimit`, `amount`, `isActive`, `lastExecutedAt`, `expiredAt`

**UserTokenLiquidityToken** — Cursor tracking current wrap schedule for a user-token-liquidity combination. Fields: `currentWrapSchedule`

### Events

AddedApprovedStrategyEvent, RemovedApprovedStrategyEvent, LimitsChangedEvent, WrapExecutedEvent, WrapScheduleCreatedEvent, WrapScheduleDeletedEvent

---

## Filter Patterns

```graphql
# Active wrap schedules for an account
{
  account: "0x...lowercase..."
  isActive: true
}
```

---

## Example Query: Get Wrap Schedules

```graphql
query getWrapSchedules(
  $where: WrapSchedule_filter = {}
  $orderBy: WrapSchedule_orderBy = id
  $orderDirection: OrderDirection = asc
) {
  wrapSchedules(
    where: $where
    orderBy: $orderBy
    orderDirection: $orderDirection
  ) {
    id
    account
    wrapScheduleId
    deletedAt
    updatedAt
    expiredAt
    createdAt
    lastExecutedAt
    strategy
    manager
    superToken
    liquidityToken
    amount
    upperLimit
    lowerLimit
    createdBlockNumber
    updatedBlockNumber
    isActive
  }
}
```
