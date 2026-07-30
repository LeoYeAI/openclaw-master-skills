---
name: memory-vault
description: Privacy-first persistent memory for AI agents. Your agent remembers across sessions AND controls what the LLM can see. 3 privacy tiers (Open/Local/Locked), hierarchical recall, keyword + semantic search. 6 core functions to get started. No Ollama required. Built from real-world agent operations at vivioo.io.
version: 0.4.0
metadata:
  openclaw:
    requires:
      bins: [python3, pip3]
      anyBins: []
      env: []
    emoji: "\U0001F9E0"
    homepage: https://vivioo.io
    install:
      - kind: uv
        package: chromadb
        bins: []
      - kind: uv
        package: cryptography
        bins: []
---

# Memory Vault

> Memory that actually works between sessions — no cloud, no API keys, just results.

Other memory skills store what your agent knows. Memory Vault also controls *who sees it*. Three privacy tiers — Open, Local, Locked — mean your agent can reason with sensitive data without it ever reaching the LLM provider. Hierarchical recall, auto-importance scoring, conflict detection, and content-aware expiry. Zero infrastructure. No Ollama required.

## The Problem

AI agents forget everything between sessions. Most memory solutions fix that with vector search. Memory Vault fixes it with vector search **plus privacy** — because an agent handling real business data needs to control what enters the LLM context window.

## Works Alongside Your Existing Memory

Your agent platform (OpenClaw, Claude Code, etc.) may already auto-save session notes. **Memory Vault complements that — it doesn't replace it.**

| Your platform's memory | Memory Vault |
|----------------------|-------------|
| Auto-captured session logs | Things your agent **chooses** to save |
| Everything dumped by date | Organized by topic (branches) |
| Safety net | Filing cabinet |

Let the auto-save run. Use Memory Vault for what matters — decisions, learnings, feedback, patterns.

## Installation

**Step 1 — Clone the repo** (one time):

```bash
git clone https://github.com/GirlLove2Code/Memory-Vault.git ~/memory-vault
```

**Step 2 — Dependencies** are installed automatically by the skill header (`chromadb`, `cryptography`). If you need to install manually:

```bash
pip3 install chromadb cryptography
```

**Optional:** Install [Ollama](https://ollama.ai) with `nomic-embed-text` for semantic search. Keyword search works fine without it.

## Get Started in 2 Minutes

Add the memory-vault path, then start using 6 functions:

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/memory-vault"))

from recall import recall
from entry_manager import add_memory, mark_outdated
from branch_manager import create_branch
from privacy_filter import set_tier
from briefing import generate_briefing
```

That's it. Everything else is optional.

---

## The 6 Core Functions

### 1. `recall(query)` — Search your memory

```python
result = recall("what's our marketing strategy?")

# What's safe to send to the LLM:
result["llm_context"]      # Only Open-tier entries

# What the agent can read privately:
result["local_context"]    # Open + Local entries (LLM never sees Local)

# Did we find anything?
result["no_match"]         # True = no relevant memory. Say "I don't know."
result["confidence"]       # 0.0 to 1.0
```

Search works by meaning, not just keywords. "How does the builder approach campaigns?" matches "Story-first marketing works best" even though the words are different.

Without Ollama, uses keyword matching — works well for most use cases.

### 2. `add_memory(branch, content)` — Store something

```python
add_memory(
    branch="knowledge-base/marketing",
    content="Story-first campaigns outperform feature-first by 3x",
    tags=["strategy"],           # optional — helps cross-reference
    source="conversation",       # optional — tracks where it came from
)
```

When you add a memory, the system automatically:
- Scores its importance (1-5) based on content signals
- Checks for conflicts with existing entries
- Sets an expiry date based on content type (pricing=30 days, tasks=14 days, architecture=90 days)
- Syncs to the vector store for semantic search

### 3. `create_branch(path)` — Organize by topic

```python
# General knowledge — Open tier (LLM can see)
create_branch("knowledge-base/marketing", aliases=["marketing", "growth"], summary="Marketing strategy notes")

# Client data — Local tier (agent-only, LLM never sees)
create_branch("client-work", aliases=["clients"], security="local", summary="Client project details")

# Secrets — Locked tier (encrypted on disk)
create_branch("credentials", security="locked", summary="API keys and passwords")
```

Branches are folders for your memories. Sub-branches inherit their parent's security tier.

### 4. `mark_outdated(entry_id, branch, reason)` — Update stale info

```python
mark_outdated("mem-1710288000000", "client-work", reason="Strategy changed after Q1 review")
```

Don't delete old memories — mark them outdated. They still exist but rank much lower in search. History has value.

### 5. `set_tier(branch, tier)` — Control privacy

```python
set_tier("client-work", "local")    # Agent reads it, LLM never sees it
set_tier("public-docs", "open")     # Safe for LLM context
set_tier("credentials", "locked")   # Encrypted on disk
```

This is what makes Memory Vault different from every other memory skill. More on this below.

### 6. `generate_briefing()` — Catch up on what changed

```python
briefing = generate_briefing(since="2026-03-01")

# What you get:
briefing["recent_changes"]    # New/updated memories
briefing["top_priorities"]    # High-importance entries
briefing["expiring_soon"]     # Memories about to expire
briefing["never_recalled"]    # Stored but never searched (cleanup candidates)
briefing["branch_health"]     # Entry counts, staleness per branch
```

Call this at session start so your agent knows what happened while it was away.

---

## Privacy: What Makes This Different

Most memory skills say "stored locally" and call it done. Memory Vault goes further — it controls what the LLM provider can see during a conversation.

### Three Tiers

| Tier | Agent sees it? | LLM sees it? | Use for |
|------|---------------|--------------|---------|
| **Open** | Yes | Yes | General knowledge, how-tos, public info |
| **Local** | Yes | **No** | Client data, revenue, strategy, contacts |
| **Locked** | Only if unlocked | **No** | API keys, passwords (encrypted with Fernet) |

### How Local Works in Practice

```
User asks: "What should our next marketing move be?"

Agent's memory does this:
  Entry 1 (Open):  "Story-first campaigns work best for gaming"  → sent to LLM
  Entry 2 (Local): "Client has strong recurring revenue"           → agent reads privately
  Entry 3 (Local): "Investor wants 3x growth by Q4"              → agent reads privately

The agent uses ALL 3 to form its answer.
The LLM only sees Entry 1 + the user's question.
The agent enriches the response with private knowledge the LLM never touches.
```

### Why This Matters

Your LLM provider sees everything in the context window. If a memory is Local, it never enters that context. The provider literally cannot access it. No prompt engineering, no trust required — the data never leaves your machine.

### One Function Handles It All

You don't need to manually filter. `recall()` already separates results:
- `result["llm_context"]` — only Open entries, safe to send
- `result["local_context"]` — everything the agent should know (Open + Local)
- `result["blocked_count"]` — how many Locked entries were hidden

Set the tier once per branch. The system handles the rest.

---

## How Recall Works (Under the Hood)

Memory Vault doesn't do flat vector search like most memory systems. It uses 3-tier hierarchical recall:

| Step | What happens | Why it's faster |
|------|-------------|-----------------|
| 1. **Master Index** | Check which branches exist (< 1KB) | Skip irrelevant topics entirely |
| 2. **Branch Summary** | Read one-paragraph overview | Often enough to answer without loading entries |
| 3. **Full Entries** | Search within the right branch | Only loads what's needed |

Your agent doesn't scan 10,000 memories to answer "what's our marketing strategy?" — it checks the index, reads the marketing summary, and only dives into individual entries if the summary isn't enough.

### Quality Scoring

Results are ranked by 4 signals:

| Signal | Weight | Effect |
|--------|--------|--------|
| Relevance | Primary | Similarity to query (min threshold: 0.65) |
| Recency | 15% boost | Recent memories rank slightly higher |
| Importance | 10% boost | Critical entries (scored 1-5) surface first |
| Outdated penalty | 0.5x | Stale entries rank much lower |

---

## Setup

The skill install handles this automatically. For manual setup:

```bash
# Clone the repo
git clone https://github.com/GirlLove2Code/Memory-Vault.git ~/memory-vault

# Install dependencies
pip3 install -r ~/memory-vault/requirements.txt

# Verify (available=False is OK — keyword search still works)
python3 -c "
import sys; sys.path.insert(0, '$HOME/memory-vault')
from embedding import check_ollama; print(check_ollama())
"
```

**No Ollama? No problem.** Keyword search is a fully functional search path, not a degraded fallback. Most use cases work well with it.

### Using in your scripts

Add this at the top of any script that uses Memory Vault:

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/memory-vault"))
```

Then import directly:

```python
from recall import recall
from entry_manager import add_memory
from branch_manager import create_branch
```

---

## For Agent Owners: Making Your Agent Actually Use This

Installing Memory Vault is step one. Making your agent **use it every session** is the critical step most people skip.

Agents reload from startup files each session. If Memory Vault isn't in those files, your agent forgets it exists.

**After installing, do these 3 things:**

1. **Find your agent's startup files** — the files loaded every session (e.g., `IDENTITY.md`, `SYSTEM.md`, `INSTRUCTIONS.md`). Check your platform's docs.

2. **Add this to the startup/identity file:**
```
## Memory System
You have a memory system at [your Memory Vault path].
- Use recall() to search before starting any task
- Use add_memory() to save learnings, instructions, and decisions
- No API key needed — keyword search works automatically
```

3. **Add a save reminder to any periodic check** (heartbeat, maintenance loop):
```
## Memory Check
- Learned something? → add_memory("branch", "what I learned", importance=4)
- Owner gave an instruction? → Save with importance=5
- Made a mistake? → Save what went wrong
```

Without these steps, your agent will forget Memory Vault exists next session and never save anything. The code works — the agent just needs to know it's there.

---

## Design Principles

1. **Entries on disk are the source of truth.** Vectors are a rebuildable mirror.
2. **Local entries never reach the LLM.** Enforced automatically, not by convention.
3. **Say "I don't know" when `no_match` is True.** Don't hallucinate from empty results.
4. **Mark outdated, don't delete.** History has value.
5. **Short entries embed better.** One concept per memory.
6. **When unsure where to file — ask your human.** Don't guess.

---

## Limitations

- **Python only** — requires Python 3.9+. No JavaScript/TypeScript port yet.
- **Clone to install** — not yet on PyPI. Clone the repo and install deps manually.
- **Single machine** — memory lives on disk. No built-in sync across devices.
- **Keyword search without Ollama** — works well but semantic search (with Ollama) is more accurate for meaning-based queries.
- **Manual curation** — this is intentional memory, not auto-capture. The agent must actively call `add_memory()`.

---

## Advanced Features

Everything below is optional. The 6 core functions above are all you need to get started.

<details>
<summary><strong>Expiry & Freshness Management</strong></summary>

```python
from expiry import set_auto_expiry, refresh_entry, get_refresh_queue, set_expiry

# Auto-detect expiry from content patterns
set_auto_expiry("mem-123", "knowledge-base")
# Pricing/cost → 30 days | Status/tasks → 14 days | Architecture → 90 days

# Manually set expiry
set_expiry("mem-123", "knowledge-base", days=60)

# Confirm entry still valid (resets clock)
refresh_entry("mem-123", "knowledge-base")

# What needs review?
queue = get_refresh_queue()
```
</details>

<details>
<summary><strong>Timeline & Decision Log</strong></summary>

```python
from timeline import get_timeline, get_decision_log
from briefing import get_weekly_digest

# Knowledge changelog — what was added, outdated, superseded
timeline = get_timeline(days=7)

# Just the decisions
decisions = get_decision_log(days=30)

# Weekly summary
digest = get_weekly_digest()
```
</details>

<details>
<summary><strong>Garbage Collection</strong></summary>

```python
from garbage_collect import generate_report, find_stale_entries, find_duplicates, archive_entry

# Dry-run report
report = generate_report(max_age_days=90)

# Find near-duplicates (keyword overlap)
dupes = find_duplicates(threshold=0.6)

# Archive instead of delete
archive_entry(entry)
```
</details>

<details>
<summary><strong>Bulk Import</strong></summary>

```python
from bulk_import import import_file, import_text, import_entries

# From markdown, text, JSON, or JSONL
import_file("notes.md", branch="knowledge-base", tags=["imported"])

# Raw text (auto-splits by paragraph)
import_text("Long document content...", branch="knowledge-base")

# Structured list of dicts
import_entries([{"content": "fact 1"}, {"content": "fact 2"}], branch="knowledge-base")
```
</details>

<details>
<summary><strong>Event Hooks</strong></summary>

```python
from hooks import register_hook, register_file_hook, list_hooks

# In-memory callback
register_hook("memory_added", my_callback)

# Log to file (JSON lines)
register_file_hook("memory_outdated", "/tmp/memory_events.jsonl")

# See all hooks
list_hooks()
```

Events: `memory_added`, `memory_outdated`, `memory_expired`, `memory_pinned`, `memory_conflict`, `memory_refreshed`, `memory_archived`
</details>

<details>
<summary><strong>Auto-Summary & Branch Health</strong></summary>

```python
from auto_summary import update_summary, update_all_summaries, needs_update, get_summary_health

# Regenerate a branch summary
update_summary("knowledge-base/marketing")

# Check if summaries are stale
health = get_summary_health()

# Regenerate all
update_all_summaries()
```
</details>

<details>
<summary><strong>Full API Reference (48 functions)</strong></summary>

**Recall:** `recall` | `startup_recall` | `recall_deep` | `recall_from_summary` | `what_do_i_know` | `get_recall_stats`

**Memory CRUD:** `add_memory` | `get_entry` | `update_memory` | `delete_memory` | `mark_outdated` | `unmark_outdated` | `pin_memory` | `unpin_memory` | `find_conflicts` | `list_entries` | `score_importance`

**Branches:** `create_branch` | `list_branches` | `load_master_index` | `rebuild_master_index`

**Privacy:** `set_tier` | `get_tier` | `filter_for_llm`

**Session Intelligence:** `generate_briefing` | `get_timeline` | `get_decision_log` | `get_weekly_digest` | `format_timeline`

**Expiry:** `set_expiry` | `set_auto_expiry` | `refresh_entry` | `get_refresh_queue` | `backfill_expiry`

**Cleanup:** `generate_report` | `find_stale_entries` | `find_duplicates` | `archive_entry`

**Bulk Ops:** `import_file` | `import_text` | `import_entries` | `update_summary` | `update_all_summaries` | `needs_update` | `get_summary_health`

**Hooks:** `register_hook` | `register_file_hook` | `fire_hooks` | `get_event_log` | `list_hooks`
</details>

---

Built at [vivioo.io](https://vivioo.io) — where we run autonomous agents on real business operations daily. This isn't theoretical. It's the memory system our agents actually use.

*Other agents forget. Yours remembers — and knows what to keep private.*
