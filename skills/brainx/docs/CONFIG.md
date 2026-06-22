# Configuration

BrainX V5 is configured through environment variables.

Recommended workflow:

- keep a local `.env` for development
- for production/system services, inject env vars via your process manager (systemd, Railway, Docker, etc.)

## Required

### `DATABASE_URL`

Postgres connection string.

Example:

```bash
DATABASE_URL=postgresql://brainx:brainx_change_me@127.0.0.1:5432/brainx
```

Note:
- existing deployments may still use a legacy physical database name such as `brainx_v4`
- that naming drift does not block BrainX V5 itself, but docs and code should not assume a specific DB name unless a migration was actually executed

### `OPENAI_API_KEY`

Used by `lib/openai-rag.js` to call the OpenAI embeddings endpoint.

## Embeddings

### `OPENAI_EMBEDDING_MODEL`

Default: `text-embedding-3-small`

### `OPENAI_EMBEDDING_DIMENSIONS`

Default: `1536`

Must match the schema type:

- `brainx_memories.embedding vector(1536)`

If you change dimensions:

1. change schema
2. rebuild embeddings for existing rows

## Shared env file

### `BRAINX_ENV`

Path to a shared env file.

`lib/db.js` and `lib/openai-rag.js` both support loading env from `BRAINX_ENV` if the main variables are missing.

This is useful when multiple agents share one secrets file.

## Inject formatting

### `BRAINX_INJECT_DEFAULT_TIER`

Default: `warm_or_hot`.

If unset and you don’t pass `--tier`, the inject command:

1. searches `hot`
2. searches `warm`
3. merges results unique by id

### `BRAINX_INJECT_MAX_CHARS_PER_ITEM`

Default: `2000`.

### `BRAINX_INJECT_MAX_LINES_PER_ITEM`

Default: `80`.
