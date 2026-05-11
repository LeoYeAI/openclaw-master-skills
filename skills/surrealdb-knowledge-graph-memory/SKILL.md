---
name: surrealdb-memory
description: "A comprehensive knowledge graph memory system with semantic search, episodic memory, working memory, automatic context injection, and per-agent isolation."
version: 2.2.2
metadata:
  openclaw:
    requires:
      env:
        - OPENAI_API_KEY
        - SURREAL_USER
        - SURREAL_PASS
        - SURREAL_URL
      bins:
        - surreal
        - python3
    primaryEnv: OPENAI_API_KEY
    emoji: "🧠"
    homepage: "https://clawhub.com/skills/surrealdb-knowledge-graph-memory"
---

# SurrealDB Knowledge Graph Memory v2.2

A comprehensive knowledge graph memory system with semantic search, episodic memory, working memory, automatic context injection, and **per-agent isolation** — enabling every agent to become a continuously self-improving AI.

## Description

Use this skill for:
- **Semantic Memory** — Store and retrieve facts with confidence-weighted vector search
- **Episodic Memory** — Record task histories and learn from past experiences
- **Working Memory** — Track active task state with crash recovery
- **Auto-Injection** — Automatically inject relevant context into agent prompts
- **Outcome Calibration** — Facts gain/lose confidence based on task outcomes
- **Self-Improvement** — Scheduled extraction and relation discovery make every agent smarter over time

**Triggers:** "remember this", "store fact", "what do you know about", "memory search", "find similar tasks", "learn from history"

> **Security:** This skill reads workspace memory files and sends their content to OpenAI for extraction. It registers two background cron jobs and (optionally) patches OpenClaw source files. All behaviors are opt-in or documented. See [SECURITY.md](SECURITY.md) for the full breakdown before enabling.
>
> **Required:** `OPENAI_API_KEY`, `surreal` binary, `python3` ≥3.10

---

## 🔄 Self-Improving Agent Loop

This is the core concept: **every agent equipped with this skill improves itself automatically**, with no manual intervention required. Two scheduled cron jobs — knowledge extraction and relationship correlation — run on a fixed schedule and continuously grow the knowledge graph. Combined with auto-injection, the agent gets progressively smarter with each conversation.

### The Cycle

```
[Agent Conversation]
       ↓  stores important facts via knowledge_store_sync
[Memory Files]  ← agent writes to MEMORY.md / daily memory/*.md files
       ↓  every 6 hours — extraction cron fires
[Entity + Fact Extraction]  ← LLM reads files, extracts structured facts + entities
       ↓  facts stored with embeddings + agent_id tag
[Knowledge Graph]  ← SurrealDB: facts, entities, mentions
       ↓  daily at 3 AM — relation discovery cron fires
[Relationship Correlation]  ← AI finds semantic links between facts
       ↓  relates_to edges created between connected facts
[Richer Knowledge Graph]  ← facts are no longer isolated; they form a web
       ↓  on every new message — auto-injection reads the graph
[Context Window]  ← relevant facts + relations + episodes injected automatically
       ↓
[Better Responses]  ← agent uses accumulated knowledge to respond more accurately
       ↑  new insights written back to memory files → cycle repeats
```

### What Each Scheduled Job Does

#### Job 1 — Knowledge Extraction (every 6 hours)
**Script:** `scripts/extract-knowledge.py extract`

- Reads `MEMORY.md` and all `memory/YYYY-MM-DD.md` files in the workspace
- Uses an LLM (GPT-4) to extract structured facts, entities, and key concepts
- Hashes file content to skip unchanged files — only processes diffs
- Stores each fact with:
  - A vector embedding (OpenAI `text-embedding-3-small`) for semantic search
  - A `confidence` score (defaults to 0.9)
  - An `agent_id` tag so facts stay isolated to the right agent
  - `source` metadata pointing back to the originating file
- Result: raw conversational knowledge becomes searchable, structured memory

#### Job 2 — Relationship Correlation (daily at 3 AM)
**Script:** `scripts/extract-knowledge.py discover-relations`

- Queries the graph for facts that have no relationships yet ("isolated facts")
- Batches them and asks an LLM to identify semantic connections between them
- Creates `relates_to` edges in SurrealDB linking related facts
- Result: isolated facts become a **connected knowledge web** — the agent can now traverse relationships, not just keyword-match
- Over time, the graph evolves from a flat list into a rich semantic network

#### Job 3 — Deduplication (daily at 4 AM)
**Script:** `scripts/extract-knowledge.py dedupe --threshold 0.92`

- Compares all facts using vector similarity (cosine distance)
- Facts above the threshold (92% similar) are flagged as duplicates
- Keeps the higher-confidence fact, removes the duplicate
- Prevents extraction from creating bloat over time
- Result: a clean, non-redundant knowledge base

#### Job 4 — Reconciliation (weekly, Sundays at 5 AM)
**Script:** `scripts/extract-knowledge.py reconcile --verbose`

- Applies time-based confidence decay to aging facts
- Prunes facts that have decayed below minimum confidence
- Cleans orphaned entities with no linked facts
- Consolidates near-duplicate entities
- Result: the knowledge graph stays healthy, relevant, and pruned of stale information

### Why This Makes Agents Self-Improving

When auto-injection is enabled, every new conversation starts with the most relevant slice of the accumulated knowledge graph. As the agent:
1. Has conversations → writes insights to memory files
2. Extraction job fires → converts those insights into structured facts
3. Relation job fires → connects those facts to existing knowledge
4. Next conversation → auto-injection pulls in richer, more connected context

...the agent effectively gets smarter with every cycle. It learns from its own outputs, grounds future responses in its accumulated history, and avoids repeating mistakes (via episodic memory and outcome calibration).

### OpenClaw Cron Jobs (Required)

The skill requires **5 cron jobs** for full self-improving operation. All run as isolated background sessions with no delivery:

| Job Name | Schedule | What it runs |
|----------|----------|--------------|
| Memory Knowledge Extraction | Every 6 hours (`0 */6 * * *`) | `extract-knowledge.py extract` — extracts facts from memory files |
| Memory Relation Discovery | Daily at 3 AM (`0 3 * * *`) | `extract-knowledge.py discover-relations` — AI-powered relationship finding |
| Memory Deduplication | Daily at 4 AM (`0 4 * * *`) | `extract-knowledge.py dedupe --threshold 0.92` — removes duplicate/near-duplicate facts |
| Memory Reconciliation | Weekly Sun 5 AM (`0 5 * * 0`) | `extract-knowledge.py reconcile --verbose` — prunes stale facts, applies confidence decay, cleans orphans |

> All jobs use `sessionTarget: "isolated"` with `delivery: none`. They run in fully isolated background sessions and **never fire into the main agent session**. A bottom-right corner toast notification appears in the Control UI when each job starts and completes.

**Setup commands** (run after installation):

```bash
# 1. Knowledge Extraction — every 6 hours
openclaw cron add \
  --name "Memory Knowledge Extraction" \
  --cron "0 */6 * * *" \
  --agent main --session isolated --no-deliver \
  --timeout-seconds 300 \
  --message "Run memory knowledge extraction. Execute: cd SKILL_DIR && source .venv/bin/activate && python3 scripts/extract-knowledge.py extract"

# 2. Relation Discovery — daily at 3 AM
openclaw cron add \
  --name "Memory Relation Discovery" \
  --cron "0 3 * * *" --exact \
  --agent main --session isolated --no-deliver \
  --timeout-seconds 300 \
  --message "Run memory relation discovery. Execute: cd SKILL_DIR && source .venv/bin/activate && python3 scripts/extract-knowledge.py discover-relations"

# 3. Deduplication — daily at 4 AM
openclaw cron add \
  --name "Memory Deduplication" \
  --cron "0 4 * * *" --exact \
  --agent main --session isolated --no-deliver \
  --timeout-seconds 120 \
  --message "Run knowledge graph deduplication. Execute: cd SKILL_DIR && source .venv/bin/activate && python3 scripts/extract-knowledge.py dedupe --threshold 0.92"

# 4. Reconciliation — weekly on Sundays at 5 AM
openclaw cron add \
  --name "Memory Reconciliation" \
  --cron "0 5 * * 0" --exact \
  --agent main --session isolated --no-deliver \
  --timeout-seconds 180 \
  --message "Run knowledge graph reconciliation. Execute: cd SKILL_DIR && source .venv/bin/activate && python3 scripts/extract-knowledge.py reconcile --verbose"
```

> Replace `SKILL_DIR` with your actual skill path.

To check job status:
```bash
openclaw cron list
```

### Adding Cron Jobs for a New Agent

When spawning a new agent that should self-improve, register its own extraction job:

```bash
# OpenClaw cron add (via Koda) — example for a 'scout-monitor' agent
# Schedule: every 6h, extract facts tagged to scout-monitor
python3 scripts/extract-knowledge.py extract --agent-id scout-monitor
```

The `--agent-id` flag ensures extracted facts are isolated to that agent's pool and don't pollute the main agent's knowledge. Each agent self-improves independently while still reading shared `scope='global'` facts.

---

## Features (v2.2)

| Feature | Description |
|---------|-------------|
| **Semantic Facts** | Vector-indexed facts with confidence scoring |
| **Episodic Memory** | Task histories with decisions, problems, solutions, learnings |
| **Working Memory** | YAML-based task state that survives crashes |
| **Outcome Calibration** | Facts used in successful tasks gain confidence |
| **Auto-Injection** | Relevant facts/episodes injected into prompts automatically |
| **Entity Extraction** | Automatic entity linking and relationship discovery |
| **Confidence Decay** | Stale facts naturally decay over time |
| **Agent Isolation** | Each agent has its own scoped memory pool; `scope='global'` facts are shared across all agents |
| **Self-Improving Loop** | Scheduled extraction + relation discovery automatically grow the graph |

---

## Agent Isolation (v2.2)

Each agent in OpenClaw has its own scoped memory pool. Facts are tagged with `agent_id` on write; all read queries filter to `(agent_id = $agent_id OR scope = 'global')`.

### How it works

```
Agent A (main)          Agent B (scout-monitor)
   ┌──────────┐              ┌──────────┐
   │ 391 facts│              │   0 facts│   ← isolated pools
   └──────────┘              └──────────┘
         ↑                         ↑
         └──── scope='global' ─────┘   ← shared facts visible to both
```

### Storing facts

All `knowledge_store` / `knowledge_store_sync` calls accept `agent_id`:

```bash
# Stored to scout-monitor's pool only
mcporter call surrealdb-memory.knowledge_store \
    content="API is healthy at /ping" \
    agent_id='scout-monitor'

# Stored globally (visible to all agents)
mcporter call surrealdb-memory.knowledge_store \
    content="Project uses Python 3.12" \
    agent_id='main' scope='global'
```

### Auto-injection (agent-aware)

With `references/enhanced-loop-hook-agent-isolation.md` applied to `src/agents/enhanced-loop-hook.ts`, the enhanced loop automatically extracts the agent ID from the session key and passes it to `memory_inject`. No manual configuration needed — each agent's auto-injection is silently scoped to its own facts.

### Extraction (agent-aware)

Pass `--agent-id` to `extract-knowledge.py` so cron-extracted facts are correctly tagged:

```bash
python3 scripts/extract-knowledge.py extract --agent-id scout-monitor
```

Default is `"main"`. Update cron jobs accordingly for non-main agents.

### Backward compatibility

Existing facts without an explicit `agent_id` are treated as owned by `"main"`. Nothing is lost on upgrade to v2.2.

---

## Dashboard UI

The Memory tab in the Control dashboard provides a two-column layout:

### Left Column: Dashboard
- **📊 Statistics** — Live counts of facts, entities, relations, and archived items
- **Confidence Bar** — Visual display of average confidence score
- **Sources Breakdown** — Facts grouped by source file
- **🏥 System Health** — Status of SurrealDB, schema, and Python dependencies
- **🔗 DB Studio** — Quick link to SurrealDB's web interface

### Right Column: Operations
- **📥 Knowledge Extraction**
  - *Extract Changes* — Incrementally extract facts from modified files
  - *Find Relations* — Discover semantic relationships between existing facts
  - *Full Sync* — Complete extraction + relation discovery
  - Progress bar with real-time status updates
  
- **🔧 Maintenance**
  - *Apply Decay* — Reduce confidence of stale facts
  - *Prune Stale* — Archive facts below threshold
  - *Full Sweep* — Complete maintenance cycle

- **💡 Tips** — Quick reference for operations

When the system needs setup, an **Installation** section appears with manual controls.

---

## Prerequisites

1. **SurrealDB** installed and running:
   ```bash
   # Install (one-time)
   ./scripts/install.sh
   
   # Start server
   surreal start --bind 127.0.0.1:8000 --user root --pass root file:~/.openclaw/memory/knowledge.db
   ```

2. **Python dependencies** (use the skill's venv):
   ```bash
   cd /path/to/surrealdb-memory
   python3 -m venv .venv
   source .venv/bin/activate
   pip install surrealdb openai pyyaml
   ```

3. **OpenAI API key** for embeddings (set in OpenClaw config or environment)

4. **mcporter** configured with this skill's MCP server

## MCP Server Setup

Add to your `config/mcporter.json`:

```json
{
  "servers": {
    "surrealdb-memory": {
      "command": ["python3", "/path/to/surrealdb-memory/scripts/mcp-server-v2.py"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "SURREAL_URL": "http://localhost:8000",
        "SURREAL_USER": "root",
        "SURREAL_PASS": "root"
      }
    }
  }
}
```

---

## MCP Tools (11 total)

### Core Tools
| Tool | Description |
|------|-------------|
| `knowledge_search` | Semantic search for facts |
| `knowledge_recall` | Get a fact with full context (relations, entities) |
| `knowledge_store` | Store a new fact |
| `knowledge_stats` | Get database statistics |

### v2 Tools
| Tool | Description |
|------|-------------|
| `knowledge_store_sync` | Store with importance routing (high importance = immediate write) |
| `episode_search` | Find similar past tasks |
| `episode_learnings` | Get actionable learnings from history |
| `episode_store` | Record a completed task episode |
| `working_memory_status` | Get current task state |
| `context_aware_search` | Search with task context boosting |
| `memory_inject` | **Intelligent context injection for prompts** |

### memory_inject Tool

The `memory_inject` tool returns formatted context ready for prompt injection:

```bash
# Scoped to a specific agent (returns only that agent's facts + global facts)
mcporter call surrealdb-memory.memory_inject \
    query="user message" \
    max_facts:7 \
    max_episodes:3 \
    confidence_threshold:0.9 \
    include_relations:true \
    agent_id='scout-monitor'
```

**Output:**
```markdown
## Semantic Memory (Relevant Facts)
📌 [60% relevant, 100% confidence] Relevant fact here...

## Related Entities
• Entity Name (type)

## Episodic Memory (Past Experiences)
✅ Task: Previous task goal [similarity]
   → Key learning from that task
```

---

## Auto-Injection (Enhanced Loop Integration)

When enabled, memory is automatically injected into every agent turn:

1. **Enable in Mode UI:**
   - Open Control dashboard → Mode tab
   - Scroll to "🧠 Memory & Knowledge Graph" section
   - Toggle "Auto-Inject Context"
   - Configure limits (max facts, max episodes, confidence threshold)

2. **How it works:**
   - On each user message, `memory_inject` is called automatically
   - Relevant facts are searched based on the user's query
   - If average fact confidence < threshold, episodic memories are included
   - Formatted context is injected into the agent's system prompt
   - **v2.2:** With `references/enhanced-loop-hook-agent-isolation.md` applied, the active agent's ID is automatically extracted from the session key and passed as `agent_id` — each agent's injection is silently scoped to its own facts

3. **Configuration (in Mode settings):**
   | Setting | Default | Description |
   |---------|---------|-------------|
   | Auto-Inject Context | Off | Master toggle |
   | Max Facts | 7 | Maximum semantic facts to inject |
   | Max Episodes | 3 | Maximum episodic memories |
   | Confidence Threshold | 90% | Include episodes when below this |
   | Include Relations | On | Include entity relationships |

---

## CLI Commands

```bash
# Activate venv
source .venv/bin/activate

# Store a fact
python scripts/memory-cli.py store "Important fact" --confidence 0.9

# Search
python scripts/memory-cli.py search "query"

# Get stats
python scripts/knowledge-tool.py stats

# Run maintenance
python scripts/memory-cli.py maintain

# Extract from files (incremental)
python scripts/extract-knowledge.py extract

# Extract for a specific agent
python scripts/extract-knowledge.py extract --agent-id scout-monitor

# Force full extraction (all files, not just changed)
python scripts/extract-knowledge.py extract --full

# Discover semantic relationships
python scripts/extract-knowledge.py discover-relations
```

---

## Database Schema (v2)

### Tables
- `fact` — Semantic facts with embeddings and confidence
- `entity` — Extracted entities (people, places, concepts)
- `relates_to` — Relationships between facts
- `mentions` — Fact-to-entity links
- `episode` — Task histories with outcomes
- `working_memory` — Active task snapshots

### Key Fields (fact)
- `content` — The fact text
- `embedding` — Vector for semantic search
- `confidence` — Base confidence (0-1)
- `success_count` / `failure_count` — Outcome tracking
- `scope` — global, client, or agent
- `agent_id` — Which agent owns this fact (v2.2)

### Key Fields (episode)
- `goal` — What was attempted
- `outcome` — success, failure, abandoned
- `decisions` — Key decisions made
- `problems` — Problems encountered (structured)
- `solutions` — Solutions applied (structured)
- `key_learnings` — Extracted lessons

---

## Confidence Scoring

Effective confidence is calculated from:
- **Base confidence** (0.0–1.0)
- **+ Inherited boost** from supporting facts
- **+ Entity boost** from well-established entities
- **+ Outcome adjustment** based on success/failure history
- **- Contradiction drain** from conflicting facts
- **- Time decay** (configurable, ~5% per month)

---

## Maintenance

### Automated — OpenClaw Cron (as deployed)

The self-improving loop runs via **4 registered OpenClaw cron jobs**:

```
Every 6h     → extract-knowledge.py extract            (extract facts from memory files)
Daily 3 AM   → extract-knowledge.py discover-relations  (find relationships between facts)
Daily 4 AM   → extract-knowledge.py dedupe              (remove duplicate facts)
Weekly Sun   → extract-knowledge.py reconcile            (prune stale, decay, clean orphans)
```

See the "OpenClaw Cron Jobs (Required)" section above for setup commands.

To verify they're active:
```bash
openclaw cron list
```

To manually trigger any job:
```bash
cd SKILL_DIR && source .venv/bin/activate
python3 scripts/extract-knowledge.py extract
python3 scripts/extract-knowledge.py discover-relations
python3 scripts/extract-knowledge.py dedupe --threshold 0.92
python3 scripts/extract-knowledge.py reconcile --verbose
```

### Manual (UI)
Use the **Maintenance** section in the Memory tab:
- **Apply Decay** — Reduce confidence of stale facts
- **Prune Stale** — Archive facts below 0.3 confidence
- **Full Sweep** — Run complete maintenance cycle

---

## Files

### Scripts
| File | Purpose |
|------|---------|
| `mcp-server-v2.py` | MCP server with all 11 tools |
| `mcp-server.py` | Legacy v1 MCP server |
| `episodes.py` | Episodic memory module |
| `working_memory.py` | Working memory module |
| `memory-cli.py` | CLI for manual operations |
| `extract-knowledge.py` | Bulk extraction from files (supports `--agent-id`) |
| `knowledge-tools.py` | Higher-level extraction |
| `schema-v2.sql` | v2 database schema |
| `migrate-v2.py` | Migration script |

### Integration
| File | Purpose |
|------|---------|
| `openclaw-integration/gateway/memory.ts` | Gateway server methods |
| `openclaw-integration/ui/memory-view.ts` | Memory dashboard UI |
| `openclaw-integration/ui/memory-controller.ts` | UI controller |

---

## Troubleshooting

**"Connection refused"**
→ Start SurrealDB: `surreal start --bind 127.0.0.1:8000 --user root --pass root file:~/.openclaw/memory/knowledge.db`

**"No MCP servers configured"**
→ Ensure mcporter is run from a directory containing `config/mcporter.json` with the surrealdb-memory server defined

**Memory injection returning null**
→ Check that `OPENAI_API_KEY` is set in the environment
→ Verify SurrealDB is running and schema is initialized

**Empty search results**
→ Run extraction from the UI or via CLI: `python3 scripts/extract-knowledge.py extract`

**"No facts to analyze" on relation discovery**
→ This is normal if all facts are already related — the graph is well-connected. Run extraction first if the graph is empty.

**Progress bar not updating**
→ Ensure the gateway has been restarted after UI updates
→ Check browser console for polling errors

**Facts from wrong agent appearing**
→ Check that `agent_id` is being passed correctly to all store/search calls
→ Verify `references/enhanced-loop-hook-agent-isolation.md` is applied for auto-injection scoping

---

## Migration from v1 / v2.1

```bash
# Apply v2 schema (additive, won't delete existing data)
./scripts/migrate-v2.sh

# Or manually:
source .venv/bin/activate
python scripts/migrate-v2.py
```

All existing facts without an `agent_id` are treated as owned by `"main"` — backward compatible.

---

## Stats

Check your knowledge graph via UI (Dashboard section) or CLI:
```bash
mcporter call surrealdb-memory.knowledge_stats
```

Example output:
```json
{
  "facts": 379,
  "entities": 485,
  "relations": 106,
  "episodes": 3,
  "avg_confidence": 0.99
}
```

---

*v2.2 — Agent isolation, self-improving loop, cron-based extraction & relationship correlation*
