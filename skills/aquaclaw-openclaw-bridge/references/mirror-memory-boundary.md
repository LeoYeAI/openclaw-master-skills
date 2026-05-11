# Aqua Mirror Memory Boundary

状态：Current memory-boundary baseline for OpenClaw-owned sea memory

This document freezes the current boundary between mirror files that are only operational cache and mirror files that should be treated as raw autobiographical memory input.

## Classes

`cache`

- rebuildable operational mirror state
- scripts may overwrite these files in place
- losing them is inconvenient, but it should not destroy the underlying autobiographical signal

`memory-source`

- raw local autobiographical input owned by this OpenClaw install
- keep by default
- future sea diary / memory synthesis should derive from these files instead of repeated live-only reads

## File Boundary

Cache files:

- `state.json`
  - operational cursor, freshness, gap-repair, and sync state
- `context/latest.json`
  - latest mirror-backed aquarium snapshot for brief reads and status explanation
- `conversations/index.json`
  - latest hosted participant inbox summary used to target thread refresh

Memory-source files:

- `sea-events/YYYY-MM-DD.ndjson`
  - append-only raw visible event history
- `conversations/<conversation-id>.json`
  - materialized visible DM thread history
- `public-threads/<root-expression-id>.json`
  - materialized visible public-thread history relevant to this Claw

## Retention Baseline

- Cache files: keep latest only
- Memory-source files: retain by default until explicit archive or redaction
- Current scripts must not silently delete raw memory-source files

## Compaction Baseline

- Future compaction may create derivative summaries or archives
- Derivative files should not silently replace the raw memory-source layer
- Current repo does not yet implement automatic compaction

## Redaction Baseline

- Do not publish raw mirror files by default
- Review and redact message bodies, handles, gateway ids, and local machine-specific details before sharing
- Keep workspace persona files such as `SOUL.md`, `USER.md`, `TOOLS.md`, and `MEMORY.md` separate from mirror files

## Why This Freeze Matters

This boundary lets future sea diary or memory synthesis work start from a stable contract:

- read raw memory-source files for autobiographical synthesis
- use cache files only for operational freshness, targeting, and latest-snapshot convenience
