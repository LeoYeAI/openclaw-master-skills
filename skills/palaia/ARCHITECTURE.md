# Palaia Architecture

## Overview

Palaia is a local, crash-safe memory system for AI agents. Zero hard dependencies — runs on Python stdlib alone.

## Core Design Decisions

| ADR | Topic | Status |
|-----|-------|--------|
| [001](docs/adr/001-semantic-search-tiered.md) | Tiered Semantic Search | Accepted |
| [002](docs/adr/002-scope-tags-knowledge-transfer.md) | Scope Tags + Knowledge Transfer | Accepted |
| [003](docs/adr/003-wal-protocol.md) | WAL Protocol | Accepted |
| [004](docs/adr/004-hot-warm-cold-tiering.md) | HOT/WARM/COLD Tiering | Accepted |
| [005](docs/adr/005-git-as-knowledge-exchange.md) | Git as Knowledge Exchange | Accepted |
| [006](docs/adr/006-memory-entry-format.md) | Memory Entry Format | Accepted |
| [007](docs/adr/007-concurrent-write-locking.md) | Concurrent Write Locking | Accepted |

## Directory Structure

```
.palaia/
├── config.json          # Configuration
├── .lock                # Advisory file lock
├── hot/                 # Active memories (< 7 days or high score)
│   └── <uuid>.md
├── warm/                # Occasional access (7-30 days)
│   └── <uuid>.md
├── cold/                # Archive (> 30 days)
│   └── <uuid>.md
├── wal/                 # Write-Ahead Log entries
│   └── <timestamp>-<uuid>.json
└── index/               # Search index (future: embeddings cache)
```

## Module Map

```
palaia/
├── __init__.py     # Version
├── cli.py          # CLI entry point (argparse)
├── config.py       # Configuration loading/saving
├── decay.py        # Decay scoring + tier classification
├── entry.py        # Memory entry format (YAML frontmatter + markdown)
├── lock.py         # File-based locking (fcntl)
├── scope.py        # Scope validation + access control
├── search.py       # BM25 search + tier detection
├── store.py        # Core store (read/write/list/gc) with WAL integration
└── wal.py          # Write-Ahead Log
```

## Data Flow

### Write Path
```
1. Dedup check (content hash)
2. Acquire file lock
3. WAL: log pending entry (with payload)
4. Write .md file to hot/ (atomic: write tmp → rename)
5. WAL: mark committed
6. Release lock
```

### Read Path
```
1. Find entry across tiers (hot → warm → cold)
2. Check scope permissions
3. Update access metadata (timestamp, count, decay score)
4. Return (meta, body)
```

### Search Path
```
1. Build BM25 index from hot + warm (+ cold if --all)
2. Tokenize query
3. Score documents
4. Return top-K with metadata
```

### GC / Tier Rotation
```
1. Acquire lock
2. For each entry across all tiers:
   a. Calculate days_since_access
   b. Recalculate decay_score
   c. Classify into target tier
   d. Move file if tier changed
3. Cleanup old WAL entries
4. Release lock
```

## Crash Safety

The WAL guarantees that no write is lost:
- Every write logs intent + payload to WAL before touching data
- On startup, `recover()` replays any pending entries
- Atomic file writes (tmp + rename) prevent partial writes
- File locking prevents concurrent corruption

## Architecture Review Notes (Elliot, 2026-03-11)

### What's solid
- Tiered search (ADR-001) is the right approach — graceful degradation
- Scope model (ADR-002) is clean and sufficient for MVP
- Git exchange (ADR-005) is pragmatic

### Gaps identified and addressed
- **ADR-006 (new):** Memory entry format was implicit — now explicit with YAML frontmatter spec
- **ADR-007 (new):** Concurrent write locking was an open question in ADR-003 — resolved with fcntl

### Future considerations (post-MVP)
- **Memory compression for COLD tier** — Could summarize old memories to save space. Not needed for MVP since .md files are tiny.
- **Plugin system** — Custom search backends, storage backends. Overkill for now, but the module structure supports it.
- **Conflict resolution** — For git import, last-write-wins with dedup by content hash. Sufficient for MVP.
- **Embedding cache** — When Tier 2/3 search is implemented, cache embeddings in index/ to avoid recomputation.
