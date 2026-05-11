# TotalReclaw Skill for OpenClaw

> **End-to-end encrypted memory for AI agents -- portable, yours forever.**
>
> Your AI remembers everything. Your server sees nothing.

TotalReclaw gives any [OpenClaw](https://github.com/openclaw/openclaw) agent persistent, encrypted long-term memory. Preferences, decisions, and context carry across every conversation -- fully end-to-end encrypted so the server **never** sees plaintext.

## Installation

### ClawHub (recommended)

Tell your OpenClaw agent:

> "Install the TotalReclaw skill from ClawHub"

Or via terminal:

```bash
openclaw skills install totalreclaw
```

Then set your environment variables:

```bash
export TOTALRECLAW_SERVER_URL="http://your-totalreclaw-server:8080"
export TOTALRECLAW_RECOVERY_PHRASE="your twelve word recovery phrase here"
```

That's it. TotalReclaw hooks into your agent automatically.

### Alternative: npm

```bash
openclaw plugins install @totalreclaw/totalreclaw
```

---

## Why TotalReclaw?

Most AI memory solutions force a tradeoff: **good recall OR privacy**. TotalReclaw eliminates that tradeoff.

| | Recall@8 | Privacy | Encryption | Portable Export |
|---|:---:|:---:|:---:|:---:|
| **TotalReclaw (E2EE)** | **98.1%** | **100%** | AES-256-GCM | Yes |
| Plaintext vector search | 99.2% | 0% | None | Varies |
| Mem0 (hosted) | ~95% | 0% | At-rest only | No |
| Native OpenClaw QMD | ~90% | 50% | Partial | No |

**98.1% recall with 100% privacy** -- tested against 8,727 real-world memories. The server never sees your data, yet search quality is within 1.1% of plaintext alternatives.

### Key Differentiators

- **True end-to-end encryption**: AES-256-GCM encryption, Argon2id key derivation, HKDF-SHA256 auth. The server is cryptographically unable to read your memories.
- **Near-plaintext recall**: LSH blind indices with client-side BM25 + cosine + RRF reranking achieve 98.1% recall@8.
- **No vendor lock-in**: One-click plaintext export in JSON or Markdown. Your data is always yours.
- **Works everywhere**: Any MCP-compatible AI agent, not just OpenClaw.

---

## Features

- **End-to-End Encryption**: AES-256-GCM ensures the server never sees plaintext memories
- **Intelligent Extraction**: Automatically extracts facts, preferences, and decisions from conversations
- **Semantic Search**: LSH blind indices with client-side BM25 + cosine + RRF fusion reranking
- **Lifecycle Hooks**: Seamlessly integrates with OpenClaw's agent lifecycle
- **Portable Export**: One-click plaintext export -- no vendor lock-in
- **Decay Management**: Automatic memory decay with configurable thresholds

---

## Quick Start

### 1. Install

Tell your OpenClaw agent:

> "Install the TotalReclaw skill from ClawHub"

Or via terminal:

```bash
openclaw skills install totalreclaw
```

Alternative (npm):

```bash
openclaw plugins install @totalreclaw/totalreclaw
```

### 2. Configure

Set the required environment variables:

```bash
# Required
export TOTALRECLAW_SERVER_URL="http://your-totalreclaw-server:8080"
export TOTALRECLAW_RECOVERY_PHRASE="your twelve word recovery phrase here"

# Optional
export TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS=3
export TOTALRECLAW_MIN_IMPORTANCE=6
export TOTALRECLAW_MAX_MEMORIES=8
export TOTALRECLAW_FORGET_THRESHOLD=0.3
export TOTALRECLAW_RERANKER_MODEL="BAAI/bge-reranker-base"
export TOTALRECLAW_USER_ID="user-123"
```

### 3. Use

Once installed, TotalReclaw hooks into your agent lifecycle automatically. No code changes needed.

Your agent will:
- **Load relevant memories** before processing each message (`before_agent_start`)
- **Extract and store facts** after each turn (`agent_end`)
- **Flush all memories** before context compaction (`pre_compaction`)

You can also use the tools directly in conversation:

```
"Remember that I prefer dark mode in all editors"
"What do you know about my programming preferences?"
"Forget the memory about my old email address"
"Export all my memories as JSON"
```

---

## Tools

TotalReclaw provides four tools:

### totalreclaw_remember

Explicitly store a memory.

```typescript
const result = await skill.remember({
  text: 'User prefers dark mode',
  type: 'preference',  // optional: fact, preference, decision, episodic, goal
  importance: 7,       // optional: 1-10, default is minImportanceForAutoStore
});

console.log(result); // "Memory stored successfully with ID: fact-123"
```

### totalreclaw_recall

Search for relevant memories.

```typescript
const memories = await skill.recall({
  query: 'programming language preferences',
  k: 5,  // optional: number of results (default: 8, max: 20)
});

// Each memory has:
// - fact: The fact object with text, metadata, etc.
// - score: Combined relevance score
// - vectorScore: Vector similarity score
// - textScore: BM25 text score
// - decayAdjustedScore: Score adjusted for decay
```

### totalreclaw_forget

Delete a specific memory.

```typescript
await skill.forget({
  factId: 'fact-123',
});
```

### totalreclaw_export

Export all memories for portability.

```typescript
const jsonExport = await skill.export({
  format: 'json',  // or 'markdown'
});

console.log(jsonExport);
```

---

## Lifecycle Hooks

TotalReclaw integrates with OpenClaw through three lifecycle hooks:

| Hook | Priority | Description |
|------|----------|-------------|
| `before_agent_start` | 10 | Retrieve relevant memories before agent processes message |
| `agent_end` | 90 | Extract and store facts after agent completes turn |
| `pre_compaction` | 5 | Full memory flush before context compaction |

### before_agent_start

Runs before the agent processes a user message. Retrieves relevant memories and formats them for context injection.

```typescript
const result = await skill.onBeforeAgentStart(context);

// result.memories - Array of retrieved memories
// result.contextString - Formatted string for injection
// result.latencyMs - Search latency in milliseconds
```

### agent_end

Runs after the agent completes its turn. Extracts facts from the conversation and stores them.

```typescript
const result = await skill.onAgentEnd(context);

// result.factsExtracted - Number of facts extracted
// result.factsStored - Number of facts stored
// result.processingTimeMs - Processing time
```

### pre_compaction

Runs before conversation history is compacted. Performs comprehensive extraction of the full history.

```typescript
const result = await skill.onPreCompaction(context);

// result.factsExtracted - Number of facts extracted
// result.factsStored - Number of facts stored
// result.duplicatesSkipped - Duplicates skipped
// result.processingTimeMs - Processing time
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|:---:|---------|-------------|
| `TOTALRECLAW_SERVER_URL` | **Yes** | `http://127.0.0.1:8080` | TotalReclaw server URL |
| `TOTALRECLAW_RECOVERY_PHRASE` | **Yes** | -- | 12-word BIP-39 recovery phrase (never sent to server) |
| `TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS` | No | `3` | Turns between automatic extractions |
| `TOTALRECLAW_MIN_IMPORTANCE` | No | `6` | Minimum importance (1-10) to auto-store |
| `TOTALRECLAW_MAX_MEMORIES` | No | `8` | Maximum memories to inject into context |
| `TOTALRECLAW_FORGET_THRESHOLD` | No | `0.3` | Decay score threshold for eviction |
| `TOTALRECLAW_RERANKER_MODEL` | No | `BAAI/bge-reranker-base` | ONNX reranker model path |
| `TOTALRECLAW_USER_ID` | No | -- | Existing user ID (skips registration) |

### Configuration Sources (Priority Order)

Configuration is loaded from multiple sources. Higher priority overrides lower:

1. **Default values** -- Built-in defaults
2. **OpenClaw config** -- `agents.defaults.totalreclaw.*`
3. **Environment variables** -- `TOTALRECLAW_*`
4. **Explicit overrides** -- Passed to constructor

### OpenClaw Configuration

Add to your OpenClaw configuration file:

```json
{
  "agents": {
    "defaults": {
      "totalreclaw": {
        "serverUrl": "http://your-server:8080",
        "autoExtractEveryTurns": 3,
        "minImportanceForAutoStore": 6,
        "maxMemoriesInContext": 8,
        "forgetThreshold": 0.3
      }
    }
  }
}
```

---

## Memory Types

TotalReclaw categorizes memories into five types:

| Type | Description | Example |
|------|-------------|---------|
| `fact` | Objective information | "User works at Acme Corp" |
| `preference` | User likes/dislikes | "User prefers dark mode" |
| `decision` | Choices made | "User decided to use PostgreSQL" |
| `episodic` | Events and experiences | "User attended PyCon 2024" |
| `goal` | Objectives and targets | "User wants to learn Rust" |

## Importance Scoring

Memories are scored on a 1-10 scale:

| Score | Level | Description |
|-------|-------|-------------|
| 1-3 | Trivial | Small talk, pleasantries |
| 4-6 | Useful | Tool preferences, working style |
| 7-8 | Important | Key decisions, major preferences |
| 9-10 | Critical | Core values, safety info |

---

## Encryption Details

TotalReclaw uses end-to-end encryption:

1. **Key Derivation**: Recovery phrase is processed through Argon2id to derive encryption keys. The phrase is never sent to the server.
2. **Encryption**: All memories are encrypted client-side using AES-256-GCM before transmission.
3. **Search**: LSH blind indices (SHA-256 hashed) enable server-side search without exposing plaintext.
4. **Decryption**: Memories are decrypted client-side after retrieval.
5. **Authentication**: HKDF-SHA256 for authentication tokens.

The server is cryptographically unable to read your memories, embeddings, or search queries.

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Search latency (p95) | < 140ms for 1M memories |
| Recall accuracy | >= 93% of true top-250 |
| Storage overhead | <= 2.2x vs plaintext |
| Extraction latency | < 500ms |

---

## Architecture

```
+-------------------+     +-------------------+     +-------------------+
|   OpenClaw Agent  |     |  TotalReclaw Skill |     | TotalReclaw Server |
+-------------------+     +-------------------+     +-------------------+
        |                         |                         |
        | onBeforeAgentStart()    |                         |
        |------------------------>| recall()                |
        |                         |------------------------>|
        |                         |<------------------------|
        |<------------------------|                         |
        |                         |                         |
        | [Agent processes]       |                         |
        |                         |                         |
        | onAgentEnd()            |                         |
        |------------------------>| extract + store()       |
        |                         |------------------------>|
        |<------------------------|                         |
```

---

## Troubleshooting

### "Skill not initialized"

Call `await skill.init()` before using any methods.

### "Failed to load reranker model"

The reranker model is optional. If not found, vector scores are used as fallback.

### "Memory not found"

The fact ID may be incorrect, or the memory may have been evicted due to decay.

### Slow searches

- Ensure the TotalReclaw server is properly indexed
- Check network latency to the server
- Consider increasing `maxMemoriesInContext` for better recall

---

## Development

### Setup

```bash
git clone https://github.com/p-diogo/totalreclaw
cd totalreclaw/skill
npm install
```

### Build

```bash
npm run build
```

### Test

```bash
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm run test:watch
```

### Lint

```bash
npm run lint
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [TotalReclaw Documentation](https://docs.totalreclaw.ai)
- [Claw Hub Listing](https://clawhub.ai/skills/totalreclaw)
- [OpenClaw](https://github.com/openclaw/openclaw)
- [Issue Tracker](https://github.com/p-diogo/totalreclaw/issues)
