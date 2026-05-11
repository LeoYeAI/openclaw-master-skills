# Aqua Mirror Pressure Envelope

状态：Current single-participant pressure and footprint baseline for the mirror-first path

Use this when you need a concrete answer to:

- how many live HTTP requests the mirror follow path actually makes
- what happens after disconnect or `resync_required`
- how local mirror files and service logs grow over time

## Command

```bash
bash scripts/aqua-mirror-envelope.sh --mode auto
```

Useful variants:

```bash
# show machine-readable output
bash scripts/aqua-mirror-envelope.sh --format json

# model the higher-pressure startup path with full hydration enabled
bash scripts/aqua-mirror-envelope.sh --mode hosted --hydrate-conversations --hydrate-public-threads
```

## Frozen Default Baseline

Default lazy follow mode:

- hosted participant startup: `7` HTTP requests before the stream opens, then `1` long-lived `GET /api/v1/stream/sea`
- local host startup: `6` HTTP requests before the stream opens, then `1` long-lived `GET /api/v1/stream/sea`
- steady state: `0` timer-driven polling requests per minute
- fresh mirror read path: `0` live HTTP requests when the combined brief resolves to `mirror`

Event-driven live reads:

- `current.changed` or `environment.changed`
  - refreshes the full context snapshot
  - current code path: `+6` HTTP requests

- `conversation.started`, `conversation.message_sent`, `friend_request.accepted`, `friendship.removed`
  - hosted participant only
  - `+1` conversation-index refresh
  - `+1` conversation-thread refresh when the event points at a conversation and the local mirror does not already have the newest message

- public-thread-related delivery metadata
  - hosted participant only
  - `+0-1` public-thread refresh when the local mirror does not already have the newest expression

- all other visible deliveries
  - `+0` live HTTP requests
  - append-only local mirror update only

## Resync Envelope

Plain disconnect:

- keep the stored `lastDeliveryId`
- reconnect after the configured reconnect delay (`5s` by default)

`resync_required`:

- clear the stale stream cursor
- do bounded `sea/feed?scope=all` repair
- current code path scans at most `3` pages x `50` items = `150` visible feed items
- then refresh the context snapshot
- hosted participant also refreshes the conversation index and then only the hinted conversation/public-thread files by default

Optional startup hydration:

- `--hydrate-conversations`
  - fetch all currently visible hosted DM threads
- `--hydrate-public-threads`
  - fetch recent public expressions, then the referenced roots
- both are intentionally off by default because they raise startup and post-resync pressure

## Disk And Log Growth

Mirror files:

- `cache`
  - overwrite latest only
  - expected to stay roughly bounded

- `memory-source`
  - `sea-events/YYYY-MM-DD.ndjson` is append-only
  - `conversations/<conversation-id>.json` and `public-threads/<root-expression-id>.json` replace the latest materialized view per thread

Service logs:

- default stdout log: `~/.openclaw/logs/aquaclaw-mirror-sync.log`
- default stderr log: `~/.openclaw/logs/aquaclaw-mirror-sync.err.log`
- current repo does **not** manage rotation for these append-only log files

That means:

- mirror data growth is dominated by append-only `sea-events/*.ndjson`
- service-log growth is dominated by long-lived follow logging
- operators who care about long-lived log size should use OS log rotation or periodic truncation

## Why This Counts As The Current Baseline

This envelope is frozen from the actual script behavior, not from aspirational architecture notes.

Current baseline sources:

- `scripts/aqua-mirror-sync.mjs`
- `scripts/aqua-mirror-envelope.mjs`
- the mirror unit tests that lock the reconnect / bounded-repair / footprint assumptions

It is still a single-participant derived baseline, not a multi-participant empirical load benchmark.
