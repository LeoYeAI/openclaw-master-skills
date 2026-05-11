# Vesting Scheduler — Subgraph Usage Guide

Companion to `vesting-scheduler.graphql`. Covers entity overview, status computation, timing fields, example queries, and filter patterns.

---

## Entity Overview

### Entities

**VestingSchedule** — Token vesting schedule with cliff and flow phases. Fields: `superToken`, `sender`, `receiver`, `startDate`, `endDate`, `cliffDate`, `cliffAmount`, `flowRate`, `claimValidityDate`, `remainderAmount`, `totalAmount`, `contractVersion`

**Task** — Scheduled automation task for cliff/flow or end execution. Fields: `type` (ExecuteCliffAndFlow, ExecuteEndVesting), `executionAt`, `expirationAt`, `executedAt`, `cancelledAt`, `failedAt`

**TokenSenderReceiverCursor** — Cursor tracking current schedule and tasks for a sender-receiver pair. Fields: `currentVestingSchedule`, `currentCliffAndFlowTask`, `currentEndVestingTask`

### Events

VestingScheduleCreatedEvent, VestingScheduleUpdatedEvent, VestingScheduleDeletedEvent, VestingCliffAndFlowExecutedEvent, VestingEndExecutedEvent, VestingEndFailedEvent, VestingClaimedEvent, VestingScheduleEndDateUpdatedEvent

---

## Schedule ID Format

Vesting schedule IDs follow the pattern `{transactionHash}-{index}`. Split on `-` to extract the original creation transaction hash:

```
ID: "0xabc123...-0"
Transaction hash: "0xabc123..."
```

```typescript
const txHash = schedule.id.split("-")[0];
```

---

## Timing Fields

```
Timeline:  startDate → [cliffDate] → cliffAndFlowDate → endDate
                                      ↑                    ↑
                                automation executes    automation executes
                                cliff+flow here        end here
```

**`startDate`** — When the vesting period begins

**`cliffDate`** — End of cliff period (optional; if absent, `cliffAndFlowDate = startDate`)

**`cliffAndFlowDate`** — When the cliff transfer + flow should be executed by automation (`= cliffDate ?? startDate`)

**`cliffAndFlowExpirationAt`** — Deadline for automation to execute cliff+flow; if missed → `CliffAndFlowExpired`

**`endDate`** — When the vesting should end and flow should stop

**`endDateValidAt`** — Earliest time the end execution becomes valid

**`cliffAndFlowExecutedAt`** — Actual timestamp when automation executed cliff+flow (null if not yet)

**`endExecutedAt`** — Actual timestamp when automation executed end (null if not yet)

**`claimValidityDate`** — If > 0, receiver must claim before this date (claimable vesting feature)

---

## Derived Field: `totalAmountWithOverpayment`

When a vesting schedule is overpaid (automation executed the end after the expected `endDate`), the actual total is:

```
If cliffAndFlowExecutedAt < endDate AND endExecutedAt > endDate:
  totalAmountWithOverpayment = totalAmount - remainderAmount + (endExecutedAt - endDate) × flowRate
```

---

## Vesting Schedule Statuses

Status is **computed client-side**, not stored in the subgraph. Fetch the schedule fields and apply the following decision tree in priority order (first match wins):

1. **DeletedAfterStart** "Deleted" — `deletedAt` exists AND `deletedAt > startDate`. Flags: isFinished, isDeleted.
2. **DeletedBeforeStart** "Deleted" — `deletedAt` exists AND `deletedAt <= startDate`. Flags: isFinished, isDeleted.
3. **EndFailed** "Cancel Error" — `failedAt` exists. Flags: isFinished, isError.
4. **EndCompensationFailed** "Transfer Error" — `didEarlyEndCompensationFail` is true. Flags: isFinished, isError.
5. **EndOverflowed** "Overflow Error" — `endExecutedAt` exists AND `claimedAt !== endExecutedAt` AND `endExecutedAt > endDate`. Flags: isFinished, isError.
6. **EndExecuted** "Vested" — `endExecutedAt` exists (and #5 conditions not met). Flags: isFinished.
7. **CliffAndFlowExecuted** "Vesting" — `cliffAndFlowExecutedAt` exists. Flags: isStreaming.
8. **ClaimExpired** "Claim Expired" — `claimValidityDate > 0` AND `now > claimValidityDate`. Flags: isFinished, isError.
9. **Claimable** "Unclaimed" — `claimValidityDate > 0` AND `now > cliffAndFlowDate` AND `now < claimValidityDate`. Flags: canClaim.
10. **CliffAndFlowExpired** "Stream Error" — `now > cliffAndFlowExpirationAt`. Flags: isStreaming, isError.
11. **CliffPeriod** "Cliff" — `cliffDate` exists AND `startDate < now < cliffAndFlowExpirationAt`. Flags: isCliff.
12. **ScheduledStart** "Scheduled" — Default, none of the above matched.

Since status depends on the current timestamp (`now`), you cannot filter for time-dependent statuses like `CliffPeriod`, `Claimable`, or `CliffAndFlowExpired` purely through subgraph filters. Fetch schedules and apply the decision tree in your application.

---

## Filter Patterns

```graphql
# Active (streaming) schedules only
{
  deletedAt: null
  failedAt: null
  endExecutedAt: null
  cliffAndFlowExecutedAt_not: null
}

# Completed (vested) schedules only
{
  endExecutedAt_not: null
}

# Pending/scheduled (not yet started)
{
  cliffAndFlowExecutedAt: null
  deletedAt: null
}

# All non-deleted schedules for a sender
{
  sender: "0x...lowercase..."
  deletedAt: null
}
```

---

## Example Query: Vesting Schedule Events

Query all 7 vesting event types using inline fragments:

```graphql
query vestingScheduleEvents(
  $where: Event_filter! = {}
  $skip: Int! = 0
  $first: Int! = 1000
  $orderBy: Event_orderBy! = timestamp
  $orderDirection: OrderDirection! = desc
  $block: Block_height
) {
  events(
    where: $where
    block: $block
    skip: $skip
    first: $first
    orderBy: $orderBy
    orderDirection: $orderDirection
  ) {
    id
    blockNumber
    transactionHash
    timestamp
    name
    order
    logIndex
    gasPrice
    __typename
    ... on VestingCliffAndFlowExecutedEvent {
      superToken
      sender
      receiver
      cliffAndFlowDate
      flowRate
      cliffAmount
      flowDelayCompensation
    }
    ... on VestingEndExecutedEvent {
      superToken
      sender
      receiver
      endDate
      earlyEndCompensation
      didCompensationFail
    }
    ... on VestingEndFailedEvent {
      superToken
      sender
      receiver
      endDate
    }
    ... on VestingScheduleCreatedEvent {
      superToken
      sender
      receiver
      startDate
      cliffDate
      flowRate
      endDate
      cliffAmount
      claimValidityDate
      remainderAmount
    }
    ... on VestingScheduleDeletedEvent {
      superToken
      sender
      receiver
    }
    ... on VestingScheduleUpdatedEvent {
      superToken
      sender
      receiver
      oldEndDate
      endDate
      oldRemainderAmount
      remainderAmount
      oldFlowRate
      flowRate
      totalAmount
      oldTotalAmount
      settledAmount
    }
    ... on VestingClaimedEvent {
      superToken
      sender
      receiver
      claimer
    }
  }
}
```
