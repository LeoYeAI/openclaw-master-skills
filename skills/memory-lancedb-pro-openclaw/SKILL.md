---
name: memory-lancedb-pro-openclaw
description: Expert skill for memory-lancedb-pro — a production-grade LanceDB-backed long-term memory plugin for OpenClaw agents with hybrid retrieval, cross-encoder reranking, multi-scope isolation, and smart auto-capture.
triggers:
  - help me set up long-term memory for my OpenClaw agent
  - configure memory-lancedb-pro plugin
  - my agent keeps forgetting things between sessions
  - enable hybrid retrieval with BM25 and vector search
  - set up cross-encoder reranking for memory
  - how do I use memory_recall and memory_store tools
  - migrate or upgrade memory-lancedb-pro
  - configure multi-scope memory isolation per agent or user
---

# memory-lancedb-pro OpenClaw Plugin

> Skill by [ara.so](https://ara.so) — Daily 2026 Skills collection.

`memory-lancedb-pro` is a production-grade long-term memory plugin for [OpenClaw](https://github.com/openclaw/openclaw) agents. It stores preferences, decisions, and project context in a local [LanceDB](https://lancedb.com) vector database and automatically recalls relevant memories before each agent reply. Key features: hybrid retrieval (vector + BM25 full-text), cross-encoder reranking, LLM-powered smart extraction (6 categories), Weibull decay-based forgetting, multi-scope isolation (agent/user/project), and a full management CLI.

---

## Installation

### Option A: One-Click Setup Script (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/CortexReach/toolbox/main/memory-lancedb-pro-setup/setup-memory.sh -o setup-memory.sh
bash setup-memory.sh
```

Flags:
```bash
bash setup-memory.sh --dry-run       # Preview changes only
bash setup-memory.sh --beta          # Include pre-release versions
bash setup-memory.sh --uninstall     # Revert config and remove plugin
bash setup-memory.sh --selfcheck-only  # Health checks, no changes
```

The script handles fresh installs, upgrades from git-cloned versions, invalid config fields, broken CLI fallback, and provider presets (Jina, DashScope, SiliconFlow, OpenAI, Ollama).

### Option B: OpenClaw CLI

```bash
openclaw plugins install memory-lancedb-pro@beta
```

### Option C: npm

```bash
npm i memory-lancedb-pro@beta
```

> **Critical:** When installing via npm, you must add the plugin's **absolute** install path to `plugins.load.paths` in `openclaw.json`. This is the most common setup issue.

---

## Minimal Configuration (`openclaw.json`)

```json
{
  "plugins": {
    "load": {
      "paths": ["/absolute/path/to/node_modules/memory-lancedb-pro"]
    },
    "slots": { "memory": "memory-lancedb-pro" },
    "entries": {
      "memory-lancedb-pro": {
        "enabled": true,
        "config": {
          "embedding": {
            "provider": "openai-compatible",
            "apiKey": "${OPENAI_API_KEY}",
            "model": "text-embedding-3-small"
          },
          "autoCapture": true,
          "autoRecall": true,
          "smartExtraction": true,
          "extractMinMessages": 2,
          "extractMaxChars": 8000,
          "sessionMemory": { "enabled": false }
        }
      }
    }
  }
}
```

**Why these defaults:**
- `autoCapture` + `smartExtraction` → agent learns from conversations automatically, no manual calls needed
- `autoRecall` → memories injected before each reply
- `extractMinMessages: 2` → triggers in normal two-turn chats
- `sessionMemory.enabled: false` → avoids polluting retrieval with session summaries early on

---

## Full Production Configuration

```json
{
  "plugins": {
    "slots": { "memory": "memory-lancedb-pro" },
    "entries": {
      "memory-lancedb-pro": {
        "enabled": true,
        "config": {
          "embedding": {
            "provider": "openai-compatible",
            "apiKey": "${OPENAI_API_KEY}",
            "model": "text-embedding-3-small",
            "baseURL": "https://api.openai.com/v1"
          },
          "reranker": {
            "provider": "jina",
            "apiKey": "${JINA_API_KEY}",
            "model": "jina-reranker-v2-base-multilingual"
          },
          "extraction": {
            "provider": "openai-compatible",
            "apiKey": "${OPENAI_API_KEY}",
            "model": "gpt-4o-mini"
          },
          "autoCapture": true,
          "captureAssistant": false,
          "autoRecall": true,
          "smartExtraction": true,
          "extractMinMessages": 2,
          "extractMaxChars": 8000,
          "enableManagementTools": true,
          "retrieval": {
            "mode": "hybrid",
            "vectorWeight": 0.7,
            "bm25Weight": 0.3,
            "topK": 10
          },
          "rerank": {
            "enabled": true,
            "type": "cross-encoder",
            "candidatePoolSize": 12,
            "minScore": 0.6,
            "hardMinScore": 0.62
          },
          "decay": {
            "enabled": true,
            "model": "weibull",
            "halfLifeDays": 30
          },
          "sessionMemory": { "enabled": false },
          "scopes": {
            "agent": true,
            "user": true,
            "project": true
          }
        }
      }
    }
  }
}
```

### Provider Options for Embedding

| Provider | `provider` value | Notes |
|---|---|---|
| OpenAI / compatible | `"openai-compatible"` | Requires `apiKey`, optional `baseURL` |
| Jina | `"jina"` | Requires `apiKey` |
| Gemini | `"gemini"` | Requires `apiKey` |
| Ollama | `"ollama"` | Local, zero API cost, set `baseURL` |
| DashScope | `"dashscope"` | Requires `apiKey` |
| SiliconFlow | `"siliconflow"` | Requires `apiKey`, free reranker tier |

### Deployment Plans

**Full Power (Jina + OpenAI):**
```json
{
  "embedding": { "provider": "jina", "apiKey": "${JINA_API_KEY}", "model": "jina-embeddings-v3" },
  "reranker": { "provider": "jina", "apiKey": "${JINA_API_KEY}", "model": "jina-reranker-v2-base-multilingual" },
  "extraction": { "provider": "openai-compatible", "apiKey": "${OPENAI_API_KEY}", "model": "gpt-4o-mini" }
}
```

**Budget (SiliconFlow free reranker):**
```json
{
  "embedding": { "provider": "openai-compatible", "apiKey": "${OPENAI_API_KEY}", "model": "text-embedding-3-small" },
  "reranker": { "provider": "siliconflow", "apiKey": "${SILICONFLOW_API_KEY}", "model": "BAAI/bge-reranker-v2-m3" },
  "extraction": { "provider": "openai-compatible", "apiKey": "${OPENAI_API_KEY}", "model": "gpt-4o-mini" }
}
```

**Fully Local (Ollama, zero API cost):**
```json
{
  "embedding": { "provider": "ollama", "baseURL": "http://localhost:11434", "model": "nomic-embed-text" },
  "extraction": { "provider": "ollama", "baseURL": "http://localhost:11434", "model": "llama3" }
}
```

---

## CLI Reference

Validate config and restart after any changes:

```bash
openclaw config validate
openclaw gateway restart
openclaw logs --follow --plain | grep "memory-lancedb-pro"
```

Expected startup log output:
```
memory-lancedb-pro: smart extraction enabled
memory-lancedb-pro@1.x.x: plugin registered
```

### Memory Management CLI

```bash
# Stats overview
openclaw memory-pro stats

# List memories (with optional scope/filter)
openclaw memory-pro list
openclaw memory-pro list --scope user --limit 20
openclaw memory-pro list --filter "typescript"

# Search memories
openclaw memory-pro search "coding preferences"
openclaw memory-pro search "database decisions" --scope project

# Delete a memory by ID
openclaw memory-pro forget <memory-id>

# Export memories (for backup or migration)
openclaw memory-pro export --scope global --output memories-backup.json
openclaw memory-pro export --scope user --output user-memories.json

# Import memories
openclaw memory-pro import --input memories-backup.json

# Upgrade schema (when upgrading plugin versions)
openclaw memory-pro upgrade --dry-run   # Preview first
openclaw memory-pro upgrade             # Run upgrade

# Plugin info
openclaw plugins info memory-lancedb-pro
```

---

## MCP Tool API

The plugin exposes MCP tools to the agent. Core tools are always available; management tools require `enableManagementTools: true` in config.

### Core Tools (always available)

#### `memory_recall`
Retrieve relevant memories for a query.

```typescript
// Agent usage pattern
const results = await memory_recall({
  query: "user's preferred code style",
  scope: "user",        // "agent" | "user" | "project" | "global"
  topK: 5
});
```

#### `memory_store`
Manually store a memory.

```typescript
await memory_store({
  content: "User prefers tabs over spaces, always wants error handling",
  category: "preference",   // "profile" | "preference" | "entity" | "event" | "case" | "pattern"
  scope: "user",
  tags: ["coding-style", "typescript"]
});
```

#### `memory_forget`
Delete a specific memory by ID.

```typescript
await memory_forget({ id: "mem_abc123" });
```

#### `memory_update`
Update an existing memory.

```typescript
await memory_update({
  id: "mem_abc123",
  content: "User now prefers 2-space indentation (changed from tabs on 2026-03-01)",
  category: "preference"
});
```

### Management Tools (requires `enableManagementTools: true`)

#### `memory_stats`
```typescript
const stats = await memory_stats({ scope: "global" });
// Returns: total count, category breakdown, decay stats, db size
```

#### `memory_list`
```typescript
const list = await memory_list({ scope: "user", limit: 20, offset: 0 });
```

#### `self_improvement_log`
Log an agent learning event for meta-improvement tracking.

```typescript
await self_improvement_log({
  event: "user corrected indentation preference",
  context: "User asked me to switch from tabs to spaces",
  improvement: "Updated coding-style preference memory"
});
```

#### `self_improvement_extract_skill`
Extract a reusable pattern from a conversation.

```typescript
await self_improvement_extract_skill({
  conversation: "...",
  domain: "code-review",
  skillName: "typescript-strict-mode-setup"
});
```

#### `self_improvement_review`
Review and consolidate recent self-improvement logs.

```typescript
await self_improvement_review({ days: 7 });
```

---

## Smart Extraction: 6 Memory Categories

When `smartExtraction: true`, the LLM automatically classifies memories into:

| Category | What gets stored | Example |
|---|---|---|
| `profile` | User identity, background | "User is a senior TypeScript developer" |
| `preference` | Style, tool, workflow choices | "Prefers functional programming patterns" |
| `entity` | Projects, people, systems | "Project 'Falcon' uses PostgreSQL + Redis" |
| `event` | Decisions made, things that happened | "Chose Vite over webpack on 2026-02-15" |
| `case` | Solutions to specific problems | "Fixed CORS by adding proxy in vite.config.ts" |
| `pattern` | Recurring behaviors, habits | "Always asks for tests before implementation" |

---

## Hybrid Retrieval Internals

With `retrieval.mode: "hybrid"`, every recall runs:

1. **Vector search** — semantic similarity via embeddings (weight: `vectorWeight`, default 0.7)
2. **BM25 full-text search** — keyword matching (weight: `bm25Weight`, default 0.3)
3. **Score fusion** — results merged with weighted RRF (Reciprocal Rank Fusion)
4. **Cross-encoder rerank** — top `candidatePoolSize` candidates reranked by a cross-encoder model
5. **Score filtering** — results below `hardMinScore` are dropped

```json
"retrieval": {
  "mode": "hybrid",
  "vectorWeight": 0.7,
  "bm25Weight": 0.3,
  "topK": 10
},
"rerank": {
  "enabled": true,
  "type": "cross-encoder",
  "candidatePoolSize": 12,
  "minScore": 0.6,
  "hardMinScore": 0.62
}
```

Retrieval mode options:
- `"vector"` — pure semantic search only
- `"bm25"` — pure keyword search only
- `"hybrid"` — both fused (recommended)

---

## Multi-Scope Isolation

Scopes let you isolate memories by context. Enabling all three gives maximum flexibility:

```json
"scopes": {
  "agent": true,    // Memories specific to this agent instance
  "user": true,     // Memories tied to a user identity
  "project": true   // Memories tied to a project/workspace
}
```

When recalling, specify scope to narrow results:

```typescript
// Get only project-level memories
await memory_recall({ query: "database choices", scope: "project" });

// Get user preferences across all agents
await memory_recall({ query: "coding style", scope: "user" });

// Global recall across all scopes
await memory_recall({ query: "error handling patterns", scope: "global" });
```

---

## Weibull Decay Model

Memories naturally fade over time. The decay model prevents stale memories from polluting retrieval.

```json
"decay": {
  "enabled": true,
  "model": "weibull",
  "halfLifeDays": 30
}
```

- Memories accessed frequently get their decay clock reset
- Important, repeatedly-recalled memories effectively become permanent
- Noise and one-off mentions fade naturally after ~30 days

---

## Upgrading

### From pre-v1.1.0

```bash
# 1. Backup first — always
openclaw memory-pro export --scope global --output memories-backup-$(date +%Y%m%d).json

# 2. Preview schema changes
openclaw memory-pro upgrade --dry-run

# 3. Run the upgrade
openclaw memory-pro upgrade

# 4. Verify
openclaw memory-pro stats
```

See `CHANGELOG-v1.1.0.md` in the repo for behavior changes and upgrade rationale.

---

## Troubleshooting

### Plugin not loading

```bash
# Check plugin is recognized
openclaw plugins info memory-lancedb-pro

# Validate config (catches JSON errors, unknown fields)
openclaw config validate

# Check logs for registration
openclaw logs --follow --plain | grep "memory-lancedb-pro"
```

**Common causes:**
- Missing or relative `plugins.load.paths` (must be absolute when using npm install)
- `plugins.slots.memory` not set to `"memory-lancedb-pro"`
- Plugin not listed under `plugins.entries`

### `autoRecall` not injecting memories

By default `autoRecall` is `false` in some versions — explicitly set it to `true`:

```json
"autoRecall": true
```

Also confirm the plugin is bound to the `memory` slot, not just loaded.

### Jiti cache issues after upgrade

```bash
# Clear jiti transpile cache
rm -rf ~/.openclaw/.cache/jiti
openclaw gateway restart
```

### Memories not being extracted from conversations

- Check `extractMinMessages` — must be ≥ number of turns in the conversation (set to `2` for normal chats)
- Check `extractMaxChars` — very long contexts may be truncated; increase to `12000` if needed
- Verify extraction LLM config has a valid `apiKey` and reachable endpoint
- Check logs: `openclaw logs --follow --plain | grep "extraction"`

### Retrieval returns nothing or poor results

1. Confirm `retrieval.mode` is `"hybrid"` not `"bm25"` alone (BM25 requires indexed content)
2. Lower `rerank.hardMinScore` temporarily (try `0.4`) to see if results exist but are being filtered
3. Check embedding model is consistent between store and recall operations — changing models requires re-embedding

### Environment variable not resolving

Ensure env vars are exported in the shell that runs OpenClaw, or use a `.env` file loaded by your process manager. The `${VAR}` syntax in `openclaw.json` is resolved at startup.

```bash
export OPENAI_API_KEY="sk-..."
export JINA_API_KEY="jina_..."
openclaw gateway restart
```

---

## Telegram Bot Quick Config Import

If using OpenClaw's Telegram integration, send this to the bot to auto-configure:

```
Help me connect this memory plugin with the most user-friendly configuration:
https://github.com/CortexReach/memory-lancedb-pro

Requirements:
1. Set it as the only active memory plugin
2. Use Jina for embedding
3. Use Jina for reranker
4. Use gpt-4o-mini for the smart-extraction LLM
5. Enable autoCapture, autoRecall, smartExtraction
6. extractMinMessages=2
7. sessionMemory.enabled=false
8. captureAssistant=false
9. retrieval mode=hybrid, vectorWeight=0.7, bm25Weight=0.3
10. rerank=cross-encoder, candidatePoolSize=12, minScore=0.6, hardMinScore=0.62
11. Generate the final openclaw.json config directly, not just an explanation
```

---

## Resources

- **GitHub:** https://github.com/CortexReach/memory-lancedb-pro
- **npm:** https://www.npmjs.com/package/memory-lancedb-pro
- **Setup script:** https://github.com/CortexReach/toolbox/tree/main/memory-lancedb-pro-setup
- **Agent skill:** https://github.com/CortexReach/memory-lancedb-pro-skill
- **Video walkthrough (YouTube):** https://youtu.be/MtukF1C8epQ
- **Video walkthrough (Bilibili):** https://www.bilibili.com/video/BV1zUf2BGEgn/
