# Event Store

Guide to designing event stores for event-sourced applications — covering event schemas, projections, snapshotting, and CQRS integration.

## What's Inside

- Event Store Architecture — streams, global position, requirements
- Technology Comparison — EventStoreDB, PostgreSQL, Kafka, DynamoDB
- Event Schema Design — envelope structure, schema evolution rules
- PostgreSQL Event Store Schema — events, snapshots, subscription checkpoints
- Event Store Implementation — append with optimistic concurrency, read stream, read all (Python)
- Projections — lifecycle, idempotent handlers, design rules, projection example
- Snapshotting — snapshot flow, aggregate rehydration optimization
- CQRS Integration — write/read separation, command handler pattern
- EventStoreDB Integration example (Python)
- DynamoDB Event Store Implementation with single-table design

## When to Use

- Designing event sourcing infrastructure
- Choosing between event store technologies
- Implementing custom event stores
- Building projections from event streams
- Adding snapshotting for aggregate performance
- Integrating CQRS with event sourcing

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/backend/event-store
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/backend/event-store .cursor/skills/event-store
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/backend/event-store ~/.cursor/skills/event-store
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/backend/event-store .claude/skills/event-store
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/backend/event-store ~/.claude/skills/event-store
```

## Related Skills

- `architecture-patterns` — Clean Architecture and DDD foundations for event sourcing
- `microservices-patterns` — Saga pattern and distributed transactions with events

---

Part of the [Backend](..) skill category.
