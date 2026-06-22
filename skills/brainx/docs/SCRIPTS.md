# Scripts

This folder contains one-shot utilities for migration, imports, and cleanup.

All scripts use `dotenv/config`, so they read `.env` automatically.

## `scripts/migrate-v2-to-v3.js`

Migrates BrainX V2 JSON storage (files) into the V3 Postgres database.

### What it does

- Looks for V2 storage under `${BRAINX_V2_HOME}/storage/<tier>/*.json`
  - tiers scanned: `hot`, `warm`, `cold`
- For each file:
  - parses JSON
  - generates a stable id if missing
  - maps tier into V3 tiers
  - calls `rag.storeMemory()` to upsert into Postgres
  - if V2 has `timestamp`, it preserves it by updating `created_at` and `last_accessed`

### Env

- `BRAINX_V2_HOME` (optional)
  - default: `../../brainx-v2` relative to this repo

### Run

```bash
node scripts/migrate-v2-to-v3.js
```

## `scripts/import-workspace-memory-md.js`

Imports a `MEMORY.md` style file into V3.

### What it does

- Reads a file path (`MEMORY_MD`), defaulting to `../../../MEMORY.md`
- Splits it into ~5000 char chunks
- Stores each chunk as a `note` memory:
  - `tier=hot`, `importance=9`, `agent=system`
  - tags: `import:memory-md`, `source:workspace-coder`

### Env

- `MEMORY_MD` (optional)

### Run

```bash
node scripts/import-workspace-memory-md.js
```

## `scripts/dedup-supersede.js`

Supersedes exact duplicates (same type/content/context/agent).

### What it does

- Finds duplicates by fingerprint:
  - `md5(type|content|context|agent)`
- Keeps the oldest `created_at`
- Updates newer duplicates:
  - `superseded_by = keep_id`
  - appends tag `dedup_superseded`

### Env

- `DEDUP_DRY_RUN=true` to preview without writing.

### Run

```bash
# preview
DEDUP_DRY_RUN=true node scripts/dedup-supersede.js

# apply
node scripts/dedup-supersede.js
```

## `scripts/cleanup-low-signal.js`

Downranks or re-tiers very short/low-signal memories.

### What it does

- For memories not superseded:
  - if `length(content) <= CLEANUP_MAX_LEN`
  - and type in `decision|action|learning|note`
- then:
  - sets `tier=CLEANUP_TIER` (default `cold`)
  - clamps `importance` to `<= CLEANUP_MAX_IMPORTANCE` (default `2`)
  - adds tag `low_signal`

### Env

- `CLEANUP_MAX_LEN` (default `12`)
- `CLEANUP_TIER` (default `cold`)
- `CLEANUP_MAX_IMPORTANCE` (default `2`)

### Run

```bash
node scripts/cleanup-low-signal.js
```
