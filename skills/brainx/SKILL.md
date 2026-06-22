---
name: "BrainX V5 — The First Brain for OpenClaw"
description: |
  Vector memory engine with PostgreSQL + pgvector + OpenAI embeddings.
  Stores, searches, and injects contextual memories into LLM prompts.
  Includes auto-injection hook for OpenClaw and full backup/recovery system.
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["psql"]
      env: ["DATABASE_URL", "OPENAI_API_KEY"]
    primaryEnv: "DATABASE_URL"
    hooks:
      - name: brainx-auto-inject
        event: agent:bootstrap
        description: Auto-injects relevant memories at session start
user-invocable: true
---

# BrainX V5 — The First Brain for OpenClaw

Persistent memory system using vector embeddings for contextual retrieval in AI agents.

## 37 Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | ✅ **Production** | Active on 32 agent profiles with centralized shared memory (2,400+ memories) |
| 2 | 🧠 **Auto-Learning** | Learns on its own from every conversation without human intervention |
| 3 | 💾 **Persistent Memory** | Remembers across sessions — PostgreSQL + pgvector |
| 4 | 🤝 **Shared Memory** | All agents share the same knowledge pool |
| 5 | 💉 **Automatic Briefing** | Personalized context injection at each agent startup |
| 6 | 🔎 **Semantic Search** | Searches by meaning, not exact keywords |
| 7 | 🏷️ **Intelligent Classification** | Auto-typed: facts, decisions, learnings, gotchas, notes |
| 8 | 📊 **Usage-Based Prioritization** | Hot/warm/cold tiers — automatic promote/degrade based on access |
| 9 | 🤝 **Cross-Agent Learning** | Propagates important gotchas and learnings across all agents |
| 10 | 🔄 **Anti-Duplicates** | Semantic deduplication by cosine similarity with intelligent merge |
| 11 | ⚡ **Anti-Contradictions** | Detects contradictory memories and supersedes the obsolete one |
| 12 | 📋 **Session Indexing** | Searches past conversations (30-day retention) |
| 13 | 🔒 **PII Scrubbing** | Automatic redaction of sensitive data before storage |
| 14 | 🔮 **Pattern Detection** | Detects recurring patterns and promotes them automatically |
| 15 | 🛡️ **Disaster Recovery** | Full backup/restore (DB + configs + hooks + workspaces) |
| 16 | ⭐ **Quality Scoring** | Evaluates memory quality and promotes only what deserves to persist |
| 17 | ⚙️ **Fact Extraction** | Regex + LLM pipelines capture both operational facts and nuanced learnings |
| 18 | 📦 **Context Packs** | Weekly project packs and bootstrap topic files for fast situational awareness |
| 19 | 📈 **Telemetry** | Query logs, injection metrics, and health monitoring built in |
| 20 | 🧵 **Supersede Chains** | Old memories can be replaced cleanly without losing history |
| 21 | 🌀 **Memory Distillation** | Consolidates raw logs into higher-signal memories over time |
| 22 | 🛡️ **Pre-Action Advisory** | Queries past mistakes before high-risk tool execution |
| 23 | 👤 **Agent Profiles** | Per-agent hook injection: boosts/filters memories by agent role |
| 24 | 🔀 **Cross-Agent Injection Slots** | Hook reserves 30% of context slots for other agents' memories |
| 25 | 📊 **Metrics Dashboard** | CLI dashboard with top patterns, memory stats, and usage trends |
| 26 | 🔧 **Doctor & Auto-Fix** | Schema integrity check + automatic repair of detected issues |
| 27 | 👍 **Memory Feedback** | Mark memories as useful/useless/incorrect to refine quality |
| 28 | 🗺️ **Trajectory Recording** | Records problem→solution paths for future reference |
| 29 | 📝 **Learning Details** | Extended metadata extraction for learnings and gotchas |
| 30 | 🔄 **Lifecycle Management** | Automatic promotion/degradation of memories by age and usage |
| 31 | 📥 **Workspace Import** | Imports existing MEMORY.md files from all workspaces into the brain |
| 32 | 🧪 **Eval Dataset Generation** | Generates evaluation datasets from real memories for quality testing |
| 33 | 🏗️ **Session Snapshots** | Captures full agent state at session close for analysis |
| 34 | 🧹 **Low-Signal Cleanup** | Automatic cleanup of low-value, outdated, or redundant memories |
| 35 | 🔃 **Memory Reclassification** | Reclassifies memories with correct types and categories post-hoc |
| 36 | 🔄 **Auto-Promotion Pipeline** | Detects high-recurrence patterns and promotes them as rules in workspace files automatically |
| 37 | 📊 **15-Step Daily Pipeline** | Consolidated daily pipeline: bootstrap, lifecycle, distiller, harvester, bridge, auto-distiller, consolidation, cross-agent, contradiction, md-harvester, error-harvester, auto-promoter, promotion-applier, memory-enforcer, audit |

## When to Use

✅ **USE when:**
- An agent needs to "remember" information from previous sessions
- You want to give additional context to an LLM about past actions
- You need semantic search by content
- You want to store important decisions with metadata

❌ **DON'T USE when:**
- Ephemeral information that doesn't need persistence
- Structured tabular data (use a regular DB)
- Simple cache (use Redis or in-memory)

## Auto-Injection (Hook)

BrainX V5 includes an **OpenClaw hook** that automatically injects relevant memories when an agent starts.

### Production Validation Status

Real validation completed on **2026-03-18**:
- Global hook enabled in `~/.openclaw/openclaw.json`
- Managed hook synced with `~/.openclaw/skills/brainx-v5/hook/` (handler.js re-synced)
- Active physical database: `brainx_v5`
- agent-profiles.json expanded from 10 to 32 profiles (all agents)
- Cross-agent injection slots (30%) activated in production
- 20 null embeddings regenerated + 17 duplicate pairs deduped via `brainx fix`
- 2 pending migrations applied
- Doctor: 18/18 passed, 0 warnings
- Real bootstrap smoke test passed for 10 agents
- Expected evidence confirmed:
  - `<!-- BRAINX:START -->` block written into `MEMORY.md`
  - `Updated:` timestamp present
  - Fresh row recorded in `brainx_pilot_log`

If this validation becomes stale, rerun a bootstrap smoke test before assuming runtime is still healthy.

### How it works:

1. `agent:bootstrap` event → Hook fires automatically
2. PostgreSQL query → Fetches hot/warm recent memories
3. Generates file → Creates `BRAINX_CONTEXT.md` in the workspace
4. Agent reads → File is loaded as initial context

### Configuration:

In `~/.openclaw/openclaw.json`:
```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "brainx-auto-inject": {
          "enabled": true,
          "limit": 5,
          "tier": "hot+warm",
          "minImportance": 5
        }
      }
    }
  }
}
```

### Per-agent setup:

Add to `AGENTS.md` in each workspace:
```markdown
## Every Session

1. Read `SOUL.md`
2. Read `USER.md`
3. Read `brainx.md`
4. Read `BRAINX_CONTEXT.md` ← Auto-injected context
```

## Available Tools

### brainx_add_memory

Saves a memory to the vector brain.

**Parameters:**
- `content` (required) — Memory text
- `type` (optional) — Type: note, decision, action, learning (default: note)
- `context` (optional) — Namespace/scope
- `tier` (optional) — Priority: hot, warm, cold, archive (default: warm)
- `importance` (optional) — Importance 1-10 (default: 5)
- `tags` (optional) — Comma-separated tags
- `agent` (optional) — Name of the agent creating the memory

**Example:**
```
brainx add --type decision --content "Use embeddings 3-small to reduce costs" --tier hot --importance 9 --tags config,openai
```

### brainx_search

Searches memories by semantic similarity.

**Parameters:**
- `query` (required) — Search text
- `limit` (optional) — Number of results (default: 10)
- `minSimilarity` (optional) — Threshold 0-1 (default: 0.3)
- `minImportance` (optional) — Filter by importance 0-10
- `tier` (optional) — Filter by tier
- `context` (optional) — Exact context filter

**Example:**
```
brainx search --query "API configuration" --limit 5 --minSimilarity 0.5
```

**Returns:** JSON with results.

### brainx_inject

Gets memories formatted for direct injection into LLM prompts.

**Parameters:**
- `query` (required) — Search text
- `limit` (optional) — Number of results (default: 10)
- `minImportance` (optional) — Filter by importance
- `tier` (optional) — Tier filter (default: hot+warm)
- `context` (optional) — Context filter
- `maxCharsPerItem` (optional) — Truncate content (default: 2000)

**Example:**
```
brainx inject --query "what decisions were made about openai" --limit 3
```

**Returns:** Formatted text ready for injection:
```
[sim:0.82 imp:9 tier:hot type:decision agent:coder ctx:openclaw]
Use embeddings 3-small to reduce costs...

---

[sim:0.71 imp:8 tier:hot type:decision agent:support ctx:brainx]
Create SKILL.md for OpenClaw integration...
```

### brainx_health

Verifies BrainX is operational.

**Parameters:** none

**Example:**
```
brainx health
```

**Returns:** PostgreSQL + pgvector connection status.

## Backup and Recovery

### Create Backup

```bash
./scripts/backup-brainx.sh ~/backups
```

Creates `brainx-v5_backup_YYYYMMDD_HHMMSS.tar.gz` containing:
- Full PostgreSQL database (SQL dump)
- OpenClaw configuration (hooks, .env)
- Skill files
- Workspace documentation

### Restore Backup

```bash
./scripts/restore-brainx.sh backup.tar.gz --force
```

Fully restores BrainX V5 including:
- All memories (with embeddings)
- Hook configuration
- Environment variables

### Full Documentation

See [RESILIENCE.md](RESILIENCE.md) for:
- Complete disaster scenarios
- Migration to new VPS
- Troubleshooting
- Automatic backup configuration

## Configuration

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/brainx_v5
OPENAI_API_KEY=sk-...

# Optional
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536
BRAINX_INJECT_DEFAULT_TIER=hot+warm
BRAINX_INJECT_MAX_CHARS_PER_ITEM=2000
BRAINX_INJECT_MAX_LINES_PER_ITEM=80
```

### Database Setup

```bash
# Schema is in ~/.openclaw/skills/brainx-v5/sql/
# Requires PostgreSQL with pgvector extension

psql $DATABASE_URL -f ~/.openclaw/skills/brainx-v5/sql/v3-schema.sql
```

## Direct Integration

You can also use the unified wrapper that reads the API key from OpenClaw:

```bash
cd ~/.openclaw/skills/brainx-v5
./brainx add --type note --content "test"
./brainx search --query "test"
./brainx inject --query "test"
./brainx health
```

Compatibility: `./brainx-v5` and `./brainx-v5-cli` also work as aliases for the main wrapper.

## Advisory System (Pre-Action Check)

BrainX includes an advisory system that queries relevant memories, trajectories, and recurring patterns before executing high-risk tools. Helps agents avoid repeating past mistakes.

### High-Risk Tools

The following tools automatically trigger advisory checks: `exec`, `deploy`, `railway`, `delete`, `rm`, `drop`, `git push`, `git force-push`, `migration`, `cron`, `message send`, `email send`.

### CLI Usage

```bash
# Check for advisories before a tool execution
./brainx-v5 advisory --tool exec --args '{"command":"rm -rf /tmp/old"}' --agent coder --json

# Quick check via helper script
./scripts/advisory-check.sh exec '{"command":"rm -rf /tmp/old"}' coder
```

### Agent Integration (Manual)

Since only `agent:bootstrap` is supported as a hook event, agents should manually call `brainx advisory` before high-risk tools:

```bash
# In agent SKILL.md or AGENTS.md, add:
# Before exec/deploy/delete/migration, run:
cd ~/.openclaw/skills/brainx-v5 && ./scripts/advisory-check.sh <tool> '<args_json>' <agent>
```

The advisory returns relevant memories, similar past problem→solution paths, and recurring patterns with a confidence score. It's informational — never blocking.

### Agent-Aware Hook Injection

The `agent:bootstrap` hook uses **agent profiles** (`hook/agent-profiles.json`) to customize memory injection per agent:

- **coder**: Boosts gotcha/error/learning memories; filters by infrastructure/code/deploy/github contexts; excludes notes
- **writer**: Boosts decision/learning; filters by content/seo/marketing; excludes errors
- **monitor**: Boosts gotcha/error; filters by infrastructure/health/monitoring
- **echo**: No filtering (default behavior)

Agents not listed in the profiles file get the default unfiltered injection. Edit `hook/agent-profiles.json` to add new agent profiles.

### Cross-Agent Memory Sharing

The hook reserves ~30% of injection slots for **cross-agent memories**, ensuring each agent sees relevant learnings from other agents. The `cross-agent-learning.js` script tags high-importance memories for cross-agent visibility without creating duplicates.

## Security & Trust

This skill is flagged with "suspicious patterns" by ClawHub's automated scanner. Here's what each pattern does and why it's necessary:

| Pattern | File | Why |
|---|---|---|
| `child_process.execFile` | `hook/handler.js` | Invokes the BrainX CLI to query memories during agent bootstrap. No arbitrary command execution. |
| `process.env` access | `lib/db.js`, `lib/openai-rag.js`, `lib/cli.js` | Reads `DATABASE_URL` and `OPENAI_API_KEY` to connect to PostgreSQL and generate embeddings. Standard for any database-backed skill. |
| `fetch('https://api.openai.com')` | `lib/openai-rag.js` | Calls OpenAI Embeddings API to generate vector representations. Single endpoint, no other network calls. |
| File read/write | `hook/handler.js` | Writes `BRAINX_CONTEXT.md` and updates `MEMORY.md` in the agent's workspace during bootstrap injection. |

**No secrets are stored in code.** All credentials come from environment variables. No data leaves the system except embedding requests to OpenAI.

## Notes

- Memories are stored with vector embeddings (1536 dimensions)
- Search uses cosine similarity
- `inject` is the most useful tool for giving context to LLMs
- Tier hot = fast access, cold/archive = long-term storage
- Memories are persistent in PostgreSQL (independent of OpenClaw)
- Auto-injection hook fires on every `agent:bootstrap`

## Feature Status (Tables)

### ✅ All Operational
| Table | Function | Status |
|---|---|---|
| `brainx_memories` | Core: stores memories with embeddings | ✅ Active (2,400+) |
| `brainx_query_log` | Tracks search/inject queries | ✅ Active |
| `brainx_pilot_log` | Tracks auto-inject per agent | ✅ Active |
| `brainx_context_packs` | Pre-generated context packages | ✅ Active |
| `brainx_patterns` | Detects recurring errors/issues | ✅ Active |
| `brainx_session_snapshots` | Captures state at session close | ✅ Active |
| `brainx_learning_details` | Extended metadata for learning/gotcha memories | ✅ Active |
| `brainx_trajectories` | Records problem→solution paths | ✅ Active |

> 8/8 tables operational. Population scripts implemented 2026-03-06.

## Full Feature Inventory (35)

### CLI Core (`brainx <cmd>`)
| # | Command | Function |
|---|---|---|
| 1 | `add` | Save memory (7 types, 20+ categories, V5 metadata) |
| 2 | `search` | Semantic search by cosine similarity |
| 3 | `inject` | Formatted memories for LLM prompt injection |
| 4 | `fact` / `facts` | Shortcut to save/list infrastructure facts |
| 5 | `resolve` | Mark pattern as resolved/promoted/wont_fix |
| 6 | `promote-candidates` | Detect memories eligible for promotion |
| 7 | `lifecycle-run` | Degrade/promote memories by age/usage |
| 8 | `metrics` | Metrics dashboard and top patterns |
| 9 | `doctor` | Full diagnostics (schema, integrity, stats) |
| 10 | `fix` | Auto-repair issues detected by doctor |
| 11 | `feedback` | Mark memory as useful/useless/incorrect |
| 12 | `health` | PostgreSQL + pgvector connection status |

### Processing Scripts (`scripts/`)
| # | Script | Function |
|---|---|---|
| 13 | `memory-bridge.js` | Syncs memory between sessions/agents |
| 14 | `memory-distiller.js` | Distills sessions into new memories |
| 15 | `session-harvester.js` | Harvests info from past sessions |
| 16 | `session-snapshot.js` | Captures state at session close |
| 17 | `pattern-detector.js` | Detects recurring errors/issues |
| 18 | `learning-detail-extractor.js` | Extracts metadata from learnings/gotchas |
| 19 | `trajectory-recorder.js` | Records problem→solution paths |
| 20 | `fact-extractor.js` | Extracts facts from conversations |
| 21 | `contradiction-detector.js` | Detects contradicting memories |
| 22 | `cross-agent-learning.js` | Shares learnings between agents |
| 23 | `quality-scorer.js` | Scores memory quality |
| 24 | `context-pack-builder.js` | Generates pre-built context packages |
| 25 | `reclassify-memories.js` | Reclassifies memories with correct types/categories |
| 26 | `cleanup-low-signal.js` | Cleans up low-value memories |
| 27 | `dedup-supersede.js` | Detects and marks duplicates |
| 28 | `eval-memory-quality.js` | Evaluates dataset quality |
| 29 | `generate-eval-dataset-from-memories.js` | Generates evaluation dataset |
| 30 | `memory-feedback.js` | Per-memory feedback system |
| 31 | `import-workspace-memory-md.js` | Imports from workspace MEMORY.md files |
| 32 | `migrate-v2-to-v3.js` | Schema migration V2→V3 |
| 33 | `promotion-applier.js` | Last-mile auto-promotion: distills patterns via LLM and writes rules to workspace files |

### Hooks and Infrastructure
| # | Component | Function |
|---|---|---|
| 34 | `brainx-auto-inject` | Auto-injection hook at each agent bootstrap |
| 35 | `backup-brainx.sh` | Full backup (DB + config + skills) |
| 36 | `restore-brainx.sh` | Full restore from backup |
| 37 | `promotion-applier.js` | Pipeline step 13: writes promoted patterns to workspace files |

### V5 Metadata
- `sourceKind` — Origin: user_explicit, agent_inference, tool_verified, llm_distilled, etc.
- `sourcePath` — Source file/URL
- `confidence` — Score 0-1
- `expiresAt` — Automatic expiration
- `sensitivity` — normal/sensitive/restricted
- Automatic PII scrubbing (`BRAINX_PII_SCRUB_ENABLED`)
- Similarity-based dedup (`BRAINX_DEDUPE_SIM_THRESHOLD`)
