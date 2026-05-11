# Elite Longterm Memory 🧠

**The ultimate memory system for AI agents.** Never lose context again.

[![npm version](https://img.shields.io/npm/v/elite-longterm-memory.svg?style=flat-square)](https://www.npmjs.com/package/elite-longterm-memory)
[![npm downloads](https://img.shields.io/npm/dm/elite-longterm-memory.svg?style=flat-square)](https://www.npmjs.com/package/elite-longterm-memory)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

## Works With

<p align="center">
  <img src="https://img.shields.io/badge/Claude-AI-orange?style=for-the-badge&logo=anthropic" alt="Claude AI" />
  <img src="https://img.shields.io/badge/GPT-OpenAI-412991?style=for-the-badge&logo=openai" alt="GPT" />
  <img src="https://img.shields.io/badge/Cursor-IDE-000000?style=for-the-badge" alt="Cursor" />
  <img src="https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=for-the-badge" alt="LangChain" />
</p>

<p align="center">
  <strong>Built for:</strong> Clawdbot • Moltbot • Claude Code • Any AI Agent
</p>

---

Combines 7 proven memory approaches into one bulletproof architecture:

- ✅ **Bulletproof WAL Protocol** — Write-ahead logging survives compaction
- ✅ **LanceDB Vector Search** — Semantic recall of relevant memories
- ✅ **Git-Notes Knowledge Graph** — Structured decisions, branch-aware
- ✅ **File-Based Archives** — Human-readable MEMORY.md + daily logs
- ✅ **Cloud Backup** — Optional SuperMemory sync
- ✅ **Memory Hygiene** — Keep vectors lean, prevent token waste
- ✅ **Mem0 Auto-Extraction** — Automatic fact extraction, 80% token reduction

## Quick Start

```bash
# Initialize in your workspace
npx elite-longterm-memory init

# Check status
npx elite-longterm-memory status

# Create today's log
npx elite-longterm-memory today
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              ELITE LONGTERM MEMORY                  │
├─────────────────────────────────────────────────────┤
│  HOT RAM          WARM STORE        COLD STORE     │
│  SESSION-STATE.md → LanceDB      → Git-Notes       │
│  (survives         (semantic       (permanent      │
│   compaction)       search)         decisions)     │
│         │              │                │          │
│         └──────────────┼────────────────┘          │
│                        ▼                           │
│                   MEMORY.md                        │
│               (curated archive)                    │
└─────────────────────────────────────────────────────┘
```

## The 5 Memory Layers

| Layer | File/System | Purpose | Persistence |
|-------|-------------|---------|-------------|
| 1. Hot RAM | SESSION-STATE.md | Active task context | Survives compaction |
| 2. Warm Store | LanceDB | Semantic search | Auto-recall |
| 3. Cold Store | Git-Notes | Structured decisions | Permanent |
| 4. Archive | MEMORY.md + daily/ | Human-readable | Curated |
| 5. Cloud | SuperMemory | Cross-device sync | Optional |

## The WAL Protocol

**Critical insight:** Write state BEFORE responding, not after.

```
User: "Let's use Tailwind for this project"

Agent (internal):
1. Write to SESSION-STATE.md → "Decision: Use Tailwind"
2. THEN respond → "Got it — Tailwind it is..."
```

If you respond first and crash before saving, context is lost. WAL ensures durability.

## Why Memory Fails (And How to Fix It)

| Problem | Cause | Fix |
|---------|-------|-----|
| Forgets everything | memory_search disabled | Enable + add OpenAI key |
| Repeats mistakes | Lessons not logged | Write to memory/lessons.md |
| Sub-agents isolated | No context inheritance | Pass context in task prompt |
| Facts not captured | No auto-extraction | Use Mem0 (see below) |

## Mem0 Integration (Recommended)

Auto-extract facts from conversations. 80% token reduction.

```bash
npm install mem0ai
export MEM0_API_KEY="your-key"
```

```javascript
const { MemoryClient } = require('mem0ai');
const client = new MemoryClient({ apiKey: process.env.MEM0_API_KEY });

// Auto-extracts facts from messages
await client.add(messages, { user_id: "user123" });

// Retrieve relevant memories  
const memories = await client.search(query, { user_id: "user123" });
```

## For Clawdbot/Moltbot Users

Add to `~/.clawdbot/clawdbot.json`:

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "openai",
    "sources": ["memory"]
  }
}
```

## Files Created

```
workspace/
├── SESSION-STATE.md    # Hot RAM (active context)
├── MEMORY.md           # Curated long-term memory
└── memory/
    ├── 2026-01-30.md   # Daily logs
    └── ...
```

## Commands

```bash
elite-memory init      # Initialize memory system
elite-memory status    # Check health
elite-memory today     # Create today's log
elite-memory help      # Show help
```

## Links

- [Full Documentation (SKILL.md)](./SKILL.md)
- [ClawdHub](https://clawdhub.com/skills/elite-longterm-memory)
- [GitHub](https://github.com/NextFrontierBuilds/elite-longterm-memory)

---

Built by [@NextXFrontier](https://x.com/NextXFrontier)
