# Flow Scheduler — Subgraph Usage Guide

Companion to `flow-scheduler.graphql`. Covers entity overview, union type handling, filter patterns, and example queries.

---

## Entity Overview

### Entities

**CreateTask** — Scheduled task to create a flow at a future date. Fields: `superToken`, `sender`, `receiver`, `flowRate`, `startDate`, `startAmount`, `startDateMaxDelay`, `executionAt`, `expirationAt`, `executedAt`, `cancelledAt`

**DeleteTask** — Scheduled task to delete a flow at a future date. Fields: `superToken`, `sender`, `receiver`, `executionAt`, `expirationAt`, `executedAt`, `cancelledAt`

**TokenSenderReceiverCursor** — Cursor tracking current flow tasks for a sender-receiver pair. Fields: `currentCreateFlowTask`, `currentDeleteFlowTask`

### Events

FlowScheduleCreatedEvent, FlowScheduleDeletedEvent, CreateFlowExecutedEvent, DeleteFlowExecutedEvent

---

## Union Type: CreateTask vs DeleteTask

The `tasks` query returns a union of `CreateTask` and `DeleteTask`. Always check `__typename` to distinguish them.

**Field differences:** `CreateTask` has additional fields that `DeleteTask` does not:
- `flowRate`, `startAmount`, `startDate`, `startDateMaxDelay`

Both types share: `id`, `cancelledAt`, `executedAt`, `executionAt`, `expirationAt`, `receiver`, `sender`, `superToken`.

---

## Filter Patterns

```graphql
# Active tasks (not yet executed or cancelled)
{
  cancelledAt: null
  executedAt: null
}

# Tasks for a specific sender
{
  sender: "0x...lowercase..."
}
```

---

## Example Query: Get All Tasks

```graphql
query getTasks(
  $where: Task_filter = {}
  $orderBy: Task_orderBy = id
  $orderDirection: OrderDirection = asc
) {
  tasks(
    first: 1000
    orderBy: $orderBy
    orderDirection: $orderDirection
    where: $where
  ) {
    __typename
    ... on CreateTask {
      superToken
      startDateMaxDelay
      startDate
      startAmount
      sender
      receiver
      id
      flowRate
      expirationAt
      executionAt
      executedAt
      cancelledAt
    }
    ... on DeleteTask {
      id
      cancelledAt
      executedAt
      executionAt
      expirationAt
      receiver
      sender
      superToken
    }
  }
}
```
