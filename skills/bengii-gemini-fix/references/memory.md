# OpenClaw Memory & Compaction Reference

## Table of Contents

- [Memory Files](#memory-files)
- [Memory Tools](#memory-tools)
- [When to Write Memory](#when-to-write-memory)
- [Automatic Memory Flush](#automatic-memory-flush)
- [Vector Memory Search](#vector-memory-search)
- [Hybrid Search (BM25 + Vector)](#hybrid-search-bm25--vector)
- [MMR Re-Ranking (Diversity)](#mmr-re-ranking-diversity)
- [Additional Memory Paths](#additional-memory-paths)
- [Embedding Providers](#embedding-providers)
- [Compaction](#compaction)
- [Session Pruning](#session-pruning)
- [Configuration Reference](#configuration-reference)

## Memory Files

Memory lives as Markdown files in the agent workspace (`agents.defaults.workspace`, default `~/.openclaw/workspace`):

| File | Purpose | Load Behavior |
|---|---|---|
| `memory/YYYY-MM-DD.md` | Daily log (append-only) | Read today + yesterday at session start |
| `MEMORY.md` | Curated long-term memory | Only loaded in main, private session (never in group contexts) |

## Memory Tools

| Tool | Description |
|---|---|
| `memory_search` | Semantic recall over indexed snippets (hybrid vector + BM25) |
| `memory_get` | Targeted read of a specific Markdown file/line range |

Notes:
- `memory_get` with a non-existent path returns `{ text: "", path }` (not an error)
- `memory_get` with an invalid path returns `ENOENT`

## When to Write Memory

- **Decisions, preferences, and durable facts** → `MEMORY.md`
- **Day-to-day notes and running context** → `memory/YYYY-MM-DD.md`
- **"Remember this"** → Write it down (do not keep in RAM)
- This area is evolving; it helps to remind the model to store memories

## Automatic Memory Flush

Pre-compaction memory flush: when the session nears compaction threshold, OpenClaw triggers a silent prompt asking the agent to save durable context to memory files.

```json5
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

Behavior:
- **Soft threshold**: triggers when token estimate crosses `contextWindow - reserveTokensFloor - softThresholdTokens`
- **Silent by default**: prompts include `NO_REPLY` so nothing is delivered to chat
- Two prompts: user prompt + system prompt append the reminder
- One flush per compaction cycle (tracked in `sessions.json`)
- **Skipped** if workspace is `workspaceAccess: "ro"` or `"none"` (sandbox read-only)

## Vector Memory Search

Watches `MEMORY.md` and `memory/*.md` for changes (debounced). Enabled by default.

### Provider Auto-Selection

If `memorySearch.provider` is not set, OpenClaw auto-selects:

1. `local` — if `memorySearch.local.modelPath` is configured and file exists
2. `openai` — if OpenAI key can be resolved
3. `gemini` — if Gemini key can be resolved
4. `voyage` — if Voyage key can be resolved
5. `mistral` — if Mistral key can be resolved
6. Otherwise — memory search stays disabled until configured

### Key Resolution

| Provider | Key Sources |
|---|---|
| OpenAI | `models.providers.openai.apiKey` or env |
| Gemini | `GEMINI_API_KEY`, `models.providers.google.apiKey` |
| Voyage | `VOYAGE_API_KEY`, `models.providers.voyage.apiKey` |
| Mistral | `MISTRAL_API_KEY`, `models.providers.mistral.apiKey` |
| Custom | `memorySearch.remote.apiKey`, `memorySearch.remote.headers` |

### Local Mode

- Uses `node-llama-cpp` for embeddings
- May require `pnpm approve-builds`
- Configure with `memorySearch.local.modelPath`

### SQLite Vector Acceleration (sqlite-vec)

When available, uses `sqlite-vec` to accelerate vector search inside SQLite. Fallback to in-memory if unavailable.

## Hybrid Search (BM25 + Vector)

Two retrieval modes combined:
- **Vector similarity**: semantic match (wording can differ)
- **BM25 keyword relevance**: exact tokens like IDs, env vars, code symbols

### How Results Are Merged

1. **Retrieve candidates** from both sides:
   - Vector: top `maxResults * candidateMultiplier` by cosine similarity
   - BM25: top `maxResults * candidateMultiplier` by FTS5 BM25 rank

2. **Convert BM25 rank** to score:
   ```
   textScore = 1 / (1 + max(0, bm25Rank))
   ```

3. **Union candidates** by chunk ID and compute weighted score:
   ```
   finalScore = vectorWeight * vectorScore + textWeight * textScore
   ```

- `vectorWeight + textWeight` normalized to 1.0 (behave as percentages)
- If embeddings unavailable, BM25 results still returned
- If FTS5 can't be created, vector-only search (no hard failure)

### Post-Processing Pipeline

```
Vector + Keyword → Weighted Merge → Temporal Decay → Sort → MMR → Top-K Results
```

## MMR Re-Ranking (Diversity)

Maximal Marginal Relevance (MMR) prevents near-duplicate results:

1. Results scored by original relevance (vector + BM25 weighted)
2. MMR iteratively selects results that maximize:
   ```
   λ × relevance − (1−λ) × max_similarity_to_selected
   ```
3. Similarity between results measured using Jaccard text similarity on tokenized content

| Lambda | Behavior |
|---|---|
| `1.0` | Pure relevance (no diversity penalty) |
| `0.0` | Maximum diversity (ignores relevance) |
| `0.7` (default) | Balanced, slight relevance bias |

### Example

Without MMR:
```
1. memory/2026-02-10.md (0.92) ← router + VLAN
2. memory/2026-02-08.md (0.89) ← router + VLAN (near-duplicate!)
3. memory/network.md   (0.85) ← reference doc
```

With MMR (λ=0.7):
```
1. memory/2026-02-10.md (0.92) ← router + VLAN
2. memory/network.md   (0.85) ← reference doc (diverse!)
3. memory/2026-02-05.md (0.78) ← AdGuard DNS (diverse!)
```

## Additional Memory Paths

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes/overview.md"],
      },
    },
  },
}
```

- Paths can be absolute or workspace-relative
- Directories are scanned recursively for `.md` files
- Only Markdown files are indexed
- Symlinks are ignored

## Embedding Providers

| Provider | Type | Config |
|---|---|---|
| Local (node-llama-cpp) | On-device | `memorySearch.local.modelPath` |
| OpenAI | Cloud | Auto or `models.providers.openai.apiKey` |
| Gemini | Cloud (native) | `GEMINI_API_KEY` or `models.providers.google.apiKey` |
| Voyage | Cloud | `VOYAGE_API_KEY` or `models.providers.voyage.apiKey` |
| Mistral | Cloud | `MISTRAL_API_KEY` or `models.providers.mistral.apiKey` |
| Custom OpenAI-compatible | Cloud | `memorySearch.remote.*` |

### Embedding Cache

Embeddings are cached to avoid re-computing on unchanged content. Cache is per-chunk keyed by content hash.

## Compaction

### What Compaction Is

When the session's context window fills up, OpenClaw summarizes older messages into a compact summary, keeping recent messages verbatim. The session then contains:
- The compaction summary
- Recent messages after the compaction point

### Auto-Compaction (Default On)

- Enabled by default
- Indicated by `🧹 Auto-compaction complete` in verbose mode
- `/status` shows `🧹 Compactions: <count>`

### Manual Compaction

```
/compact
/compact Focus on decisions and open questions
```

### Configuration

```json5
{
  agents: {
    defaults: {
      compaction: {
        // identifierPolicy controls how identifiers are preserved in summaries
        identifierPolicy: "strict",    // "strict" | "off" | "custom"
        identifierInstructions: "...", // custom instructions when policy = "custom"
        reserveTokensFloor: 20000,
        memoryFlush: { enabled: true, ... },
      },
    },
  },
}
```

### Compaction vs Pruning

| Feature | Compaction | Session Pruning |
|---|---|---|
| What it does | Summarizes and persists in JSONL | Trims old tool results only |
| Scope | Full older context | In-memory, per request |
| Persistence | Permanent (saved to transcript) | Temporary |

### OpenAI Server-Side Compaction

For OpenAI models, two compaction modes:
- **Local compaction**: OpenClaw summarizes and persists into session JSONL
- **Server-side compaction**: OpenAI compacts context on the provider side when `store` + `context_management` are enabled

See: [OpenAI provider](https://docs.openclaw.ai/providers/openai)

### Tips

- Use `/compact` when sessions feel stale or context is bloated
- Large tool outputs are already truncated; pruning can further reduce tool-result buildup
- `/new` or `/reset` starts a fresh session if compaction isn't enough

## Session Pruning

Separate from compaction. See: [Session Pruning](https://docs.openclaw.ai/concepts/session-pruning)

- Trims old tool results in-memory, per request
- Does not persist changes
- Complementary to compaction (can use both)

## Configuration Reference

### Full Memory Search Config

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        // Provider selection (auto if not set)
        provider: "openai",           // "local" | "openai" | "gemini" | "voyage" | "mistral"
        
        // Remote embedding config
        remote: {
          apiKey: "${OPENAI_API_KEY}",
          headers: {},
        },
        
        // Local embedding config
        local: {
          modelPath: "/path/to/embedding-model.gguf",
        },
        
        // Search tuning
        query: {
          hybrid: true,               // Enable hybrid BM25 + vector
          vectorWeight: 0.7,
          textWeight: 0.3,
          maxResults: 10,
          candidateMultiplier: 3,
          lambda: 0.7,                // MMR diversity factor
        },
        
        // Additional indexed paths
        extraPaths: ["../team-docs"],
      },
    },
  },
}
```

## QMD Backend (Experimental)

An alternative memory backend using [QMD](https://github.com/tobi/qmd) for local vector search.

### Setup

- Disabled by default. Opt in per-config: `memory.backend = "qmd"`.
- Install QMD CLI separately: `bun install -g https://github.com/tobi/qmd` and ensure `qmd` binary is on the Gateway's `PATH`.
- Requires SQLite build that allows extensions (`brew install sqlite` on macOS).
- Runs fully locally via Bun + node-llama-cpp, auto-downloads GGUF models from HuggingFace on first use (no Ollama daemon required).

### State Location

- Gateway runs QMD in a self-contained XDG home under `~/.openclaw/agents/<agentId>/qmd/` by setting `XDG_CONFIG_HOME` and `XDG_CACHE_HOME`.

### Behavior

- Collections created from `memory.qmd.paths` plus default workspace memory files.
- `qmd update` + `qmd embed` run on boot and on a configurable interval (`memory.qmd.update.interval`, default 5 min).
- Boot refresh runs in the background by default (set `memory.qmd.update.waitForBootSync = true` for blocking behavior).
- Search via `memory.qmd.searchMode` (default `qmd search --json`; also supports `vsearch` and `query`).
- If QMD fails or the binary is missing, OpenClaw automatically falls back to the builtin SQLite manager.

### Pre-downloading Models

```bash
STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
export XDG_CONFIG_HOME="$STATE_DIR/agents/main/qmd/xdg-config"
export XDG_CACHE_HOME="$STATE_DIR/agents/main/qmd/xdg-cache"
qmd query "test"  # triggers model download
```

### OS Support

- macOS and Linux work out of the box once Bun + SQLite are installed.
- Windows is best supported via WSL2.

## Ollama Embeddings

`memorySearch.provider = "ollama"` is supported for local/self-hosted Ollama embeddings (`/api/embeddings`), but it is **not auto-selected**. Must be explicitly configured.

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "ollama",
      },
    },
  },
}
```

Environment: `OLLAMA_API_KEY=ollama-local` (if needed).

## Session Memory Search (Experimental)

Search across session transcripts, not just memory files. Experimental feature.

## See Also

- [Sessions](sessions.md) — session management, lifecycle, maintenance
- [Tools](tools.md) — `memory_search` and `memory_get` tool parameters
- [Streaming](streaming.md) — block streaming and chunking
