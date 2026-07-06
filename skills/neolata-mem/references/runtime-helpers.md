# Runtime Helpers ΓÇö `src/runtime.mjs`

Session-aware utilities for detecting key moments, storing memories during heartbeats, recalling context, and dumping state before compaction.

All functions are re-exported from `src/index.mjs`.

---

## `detectKeyMoments(text, { role? })`

Scans text for pattern-matched key moments.

**Returns:** `Array<{ type, text, importance }>`

| Type | Importance | Trigger patterns |
|------|-----------|-----------------|
| `decision` | 0.9 | "Decision:", "We decided", "Going with", "Let's do", "Ship it" |
| `commitment` | 0.8 | "I will", "We will", "TODO:", "Action item:" |
| `blocker` | 0.85 | "Blocked by", "Blocker:", "Can't proceed", "Waiting on" |
| `preference` | 0.7 | "I prefer", "I like", "I want", "Always use" |

```js
import { detectKeyMoments } from '@jeremiaheth/neolata-mem';

const moments = detectKeyMoments('Decision: use PostgreSQL. I prefer dark mode.');
// [{ type: 'decision', text: 'Decision: use PostgreSQL.', importance: 0.9 },
//  { type: 'preference', text: 'I prefer dark mode.', importance: 0.7 }]
```

---

## `heartbeatStore(mem, agent, turns, config?)`

Stores key moments from new conversation turns during periodic heartbeats. Falls back to a session snapshot if no moments are detected.

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `mem` | `MemoryGraph` | Memory instance |
| `agent` | `string` | Agent ID |
| `turns` | `Array<{ role, content, timestamp? }>` | Conversation turns |
| `config.sessionId` | `string?` | Tags memories with `session:<id>` |
| `config.topicSlug` | `string?` | Tags memories with `topic:<slug>` |
| `config.projectSlug` | `string?` | Tags memories with `project:<slug>` |
| `config.minNewTurns` | `number` | Min new turns to process (default: 3) |
| `config.lastStoredIndex` | `number` | Index of last processed turn (default: -1) |

**Returns:** `{ stored, ids, lastIndex, moments }` or `{ stored: 0, skipped: 'insufficient_turns', lastIndex }`

```js
const result = await heartbeatStore(mem, 'my-agent', turns, {
  sessionId: 'sess-abc',
  projectSlug: 'myproject',
  lastStoredIndex: 4,
});
// { stored: 2, ids: ['...', '...'], lastIndex: 9, moments: [...] }
```

---

## `extractTopicSlug(text, { synonyms? })`

Extracts the dominant topic word from text after removing stop words. Supports synonym mapping.

**Returns:** `string | null`

```js
extractTopicSlug('Fix the OCI deployment pipeline');
// 'fix' or 'oci' or 'deployment' or 'pipeline' (most frequent non-stop word)

extractTopicSlug('oracle tenancy setup', { synonyms: { oci: ['oracle', 'tenancy'] } });
// 'oci'
```

---

## `contextualRecall(mem, agent, seedText, config?)`

Multi-channel recall blending recency, semantic similarity, and importance filtering under a token budget.

**Channels:**
1. **Recency** ΓÇö latest memories (no rerank)
2. **Semantic** ΓÇö similarity to `seedText` (reranked)
3. **Importance** ΓÇö high-importance memories matching topic slug (filtered by threshold)

**Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `config.maxTokens` | `number` | 2000 | Token budget |
| `config.recentCount` | `number` | 5 | Recent memories to fetch |
| `config.semanticCount` | `number` | 8 | Semantic results to fetch |
| `config.importantCount` | `number` | 10 | Important results to fetch |
| `config.importanceThreshold` | `number` | 0.8 | Min importance for channel C |
| `config.synonyms` | `object` | `{}` | Synonym map for topic extraction |

**Returns:** `{ topicSlug, memories, totalTokens, excluded }`

```js
const ctx = await contextualRecall(mem, 'my-agent', 'database migration plan', {
  maxTokens: 1500,
});
// { topicSlug: 'database', memories: [...], totalTokens: 1200, excluded: 3 }
```

---

## `preCompactionDump(mem, agent, turns, config?)`

Extracts and stores all key moments from a full conversation before context compaction. Deduplicates moments, caps at `maxTakeaways`, and stores a structured session snapshot.

**Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `config.sessionId` | `string?` | ΓÇö | Session tag |
| `config.topicSlug` | `string?` | ΓÇö | Topic tag |
| `config.projectSlug` | `string?` | ΓÇö | Project tag |
| `config.maxTakeaways` | `number` | 10 | Max moments to store |

All stored memories are tagged with `trigger:pre-compaction`.

**Snapshot format:**
```
## Session Snapshot
**Decisions:** <texts or 'none'>
**Open threads:** <texts or 'none'>
**Commitments:** <texts or 'none'>
**Preferences:** <texts or 'none'>
```

**Returns:** `{ takeaways, snapshotId, ids }`

```js
const dump = await preCompactionDump(mem, 'my-agent', turns, {
  sessionId: 'sess-abc',
  maxTakeaways: 5,
});
// { takeaways: 4, snapshotId: '...', ids: ['...', '...', '...', '...'] }
```

---

## Integration Example

```js
import { createMemory, heartbeatStore, contextualRecall, preCompactionDump } from '@jeremiaheth/neolata-mem';

const mem = createMemory({ storage: { type: 'memory' }, embeddings: { type: 'noop' } });
const agent = 'my-agent';

// During heartbeat
const hb = await heartbeatStore(mem, agent, turns, { sessionId: 's1', lastStoredIndex: prev });

// Before responding
const ctx = await contextualRecall(mem, agent, userMessage, { maxTokens: 2000 });

// Before compaction
const dump = await preCompactionDump(mem, agent, allTurns, { sessionId: 's1' });
```
