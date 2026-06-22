# Tests

## `tests/smoke.js`

A basic health check for:

- database connectivity
- pgvector extension installed
- schema installed (counts `brainx_*` tables)

Run:

```bash
node tests/smoke.js
# or
pnpm test
```

## `tests/rag.js`

A minimal end-to-end RAG test:

- stores a small `note` memory
- searches with a related query
- prints the top results

Run:

```bash
node tests/rag.js
```

Notes:

- Requires `OPENAI_API_KEY` and a working `DATABASE_URL`.
