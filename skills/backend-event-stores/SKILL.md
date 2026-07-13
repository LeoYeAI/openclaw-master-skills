---
name: event-store
model: standard
description: Design and implement event stores for event-sourced systems. Use when building event sourcing infrastructure, implementing event persistence, projections, snapshotting, or CQRS patterns.
---

# Event Store

Guide to designing event stores for event-sourced applications — covering event schemas, projections, snapshotting, and CQRS integration.

## When to Use This Skill

- Designing event sourcing infrastructure
- Choosing between event store technologies
- Implementing custom event stores
- Building projections from event streams
- Adding snapshotting for aggregate performance
- Integrating CQRS with event sourcing

## Core Concepts

### Event Store Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Event Store                       │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Stream 1   │  │   Stream 2   │  │   Stream 3   │ │
│  │ (Aggregate)  │  │ (Aggregate)  │  │ (Aggregate)  │ │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤ │
│  │ Event 1     │  │ Event 1     │  │ Event 1     │ │
│  │ Event 2     │  │ Event 2     │  │ Event 2     │ │
│  │ Event 3     │  │ ...         │  │ Event 3     │ │
│  │ ...         │  │             │  │ Event 4     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────┤
│  Global Position: 1 → 2 → 3 → 4 → 5 → 6 → ...     │
└─────────────────────────────────────────────────────┘
```

### Event Store Requirements

| Requirement       | Description                        |
| ----------------- | ---------------------------------- |
| **Append-only**   | Events are immutable, only appends |
| **Ordered**       | Per-stream and global ordering     |
| **Versioned**     | Optimistic concurrency control     |
| **Subscriptions** | Real-time event notifications      |
| **Idempotent**    | Handle duplicate writes safely     |

### Technology Comparison

| Technology       | Best For                | Limitations                      |
| ---------------- | ----------------------- | -------------------------------- |
| **EventStoreDB** | Pure event sourcing     | Single-purpose                   |
| **PostgreSQL**   | Existing Postgres stack | Manual implementation            |
| **Kafka**        | High-throughput streams | Not ideal for per-stream queries |
| **DynamoDB**     | Serverless, AWS-native  | Query limitations                |

## Event Schema Design

Events are the source of truth. Well-designed schemas ensure long-term evolvability.

### Event Envelope Structure

```json
{
  "event_id": "uuid",
  "stream_id": "Order-abc123",
  "event_type": "OrderPlaced",
  "version": 1,
  "schema_version": 1,
  "data": {
    "customer_id": "cust-1",
    "total_cents": 5000
  },
  "metadata": {
    "correlation_id": "req-xyz",
    "causation_id": "evt-prev",
    "user_id": "user-1",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "global_position": 42
}
```

### Schema Evolution Rules

1. **Add fields freely** — new optional fields are always safe
2. **Never remove or rename fields** — introduce a new event type instead
3. **Version event types** — `OrderPlacedV2` when the schema changes materially
4. **Upcast on read** — transform old versions to the current shape in the deserializer

## PostgreSQL Event Store Schema

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id VARCHAR(255) NOT NULL,
    stream_type VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    version BIGINT NOT NULL,
    global_position BIGSERIAL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_stream_version UNIQUE (stream_id, version)
);

CREATE INDEX idx_events_stream ON events(stream_id, version);
CREATE INDEX idx_events_global ON events(global_position);
CREATE INDEX idx_events_type ON events(event_type);

CREATE TABLE snapshots (
    stream_id VARCHAR(255) PRIMARY KEY,
    stream_type VARCHAR(255) NOT NULL,
    snapshot_data JSONB NOT NULL,
    version BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE subscription_checkpoints (
    subscription_id VARCHAR(255) PRIMARY KEY,
    last_position BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Event Store Implementation

```python
@dataclass
class Event:
    stream_id: str
    event_type: str
    data: dict
    metadata: dict = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    version: int | None = None
    global_position: int | None = None

class EventStore:  # backed by PostgreSQL schema above
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def append(self, stream_id: str, stream_type: str,
                     events: list[Event],
                     expected_version: int | None = None) -> list[Event]:
        """Append events with optimistic concurrency control."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                if expected_version is not None:
                    current = await conn.fetchval(
                        "SELECT MAX(version) FROM events "
                        "WHERE stream_id = $1", stream_id
                    ) or 0
                    if current != expected_version:
                        raise ConcurrencyError(
                            f"Expected {expected_version}, got {current}"
                        )

                start = await conn.fetchval(
                    "SELECT COALESCE(MAX(version), 0) + 1 "
                    "FROM events WHERE stream_id = $1", stream_id
                )
                for i, evt in enumerate(events):
                    evt.version = start + i
                    row = await conn.fetchrow(
                        "INSERT INTO events (id, stream_id, stream_type, "
                        "event_type, event_data, metadata, version) "
                        "VALUES ($1,$2,$3,$4,$5,$6,$7) "
                        "RETURNING global_position",
                        evt.event_id, stream_id, stream_type,
                        evt.event_type, json.dumps(evt.data),
                        json.dumps(evt.metadata), evt.version,
                    )
                    evt.global_position = row["global_position"]
                return events

    async def read_stream(self, stream_id: str,
                          from_version: int = 0) -> list[Event]:
        """Read events for a single stream."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM events WHERE stream_id = $1 "
                "AND version >= $2 ORDER BY version",
                stream_id, from_version,
            )
            return [self._to_event(r) for r in rows]

    async def read_all(self, from_position: int = 0,
                       limit: int = 1000) -> list[Event]:
        """Read global event stream for projections / subscriptions."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM events WHERE global_position > $1 "
                "ORDER BY global_position LIMIT $2",
                from_position, limit,
            )
            return [self._to_event(r) for r in rows]
```

## Projections

Projections build read-optimised views by replaying events. They are the "Q" side of CQRS.

### Projection Lifecycle

1. **Start from checkpoint** — resume from last processed global position
2. **Apply events** — update the read model for each relevant event type
3. **Save checkpoint** — persist the new position atomically with the read model

### Projection Example

```python
class OrderSummaryProjection:
    def __init__(self, db, event_store: EventStore):
        self.db = db
        self.store = event_store

    async def run(self, batch_size: int = 100):
        position = await self._load_checkpoint()
        while True:
            events = await self.store.read_all(position, batch_size)
            if not events:
                await asyncio.sleep(1)
                continue
            for evt in events:
                await self._apply(evt)
                position = evt.global_position
            await self._save_checkpoint(position)

    async def _apply(self, event: Event):
        match event.event_type:
            case "OrderPlaced":
                await self.db.execute(
                    "INSERT INTO order_summaries (id, customer, total, status) "
                    "VALUES ($1,$2,$3,'placed')",
                    event.data["order_id"], event.data["customer_id"],
                    event.data["total_cents"],
                )
            case "OrderShipped":
                await self.db.execute(
                    "UPDATE order_summaries SET status='shipped' "
                    "WHERE id=$1", event.data["order_id"],
                )
```

### Projection Design Rules

- **Idempotent handlers** — replaying the same event twice must not corrupt state
- **One projection per read model** — keep projections focused
- **Rebuild from scratch** — projections should be deletable and fully replayable
- **Separate storage** — projections can live in different databases (Postgres, Elasticsearch, Redis)

## Snapshotting

Snapshots accelerate aggregate rehydration by caching state at a known version.

Use when streams exceed ~100 events, aggregates have expensive rehydration, or on a cadence (e.g., every 50 events).

### Snapshot Flow

```python
class SnapshottedRepository:
    def __init__(self, event_store: EventStore, pool):
        self.store = event_store
        self.pool = pool

    async def load(self, stream_id: str) -> Aggregate:
        # 1. Try loading snapshot
        snap = await self._load_snapshot(stream_id)
        from_version = 0
        aggregate = Aggregate(stream_id)

        if snap:
            aggregate.restore(snap["data"])
            from_version = snap["version"] + 1

        # 2. Replay events after snapshot
        events = await self.store.read_stream(stream_id, from_version)
        for evt in events:
            aggregate.apply(evt)

        # 3. Snapshot if too many events replayed
        if len(events) > 50:
            await self._save_snapshot(
                stream_id, aggregate.snapshot(), aggregate.version
            )

        return aggregate
```

## CQRS Integration

CQRS separates the write model (commands → events) from the read model (projections).

```
Commands ──► Aggregate ──► Event Store ──► Projections ──► Query API
 (write)     (domain)      (append)        (build)        (read)
```

### Key Principles

1. **Write side** validates commands, emits events, enforces invariants
2. **Read side** subscribes to events, builds optimised query models
3. **Eventual consistency** — reads may lag behind writes by milliseconds to seconds
4. **Independent scaling** — scale reads and writes separately

### Command Handler Pattern

```python
class PlaceOrderHandler:
    def __init__(self, event_store: EventStore):
        self.store = event_store

    async def handle(self, cmd: PlaceOrderCommand):
        # Load aggregate from events
        events = await self.store.read_stream(f"Order-{cmd.order_id}")
        order = Order.reconstitute(events)

        # Execute command — validates and produces new events
        new_events = order.place(cmd.customer_id, cmd.items)

        # Persist with concurrency check
        await self.store.append(
            f"Order-{cmd.order_id}", "Order", new_events,
            expected_version=order.version,
        )
```

## EventStoreDB Integration

```python
from esdbclient import EventStoreDBClient, NewEvent, StreamState
import json

client = EventStoreDBClient(uri="esdb://localhost:2113?tls=false")

def append_events(stream_name: str, events: list, expected_revision=None):
    new_events = [
        NewEvent(
            type=event['type'],
            data=json.dumps(event['data']).encode(),
            metadata=json.dumps(event.get('metadata', {})).encode()
        )
        for event in events
    ]
    state = (StreamState.ANY if expected_revision is None
             else StreamState.NO_STREAM if expected_revision == -1
             else expected_revision)
    return client.append_to_stream(stream_name, new_events, current_version=state)

def read_stream(stream_name: str, from_revision: int = 0):
    return [
        {'type': e.type, 'data': json.loads(e.data),
         'stream_position': e.stream_position}
        for e in client.get_stream(stream_name, stream_position=from_revision)
    ]

# Category projection: read all events for Order-* streams
def read_category(category: str):
    return read_stream(f"$ce-{category}")
```

## DynamoDB Event Store

```python
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import json, uuid

class DynamoEventStore:
    def __init__(self, table_name: str):
        self.table = boto3.resource('dynamodb').Table(table_name)

    def append(self, stream_id: str, events: list, expected_version: int = 0):
        with self.table.batch_writer() as batch:
            for i, event in enumerate(events):
                version = expected_version + i + 1
                batch.put_item(Item={
                    'PK': f"STREAM#{stream_id}",
                    'SK': f"VERSION#{version:020d}",
                    'GSI1PK': 'EVENTS',
                    'GSI1SK': datetime.utcnow().isoformat(),
                    'event_id': str(uuid.uuid4()),
                    'event_type': event['type'],
                    'event_data': json.dumps(event['data']),
                    'version': version,
                })

    def read_stream(self, stream_id: str, from_version: int = 0):
        resp = self.table.query(
            KeyConditionExpression=
                Key('PK').eq(f"STREAM#{stream_id}") &
                Key('SK').gte(f"VERSION#{from_version:020d}")
        )
        return [
            {'event_type': item['event_type'],
             'data': json.loads(item['event_data']),
             'version': item['version']}
            for item in resp['Items']
        ]
```

**DynamoDB table design:** PK=`STREAM#{id}`, SK=`VERSION#{version}`, GSI1 for global ordering.

## Best Practices

### Do

- **Name streams `{Type}-{id}`** — e.g., `Order-abc123`
- **Include correlation / causation IDs** in metadata for tracing
- **Version event schemas from day one** — plan for evolution
- **Implement idempotent writes** — use event IDs for deduplication
- **Index for your query patterns** — stream, global position, event type

### Don't

- **Mutate or delete events** — they are immutable facts
- **Store large payloads** — keep events small; reference blobs externally
- **Skip optimistic concurrency** — prevents data corruption
- **Ignore backpressure** — handle slow consumers gracefully
- **Couple projections to the write model** — projections should be independently deployable

## NEVER Do

- **NEVER update or delete events** — Events are immutable historical facts; create compensating events instead
- **NEVER skip version checks on append** — Optimistic concurrency prevents lost updates and corruption
- **NEVER embed large blobs in events** — Store blobs externally, reference by ID in the event
- **NEVER use random UUIDs for event IDs without idempotency checks** — Retries create duplicates
- **NEVER read projections for command validation** — Use the event stream as the source of truth
- **NEVER couple projections to the write transaction** — Projections must be rebuildable independently
