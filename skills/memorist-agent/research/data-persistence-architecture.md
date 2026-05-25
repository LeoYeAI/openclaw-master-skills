# Data Persistence Architecture for LLM-Powered Interview Agent

Research compiled March 2026. Focused on an agent that conducts memoir interviews via WhatsApp, currently using multiple JSON files (profile.json, entities.json, sessions.json, fragment files) read/written on every message exchange.

---

## 1. KV-Cache Optimization for LLM APIs

### How Prompt Caching Works Across Providers

All three major providers now offer prompt caching, but with different mechanics:

**Anthropic Claude**
- Explicit cache breakpoints via `cache_control` parameter on content blocks
- Up to 4 cache breakpoints per request
- Cache prefixes evaluated in order: tools → system → messages
- Minimum cacheable prefix: 1,024 tokens (Claude 3.5 Sonnet), 2,048 tokens (Claude 3.5 Haiku)
- Cache lifetime: 5 minutes (refreshed on each hit, no extra cost)
- Pricing: cache writes cost 1.25x base input price; cache reads cost 0.1x base input price (90% discount)
- You must explicitly mark cache boundaries; the system checks ~20 blocks before your breakpoint for hits

**OpenAI**
- Fully automatic — no configuration needed
- Minimum: 1,024 tokens, cache hits in 128-token increments
- Requests routed by hash of first ~256 tokens of prompt prefix
- Cache lifetime: ~5-10 minutes (varies)
- Pricing: cached tokens are 50% cheaper (not 90% like Anthropic)
- Optional `prompt_cache_key` parameter to influence routing for better hit rates

**Google Gemini**
- Both implicit (automatic, free) and explicit (manual, has storage costs) caching
- Implicit caching: enabled by default since May 2025, no storage costs, 90% discount on reads
- Explicit caching: storage costs of $1-4.50 per million tokens per hour
- Gemini 2.5+: 90% discount on cached reads
- Best for very large contexts (documents, codebases) that persist across many requests

### The Golden Rule: Stable Prefix = Cache Hit

The single most important principle: **the beginning of your prompt must be identical across requests**. Any change to early content invalidates the cache for everything after it.

```
┌─────────────────────────────────────────────────┐
│ STABLE PREFIX (cached)                          │
│ ┌─────────────────────────────────────────────┐ │
│ │ System instructions (never changes)         │ │
│ │ Tool definitions (rarely changes)           │ │
│ │ Narrator profile (changes infrequently)     │ │
│ │ Entity database (changes infrequently)      │ │
│ │ Summarized history (changes per session)    │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│ DYNAMIC SUFFIX (not cached, small)              │
│ ┌─────────────────────────────────────────────┐ │
│ │ Recent conversation turns (last 3-5)        │ │
│ │ Current user message                        │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### One Big File vs. Many Small Files

**Recommendation: Generate a single `context.md` for LLM consumption.**

Rationale:
- Reading 4+ files and injecting them as separate content blocks creates multiple opportunities for ordering inconsistencies or subtle changes that break cache prefixes
- A single consolidated context block means one stable prefix boundary
- The underlying storage can still be structured (SQLite, multiple files) — but what the LLM sees should be one unified document
- This also simplifies the `cache_control` placement: put one breakpoint at the end of the stable context block

### File Ordering and Cache Stability

Key findings from the paper ["Don't Break the Cache" (arXiv:2601.06007)](https://arxiv.org/abs/2601.06007):
- Prompt caching reduces API costs by 41-80% and improves time-to-first-token by 13-31%
- **Strategic cache boundary control** (e.g., caching only system prompts while excluding dynamic tool results) provides more consistent benefits than naive full-context caching
- Full context caching can paradoxically increase latency when dynamic content changes frequently

**Practical ordering for our agent:**
1. System prompt (static) — CACHE BREAKPOINT 1
2. Tool definitions (static) — CACHE BREAKPOINT 2
3. Narrator context (profile + entities + summarized history) — CACHE BREAKPOINT 3
4. Recent conversation turns (dynamic, last 3-5 exchanges)
5. Current user message

This gives us 3 stable cache layers. The narrator context changes only when we update the profile or add entities — typically once per session, not every message.

### Things That Break the Cache

- Changing tool definitions or `tool_choice` (Anthropic)
- Reordering JSON keys in tool definitions (languages like Swift/Go randomize key order)
- Adding/removing images anywhere in the prompt (Anthropic)
- Any modification to content before a cache breakpoint
- Timestamps or request IDs embedded in system prompts

---

## 2. Cost Reduction Strategies

### Current Cost Problem

If the agent reads ~10KB of context per message (profile + entities + sessions + fragments), that's roughly 2,500-3,000 input tokens per exchange. At $3/M input tokens (Claude 3.5 Sonnet), that's ~$0.009 per exchange. Over a 60-minute interview with 100+ exchanges, context alone costs ~$0.90. With growing context (new entities, longer history), this compounds.

### Strategy 1: Tiered Context Loading

Split context into tiers:

| Tier | Content | When Loaded | Token Cost |
|------|---------|-------------|------------|
| Always | System prompt + tools | Every message | ~500 tokens (fixed) |
| Always | Narrator profile (name, age, key facts) | Every message | ~200 tokens |
| Always | Compact entity list (names only) | Every message | ~100 tokens |
| Session | Current session summary + last 5 turns | Every message | ~500-1000 tokens |
| On-demand | Full entity details | When entity mentioned | ~200-500 tokens |
| On-demand | Historical session summaries | When referencing past | ~300-800 tokens |
| Never re-read | Raw fragment text | Already in summaries | 0 tokens |

**Result: Base context drops from ~3,000 tokens to ~1,300 tokens per message (57% reduction).**

### Strategy 2: Progressive Summarization

```
Exchange 1-5:   Keep full text          (~150 tokens each = 750)
Exchange 6-15:  Summarize to 1 line     (~20 tokens each = 200)
Exchange 16+:   Merge into session note (~100 tokens total)
```

Implementation approach:
```python
def build_conversation_context(exchanges, current_idx):
    context_parts = []

    # Full text for last 5 exchanges
    recent = exchanges[max(0, current_idx-5):current_idx]
    for ex in recent:
        context_parts.append(f"[{ex.role}]: {ex.content}")

    # One-line summaries for exchanges 6-15 back
    mid_range = exchanges[max(0, current_idx-15):max(0, current_idx-5)]
    if mid_range:
        summaries = [ex.summary for ex in mid_range]
        context_parts.insert(0, "Previous exchanges: " + "; ".join(summaries))

    # Session-level summary for everything older
    if current_idx > 15:
        old = exchanges[:max(0, current_idx-15)]
        context_parts.insert(0, f"Earlier in session: {generate_session_summary(old)}")

    return "\n".join(context_parts)
```

### Strategy 3: Cache-Aware Prompt Construction

Since cached tokens cost 90% less on Anthropic/Gemini:

```python
def build_prompt_for_cache(narrator_context, recent_turns, user_message):
    """
    Structure prompt so the expensive part (narrator context) is cached,
    and only cheap dynamic content varies per message.
    """
    return {
        "system": [
            {
                "type": "text",
                "text": SYSTEM_INSTRUCTIONS,  # ~500 tokens, static
            },
            {
                "type": "text",
                "text": narrator_context,      # ~800 tokens, changes rarely
                "cache_control": {"type": "ephemeral"}  # CACHE BREAKPOINT
            }
        ],
        "messages": [
            # Recent turns — small, dynamic, NOT cached
            *recent_turns,
            {"role": "user", "content": user_message}
        ]
    }
```

**Cost calculation with caching:**
- Narrator context (800 tokens): first write = 800 * $3.75/M = $0.003; subsequent reads = 800 * $0.30/M = $0.00024
- Dynamic content (500 tokens): 500 * $3.00/M = $0.0015 per message
- Per-exchange cost after first: ~$0.002 instead of ~$0.009 (78% savings)
- Over 100 exchanges: ~$0.20 instead of ~$0.90

### Strategy 4: Smart Model Routing

Not every exchange needs the most powerful model:
- Simple acknowledgments, clarifications → use Haiku/GPT-4o-mini (~10x cheaper)
- Deep follow-up questions, emotional moments → use Sonnet/GPT-4o
- Summary generation, entity extraction → can be batched, use cheaper model

This alone can cut costs by 40-60% with no quality loss on the important turns.

---

## 3. Save/Load Latency Reduction

### Current Problem: 7 File I/O Operations Per Message

```
READ:  profile.json + entities.json + sessions.json + fragments/*.json = 4+ reads
WRITE: profile.json + entities.json + sessions.json = 3 writes
Total: 7+ file operations per message exchange
```

On macOS with APFS, each file open/read/close takes ~0.1-0.5ms for small files. So 7 operations = ~1-3ms. This isn't the bottleneck (LLM API calls take 1-5 seconds), but it creates complexity and race condition risks.

### Option A: Single State File (state.json)

```json
{
  "version": 3,
  "updated_at": "2026-03-11T10:30:00Z",
  "profile": {
    "name": "Maria",
    "birth_year": 1945,
    "key_facts": ["grew up in Buenos Aires", "moved to NYC 1970"]
  },
  "entities": {
    "carlos": {"type": "person", "relation": "husband", "mentions": 12},
    "buenos_aires": {"type": "place", "significance": "childhood home"}
  },
  "current_session": {
    "id": "sess_20260311",
    "topic": "childhood memories",
    "exchange_count": 15,
    "summary": "Discussed growing up near the river...",
    "recent_turns": [
      {"role": "assistant", "content": "Tell me about..."},
      {"role": "user", "content": "I remember..."}
    ]
  },
  "past_sessions": [
    {"id": "sess_20260308", "summary": "First session. Covered basic biography..."}
  ]
}
```

**Pros:** 1 read + 1 write per exchange. Atomic. Simple. No partial-state bugs.
**Cons:** Rewrites everything on every save. No built-in history. File grows over time.
**Verdict:** Good starting point. Works well up to ~50KB.

### Option B: Append-Only Log + Periodic Snapshot

```
narrator_123/
  snapshot_v5.json      ← Full state as of version 5
  log.jsonl             ← Append-only changes since snapshot
```

Each exchange appends one line to `log.jsonl`:
```jsonl
{"v":6,"ts":"2026-03-11T10:30:00Z","type":"exchange","turn":{"role":"user","content":"I remember the garden"},"entities_added":["garden"]}
{"v":7,"ts":"2026-03-11T10:30:15Z","type":"exchange","turn":{"role":"assistant","content":"Tell me more about the garden"},"profile_updates":null}
```

Every N exchanges (e.g., 20), or at session end, create a new snapshot:
```python
def save_exchange(state_dir, exchange_data):
    # Append to log — fast, no read required
    with open(f"{state_dir}/log.jsonl", "a") as f:
        f.write(json.dumps(exchange_data) + "\n")

def load_state(state_dir):
    # Read latest snapshot
    snapshot = read_latest_snapshot(state_dir)
    # Replay log entries after snapshot
    log_entries = read_log_after(state_dir, snapshot["version"])
    # Apply log entries to snapshot
    return apply_log(snapshot, log_entries)

def maybe_checkpoint(state_dir, state, force=False):
    if force or state["exchanges_since_snapshot"] >= 20:
        write_snapshot(state_dir, state)
        truncate_log(state_dir, state["version"])
```

**Pros:** Writes are append-only (fastest possible I/O). Natural versioning. Can reconstruct any point in time. No data loss on crash.
**Cons:** Reads require snapshot + log replay. Slightly more complex. Need periodic compaction.
**Verdict:** Best balance of performance, versioning, and simplicity. Recommended for production.

### Option C: SQLite

```python
import sqlite3

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")  # Concurrent reads + writes
    conn.execute("PRAGMA synchronous=NORMAL")  # Faster, still safe
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS profile (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS entities (
            name TEXT PRIMARY KEY,
            type TEXT,
            data TEXT,  -- JSON blob
            first_mentioned TEXT,
            mention_count INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS exchanges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            summary TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            topic TEXT,
            summary TEXT,
            started_at TEXT,
            ended_at TEXT
        );
    """)
    return conn
```

**Pros:** ACID guarantees. Concurrent access safe. Incremental reads/writes (only touch changed rows). Built-in on macOS. WAL mode = fast concurrent reads. Can query efficiently (e.g., "find all exchanges mentioning 'carlos'"). Single file when not in use.
**Cons:** Requires SQL. Slightly more complex than JSON for simple cases. Three files on disk during use (.db, .db-wal, .db-shm). Harder to inspect/edit manually.
**Verdict:** Best technical choice for production. Overkill for MVP but scales perfectly.

### Performance Comparison

| Operation | JSON (4 files) | Single JSON | Append Log | SQLite WAL |
|-----------|----------------|-------------|------------|------------|
| Read full state | ~2ms | ~0.5ms | ~1ms (snapshot+replay) | ~0.5ms |
| Write after exchange | ~2ms (3 writes) | ~0.5ms (full rewrite) | ~0.1ms (append) | ~0.2ms (INSERT) |
| Concurrent safety | None | None | Append-safe | Full ACID |
| 1000 exchanges | ~200KB across files | ~200KB one file | ~50KB snapshot + ~150KB log | ~250KB |
| Manual inspection | Easy | Easy | Moderate | Requires tool |

---

## 4. Multi-Version Data Support

### Requirements
1. The narrator's story evolves — corrections, additions, reinterpretations
2. Family members may annotate or edit chapters
3. Need ability to see what changed and when
4. Must support rollback if edits are unwanted

### Approach: Event Sourcing with Snapshots

This is the append-only log pattern from Section 3, extended with version metadata:

```jsonl
{"v":1,"ts":"...","actor":"agent","type":"profile_update","data":{"name":"Maria","birth_year":1945}}
{"v":2,"ts":"...","actor":"agent","type":"entity_add","data":{"name":"carlos","type":"person"}}
{"v":3,"ts":"...","actor":"narrator","type":"exchange","data":{"content":"I was born in..."}}
{"v":4,"ts":"...","actor":"family:daughter_ana","type":"annotation","target":"v3","data":{"note":"Mom actually born in 1944, not 1945"}}
{"v":5,"ts":"...","actor":"agent","type":"profile_update","data":{"birth_year":1944},"reason":"correction from family:daughter_ana at v4"}
```

Key design features:
- Every change is an immutable event with a version number
- `actor` field tracks who made the change (agent, narrator, family member)
- Annotations reference specific versions
- Corrections create new events (never modify old ones)
- Snapshots compress the event log periodically

### Diffing and Rollback

```python
def diff_versions(log, from_v, to_v):
    """Show what changed between two versions."""
    changes = [e for e in log if from_v < e["v"] <= to_v]
    return changes

def rollback_to(state_dir, target_version):
    """Reconstruct state at a specific version."""
    snapshot = find_snapshot_before(state_dir, target_version)
    log = read_log_between(state_dir, snapshot["version"], target_version)
    return apply_log(snapshot, log)

def create_branch(state_dir, branch_name, from_version):
    """Create a named branch for family editing."""
    # Copy snapshot + relevant log entries
    branch_dir = f"{state_dir}/branches/{branch_name}"
    os.makedirs(branch_dir, exist_ok=True)
    state = rollback_to(state_dir, from_version)
    write_snapshot(branch_dir, state)
    # New edits go to branch log
    return branch_dir
```

### Concurrent Access (Family Co-Editing)

For a local-first app where family members edit via a shared folder or sync service:

1. **File locking (simplest):** Use `fcntl.flock()` on macOS. Only one writer at a time.
2. **Append-only log (recommended):** Multiple writers can safely append to a JSONL file (atomic on macOS for lines < 4KB via PIPE_BUF). Conflicts resolved at read time by version ordering.
3. **SQLite (most robust):** WAL mode supports concurrent readers + one writer. Perfect for this use case.

```python
# Safe concurrent append to JSONL (works on macOS for small writes)
import fcntl

def append_event(log_path, event):
    with open(log_path, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(event) + "\n")
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)
```

### Storage Budget

Assuming ~200 bytes per event, 100 exchanges per session, 50 sessions per narrator:
- Raw log: 200 * 100 * 50 = ~1MB
- With snapshots every 20 events: ~250KB snapshots + ~1MB log = ~1.25MB
- Very manageable for local storage

---

## 5. Proposed Architecture

### Recommended: Hybrid Append-Log + Generated Context

After evaluating all options, the recommended architecture separates **storage** from **LLM context generation**:

```
┌─────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                         │
│                                                         │
│  narrator_123/                                          │
│    state.db          ← SQLite (profile, entities,       │
│                        sessions, exchanges, versions)   │
│    -- OR --                                             │
│    snapshot.json     ← Latest full state                │
│    log.jsonl         ← Append-only event log            │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                 CONTEXT GENERATION LAYER                 │
│                                                         │
│  On each message:                                       │
│    1. Read state (1 file op)                            │
│    2. Generate context string (in-memory)               │
│    3. Send to LLM with cache breakpoints                │
│    4. Process response                                  │
│    5. Append event to log / INSERT to SQLite (1 file op)│
│                                                         │
│  Total I/O: 1 read + 1 write (down from 4+3 = 7)       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                   LLM PROMPT STRUCTURE                   │
│                                                         │
│  [SYSTEM PROMPT - static]              ← CACHE BREAK 1  │
│  [TOOL DEFINITIONS - static]           ← CACHE BREAK 2  │
│  [NARRATOR CONTEXT - generated block]  ← CACHE BREAK 3  │
│  [RECENT TURNS - dynamic, last 3-5]                     │
│  [USER MESSAGE - current]                               │
└─────────────────────────────────────────────────────────┘
```

### The Context Generation Function

This is the critical bridge between storage and LLM:

```python
def generate_narrator_context(state: dict) -> str:
    """
    Generate a single stable context string from narrator state.
    This string goes into the system prompt and gets cached.

    IMPORTANT: Output must be deterministic for same input state.
    - No timestamps that change per-call
    - No random ordering
    - Sorted keys/lists for consistency
    """
    parts = []

    # Profile section
    p = state["profile"]
    parts.append(f"# Narrator: {p['name']}")
    parts.append(f"Born: {p.get('birth_year', 'unknown')}")
    if p.get('key_facts'):
        parts.append("Key facts: " + "; ".join(sorted(p['key_facts'])))

    # Entities section
    parts.append("\n# Key People & Places")
    for name, ent in sorted(state["entities"].items()):
        parts.append(f"- {name} ({ent['type']}): {ent.get('relation', ent.get('significance', ''))}")

    # Session history (summarized)
    parts.append("\n# Interview History")
    for sess in state.get("past_sessions", []):
        parts.append(f"- Session {sess['id']}: {sess['summary']}")

    # Current session summary (not recent turns — those go in messages)
    curr = state.get("current_session", {})
    if curr.get("summary"):
        parts.append(f"\n# Current Session ({curr.get('topic', 'ongoing')})")
        parts.append(curr["summary"])

    return "\n".join(parts)
```

### Why This Maximizes Cache Hits

1. **System prompt** never changes → always cached after first call
2. **Tool definitions** rarely change → almost always cached
3. **Narrator context** only changes when profile/entities/summary update — typically once per session, not every message. Between updates, this is an identical string → cached
4. **Recent turns** are small (3-5 exchanges = ~300-500 tokens) and are the only "expensive" uncached content
5. **Deterministic generation** (sorted keys, no timestamps) ensures identical state produces identical strings

### When to Update the Narrator Context

The context block should be regenerated (breaking cache for that layer) only when:
- A new entity is extracted (every few exchanges)
- Profile information is corrected
- The rolling summary is updated (every ~10 exchanges)

**Optimization: Batch context updates.** Instead of updating after every exchange, accumulate changes and update the context block every N exchanges:

```python
class ContextManager:
    def __init__(self):
        self.cached_context = None
        self.pending_changes = 0
        self.UPDATE_INTERVAL = 5  # Regenerate context every 5 exchanges

    def get_context(self, state):
        if self.cached_context is None or self.pending_changes >= self.UPDATE_INTERVAL:
            self.cached_context = generate_narrator_context(state)
            self.pending_changes = 0
        return self.cached_context

    def record_change(self):
        self.pending_changes += 1
```

This means the narrator context string stays identical for 5 consecutive exchanges → 5 consecutive cache hits on that layer.

### Concrete Implementation for Single-File Skill

For the simplest possible implementation that still gets most benefits:

```python
import json
import os
from pathlib import Path

STATE_DIR = Path("~/.memoirist/narrators").expanduser()

def load_state(narrator_id: str) -> dict:
    """Single read operation. Returns full narrator state."""
    state_file = STATE_DIR / narrator_id / "state.json"
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {
        "version": 0,
        "profile": {},
        "entities": {},
        "current_session": {"turns": [], "summary": ""},
        "past_sessions": [],
        "log": []  # Append-only history within the file
    }

def save_state(narrator_id: str, state: dict, exchange_event: dict):
    """Single write operation. Atomic via temp file + rename."""
    state_dir = STATE_DIR / narrator_id
    state_dir.mkdir(parents=True, exist_ok=True)

    # Append event to in-memory log
    state["version"] += 1
    exchange_event["v"] = state["version"]
    state["log"].append(exchange_event)

    # Trim old turns from current session (keep last 10 full, summarize rest)
    trim_session_history(state)

    # Atomic write: write to temp, then rename
    state_file = state_dir / "state.json"
    tmp_file = state_dir / "state.json.tmp"
    tmp_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    tmp_file.rename(state_file)  # Atomic on macOS/APFS

def trim_session_history(state):
    """Keep last 10 turns in full, summarize older ones into session summary."""
    turns = state["current_session"].get("turns", [])
    if len(turns) > 10:
        old_turns = turns[:-10]
        # These would be summarized by the LLM in a separate call
        # For now, just truncate
        state["current_session"]["turns"] = turns[-10:]

def build_llm_messages(state: dict, user_message: str) -> dict:
    """Build the prompt structure optimized for cache hits."""
    narrator_context = generate_narrator_context(state)
    recent_turns = state["current_session"].get("turns", [])[-6:]  # Last 3 exchanges

    return {
        "system": [
            {
                "type": "text",
                "text": SYSTEM_INSTRUCTIONS,
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text",
                "text": narrator_context,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        "messages": [
            *[{"role": t["role"], "content": t["content"]} for t in recent_turns],
            {"role": "user", "content": user_message}
        ]
    }
```

### Migration Path

| Phase | Storage | LLM Context | I/O per msg | Cache hits |
|-------|---------|-------------|-------------|------------|
| Current | 4+ JSON files | Read all files | 7 ops | None |
| Phase 1 | Single state.json | Generated context string | 2 ops | ~80% |
| Phase 2 | state.json + log.jsonl | Batched context updates | 1 read + 1 append | ~90% |
| Phase 3 | SQLite | Same generated context | 1 query + 1 insert | ~90% |

**Recommendation: Start with Phase 1 immediately.** It's the simplest change with the biggest impact. Phase 2 adds versioning when needed. Phase 3 is for when concurrent access or complex queries become important.

### Decision Matrix

| Criterion | Single JSON | Log + Snapshot | SQLite | Consolidated .md |
|-----------|------------|----------------|--------|-------------------|
| Simplicity | 5/5 | 3/5 | 3/5 | 4/5 |
| I/O efficiency | 4/5 | 5/5 | 5/5 | 3/5 |
| Versioning | 2/5 | 5/5 | 4/5 | 1/5 |
| Concurrent access | 1/5 | 3/5 | 5/5 | 1/5 |
| Cache-friendliness | 4/5 | 4/5 | 4/5 | 5/5 |
| Manual inspection | 5/5 | 3/5 | 2/5 | 5/5 |
| Local-first/privacy | 5/5 | 5/5 | 5/5 | 5/5 |
| Single-file skill fit | 5/5 | 3/5 | 2/5 | 4/5 |

### Final Recommendation

**Use Single state.json + generated context string (Phase 1)** with the following specific practices:

1. **Storage:** One `state.json` per narrator, atomic writes via temp+rename
2. **LLM context:** Generate a deterministic context string from state; place it in system prompt with `cache_control` breakpoint
3. **History management:** Keep last 5 turns in full; summarize older turns every 10 exchanges using a cheap model call
4. **Versioning:** Keep an append-only `log` array inside state.json; periodically archive old log entries to `archive.jsonl`
5. **Cache optimization:** Only regenerate the context string when state actually changes (batch updates every 5 exchanges)
6. **Cost savings:** ~78% reduction from prompt caching + ~57% reduction from tiered context = total ~90% cost reduction vs. current approach

This architecture achieves the core goals:
- 1 read + 1 write per exchange (down from 7 operations)
- ~90% cache hit rate on the expensive context prefix
- Natural versioning via event log
- Local-first, single-file friendly
- Simple enough for a single skill file to implement

---

## Sources

- [Anthropic Prompt Caching Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [OpenAI Prompt Caching Guide](https://platform.openai.com/docs/guides/prompt-caching)
- [Google Gemini Context Caching](https://ai.google.dev/gemini-api/docs/caching)
- [Don't Break the Cache: Evaluation of Prompt Caching for Agentic Tasks (arXiv:2601.06007)](https://arxiv.org/abs/2601.06007)
- [Prompt Caching: 10x Cheaper LLM Tokens (ngrok)](https://ngrok.com/blog/prompt-caching)
- [Prompt Caching Guide 2025: Token Economics (PromptBuilder)](https://promptbuilder.cc/blog/prompt-caching-token-economics-2025)
- [Cutting Through the Noise: Context Management for LLM Agents (JetBrains)](https://blog.jetbrains.com/research/2025/12/efficient-context-management/)
- [Token Optimization Strategies for AI Agents (Medium/Elementor)](https://medium.com/elementor-engineers/optimizing-token-usage-in-agent-based-assistants-ffd1822ece9c)
- [LLM Token Optimization: Cut Costs & Latency (Redis)](https://redis.io/blog/llm-token-optimization-speed-up-apps/)
- [Context Window Management Strategies (Maxim)](https://www.getmaxim.ai/articles/context-window-management-strategies-for-long-context-ai-agents-and-chatbots/)
- [SQLite WAL Mode Documentation](https://sqlite.org/wal.html)
- [SQLite in 2025: The Unsung Hero (NerdLevelTech)](https://nerdleveltech.com/sqlite-in-2025-the-unsung-hero-powering-modern-apps)
- [How Prompt Caching Works: Paged Attention and APC](https://sankalp.bearblog.dev/how-prompt-caching-works/)
- [Anthropic Automatic Prompt Caching (Medium)](https://medium.com/ai-software-engineer/anthropic-just-fixed-the-biggest-hidden-cost-in-ai-agents-using-automatic-prompt-caching-9d47c95903c5)
