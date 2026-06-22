# Architecture (BrainX V5)

BrainX V5 is a lightweight memory service implemented as:

- **PostgreSQL** for storage + metadata filters
- **pgvector** for vector similarity search
- **OpenAI embeddings API** to generate vectors
- A small **Node.js CLI** to write/search/inject memory into prompts

This repo is intentionally minimal: it can be embedded into larger systems (e.g. OpenClaw) without running a dedicated HTTP service.

## High-level components

### 1) CLI entrypoints

- `./brainx-v5` (bash wrapper)
  - `health` → runs `tests/smoke.js`
  - `add|search|inject` → runs `lib/cli.js`

### 2) CLI implementation

- `lib/cli.js`
  - `add`: validates input, generates an id, calls `openai-rag.storeMemory()`
  - `search`: calls `openai-rag.search()` and prints JSON
  - `inject`: calls `search()` and prints a **prompt-ready text block** with metadata headers per item

### 3) Storage + vector search

- `lib/openai-rag.js`
  - `embed(text)` → calls `POST https://api.openai.com/v1/embeddings`
  - `storeMemory(memory)` → inserts/updates `brainx_memories` (with `embedding`)
  - `search(query, opts)` → embeds query, runs SQL with pgvector distance operator, applies filters, orders by `score`

### 4) Database layer

- `lib/db.js`
  - wraps a `pg.Pool`
  - exposes `query()` and `health()`

## Execution flow

### Add

1. CLI receives `--type`, `--content`, etc.
2. `openai-rag.storeMemory()`:
   - builds an embedding input string: `"${type}: ${content} [context: ${context}]"`
   - calls OpenAI embeddings
   - upserts into `brainx_memories`

### Search

1. `openai-rag.search()` embeds the query
2. SQL ranks candidates using:
   - cosine similarity (via `1 - (embedding <=> query_embedding)`)
   - importance boost
   - tier boost/penalty
3. Results are returned (and filtered by `minSimilarity` in JS)
4. Access tracking updates `last_accessed` and increments `access_count`

### Inject

Same as search, but output is formatted for direct prompt injection:

- Each memory is printed as:

```
[sim:0.62 imp:9 tier:hot type:decision agent:coder ctx:openclaw]
<content...>
```

## Filters and ranking

### Filters

`search()` supports:

- `minImportance`
- `tierFilter` (exact tier)
- `contextFilter` (exact context)
- excludes superseded memories: `superseded_by IS NULL`

### Ranking

Current SQL uses a composite score:

- base: similarity
- plus: `(importance/10) * 0.25`
- plus: tier adjustment:
  - hot +0.15
  - warm +0.05
  - cold -0.05
  - archive -0.10

This is intentionally simple and easy to tune.

## Environment

Common env vars (see `.env.example`):

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_EMBEDDING_DIMENSIONS` (must match schema vector dim)

Optional:

- `BRAINX_ENV` path to an env file to load from multiple processes
- `BRAINX_INJECT_DEFAULT_TIER` (`warm_or_hot` by default)
- `BRAINX_INJECT_MAX_CHARS_PER_ITEM`
- `BRAINX_INJECT_MAX_LINES_PER_ITEM`

## Design notes / tradeoffs

- No HTTP service by default: easier to run locally, in cron jobs, or as a library.
- `context` filtering is exact-match right now (simple + predictable).
- `superseded_by` enables cheap “soft delete” / dedup without losing history.

## Recommended next improvements (optional)

- Make vector dimension configurable end-to-end (schema + code) without manual edits.
- Add migrations tool (e.g. `node scripts/migrate.js`).
- Add a proper “learning” write path using `brainx_learning_details`.
- Add “context packs” builder and snapshot summarizer.
