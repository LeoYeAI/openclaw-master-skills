# SignalRadar Operations Reference

## Decision Outcomes

- `BASELINE`: first observation; write baseline; do not push.
- `SILENT`: change below threshold; do not push.
- `HIT`: threshold crossed; emit `SignalEvent`; route delivery; update baseline.

## Time Rules

- Internal storage timestamps: UTC only.
- User-facing render: `UTC + user timezone`.

## Observability Minimum

Every event record must include:

- `request_id`
- `entry_id`
- decision outcome
- route target
- delivery result
- UTC timestamp

Recommended append-only file:

- `~/.signalradar/cache/events/signal_events.jsonl`

## SLO (Rolling 24h)

- Delivery success rate >= 98%
- p95 end-to-end latency < 30s
- Trace completeness = 100%

## Retry and Degrade

- Retry upstream/timeouts with bounded exponential backoff.
- On exhausted retries: return structured error and degrade gracefully.
- Do not silently drop critical failures.
