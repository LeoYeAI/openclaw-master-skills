# 🧠 BrainX V5 — The First Brain for OpenClaw

![BrainX Banner](assets/brainx-banner.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-blue.svg)](https://openclaw.ai)
[![Version](https://img.shields.io/badge/version-0.3.1-green.svg)](https://github.com/Mdx2025/brainx-v5)

BrainX V5 is a **persistent memory and vector database system** for AI agents, built on PostgreSQL + pgvector + OpenAI embeddings. It gives every OpenClaw agent the ability to remember, learn, and share knowledge across sessions — delivering true **AI agent memory**, **cross-agent learning**, and **semantic search** at production scale.

> **Production-tested · 30+ agent profiles supported · 18/18 doctor checks · Version 0.3.1**

| # | Feature | Description |
|---|---------|-------------|
| 1 | ✅ **Production** | Active with centralized shared memory across all agents |
| 2 | 🧠 **Auto-Learning** | Learns on its own from every conversation without human intervention |
| 3 | 💾 **Persistent Memory** | Remembers across sessions — PostgreSQL + pgvector vector database |
| 4 | 🤝 **Shared Memory** | All agents share the same knowledge management pool |
| 5 | 💉 **Automatic Briefing** | Personalized context injection at each agent startup |
| 6 | 🔎 **Semantic Search** | Searches by meaning, not exact keywords — pgvector cosine similarity |
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
| 22 | 🛡️ **Pre-Action Advisory** | Queries past mistakes before high-risk tool execution (exec, deploy, delete) |
| 23 | 👤 **Agent Profiles** | Per-agent hook injection: boosts/filters memories by agent role |
| 24 | 🔀 **Cross-Agent Injection Slots** | Hook reserves 30% of context slots for other agents' memories |
| 25 | 📊 **Metrics Dashboard** | CLI dashboard with top patterns, memory stats, and usage trends |
| 26 | 🔧 **Doctor & Auto-Fix** | Schema integrity check + automatic repair of detected issues (18/18 passing) |
| 27 | 👍 **Memory Feedback** | Mark memories as useful/useless/incorrect to refine quality |
| 28 | 🗺️ **Trajectory Recording** | Records problem→solution paths for future reference |
| 29 | 📝 **Learning Details** | Extended metadata extraction for learnings and gotchas |
| 30 | 🔄 **Lifecycle Management** | Automatic promotion/degradation of memories by age and usage |
| 31 | 📥 **Workspace Import** | Imports existing MEMORY.md files from all workspaces into the brain |
| 32 | 🧪 **Eval Dataset Generation** | Generates evaluation datasets from real memories for quality testing |
| 33 | 🏗️ **Session Snapshots** | Captures full agent state at session close for analysis |
| 34 | 🧹 **Low-Signal Cleanup** | Automatic cleanup of low-value, outdated, or redundant memories |
| 35 | 🔃 **Memory Reclassification** | Reclassifies memories with correct types and categories post-hoc |
| 36 | 🔄 **Auto-Promotion Pipeline** | Detects high-recurrence patterns and automatically promotes them as rules in agent workspace files (AGENTS.md, TOOLS.md, SOUL.md). Closes the learning → rule loop without human intervention. |
| 37 | 📊 **15-Step Daily Pipeline** | Consolidated daily pipeline running 15 automated steps: bootstrap, lifecycle, distiller, harvester, bridge, auto-distiller, consolidation, cross-agent learning, contradiction detection, markdown harvester, error harvester, auto-promoter, promotion-applier, memory-enforcer, and audit. |

> **Name:** The repo/CLI keeps the historical name `brainx-v5`. The current version is **BrainX V5** (v0.3.1) with governance, observability, lifecycle management, auto-promotion pipeline, and an LLM-powered auto-feeding system.

---

## Status

### Validation — 2026-03-18

BrainX V5 is fully validated and production-tested:

- **18/18 doctor checks passing** — database, schema, embeddings, hooks, and pipeline all green
- **Multi-agent smoke-tested** — bootstrap injection, context generation, and telemetry confirmed working
- **Cross-agent injection** active — agents receive relevant memories from other agents (30% injection slots)
- **Agent profiles** configured with role-specific boosting and filtering

Run `./brainx-v5 doctor` anytime to verify your installation health.

## Post-Update Sync Checklist

After updating BrainX V5, sync the managed hook to prevent runtime drift:

1. Copy hook files from the skill source to the managed hook directory
2. Run `./brainx-v5 doctor` — expect all checks passing
3. Run a bootstrap smoke test on any agent and verify `MEMORY.md` updates
4. Confirm telemetry lands in the database
7. **If cron architecture changes again, update both code and docs together**
   - Update `lib/doctor.js`
   - Update this `README.md`
   - Update `hook/HOOK.md` if deployment steps change
   - Update `CRON.md` if production scheduler topology changed

### Key files to keep in sync

When updating BrainX V5, ensure these stay aligned:
- Skill source files: `README.md`, `lib/doctor.js`, `hook/*`
- Managed hook: the deployed copy of hook files in your OpenClaw hooks directory
- Cron config: if you change the pipeline schedule or steps

---

## 🧠 Auto-Learning

> **BrainX doesn't just store memories — it learns on its own.** Auto-Learning is the integrated system that makes every agent improve with every conversation, without human intervention.

Auto-Learning is NOT a single script. It is the **complete orchestration** of capture, curation, propagation, and injection that converts ephemeral conversations into permanent, shared knowledge. It runs 24/7 via cron jobs, with no human intervention required.

### Complete Auto-Learning Cycle

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    🧠 AUTO-LEARNING CYCLE                               │
│                                                                          │
│   ┌─────────────┐    ┌──────────────┐    ┌──────────────┐               │
│   │   Agent      │    │    Files     │    │   Agents     │               │
│   │  Sessions    │    │  memory/*.md │    │  (manual)    │               │
│   └──────┬──────┘    └──────┬───────┘    └──────┬───────┘               │
│          │                  │                    │                        │
│          ▼                  ▼                    ▼                        │
│   ┌─────────────────────────────────────────────────────┐               │
│   │         📥 AUTOMATIC CAPTURE (3 layers)              │               │
│   │                                                      │               │
│   │  Memory Distiller ──► LLM extracts memories          │               │
│   │  Fact Extractor   ──► Regex extracts hard data       │               │
│   │  Session Harvester ─► Heuristics classify            │               │
│   │  Memory Bridge    ──► Sync markdown → vector         │               │
│   └──────────────────────────┬──────────────────────────┘               │
│                              ▼                                           │
│                    ┌─────────────────┐                                   │
│                    │  PostgreSQL +   │                                   │
│                    │  pgvector       │                                   │
│                    │  (centralized   │                                   │
│                    │   memory)       │                                   │
│                    └────────┬────────┘                                   │
│                             │                                            │
│          ┌──────────────────┼──────────────────┐                        │
│          ▼                  ▼                   ▼                        │
│   ┌─────────────┐  ┌──────────────┐  ┌────────────────┐                │
│   │ 🔄 AUTO-    │  │ 🤝 CROSS-   │  │ 🔮 PATTERN    │                │
│   │ IMPROVEMENT │  │ AGENT       │  │ DETECTION     │                │
│   │             │  │ LEARNING    │  │               │                │
│   │ Quality     │  │             │  │ Recurrence    │                │
│   │ Scoring     │  │ Propagate   │  │ counting      │                │
│   │ Dedup       │  │ gotchas &   │  │ Pattern keys  │                │
│   │ Contradict. │  │ learnings   │  │ Auto-promote  │                │
│   │ Cleanup     │  │ to ALL      │  │ → workspace   │                │
│   │ Lifecycle   │  │ agents      │  │   rule files  │                │
│   └──────┬──────┘  └──────┬──────┘  └───────┬──────┘                │
│          │                │                  │                        │
│          └────────────────┼──────────────────┘                        │
│                           ▼                                            │
│                  ┌─────────────────┐                                   │
│                  │ 💉 CONTEXTUAL   │                                   │
│                  │ INJECTION       │                                   │
│                  │                 │                                   │
│                  │ Auto-inject at  │                                   │
│                  │ every agent     │                                   │
│                  │ bootstrap       │                                   │
│                  │ Score-based     │                                   │
│                  │ ranking         │                                   │
│                  └─────────────────┘                                   │
│                           │                                            │
│                           ▼                                            │
│                  ┌─────────────────┐                                   │
│                  │ 🤖 SMARTER     │                                   │
│                  │ AGENT           │                                   │
│                  │ each session    │                                   │
│                  └─────────────────┘                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

**Result:** Every session of every agent feeds the memory → the memory self-optimizes → knowledge propagates → all agents are smarter in the next session. **Infinite improvement cycle.**

---

### 📥 Automatic Memory Capture

**What it does:** Converts ALL agent activity into vector memories without anyone having to do anything.

**Why it matters:** Without this, every session would be disposable. Agents would forget everything. With Auto-Learning, every conversation is a permanent learning opportunity.

BrainX captures memories through **4 complementary mechanisms** working in parallel:

| Mechanism | How it works | What it captures | Frequency |
|-----------|--------------|-----------------|-----------|
| **Memory Distiller** (`scripts/memory-distiller.js`) | LLM (gpt-4.1-mini) reads full session transcripts | Preferences, decisions, personal/technical/financial data — ALL memory types | Every 6h |
| **Fact Extractor** (`scripts/fact-extractor.js`) | Regex patterns extract structured data | Production URLs, services, repos, ports, branches, configs | Every 6h |
| **Session Harvester** (`scripts/session-harvester.js`) | Heuristics and regex classify conversations | Conversation patterns, recurring topics, operational context | Every 4h |
| **Memory Bridge** (`scripts/memory-bridge.js`) | Syncs markdown files to vector database | Manual notes in `memory/*.md`, documentation, written decisions | Every 6h |

**Real example:** An agent discusses a deployment with the user. Without anyone doing anything:
- The **Fact Extractor** captures the service URL and repo name
- The **Memory Distiller** extracts the decision to use that service and why
- The **Memory Bridge** syncs the daily notes
- Everything is available for ANY agent in the next session

---

### 🤝 Cross-Agent Learning

**What it does:** When an agent discovers something important (a bug, a gotcha, a learning), it automatically propagates it to ALL other agents.

**Why it matters:** Without this, each agent would be an island. The coder would discover a bug and the researcher would find it again. With cross-agent learning, knowledge flows between all agents.

**Script:** `scripts/cross-agent-learning.js`
**Frequency:** Daily (cron)

**How it works:**

1. Scans recent memories with importance ≥ 7 and types `gotcha`, `learning`, `correction`
2. Identifies memories created by a specific agent
3. Replicates those memories in the context of other agents
4. Generates **weekly context packs** by project and by agent (`scripts/context-pack-builder.js`)

**Real example:**
```
Coder discovers: "CLI tool v4.29 requires --detach for background deploys"
    ↓ cross-agent-learning.js (daily cron)
    ↓
All other agents → receive this gotcha automatically
    ↓
No agent makes that mistake again
```

---

### 🔄 Auto-Improvement and Quality Curation

**What it does:** Memory self-optimizes — good memories rise, bad ones fall, duplicates are removed, contradictions are resolved.

**Why it matters:** Without automatic curation, memory would fill up with noise, duplicates, and obsolete information. Retrieval quality would degrade over time. With auto-improvement, memory becomes MORE accurate with each cycle.

**5 scripts work together:**

| Script | What it does | Frequency |
|--------|-------------|-----------|
| `scripts/quality-scorer.js` | Evaluates each memory on multiple dimensions (specificity, actionability, relevance). Promotes high-quality memories, degrades low-quality ones | Daily |
| `scripts/contradiction-detector.js` | Finds memories that contradict each other. Supersedes the obsolete version, keeps the most recent/accurate | Daily |
| `scripts/dedup-supersede.js` | Detects duplicate or near-identical memories by cosine similarity. Intelligent merge keeping the most complete information | Weekly |
| `scripts/cleanup-low-signal.js` | Archives low-value memories: too short, low importance, no recent accesses. Frees space for useful memories | Weekly |
| **Lifecycle run** (via `lifecycle-run` CLI) | Promotes memories between tiers: `hot` → `warm` → `cold` based on age, accesses, and quality. Hot memories always available, cold ones archived | Automatic |

**Curation flow:**
```
New memory arrives
    ↓
Quality Scorer → Is it useful? Specific? Actionable?
    ↓                                    ↓
  Yes → promote (importance +1)     No → degrade (importance -1)
    ↓                                    ↓
Contradiction Detector              Cleanup → archive if importance < 3
    ↓
Does it contradict something existing?
    ↓              ↓
  Yes → supersede   No → keep both
    ↓
Dedup → Duplicate?
    ↓              ↓
  Yes → merge       No → keep
    ↓
Lifecycle → hot/warm/cold based on usage
```

---

### 🔄 Auto-Promotion Pipeline

**What it does:** Detects high-recurrence patterns and automatically promotes them as permanent rules into agent workspace files (AGENTS.md, TOOLS.md, SOUL.md). Closes the learning → rule loop without any human intervention required.

**Why it matters:** Patterns that repeat 10+ times in memory are operationally critical. Instead of staying buried in vector search results, they get written directly into the files every agent reads at startup — becoming permanent behavioral rules.

**Scripts:** `scripts/auto-promoter.js` → `scripts/promotion-applier.js`
**Frequency:** Daily (pipeline steps 12–13)

**How it works:**

1. `auto-promoter.js` scans `brainx_patterns` for entries with `recurrence_count ≥ threshold`
2. Classifies each pattern to its target file (AGENTS.md, TOOLS.md, or SOUL.md) based on content type
3. Saves suggestions as BrainX memories tagged `promotion-suggestion`
4. `promotion-applier.js` reads pending suggestions, distills them via LLM (gpt-4.1-mini), and writes the final rules into the workspace files under the `## Auto-Promoted Rules` section

**Result:**
```
Pattern: "Use plugin v2 for WordPress publishing" (×33)
    ↓ auto-promoter.js detects threshold exceeded
    ↓ saves promotion-suggestion memory
    ↓ promotion-applier.js distills via LLM
    ↓
TOOLS.md → "Usar siempre la versión v2 del plugin WordPress…" written permanently
    ↓
Every future agent reads it at startup — zero re-learning
```

---

### 💉 Intelligent Contextual Injection

**What it does:** At every agent session start, automatically injects the most relevant memories for the current context.

**Why it matters:** There's no point having perfect memory if the agent doesn't receive it. Contextual injection is the bridge between "stored memories" and "informed agent." Without this, BrainX would be a database no one queries.

**Component:** Auto-inject hook (`hook/handler.js` + `lib/cli.js inject`)
**Frequency:** Every agent bootstrap (every new session)

**How it works:**

1. The hook executes automatically when starting any agent session
2. Runs `brainx inject --agent <agent_id>` which:
   - Searches for memories relevant to the current agent (by context `agent:ID`)
   - Ranks by **composite score**: semantic similarity × importance × tier
   - Always includes **operational facts** (URLs, configs, services)
   - Formats everything as an injectable markdown block in the prompt
3. The result is written to `BRAINX_CONTEXT.md` which the agent reads at startup

**Injection ranking:**
```
Score = (cosine_similarity × 0.4) + (importance/10 × 0.3) + (tier_weight × 0.2) + (recency × 0.1)

Where:
  tier_weight: hot=1.0, warm=0.6, cold=0.2
  recency: exponential decay from last_accessed
```

---

### 🔮 Pattern Detection and Recurrence

**What it does:** Detects when something appears repeatedly in memories and automatically promotes it as an important pattern.

**Why it matters:** Recurring patterns are the most valuable memories — if something appears 5 times, it's probably critical. Automatic detection ensures these memories are never lost or degraded.

**Mechanism integrated in:** `scripts/quality-scorer.js` + `lib/openai-rag.js`

**How it works:**

1. **Recurrence counting:** Each time a memory is accessed or a similar one is created, `recurrence_count` increments
2. **Pattern key:** Similar memories are grouped under a common `pattern_key` (semantic hash)
3. **Auto-promote:** When `recurrence_count` exceeds a threshold:
   - ≥ 3 occurrences → importance +1
   - ≥ 5 occurrences → promote to `hot` tier
   - ≥ 10 occurrences → mark as `core_knowledge` (never archived)

**Example:**
```
Memory: "CLI tool requires --detach for deploys"
  → Appears in 3 different sessions from 3 agents
  → recurrence_count = 3
  → Auto-promote: importance 6 → 7
  → Appears 2 more times
  → recurrence_count = 5
  → Auto-promote to hot tier (always available)
```

---

### 📊 15-Step Daily Pipeline

BrainX V5 runs a consolidated daily pipeline with 15 sequential steps, ensuring complete memory lifecycle management in a single orchestrated run.

**Pipeline name:** `BrainX Daily Core Pipeline V5`
**Frequency:** Daily (OpenClaw cron)

| Step | Script | Function |
|------|--------|----------|
| 1 | `bootstrap` | Environment validation and DB connectivity check |
| 2 | `lifecycle` | Lifecycle-run (promote/degrade by age and usage) |
| 3 | `distiller` | Memory Distiller (LLM extraction from session transcripts) |
| 4 | `harvester` | Session Harvester (regex-based session capture) |
| 5 | `bridge` | Memory Bridge (markdown → vector sync) |
| 6 | `auto-distiller` | Auto-distiller pass for recent unprocessed sessions |
| 7 | `consolidation` | Memory consolidation and quality normalization |
| 8 | `cross-agent` | Cross-agent learning propagation |
| 9 | `contradiction` | Contradiction detection and supersede |
| 10 | `markdown-harvester` | Markdown harvester for workspace files |
| 11 | `error-harvester` | Error harvester from session logs |
| 12 | `auto-promoter` | Pattern promotion candidate detection |
| 13 | `promotion-applier` | Apply pending promotions to workspace files |
| 14 | `memory-enforcer` | Memory enforcement and integrity validation |
| 15 | `audit` | Full audit and metrics generation |

---

### 📋 Summary: Auto-Learning Crons

All crons that feed the auto-learning cycle:

| Frequency | Scripts | Function |
|-----------|---------|----------|
| **Every 4h** | `session-harvester.js` | Capture new sessions |
| **Every 6h** | `memory-distiller.js`, `fact-extractor.js`, `memory-bridge.js` | Extract memories and facts |
| **Daily** | 15-step pipeline (cross-agent, contradiction, quality, auto-promoter, promotion-applier, etc.) | Full orchestration cycle |
| **Weekly** | `context-pack-builder.js`, `cleanup-low-signal.js`, `dedup-supersede.js` | Packs, cleanup, dedup |
| **Each session** | Auto-inject hook | Inject memories into agent |

> **Zero-maintenance:** Once crons are set up, BrainX learns, self-optimizes, promotes patterns to rules, and shares knowledge completely on its own. Agents improve with every session without anyone touching anything.

---

## Script and Tool Summary Table

### Pipeline Scripts (`scripts/`)

| Script | Description | LLM | Cron |
|--------|-------------|-----|------|
| `memory-distiller.js` | 🧬 LLM-powered memory extractor from session transcripts | gpt-4.1-mini | Every 6h |
| `fact-extractor.js` | 📌 Regex extractor of operational facts (URLs, services, configs) | No | Every 6h |
| `session-harvester.js` | 🔍 Session harvester based on regex heuristics | No | Every 4h |
| `memory-bridge.js` | 🌉 Syncs `memory/*.md` files to vector brain | No | Every 6h |
| `cross-agent-learning.js` | 🤝 Propagates high-importance learnings between agents | No | Daily |
| `contradiction-detector.js` | ⚡ Detects contradictory memories and supersedes obsolete ones | No | Daily |
| `quality-scorer.js` | ⭐ Evaluates memory quality (promote/degrade/archive) | No | Daily |
| `context-pack-builder.js` | 📦 Generates weekly context packs per agent/project | No | Weekly |
| `cleanup-low-signal.js` | 🧹 Cleans low-value memories (short, low importance) | No | Weekly |
| `dedup-supersede.js` | 🔗 Exact deduplication and superseding of identical memories | No | Weekly |
| `error-harvester.js` | 🔍 Scans session logs for command failures, saves as gotchas | No | Daily |
| `auto-promoter.js` | 📋 Detects high-recurrence patterns, suggests workspace promotions | No | Daily (pipeline step 12) |
| `promotion-applier.js` | 🔄 Reads pending pattern suggestions, distills via LLM, writes rules to workspace files | gpt-4.1-mini | Daily (pipeline step 13) |
| `reclassify-memories.js` | 🏷️ Reclassifies existing memories to new categories | No | Manual |
| `eval-memory-quality.js` | 📊 Offline evaluation of retrieval quality | No | Manual |
| `generate-eval-dataset-from-memories.js` | 📋 Generates JSONL dataset for benchmarks | No | Manual |
| `import-workspace-memory-md.js` | 📥 Imports workspace MEMORY.md into vector brain | No | Manual |
| `migrate-v2-to-v3.js` | 🔄 Data migration from BrainX V2 | No | Once |
| `backup-brainx.sh` | 🛡️ Full backup (DB + configs + hooks) | No | Daily (recommended cron) |
| `restore-brainx.sh` | 🛡️ Full restore from backup | No | Manual |

### Cron Scripts (`cron/`)

| Script | Description | Frequency |
|--------|-------------|-----------|
| `health-check.sh` | BrainX health check + memory count | Every 30 min |
| `ops-alerts.sh` | Operational report with latency alerts and lifecycle | Daily |
| `weekly-dashboard.sh` | Weekly dashboard with metrics, trends, and distribution | Weekly |

### Core Modules (`lib/`)

| Module | Description |
|--------|-------------|
| `openai-rag.js` | Core RAG: OpenAI embeddings, store with semantic dedup, search with scoring, query logging |
| `brainx-phase2.js` | PII scrubbing (14 patterns), dedup config, tag merging, merge plan derivation |
| `db.js` | PostgreSQL connection pool with transaction support |
| `cli.js` | Full CLI with all commands (health, add, fact, facts, search, inject, resolve, etc.) |

---

## Architecture

BrainX V5 operates in **3 feeding layers** working together:

```
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 3: Agents (manual)                    │
│  Agents write directly with: brainx add / brainx fact       │
│  → Decisions, gotchas, notes during work                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│               LAYER 2: Memory Distiller (LLM)               │
│  scripts/memory-distiller.js — gpt-4.1-mini                 │
│  → Reads complete session transcripts                       │
│  → Extracts ALL types: personal, financial, preferences     │
│  → Understands context and language nuances                 │
│  → Automatic cron every 6h                                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│               LAYER 1: Fact Extractor (regex)               │
│  scripts/fact-extractor.js — no LLM                        │
│  → Extracts URLs (services, repos, deployments)                  │
│  → Detects services, repos, ports, branches                 │
│  → Fast, no API cost                                        │
│  → Complements the distiller for structured data            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
              PostgreSQL + pgvector
              (centralized database)
                        │
                        ▼
              hook/handler.js (auto-inject)
              → BRAINX_CONTEXT.md in each workspace
```

### Data flow

```
Agent sessions ──→ Fact Extractor (regex)     ──→ PostgreSQL
               ──→ Memory Distiller (LLM)     ──→ PostgreSQL
               ──→ Session Harvester (regex)   ──→ PostgreSQL
               ──→ Memory Bridge (markdown)    ──→ PostgreSQL
               ──→ Agents write directly       ──→ PostgreSQL
                                                      │
                               ┌─────────────────────┤
                               │                     │
                               ▼                     ▼
                        Quality Scorer        hook/handler.js
                        Contradiction Det.          │
                        Cross-Agent Learning        ▼
                        Dedup/Supersede       BRAINX_CONTEXT.md
                        Cleanup Low-Signal    (3 sections:
                        Lifecycle-Run          📌 Project Facts
                        Auto-Promoter          🤖 Own memories
                        Promotion-Applier      🔥 High-imp. team)
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Mdx2025/brainx-v5.git
cd brainx-v5

# 2. Install dependencies
pnpm install  # or npm install

# 3. Configure environment
cp .env.example .env
# Edit: DATABASE_URL, OPENAI_API_KEY

# 4. Database setup (requires PostgreSQL with pgvector)
psql "$DATABASE_URL" -f sql/v3-schema.sql

# 5. Verify
./brainx-v5 health
```

---

## Full CLI Reference

The CLI (`lib/cli.js`) provides all commands to interact with BrainX. The entry point is the bash script `brainx-v5` (or the wrapper `brainx`).

### `health` — Check status

```bash
./brainx-v5 health
# BrainX V5 health: OK
# - pgvector: yes
# - brainx tables: 9
```

### `add` — Add memory

```bash
./brainx-v5 add \
  --type decision \
  --content "Use text-embedding-3-small to reduce costs" \
  --context "project:openclaw" \
  --tier hot \
  --importance 9 \
  --tags config,openai \
  --agent coder
```

**Available flags:**

| Flag | Required | Description |
|------|----------|-------------|
| `--type` | ✅ | Memory type (see Types section) |
| `--content` | ✅ | Text content of the memory |
| `--context` | ❌ | Namespace: `agent:coder`, `project:my-project`, `personal:finances` |
| `--tier` | ❌ | `hot` \| `warm` \| `cold` \| `archive` (default: `warm`) |
| `--importance` | ❌ | 1-10 (default: 5) |
| `--tags` | ❌ | Comma-separated tags: `deploy,service,url` |
| `--agent` | ❌ | Name of the agent creating the memory |
| `--id` | ❌ | Custom ID (auto-generated if omitted) |
| `--status` | ❌ | `pending` \| `in_progress` \| `resolved` \| `promoted` \| `wont_fix` |
| `--category` | ❌ | Category (see Categories section) |
| `--patternKey` | ❌ | Recurring pattern key |
| `--recurrenceCount` | ❌ | Recurrence counter |
| `--resolutionNotes` | ❌ | Resolution notes |
| `--promotedTo` | ❌ | Promotion destination |

### `fact` — Shortcut for operational data

The `fact` type is a shortcut for `add --type fact --tier hot --category infrastructure`.

```bash
# Register a service URL
./brainx-v5 fact \
  --content "Frontend my-project: https://my-app-frontend.example.com" \
  --context "project:my-project" \
  --importance 8

# Register service config
./brainx-v5 fact \
  --content "Service 'my-api' → port 3001, branch main" \
  --context "project:my-project" \
  --importance 7 \
  --tags service,config
```

**What is a FACT?** Hard data that another agent would need to work without asking:
- Production/staging URLs
- Service ↔ repo ↔ directory mapping
- Key environment variables
- Project structure
- Main branch, deploy target
- Personal data, financial data, contacts

### `facts` — List stored facts

```bash
# All facts
./brainx-v5 facts

# Filter by context
./brainx-v5 facts --context "project:my-project"

# Limit results
./brainx-v5 facts --limit 5
```

### `feature` — Shortcut for feature requests

```bash
# Save a feature request
./brainx-v5 feature "Add webhook support for real-time notifications"

# With project context
./brainx-v5 feature --content "Dark mode for dashboard" --context "project:control-panel" --importance 8
```

Shortcut for: `add --type feature_request --tier warm --importance 6 --category feature_request`

### `features` — List stored feature requests

```bash
# All feature requests
./brainx-v5 features

# Filter by status
./brainx-v5 features --status pending

# Filter by context
./brainx-v5 features --context "project:my-project" --limit 10
```

### `search` — Semantic search

```bash
./brainx-v5 search \
  --query "deploy strategy" \
  --limit 10 \
  --minSimilarity 0.15 \
  --context "project:my-project" \
  --tier hot
```

**Score-based ranking:** Results are sorted by a composite score:
- **Cosine similarity** — main embedding weight
- **Importance** — `(importance / 10) × 0.25` bonus
- **Tier bonus** — `hot: +0.15`, `warm: +0.05`, `cold: -0.05`, `archive: -0.10`

**Access tracking:** Each returned result automatically updates `last_accessed` and `access_count`.

### `inject` — Get context ready for prompts

```bash
./brainx-v5 inject \
  --query "what did we decide about the deploy?" \
  --limit 8 \
  --minScore 0.25 \
  --maxTotalChars 12000
```

**Output format:**
```
[sim:0.82 imp:9 tier:hot type:decision agent:coder ctx:openclaw]
Use text-embedding-3-small to reduce costs...

---

[sim:0.41 imp:6 tier:warm type:note agent:writer ctx:project-x]
Another relevant memory...
```

**Injection limits:**

| Limit | Default | Env Override | Flag Override |
|-------|---------|--------------|---------------|
| Max chars per item | 2000 | `BRAINX_INJECT_MAX_CHARS_PER_ITEM` | `--maxCharsPerItem` |
| Max lines per item | 80 | `BRAINX_INJECT_MAX_LINES_PER_ITEM` | `--maxLinesPerItem` |
| Max chars total output | 12000 | `BRAINX_INJECT_MAX_TOTAL_CHARS` | `--maxTotalChars` |
| Min score gate | 0.25 | `BRAINX_INJECT_MIN_SCORE` | `--minScore` |

### `resolve` — Resolve/promote memories

```bash
# Resolve a memory
./brainx-v5 resolve --id m_123 --status resolved \
  --resolutionNotes "Patched retry backoff"

# Promote all memories of a pattern
./brainx-v5 resolve \
  --patternKey retry.429.swallow \
  --status promoted \
  --promotedTo docs/runbooks/retry.md \
  --resolutionNotes "Standard retry policy captured"
```

### `promote-candidates` — View promotion candidates

```bash
./brainx-v5 promote-candidates --json
./brainx-v5 promote-candidates --minRecurrence 3 --days 30 --limit 10
```

### `lifecycle-run` — Auto-promote/degrade memories

```bash
# Dry run first
./brainx-v5 lifecycle-run --dryRun --json

# Execute
./brainx-v5 lifecycle-run --json
```

### `metrics` — Operational KPIs

```bash
./brainx-v5 metrics --days 30 --topPatterns 10 --json
```

Returns:
- Distribution by tier
- Top recurring patterns
- Query performance (average duration, call count)
- Lifecycle statistics

---

## Memory Types

| Type | Description | Example |
|------|-------------|---------|
| `fact` | Concrete operational data | URLs, services, configs, personal data, finances |
| `decision` | Decisions made | "We use gpt-4.1-mini for the distiller" |
| `learning` | Things discovered/learned | "Service X doesn't support websockets on free plan" |
| `gotcha` | Traps to avoid | "Don't use `rm -rf` without confirming path first" |
| `action` | Actions executed | "Deployed my-project v2.3 to production" |
| `note` | General notes | "The client prefers morning meetings" |
| `feature_request` | Requested/planned features | "Add webhook support in v3" |

---

## Supported Categories

### Original categories (technical)

| Category | Use |
|----------|-----|
| `learning` | Technical learnings |
| `error` | Errors encountered and resolved |
| `feature_request` | Feature requests |
| `correction` | Corrections to previous information |
| `knowledge_gap` | Detected knowledge gaps |
| `best_practice` | Discovered best practices |

### New categories (contextual)

| Category | Use |
|----------|-----|
| `infrastructure` | Infra: URLs, services, deployments |
| `project_registry` | Project registry and configs |
| `personal` | Personal user data |
| `financial` | Financial information (costs, budgets) |
| `contact` | Contacts (names, roles, companies) |
| `preference` | User preferences |
| `goal` | Objectives and goals |
| `relationship` | Relationships between people/entities |
| `health` | Health data |
| `business` | Business information |
| `client` | Client data |
| `deadline` | Deadlines and due dates |
| `routine` | Routines and recurring processes |
| `context` | General context for sessions |

---

## Core Features

### Automatic PII Scrubbing

**Module:** `lib/brainx-phase2.js`

Before saving any memory, BrainX automatically applies sensitive data redaction. The 14 detected patterns:

| Pattern | Detected example |
|---------|-----------------|
| `email` | `user@domain.com` |
| `phone` | `+1 (555) 123-4567` |
| `openai_key` | `sk-abc123...` |
| `github_token` | `ghp_xxxx...` |
| `github_pat` | `github_pat_xxxx...` |
| `aws_access_key` | `AKIAIOSFODNN7EXAMPLE` |
| `slack_token` | `xoxb-xxx-xxx` |
| `bearer_token` | `Bearer eyJ...` |
| `api_key_assignment` | `api_key=sk_live_xxx` |
| `jwt_token` | `eyJhbGciOi...` |
| `private_key_block` | `-----BEGIN RSA PRIVATE KEY-----` |
| `iban` | `DE89370400440532013000` |
| `credit_card` | `4111 1111 1111 1111` |
| `ipv4` | `192.168.1.100` |

**Behavior:**
- Enabled by default (`BRAINX_PII_SCRUB_ENABLED=true`)
- Data is replaced with `[REDACTED]` (configurable)
- Auto-tags added: `pii:redacted`, `pii:email`, etc.
- Contexts in allowlist are exempt

```bash
BRAINX_PII_SCRUB_ENABLED=true                        # default: true
BRAINX_PII_SCRUB_REPLACEMENT=[REDACTED]               # default
BRAINX_PII_SCRUB_ALLOWLIST_CONTEXTS=internal-safe,trusted
```

### Semantic Deduplication

**Module:** `lib/openai-rag.js` (storeMemory)

When storing a memory, BrainX checks if a similar one already exists:

1. **By `pattern_key`** — If the memory has a pattern_key, looks for another with the same key
2. **By cosine similarity** — If no pattern_key, compares the embedding against recent memories from the same context and category

If a duplicate is detected (similarity ≥ threshold):
- **Does NOT create a new one** — updates the existing one
- **Increments `recurrence_count`** — tracks how many times the pattern repeats
- **Updates `last_seen`** — date of last observation
- **Preserves `first_seen`** — keeps the original date

```bash
BRAINX_DEDUPE_SIM_THRESHOLD=0.92  # default: if similarity > 0.92, merge
BRAINX_DEDUPE_RECENT_DAYS=30      # comparison window
```

### Score-Based Ranking

**Module:** `lib/openai-rag.js` (search)

Searches use a composite score to sort results:

```
score = cosine_similarity
      + (importance / 10) × 0.25     # bonus for importance
      + tier_bonus                     # hot: +0.15, warm: +0.05, cold: -0.05, archive: -0.10
```

This ensures high-importance, hot-tier memories appear first, even with slightly lower similarity.

### Access Tracking

**Module:** `lib/openai-rag.js` (search)

Each time a memory appears in search results:
- `last_accessed` updates to `NOW()`
- `access_count` increments by 1

This allows `quality-scorer.js` to identify actively used vs. stale memories.

### Memory Superseding

**Column:** `superseded_by` (FK to another memory)

When a memory is replaced by a newer or more complete version:
- Marked with `superseded_by = ID_of_new_memory`
- Superseded memories are **automatically excluded** from searches (`WHERE superseded_by IS NULL`)
- `contradiction-detector.js` and `dedup-supersede.js` handle this automatically

### Pattern Detection and Recurrence Counting

**Table:** `brainx_patterns`

When a memory repeats (by `pattern_key` or by semantic similarity):
- The record in `brainx_patterns` updates with:
  - `recurrence_count` — times observed
  - `first_seen` / `last_seen` — temporal range
  - `impact_score` — `importance × tier_impact`
  - `representative_memory_id` — the most representative memory
- High-recurrence patterns are candidates for **promotion** (via `promote-candidates`)

### Query Logging and Performance Tracking

**Table:** `brainx_query_log`

Every `search` and `inject` operation records:
- `query_hash` — hash of the query
- `query_kind` — `search` | `inject`
- `duration_ms` — execution time
- `results_count` — number of results
- `avg_similarity` / `top_similarity` — similarity metrics

This feeds the `metrics` command and `ops-alerts.sh` and `weekly-dashboard.sh` reports.

### Lifecycle Management (Promote/Degrade/Archive)

**Command:** `lifecycle-run`

The automatic lifecycle manager evaluates memories and decides on actions:

| Action | Criterion |
|--------|-----------|
| **Promote** (cold/warm → hot) | High-recurrence patterns + importance ≥ threshold |
| **Degrade** (hot → warm, warm → cold) | No recent access + low importance + little usage |
| **Archive** (any → archive) | Very low quality or no prolonged usage |

```bash
# See what it would do without executing
./brainx-v5 lifecycle-run --dryRun --json

# Execute promotions/degradations
./brainx-v5 lifecycle-run --json
```

Flags: `--promoteMinRecurrence`, `--promoteDays`, `--degradeDays`, `--lowImportanceMax`, `--lowAccessMax`

### Memory Injection Engine

**Module:** `lib/cli.js` → `cmdInject()` + `formatInject()`

The **Memory Injection Engine** is the central component that connects stored memory with agents. It's not a simple `SELECT` — it's a complete pipeline of retrieval, filtering, ranking, truncation, and formatting.

#### Complete injection pipeline flow:

```
Text query
     │
     ▼
  embed(query)               ← Generates embedding via OpenAI API
     │
     ▼
  warm_or_hot strategy       ← Searches hot first, then warm, merges unique
     │
     ▼
  SQL Ranking                 ← score = similarity + (importance/10 × 0.25) + tier_bonus
     │
     ▼
  Min Score Gate              ← Filters results with score < 0.25 (configurable)
     │
     ▼
  formatInject()              ← Intelligent truncation by lines and characters
     │
     ▼
  Prompt-ready output         ← Text ready to inject into LLM context
```

#### `warm_or_hot` search strategy (default)

When no tier is specified, inject:
1. Searches `hot` memories (high priority)
2. Searches `warm` memories (medium priority)
3. Merge: removes duplicates by ID, prioritizes hot, limits to configured `--limit`

This ensures critical (hot) memories always appear, complemented by warm if there's room.

#### Intelligent truncation (`formatInject`)

Output is controlled with 3 limits:

| Parameter | Default | Environment variable | CLI flag |
|-----------|---------|---------------------|----------|
| Max chars per item | 2000 | `BRAINX_INJECT_MAX_CHARS_PER_ITEM` | `--maxCharsPerItem` |
| Max lines per item | 80 | `BRAINX_INJECT_MAX_LINES_PER_ITEM` | `--maxLinesPerItem` |
| Max total chars | 12000 | `BRAINX_INJECT_MAX_TOTAL_CHARS` | `--maxTotalChars` |
| Min score gate | 0.25 | `BRAINX_INJECT_MIN_SCORE` | `--minScore` |

If an item exceeds the limit, it's truncated with `…`. If total output exceeds `maxTotalChars`, it cuts without adding more items.

#### Output format

Each memory is formatted as:

```
[sim:0.82 score:1.12 imp:9 tier:hot type:decision agent:coder ctx:openclaw]
Memory content here...

---

[sim:0.71 score:0.98 imp:8 tier:warm type:learning agent:support ctx:brainx]
Other content...
```

The metadata in the `[sim:... score:... ...]` header allows the agent to evaluate the relevance of each memory.

#### Auto-Inject Hook: From engine to agent

The `hook/handler.js` hook uses the injection engine to automatically create `BRAINX_CONTEXT.md`:

```
Event agent:bootstrap
     │
     ▼
  handler.js executes
     │
     ├─ Section 1: direct psql → Facts (type=fact, hot/warm tier)
     │
     ├─ Section 2: brainx inject → Agent's own memories (context=agent:NAME, imp≥6)
     │
     ├─ Section 3: brainx inject → Team memories (imp≥8, no context filter)
     │
     ▼
  BRAINX_CONTEXT.md generated → Agent reads it as Project Context
```

**Hook telemetry:** Each injection records in `brainx_pilot_log`:
- Agent, own memories, team memories, total chars generated

### Memory Store Engine

**Module:** `lib/openai-rag.js` → `storeMemory()`

Storage is NOT a simple INSERT. It's a 6-step pipeline inside a transaction:

```
New memory
     │
     ▼
  1. PII Scrubbing          ← scrubTextPII() on content and context
     │
     ▼
  2. Tag merging             ← mergeTagsWithMetadata() adds pii:redacted tags if applicable
     │
     ▼
  3. Embedding               ← embed("type: content [context: ctx]")
     │
     ▼
  4. Dedup check             ← By pattern_key OR by cosine similarity (threshold 0.92)
     │                         deriveMergePlan() decides: merge vs. create new
     ▼
  5. UPSERT                  ← INSERT ... ON CONFLICT DO UPDATE (transactional)
     │                         Preserves first_seen, increments recurrence, updates last_seen
     ▼
  6. Pattern upsert          ← upsertPatternRecord() updates brainx_patterns
     │
     ▼
  Return metadata            ← {id, pattern_key, recurrence_count, pii_scrub_applied,
                                 redacted, redaction_reasons, dedupe_merged, dedupe_method}
```

#### Lifecycle normalization (`normalizeLifecycle`)

Before storing, each memory goes through normalization that:
- Maps camelCase ↔ snake_case fields (`firstSeen` → `first_seen`)
- Assigns defaults (`status: 'pending'`, timestamps to NOW())
- Preserves existing fields if not provided

#### Impact score for patterns (`tierImpact`)

A pattern's impact score is calculated as:

```
impact = importance × tier_factor

tier_factor:
  hot     → 1.0
  warm    → 0.7
  cold    → 0.4
  archive → 0.2
```

### Embedding Engine

**Module:** `lib/openai-rag.js` → `embed()`

- **Model:** `text-embedding-3-small` (configurable via `OPENAI_EMBEDDING_MODEL`)
- **Dimensions:** 1536 (must match schema `vector(1536)`)
- **Input:** Concatenated as `"type: content [context: ctx]"` to maximize semantic relevance
- **API:** POST to `https://api.openai.com/v1/embeddings`
- **Cost:** ~$0.02 per million tokens (text-embedding-3-small)

### Database Layer

**Module:** `lib/db.js`

- PostgreSQL connection pool via `pg.Pool`
- `withClient(fn)` — gets a client from the pool, executes fn, and returns it (for transactions)
- `query(sql, params)` — executes direct query
- `health()` — verifies connection
- Automatic env loading from `BRAINX_ENV` if `DATABASE_URL` is not set directly

---

## Detailed Script Documentation

### `memory-distiller.js` — LLM Memory Extractor

**File:** `scripts/memory-distiller.js`

The Memory Distiller uses an LLM (default `gpt-4.1-mini`) to read complete transcripts of agent sessions and extract **ALL** relevant memory types.

#### What it extracts

Unlike regex extractors, the distiller **understands context**:

1. **Facts** — URLs, endpoints, configs, personal data, finances, contacts, dates
2. **Decisions** — Technical and business decisions
3. **Learnings** — Resolved bugs, discovered workarounds
4. **Gotchas** — Common traps and mistakes
5. **Preferences** — How the user likes things

#### Usage

```bash
# Manual execution (last 8 hours by default)
node scripts/memory-distiller.js

# Custom time window
node scripts/memory-distiller.js --hours 24

# Only one agent
node scripts/memory-distiller.js --agent coder

# Dry run (saves nothing)
node scripts/memory-distiller.js --dry-run --verbose

# Alternative model
node scripts/memory-distiller.js --model gpt-4o-mini

# Limit processed sessions
node scripts/memory-distiller.js --max-sessions 5
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--hours` | 8 | Time window to search sessions |
| `--dry-run` | false | Simulate without saving anything |
| `--agent` | all | Filter by specific agent |
| `--verbose` | false | Detailed output |
| `--model` | `gpt-4.1-mini` | LLM model to use |
| `--max-sessions` | 20 | Maximum sessions to process |

#### Session tracking

Already-processed sessions are tracked in `data/distilled-sessions.json`. If a session hasn't been modified since the last run, it's skipped automatically (idempotent).

#### Configuration

| Environment variable | Default | Description |
|---------------------|---------|-------------|
| `BRAINX_DISTILLER_MODEL` | `gpt-4.1-mini` | Default model |
| `OPENAI_API_KEY` | — | **Required** |

---

### `fact-extractor.js` — Regex Fact Extractor

**File:** `scripts/fact-extractor.js`

Fast regex-based extractor that complements the Memory Distiller. No LLM, so it's free and fast.

#### What it extracts

| Pattern | Example |
|---------|---------|
| Service URLs | `https://my-app.example.com` |
| Vercel URLs | `https://app.vercel.app` |
| GitHub repos | `github.com/user/repo` |
| Service mappings | `service my-api → backend` |
| Ports and configs | `PORT=3001`, `NODE_ENV=production` |
| Branches | `branch: main`, `deploy target: staging` |

#### Usage

```bash
# Manual execution (last 24 hours by default)
node scripts/fact-extractor.js

# Custom time window
node scripts/fact-extractor.js --hours 48

# Only one agent
node scripts/fact-extractor.js --agent raider

# Dry run
node scripts/fact-extractor.js --dry-run --verbose
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--hours` | 24 | Time window to search sessions |
| `--dry-run` | false | Simulate without saving |
| `--agent` | all | Filter by agent |
| `--verbose` | false | Detailed output |

---

### `session-harvester.js` — Session Harvester

**File:** `scripts/session-harvester.js`

Reads recent OpenClaw sessions (JSONL files) and extracts high-signal memories using regex heuristics. Looks for patterns like decisions, errors, learnings, and gotchas in conversation text.

#### Usage

```bash
# Manual execution (last 4 hours by default)
node scripts/session-harvester.js

# Customize window and limits
node scripts/session-harvester.js --hours 8 --max-memories 40

# Only one agent, with dry-run
node scripts/session-harvester.js --agent main --dry-run --verbose

# Filter by minimum content size
node scripts/session-harvester.js --min-chars 200
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--hours` | 4 | Time window to search sessions |
| `--dry-run` | false | Simulate without saving |
| `--agent` | all | Filter by agent |
| `--verbose` | false | Detailed output |
| `--min-chars` | 120 | Minimum characters to consider a memory valid |
| `--max-memories` | (no limit) | Maximum memories to extract |

#### Difference from Memory Distiller

| Feature | Session Harvester | Memory Distiller |
|---------|-------------------|------------------|
| Method | Regex/heuristics | LLM (gpt-4.1-mini) |
| Cost | Free | ~$0.01-0.05 per session |
| Understanding | Text patterns | Understands full context |
| Speed | Very fast | Slow (API calls) |
| Quality | Medium (false positives) | High |

---

### `memory-bridge.js` — Markdown → Vector Bridge

**File:** `scripts/memory-bridge.js`

Syncs `memory/*.md` files from all OpenClaw workspaces to the vector database. Each H2 section (`##`) in markdown becomes an independent, searchable memory.

#### Usage

```bash
# Manual execution (files from last 6 hours)
node scripts/memory-bridge.js

# Wider window
node scripts/memory-bridge.js --hours 24

# Limit memories created
node scripts/memory-bridge.js --max-memories 30

# Dry run
node scripts/memory-bridge.js --dry-run --verbose
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--hours` | 6 | Time window (recently modified files) |
| `--dry-run` | false | Simulate without saving |
| `--max-memories` | 20 | Maximum memories to create |
| `--verbose` | false | Detailed output |

#### How it works

1. Scans all `~/.openclaw/workspace-*/memory/` directories
2. Finds `.md` files modified in the last N hours
3. Splits each file into blocks by H2 sections
4. Each block is saved as a `note` type memory with workspace context
5. Already-synced sections are marked with `<!-- brainx-synced -->`

---

### `cross-agent-learning.js` — Cross-Agent Propagation

**File:** `scripts/cross-agent-learning.js`

Propagates high-importance learnings and gotchas from an individual agent to the global context, so **all** agents benefit from shared discoveries.

#### Usage

```bash
# Manual execution (last 24 hours)
node scripts/cross-agent-learning.js

# Custom window
node scripts/cross-agent-learning.js --hours 48

# Dry run (recommended first)
node scripts/cross-agent-learning.js --dry-run --verbose

# Limit shares
node scripts/cross-agent-learning.js --max-shares 5
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--hours` | 24 | Time window |
| `--dry-run` | false | Simulate without sharing |
| `--verbose` | false | Detailed output |
| `--max-shares` | 10 | Maximum memories to share |

#### Logic

1. Searches recent memories of type `learning` or `gotcha` with high importance
2. Filters those with `agent:*` context (specific to one agent)
3. Creates a copy with `global` context so all agents can see it
4. Avoids duplicates by checking if a global copy already exists

---

### `error-harvester.js` — Post-Error Capture

**File:** `scripts/error-harvester.js`

Scans OpenClaw session logs for command failures (non-zero exit codes, error patterns) and stores them as gotcha memories in BrainX. Runs in the daily cron pipeline.

#### Usage

```bash
# Dry run (recommended first)
node scripts/error-harvester.js --dry-run --verbose

# Scan last 24 hours (default)
node scripts/error-harvester.js

# Custom time window
node scripts/error-harvester.js --hours 48
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--hours` | 24 | Time window to scan |
| `--dry-run` | false | Show errors without saving |
| `--verbose` | false | Print each error found |

#### Detects

- Non-zero exit codes from tool executions
- `TypeError`, `ReferenceError`, `SyntaxError` patterns
- `ENOENT`, `EACCES`, `EPERM`, `ECONNREFUSED` errors
- `permission denied`, `command not found` patterns

Saved memories are tagged `auto-harvested,error` with type `gotcha`.

---

### `auto-promoter.js` — Pattern Promotion Suggestions

**File:** `scripts/auto-promoter.js`

Detects high-recurrence patterns and generates suggestions for which workspace file they should be promoted to (AGENTS.md, TOOLS.md, or SOUL.md). **Does not write to workspace files** — outputs suggestions only, which are then consumed by `promotion-applier.js`.

#### Usage

```bash
# View suggestions
node scripts/auto-promoter.js

# JSON output
node scripts/auto-promoter.js --json

# Save suggestions as BrainX memories
node scripts/auto-promoter.js --save

# Custom thresholds
node scripts/auto-promoter.js --min-recurrence 5 --days 14
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--min-recurrence` | 3 | Minimum pattern recurrence to qualify |
| `--days` | 30 | Time window |
| `--json` | false | JSON output |
| `--save` | false | Save suggestions as BrainX memories (tag: `promotion-suggestion`) |
| `--dry-run` | false | Simulate without saving |

#### Classification Logic

| Target File | Triggers |
|-------------|----------|
| `TOOLS.md` | Infrastructure, CLI, API, config, integration patterns |
| `SOUL.md` | Behavioral, style, communication patterns |
| `AGENTS.md` | Workflow, execution, delegation patterns |

---

### `promotion-applier.js` — Last-Mile Promotion Applier

**File:** `scripts/promotion-applier.js`

Reads pending promotion suggestions (saved by `auto-promoter.js` with tag `promotion-suggestion`), distills each suggestion via LLM (gpt-4.1-mini) into a concise rule, and writes the final rules into the target workspace files under the `## Auto-Promoted Rules` section. This is the last-mile step that closes the learning → rule loop.

#### What it does

1. Queries BrainX for memories tagged `promotion-suggestion` with `status = pending`
2. For each suggestion, calls gpt-4.1-mini to distill it into a 1-2 sentence actionable rule
3. Appends the rule to the `## Auto-Promoted Rules` section in the target workspace file (AGENTS.md, TOOLS.md, or SOUL.md)
4. Marks the suggestion memory as `status = promoted`
5. Reports applied, skipped, and failed promotions

#### Usage

```bash
# Apply all pending promotions (default)
node scripts/promotion-applier.js --apply

# Dry run (show what would be applied without writing)
node scripts/promotion-applier.js --dry-run --verbose

# Limit number of promotions to apply
node scripts/promotion-applier.js --apply --limit 5

# Only apply patterns with high recurrence
node scripts/promotion-applier.js --apply --min-recurrence 10

# Verbose output
node scripts/promotion-applier.js --apply --verbose
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--apply` | false | Execute the promotion (write to workspace files) |
| `--dry-run` | false | Simulate without writing. Shows what rules would be added |
| `--limit` | 20 | Maximum number of promotions to apply per run |
| `--min-recurrence` | 5 | Minimum recurrence count for a suggestion to qualify |
| `--verbose` | false | Print each rule being written |

#### Example output

```
[promotion-applier] Found 3 pending promotion suggestions
[promotion-applier] Distilling: "Use plugin v2 for WordPress publishing" → target: TOOLS.md
[promotion-applier] Writing rule to TOOLS.md
[promotion-applier] Distilling: "Always verify auth token before deploy" → target: AGENTS.md
[promotion-applier] Writing rule to AGENTS.md
[promotion-applier] Done: 2 applied, 1 skipped (below min-recurrence), 0 failed
```

#### Configuration

| Environment variable | Default | Description |
|---------------------|---------|-------------|
| `BRAINX_DISTILLER_MODEL` | `gpt-4.1-mini` | LLM model for distillation |
| `OPENAI_API_KEY` | — | **Required** |
| `BRAINX_PROMOTER_MIN_RECURRENCE` | `5` | Default min recurrence |

---

### `contradiction-detector.js` — Contradiction Detector

**File:** `scripts/contradiction-detector.js`

Detects hot memories that are semantically very similar to each other and marks the older/shorter ones as superseded by the newer/more complete ones.

#### Usage

```bash
# Dry run (recommended first)
node scripts/contradiction-detector.js --dry-run --verbose

# Analyze top 50 hot memories with threshold 0.80
node scripts/contradiction-detector.js --top 50 --threshold 0.80

# Execute (modifies DB)
node scripts/contradiction-detector.js --verbose
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--top` | 30 | Number of hot memories to analyze |
| `--threshold` | 0.85 | Cosine similarity threshold to consider a contradiction |
| `--dry-run` | false | Report only, don't modify |
| `--verbose` | false | Print detailed analysis of each pair |

#### Logic

1. Loads top N hot memories (with embeddings)
2. Compares each pair by calculating cosine similarity
3. If similarity ≥ threshold, marks the older or shorter as superseded
4. The newer/more complete becomes the canonical memory

---

### `quality-scorer.js` — Quality Evaluator

**File:** `scripts/quality-scorer.js`

Evaluates existing memories based on multiple factors and decides whether they should be promoted, maintained, degraded, or archived.

#### Usage

```bash
# Dry run (recommended first)
node scripts/quality-scorer.js --dry-run --verbose

# Evaluate more memories
node scripts/quality-scorer.js --limit 100 --verbose

# Execute (modifies tiers)
node scripts/quality-scorer.js
```

#### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--limit` | 50 | Number of memories to evaluate |
| `--dry-run` | false | Report only, don't modify |
| `--verbose` | false | Show scoring detail per memory |

#### Scoring Factors

| Factor | Effect |
|--------|--------|
| **Access age** | >30 days without access: -2, >14 days: -1, <3 days: +1 |
| **Access count** | ≥10 accesses: +2, ≥5: +1, 0 accesses: -1 |
| **Content length** | ≥100 chars: +1, <50 chars: -1 |
| **Referenced files** | For each non-existent file: -0.5 |
| **Tier/importance coherence** | Importance ≥8 in cold: +2 (promote); importance ≤3 in hot: -2 (degrade) |

**Result:** Score 1-10 → decides action:
- High score → **promote** (raise tier)
- Medium score → **maintain** (no change)
- Low score → **degrade** (lower tier)
- Very low score → **archive**

---

### `context-pack-builder.js` — Context Pack Builder

**File:** `scripts/context-pack-builder.js`

Generates weekly "context packs" that summarize hot/warm memories grouped by context (`agent:*`, `project:*`). Packs are compact markdown blocks designed for efficient LLM injection (fewer tokens, more signal).

#### Usage

```bash
# Generate packs for all agents
node scripts/context-pack-builder.js

# Only one agent
node scripts/context-pack-builder.js --agent coder

# Limit memories per pack
node scripts/context-pack-builder.js --limit 20

# Dry run
node scripts/context-pack-builder.js --dry-run --verbose
```

---

### `cleanup-low-signal.js` — Low Signal Cleanup

**File:** `scripts/cleanup-low-signal.js`

Archives memories that provide little value: too short, low importance, or not accessed recently.

#### Usage

```bash
# Dry run first
node scripts/cleanup-low-signal.js --dry-run --verbose

# Execute cleanup
node scripts/cleanup-low-signal.js

# Adjust thresholds
node scripts/cleanup-low-signal.js --maxImportance 3 --minLength 50 --days 90
```

---

### `dedup-supersede.js` — Deduplication and Superseding

**File:** `scripts/dedup-supersede.js`

Finds exact or near-identical memory pairs and merges them, keeping the most complete version.

#### Usage

```bash
# Dry run (recommended first)
node scripts/dedup-supersede.js --dry-run --verbose

# Adjust similarity threshold
node scripts/dedup-supersede.js --threshold 0.95 --verbose

# Execute
node scripts/dedup-supersede.js
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | **Required.** PostgreSQL connection string |
| `OPENAI_API_KEY` | — | **Required.** OpenAI API key |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `BRAINX_ENV` | — | Path to `.env` file with database config |
| `BRAINX_PII_SCRUB_ENABLED` | `true` | Enable PII scrubbing |
| `BRAINX_PII_SCRUB_REPLACEMENT` | `[REDACTED]` | Replacement text for scrubbed data |
| `BRAINX_PII_SCRUB_ALLOWLIST_CONTEXTS` | — | Comma-separated exempt contexts |
| `BRAINX_DEDUPE_SIM_THRESHOLD` | `0.92` | Similarity threshold for deduplication |
| `BRAINX_DEDUPE_RECENT_DAYS` | `30` | Comparison window for deduplication |
| `BRAINX_INJECT_MAX_CHARS_PER_ITEM` | `2000` | Max chars per injected memory |
| `BRAINX_INJECT_MAX_LINES_PER_ITEM` | `80` | Max lines per injected memory |
| `BRAINX_INJECT_MAX_TOTAL_CHARS` | `12000` | Max total chars in injection output |
| `BRAINX_INJECT_MIN_SCORE` | `0.25` | Minimum score gate for injection |
| `BRAINX_DISTILLER_MODEL` | `gpt-4.1-mini` | Default model for Memory Distiller and Promotion Applier |
| `BRAINX_PROMOTER_MIN_RECURRENCE` | `5` | Default minimum recurrence for auto-promotion |

---

## Cron Jobs Setup

The recommended setup uses the **15-step consolidated daily pipeline** managed by OpenClaw cron. Individual cron entries are still supported for granular control.

### Consolidated Pipeline (recommended)

Configure in `~/.openclaw/cron/jobs.json` as a single daily job named `BrainX Daily Core Pipeline V5` that runs all 15 steps sequentially (bootstrap → lifecycle → distiller → harvester → bridge → auto-distiller → consolidation → cross-agent → contradiction → markdown-harvester → error-harvester → auto-promoter → promotion-applier → memory-enforcer → audit).

### Individual Cron Entries (add to `crontab -e`)

```bash
# Every 4h: Session Harvester
0 */4 * * * cd /path/to/brainx-v5 && node scripts/session-harvester.js >> logs/harvester.log 2>&1

# Every 6h: Memory Distiller + Fact Extractor + Memory Bridge
0 */6 * * * cd /path/to/brainx-v5 && node scripts/memory-distiller.js >> logs/distiller.log 2>&1
30 */6 * * * cd /path/to/brainx-v5 && node scripts/fact-extractor.js >> logs/fact-extractor.log 2>&1
0 1,7,13,19 * * * cd /path/to/brainx-v5 && node scripts/memory-bridge.js >> logs/bridge.log 2>&1

# Daily: Cross-agent learning + Contradiction detection + Quality scoring + Promotions
0 3 * * * cd /path/to/brainx-v5 && node scripts/cross-agent-learning.js >> logs/cross-agent.log 2>&1
30 3 * * * cd /path/to/brainx-v5 && node scripts/contradiction-detector.js >> logs/contradiction.log 2>&1
0 4 * * * cd /path/to/brainx-v5 && node scripts/quality-scorer.js >> logs/quality.log 2>&1
15 4 * * * cd /path/to/brainx-v5 && node scripts/auto-promoter.js --save >> logs/auto-promoter.log 2>&1
30 4 * * * cd /path/to/brainx-v5 && node scripts/promotion-applier.js --apply >> logs/promotion-applier.log 2>&1
45 4 * * * cd /path/to/brainx-v5 && bash scripts/backup-brainx.sh >> logs/backup.log 2>&1

# Weekly: Context packs + Cleanup + Dedup
0 5 * * 0 cd /path/to/brainx-v5 && node scripts/context-pack-builder.js >> logs/packs.log 2>&1
30 5 * * 0 cd /path/to/brainx-v5 && node scripts/cleanup-low-signal.js >> logs/cleanup.log 2>&1
0 6 * * 0 cd /path/to/brainx-v5 && node scripts/dedup-supersede.js >> logs/dedup.log 2>&1

# Health check every 30min
*/30 * * * * cd /path/to/brainx-v5 && bash cron/health-check.sh >> logs/health.log 2>&1
```

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `npm test`
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE) for details.