# Practical Implementation Notes — neolata-mem v0.8.1+

> Architecture & semantics reference for contributors. Code-aligned to actual method signatures in `src/graph.mjs`.

---

## 1. API Surface (exact signatures)

All methods live on the `MemoryGraph` instance returned by `createMemory()`.

### Core

| Method | Signature | Notes |
|--------|-----------|-------|
| `store` | `(agent, text, { category, importance, tags, eventTime, claim, provenance, quarantine, onConflict })` | `onConflict`: `'quarantine'` (default) or `'keep_active'` |
| `search` | `(agent, query, { limit, minSimilarity, before, after, rerank, includeAll, statusFilter, includeSuperseded, includeDisputed, includeQuarantined, sessionId, explain })` | `statusFilter` defaults to `['active']` |
| `context` | `(agent, query, { maxMemories, before, after, maxTokens, explain })` | Budget-aware packing via greedy value-density (`score/tokens`) |
| `storeMany` | `(agent, items, { embeddingBatchSize })` | Batch store; items = `[{ text, category, importance, tags, ... }]` |
| `searchMany` | `(agent, queries, { limit, minSimilarity, rerank, ... })` | Parallel multi-query search |
| `ingest` | `(agent, text, { minImportance })` | LLM extraction → structured facts → `store()` each |

### Graph & Links

| Method | Signature | Notes |
|--------|-----------|-------|
| `links` | `(memoryId)` | Returns all links for a memory |
| `traverse` | `(startId, maxHops, { types })` | Graph traversal with optional link type filter |
| `clusters` | `(minSize)` | Returns clusters of linked memories |
| `evolve` | `(agent, text, { category, importance, tags })` | Find + supersede related memory |

### Trust & Feedback

| Method | Signature | Notes |
|--------|-----------|-------|
| `reinforce` | `(memoryId, boost)` | Boost = 0.1 default. Increments `reinforcements`. |
| `dispute` | `(memoryId, { reason })` | Increments `disputes`, may quarantine. |

### Quarantine & Conflict Review

| Method | Signature | Notes |
|--------|-----------|-------|
| `listQuarantined` | `({ agent, limit })` | List quarantined memories. Limit default 50. |
| `reviewQuarantine` | `(memoryId, { action, reason })` | `action`: `'activate'` or `'reject'` |

### Explainability

| Method | Signature | Notes |
|--------|-----------|-------|
| `explainMemory` | `(memoryId)` | Trust breakdown, links, conflicts, provenance |
| `explainSupersession` | `(memoryId)` | Supersession chain + rationale |
| `search(..., { explain: true })` | — | Per-result `retrieved`/`rerank` breakdown + `meta` with counts |
| `context(..., { explain: true })` | — | Adds packing decisions + excluded-by-budget info |

### Maintenance

| Method | Signature | Notes |
|--------|-----------|-------|
| `decay` | `({ dryRun })` | Archive/delete low-strength memories, clean broken links |
| `autoCompress` | `({ maxDigests, minClusterSize, archiveOriginals, agent, method })` | `method`: `'extractive'` (default) |
| `consolidate` | `({ ... })` | Full lifecycle: dedupe → contradictions → corroboration → compress → prune |

---

## 2. Conflict Semantics (how contradictions work)

Conflicts are **deterministic**, not probabilistic. The system checks structural rules before any trust comparison.

### Resolution flow

```
store() with claim → normalize claim value
  → find existing memories with same (subject, predicate)
  → for each existing:
      1. Cardinality check: if predicate schema says "multi" → skip (no conflict)
      2. Exclusivity check: if either claim has exclusive=false → skip
      3. Validity overlap: if time windows don't overlap → skip
      4. Scope check: session-scoped claims don't conflict with global claims
      5. Dedupe check: if normalized values match → corroborate, don't create new
      6. Conflict! → apply predicate's conflictPolicy:
         - "keep_both" → record resolved conflict, store both
         - "require_review" → quarantine new + create pending_conflict
         - "supersede" → trust-gated comparison:
           - newTrust >= oldTrust → supersede old
           - newTrust < oldTrust → quarantine new + pending_conflict
```

### Predicate Schema Registry

Configured via `createMemory({ predicateSchemas: { ... } })`. In-memory map.

```js
{
  budget: {
    cardinality: 'single',       // 'single' | 'multi'
    conflictPolicy: 'supersede', // 'supersede' | 'require_review' | 'keep_both'
    normalize: 'currency',       // 'none' | 'trim' | 'lowercase' | 'lowercase_trim' | 'currency'
    dedupPolicy: 'corroborate',  // 'corroborate' | 'store'
  }
}
```

Default schema (when predicate not registered): `{ cardinality: 'single', conflictPolicy: 'supersede', normalize: 'none', dedupPolicy: 'corroborate' }`.

### Trust Computation

`computeTrust(provenance, reinforcements, disputes, ageDays)` assigns base trust by source:
- `user_explicit` → highest
- `system`, `tool_output` → medium
- `document`, `user_implicit` → lower
- `inference` → lowest

Adjusted by: `+` corroboration/reinforcements, `−` disputes, `−` age decay.

---

## 3. Reranking Formula

Search results are reranked with a weighted composite:

```
composite = 0.40 * relevance + 0.25 * confidence + 0.20 * recency + 0.15 * importance
```

- **relevance**: embedding cosine similarity
- **confidence**: trust score only (deliberately excludes importance/recency to avoid double-counting)
- **recency**: exponential decay over days
- **importance**: user/LLM-assigned 0–1

Weights are overridable via `search(..., { rerank: { relevance: 0.5, confidence: 0.2, ... } })`.

---

## 4. Context Packing

`context(agent, query, { maxTokens })`:

1. Retrieve candidates via `search()`
2. Expand 1-hop linked memories
3. Rerank combined set
4. **Greedy value-density packing**: sort by `compositeScore / estimateTokens(text)`, include until budget exhausted
5. Return formatted context string + excluded info (when `explain: true`)

`estimateTokens(text)` uses word-count heuristic (~0.75 tokens/word).

---

## 5. Integration Boundaries

**neolata-mem is a library, not a runtime.** It does not:
- Detect idle/quiet periods
- Monitor token window usage
- Trigger compaction
- Schedule heartbeats or cron jobs
- Own the conversation loop

**The host agent (e.g., OpenClaw) is responsible for:**
- Detecting when to store (idle timer, decision signals, compaction threshold)
- Calling `store()` / `ingest()` with appropriate context
- Calling `search()` / `context()` at session startup
- Running `consolidate()` / `decay()` on a schedule

See the [guide](guide.md#openclaw-integration) for the integration design.

---

## 6. Storage Backends

### JSON (local)
- `jsonStorage({ dir })` — persists memories, links, episodes, clusters, pending conflicts as separate JSON files
- Good for: development, single-agent, offline use

### Supabase (production)
- `supabaseStorage({ url, key, fetch })` — maps to `memories`, `memory_links`, `memory_archive` tables
- Supports RPC search (`search_memories_semantic`, `search_memories_global`)
- Error redaction: strips bearer tokens / JWT-like strings before surfacing errors
- Rate-limit retry built in

### In-Memory
- `memoryStorage()` — ephemeral, for testing

### BYO Storage
Implement the storage interface:
```js
{
  load(agent),           // → { memories, links }
  save(agent, data),     // persist { memories, links }
  archive(agent, ids),   // move to archive
  // + optional: loadEpisodes, saveEpisodes, loadClusters, saveClusters,
  //   loadPendingConflicts, savePendingConflicts
}
```

---

## 7. Extraction & Safety

### Extraction Pipeline
`ingest(agent, text, { minImportance })`:
1. Fences raw text in XML tags (prompt injection mitigation)
2. LLM extracts structured facts: `{ text, category, importance, tags }`
3. Filters by `minImportance`
4. Calls `store()` for each extracted fact

### Safety Controls
- **SSRF guard** (`validate.mjs`): blocks cloud metadata endpoints (`169.254.169.254`, etc.) and private IPs by default
- **Extraction fencing**: XML-wraps user content, instructs LLM not to follow embedded instructions
- **Trust-gated writes**: low-trust sources can't silently supersede high-trust memories
- **Error redaction**: Supabase storage strips credentials from error messages

---

## 8. Write-Through Hooks

Optional side-effects on memory writes:

```js
import { markdownWritethrough, webhookWritethrough } from '@jeremiaheth/neolata-mem';

createMemory({
  writethrough: [
    markdownWritethrough({ dir: './memory-log' }),    // append to daily .md files
    webhookWritethrough({ url: 'https://...' }),       // POST on each store
  ]
});
```

Events emitted: `store`, `supersede`, `quarantine`, `archive`, `decay`.

---

## 9. Database Schema (Supabase)

### Core Tables
- `memories` — id, agent_id, content, category, tags, embedding, importance, access_count, created_at, updated_at, claim, provenance, confidence, status, quarantine, reinforcements, disputes, superseded_by, supersedes
- `memory_links` — source_id, target_id, similarity, created_at
- `memory_archive` — same shape as memories (archived/deleted records)

### Support Tables (v0.8 migration)
- `pending_conflicts` — conflict records awaiting review
- `episodes` — conversation episode boundaries
- `memory_clusters` — labeled clusters with metadata

### RPC Functions
- `search_memories_semantic(query_embedding, agent_filter, match_count, similarity_threshold)` — vector similarity search
- `search_memories_global(query_embedding, match_count, similarity_threshold)` — cross-agent search

### RLS
Enabled on all tables. See `sql/migration-v0.8.sql` for policy suggestions.

---

## 10. Testing

333 tests across 29 files. Key test areas:
- `test/claims.test.mjs` — conflict semantics: exclusivity, validity overlap, scope rules, dedupe/corroboration, backwards compat
- `test/graph.test.mjs` — core store/search/context/decay/consolidate
- `test/supabase-storage.test.mjs` — storage layer
- `test/extraction.test.mjs` — LLM extraction + injection resistance
- `test/validate.test.mjs` — SSRF guard

Run: `npx vitest run`
