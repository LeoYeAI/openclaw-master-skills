---
name: neolata-mem
version: 0.8.4
description: Graph-native memory engine for AI agents — hybrid vector+keyword search, biological decay, Zettelkasten linking, trust-gated conflict resolution, explainability, episodes, compression & consolidation. Zero dependencies. npm install and go.
metadata:
  openclaw:
    requires:
      bins:
        - node
    optionalEnv:
      - OPENAI_API_KEY           # For OpenAI embeddings/extraction (read by code)
      - OPENCLAW_GATEWAY_TOKEN   # For OpenClaw LLM gateway routing (read by code)
      - NVIDIA_API_KEY           # For NVIDIA NIM embeddings (passed via config)
      - AZURE_API_KEY            # For Azure OpenAI embeddings (passed via config)
      - SUPABASE_URL             # For Supabase storage backend (passed via config)
      - SUPABASE_KEY             # Supabase anon key — prefer over service key (passed via config)
    dataFlow:
      local:
        - "Default: JSON files in ./neolata-mem-data/ (configurable dir)"
        - "In-memory mode: storage.type='memory' — nothing written to disk"
      remote:
        - "Supabase: if storage.type='supabase', memories are stored/read from your Supabase project"
        - "Embeddings: if configured, text is sent to OpenAI/NVIDIA/Azure/Ollama for vectorization"
        - "LLM: if configured, text sent to OpenAI/OpenClaw/Ollama for extraction/compression/evolution"
        - "Webhooks: if webhookWritethrough is enabled, each store event POSTs to the configured URL"
      note: "No data leaves the host unless you explicitly configure a remote backend, embedding provider, LLM, or webhook. Default config is fully local (JSON storage + no embeddings)."
    securityNotes:
      - "Prefer Supabase anon key + RLS over service key — service key bypasses row-level security"
      - "Webhook URLs are an explicit exfiltration surface — only configure trusted endpoints"
      - "Test with storage.type='memory' first to evaluate without persisting any data"
      - "All env vars except OPENAI_API_KEY and OPENCLAW_GATEWAY_TOKEN are passed via config objects, not read from env directly"
    license: Elastic-2.0
    homepage: https://github.com/Jeremiaheth/neolata-mem
    repository: https://github.com/Jeremiaheth/neolata-mem
---

# neolata-mem — Agent Memory Engine

Graph-native memory for AI agents with hybrid search, biological decay, and zero infrastructure.

**npm package:** `@jeremiaheth/neolata-mem`
**Repository:** [github.com/Jeremiaheth/neolata-mem](https://github.com/Jeremiaheth/neolata-mem)
**License:** Elastic-2.0 | **Tests:** 367/367 passing (34 files) | **Node:** ≥18

## When to Use This Skill

Use neolata-mem when you need:
- **Persistent memory across sessions** that survives context compaction
- **Semantic search** over stored facts, decisions, and findings
- **Memory decay** so stale information naturally fades
- **Multi-agent memory** with cross-agent search and graph linking
- **Conflict resolution** — detect and evolve contradictory memories

Do NOT use if:
- You only need OpenClaw's built-in `memorySearch` (keyword + vector on workspace files)
- You want cloud-hosted memory (use Mem0 instead)
- You need a full knowledge graph database (use Graphiti + Neo4j)

## Install

```bash
npm install @jeremiaheth/neolata-mem
```

No Docker. No Python. No Neo4j. No cloud API required.

> **Supply-chain verification:** This package has zero runtime dependencies and no install scripts. Verify before installing:
> ```bash
> # Check for install scripts (should show only "test"):
> npm view @jeremiaheth/neolata-mem scripts
> # Check for runtime deps (should be empty):
> npm view @jeremiaheth/neolata-mem dependencies
> # Audit the tarball contents (15 files, ~40 kB):
> npm pack @jeremiaheth/neolata-mem --dry-run
> ```
> Source is fully auditable at [github.com/Jeremiaheth/neolata-mem](https://github.com/Jeremiaheth/neolata-mem).

## Security & Data Flow

**Default configuration is fully local** — JSON files on disk, no network calls, no embeddings, no external services.

Data only leaves the host if you **explicitly configure** one of these:

| Feature | What leaves | Where it goes | How to avoid |
|---------|------------|---------------|-------------|
| Embeddings (OpenAI/NVIDIA/Azure) | Memory text | Embedding API endpoint | Use `noop` embeddings or Ollama (local) |
| LLM (OpenAI/OpenClaw/Ollama) | Memory text for extraction/compression | LLM API endpoint | Don't configure `llm` option, or use Ollama |
| Supabase storage | All memory data | Your Supabase project | Use `json` or `memory` storage (default) |
| Webhook writethrough | Store/decay event payloads | Your webhook URL | Don't configure `webhookWritethrough` |

**Key security properties:**
- Only 2 env vars are read directly by code: `OPENAI_API_KEY` and `OPENCLAW_GATEWAY_TOKEN`. All others (Supabase, NVIDIA, Azure) are passed via explicit config objects.
- All provider URLs are validated against SSRF (private IPs blocked, cloud metadata blocked).
- Supabase: prefer anon key + RLS over service key. Service key bypasses row-level security.
- JSON storage uses atomic writes (temp file + rename) to prevent corruption.
- All user content sent to LLMs is XML-fenced with injection guards.
- Test safely with `storage: { type: 'memory' }` — nothing touches disk or network.

See `docs/guide.md § Security` for the full security model.

## Quick Start (Zero Config)

```javascript
import { createMemory } from '@jeremiaheth/neolata-mem';

const mem = createMemory();
await mem.store('agent-1', 'User prefers dark mode');
const results = await mem.search('agent-1', 'UI preferences');
```

Works immediately with local JSON storage and keyword search. No API keys needed.

## With Semantic Search

```javascript
const mem = createMemory({
  embeddings: {
    type: 'openai',
    apiKey: process.env.OPENAI_API_KEY,
    model: 'text-embedding-3-small',
  },
});

// Agent IDs like 'kuro' and 'maki' are just examples — use any string.
await mem.store('kuro', 'Found XSS in login form', { category: 'finding', importance: 0.9 });
const results = await mem.search('kuro', 'security vulnerabilities');
```

Supports **5+ embedding providers**: OpenAI, NVIDIA NIM, Ollama, Azure, Together, or any OpenAI-compatible endpoint.

## Key Features

### Hybrid Search (Vector + Keyword Fallback)
Uses semantic similarity when embeddings are configured; falls back to tokenized keyword matching when they're not:
```javascript
// With embeddings → vector cosine similarity search
// Without embeddings → normalized keyword matching (stop word removal, lowercase, dedup)
const results = await mem.search('agent', 'security vulnerabilities');
```

Keyword search uses an inverted token index for O(1) lookups. When >500 memories exist, vector search pre-filters candidates using token overlap before cosine similarity (candidate narrowing).

### Biological Decay
Memories fade over time unless reinforced. Old, unaccessed memories naturally lose relevance:
```javascript
await mem.decay();        // Run maintenance — archive/delete stale memories
await mem.reinforce(id);  // Boost a memory to resist decay
```

### Memory Graph (Zettelkasten Linking)
Every memory is automatically linked to related memories by semantic similarity:
```javascript
const links = await mem.links(memoryId);     // Direct connections
const path = await mem.path(idA, idB);       // Shortest path between memories
const clusters = await mem.clusters();        // Detect topic clusters
```

### Conflict Resolution & Quarantine
Detect contradictions before storing — with claim-based structural detection or LLM-based semantic detection:
```javascript
// Structural (no LLM needed): claim-based conflict detection
await mem.store('agent', 'Server uses port 443', {
  claim: { subject: 'server', predicate: 'port', value: '443' },
  provenance: { source: 'user_explicit', trust: 1.0 },
  onConflict: 'quarantine',  // low-trust conflicts quarantined for review
});

// Semantic (requires LLM): LLM classifies as conflict/update/novel
await mem.evolve('agent', 'Server now uses port 8080');

// Review quarantined memories
const quarantined = await mem.listQuarantined();
await mem.reviewQuarantine(quarantined[0].id, { action: 'activate' });
```

### Predicate Schema Registry
Define per-predicate rules for conflict handling, normalization, and deduplication:
```javascript
const mem = createMemory({
  predicateSchemas: {
    'preferred_language': { cardinality: 'single', conflictPolicy: 'supersede', normalize: 'lowercase_trim' },
    'spoken_languages':   { cardinality: 'multi', dedupPolicy: 'corroborate' },
    'salary':             { cardinality: 'single', conflictPolicy: 'require_review', normalize: 'currency' },
  },
});
```

Options: `cardinality` (single/multi), `conflictPolicy` (supersede/require_review/keep_both), `normalize` (none/trim/lowercase/lowercase_trim/currency), `dedupPolicy` (corroborate/store).

### Explainability API
Understand why search returned or filtered specific memories:
```javascript
const results = await mem.search('agent', 'query', { explain: true });
console.log(results.meta);        // query options, result count
console.log(results[0].explain);  // retrieved, rerank, statusFilter details

const detail = await mem.explainMemory(memoryId);
// { id, status, trust, confidence, provenance, claimSummary }
```

### Multi-Agent Support
```javascript
await mem.store('kuro', 'Vuln found in API gateway');
await mem.store('maki', 'API gateway deployed to prod');
const all = await mem.searchAll('API gateway');  // Cross-agent search
```

### Episodes (Temporal Grouping)
Group related memories into named episodes:
```javascript
const ep = await mem.createEpisode('Deploy v2.0', [id1, id2, id3], { tags: ['deploy'] });
const ep2 = await mem.captureEpisode('kuro', 'Standup', { start: '...', end: '...' });
const results = await mem.searchEpisode(ep.id, 'database migration');
const { summary } = await mem.summarizeEpisode(ep.id);  // requires LLM
```

### Memory Compression & Consolidation
Consolidate redundant memories into digests:
```javascript
await mem.compress([id1, id2, id3], { method: 'llm', archiveOriginals: true });
await mem.compressEpisode(episodeId);
await mem.autoCompress({ minClusterSize: 3, maxDigests: 5 });

// Full maintenance: dedup → contradictions → corroborate → compress → prune
await mem.consolidate({ dedupThreshold: 0.95, compressAge: 30, pruneAge: 90 });
```

### Labeled Clusters
Persistent named groups:
```javascript
await mem.createCluster('Security findings', [id1, id2]);
await mem.autoLabelClusters();  // LLM labels unlabeled clusters
```

### Event Emitter
Hook into the memory lifecycle:
```javascript
mem.on('store', ({ agent, content, id }) => { /* ... */ });
mem.on('search', ({ agent, query, results }) => { /* ... */ });
mem.on('decay', ({ archived, deleted, dryRun }) => { /* counts, not arrays */ });
```

### Batch APIs
Amortize embedding calls and I/O with bulk operations:
```javascript
// Store many memories in one call (single embed batch + single persist)
const result = await mem.storeMany('agent', [
  { text: 'Fact one', category: 'fact', importance: 0.8 },
  { text: 'Fact two', tags: ['infra'] },
  'Plain string also works',
]);
// { total: 3, stored: 3, results: [{ id, links }, ...] }

// Search multiple queries in one call (single embed batch)
const results = await mem.searchMany('agent', ['query one', 'query two']);
// [{ query: 'query one', results: [...] }, { query: 'query two', results: [...] }]
```

Batch operations include:
- Atomic rollback on persist failure (memories, indexes, backlinks all reverted)
- Cross-linking within the same batch
- Configurable caps: `maxBatchSize` (default 1000), `maxQueryBatchSize` (default 100)

### Bulk Ingestion with Fact Extraction
Extract atomic facts from text using an LLM, then store each with A-MEM linking:
```javascript
const mem = createMemory({
  embeddings: { type: 'openai', apiKey: process.env.OPENAI_API_KEY },
  extraction: { type: 'llm', apiKey: process.env.OPENAI_API_KEY },
});

const result = await mem.ingest('agent', longText);
// { total: 12, stored: 10, results: [...] }
```

## CLI

```bash
npx neolata-mem store myagent "Important fact here"
npx neolata-mem search myagent "query"
npx neolata-mem decay --dry-run
npx neolata-mem health
npx neolata-mem clusters
```

## OpenClaw Integration

neolata-mem complements OpenClaw's built-in `memorySearch`:
- **memorySearch** = searches your workspace `.md` files (BM25 + vector)
- **neolata-mem** = structured memory store with graph, decay, evolution, multi-agent

Use both together: memorySearch for workspace file recall, neolata-mem for agent-managed knowledge.

### Recommended Setup

In your agent's daily cron or heartbeat:
```javascript
// Store important facts from today's session
await mem.store(agentId, 'Key decision: migrated to Postgres', {
  category: 'decision',
  importance: 0.8,
  tags: ['infrastructure'],
});

// Run decay maintenance
await mem.decay();
```

## Comparison

| Feature | neolata-mem | Mem0 | OpenClaw memorySearch |
|---------|:-----------:|:----:|:---------------------:|
| Local-first (data stays on machine) | ✅ (default) | ❌ | ✅ |
| Hybrid search (vector + keyword) | ✅ | ❌ | ✅ |
| Memory decay | ✅ | ❌ | ❌ |
| Memory graph / linking | ✅ | ❌ | ❌ |
| Conflict resolution | ✅ | Partial | ❌ |
| Quarantine lane | ✅ | ❌ | ❌ |
| Predicate schemas | ✅ | ❌ | ❌ |
| Explainability API | ✅ | ❌ | ❌ |
| Episodes & compression | ✅ | ❌ | ❌ |
| Labeled clusters | ✅ | ❌ | ❌ |
| Multi-agent | ✅ | ✅ | Per-agent |
| Zero infrastructure | ✅ | ❌ | ✅ |
| Event emitter | ✅ | ❌ | ❌ |
| Batch APIs (storeMany/searchMany) | ✅ | ❌ | ❌ |
| npm package | ✅ | ✅ | Built-in |

## Security

neolata-mem includes hardening against common agent memory attack vectors:

- **Prompt injection mitigation**: XML-fenced user content in all LLM prompts + structural output validation
- **Input validation**: Agent names (alphanumeric, max 64), text length caps (10KB), bounded memory count (50K), batch size caps (1000 store / 100 query)
- **Batch atomicity**: `storeMany` rolls back all memories, indexes, and backlinks on persist failure
- **SSRF protection**: All provider URLs validated via `validateBaseUrl()` — blocks cloud metadata endpoints (`169.254.169.254`), private IP ranges, non-HTTP protocols
- **Supabase hardening**: UUID validation on query params, error text sanitized (strips tokens/keys), upsert-based save (crash-safe), 429 retry with backoff
- **Atomic writes**: Write-to-temp + rename prevents file corruption
- **Path traversal guards**: Storage directories and write-through paths validated with `resolve()` + prefix checks
- **Cryptographic IDs**: `crypto.randomUUID()` — no predictable memory references
- **Retry bounds**: Exponential backoff with max 3 retries on 429s
- **Error surfacing**: Failed conflict detection returns `{ error }` instead of silent fallthrough

**Supabase key guidance:** Prefer the anon key with Row Level Security (RLS) policies over the service role key. The service key bypasses RLS and grants full access to all stored memories. Only use it for admin/migration tasks.

See the [full security section](docs/guide.md#security) for details.

### Data Residency & External API Usage

**Local-only mode** (default): Memories are stored as JSON at `./neolata-mem-data/graph.json` (relative to CWD). No data leaves your machine. Keyword search works without any API keys.

**With embeddings/extraction/LLM**: When you configure an external provider (OpenAI, NIM, Ollama, etc.), your memory text is sent to that provider's API for embedding or extraction. This is opt-in — you must explicitly provide an API key and base URL.

| Mode | Data sent externally? | Storage location |
|------|:---------------------:|------------------|
| Default (no config) | ❌ No | `./neolata-mem-data/graph.json` |
| Ollama embeddings | ❌ No (local) | `./neolata-mem-data/graph.json` |
| OpenAI/NIM embeddings | ⚠️ Memory text → provider | `./neolata-mem-data/graph.json` |
| Supabase storage | ⚠️ All data → Supabase | Supabase PostgreSQL |
| LLM conflict resolution | ⚠️ Memory text → provider | Storage unchanged |

**To keep all data local**: Use Ollama for embeddings and JSON storage. No API keys needed for keyword-only search.

## Links

- **npm:** [@jeremiaheth/neolata-mem](https://www.npmjs.com/package/@jeremiaheth/neolata-mem)
- **GitHub:** [Jeremiaheth/neolata-mem](https://github.com/Jeremiaheth/neolata-mem)
- **Full docs:** See `docs/guide.md` in the package
