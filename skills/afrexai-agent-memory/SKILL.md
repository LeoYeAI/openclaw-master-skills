---
name: Agent Memory Architecture
description: Complete zero-dependency memory system for AI agents — file-based architecture, daily notes, long-term curation, context management, heartbeat integration, and memory hygiene. No APIs, no databases, no external tools. Works with any agent framework.
metadata:
  category: agent
  skills: ["memory", "agent", "context", "persistence", "knowledge-management", "openclaw", "productivity"]
---

# Agent Memory Architecture

Complete memory system for AI agents using only files. No APIs. No databases. No external dependencies. Just smart file structures and disciplined practices that give your agent perfect recall.

---

## 1. Memory Architecture Overview

```
workspace/
├── MEMORY.md              ← Long-term curated memory (the brain)
├── ACTIVE-CONTEXT.md      ← Hot working memory (what matters NOW)
├── AGENTS.md              ← Operating manual (how you work)
├── memory/
│   ├── 2026-01-15.md      ← Daily notes (raw event log)
│   ├── 2026-01-16.md
│   ├── heartbeat-state.json  ← Heartbeat tracking state
│   ├── topics/
│   │   ├── project-alpha.md  ← Topic-specific deep context
│   │   ├── client-acme.md
│   │   └── tech-stack.md
│   └── archive/
│       ├── 2025-Q4.md       ← Quarterly archive summaries
│       └── 2025-Q3.md
```

### The 5 Memory Layers

| Layer | File | Purpose | Read Frequency | Write Frequency |
|-------|------|---------|----------------|-----------------|
| **1. Hot** | ACTIVE-CONTEXT.md | Current priorities, blockers, in-flight work | Every session | Multiple times/day |
| **2. Warm** | MEMORY.md | Curated long-term knowledge, decisions, people | Every main session | Weekly curation |
| **3. Daily** | memory/YYYY-MM-DD.md | Raw event log, conversations, actions taken | Today + yesterday | Throughout the day |
| **4. Topic** | memory/topics/*.md | Deep context on specific subjects | When topic comes up | As knowledge grows |
| **5. Cold** | memory/archive/*.md | Historical summaries, rarely accessed | On explicit search | Quarterly rollup |

### Core Principle: Write It Down

**Memory is limited. Files are permanent.**

- "Mental notes" don't survive session restarts. Files do.
- If someone says "remember this" → write to a file
- If you learn a lesson → update the relevant file
- If you make a mistake → document it so future-you doesn't repeat it
- **Text > Brain** 📝

---

## 2. Layer 1: Hot Memory (ACTIVE-CONTEXT.md)

Your working scratchpad. What's happening RIGHT NOW.

### Template

```markdown
# ACTIVE-CONTEXT.md — What's Hot

Last updated: 2026-01-15 14:30 GMT

## 🔥 Current Priority
[ONE sentence: what is the most important thing right now?]

## In Progress
- [ ] Task A — status, next step
- [ ] Task B — status, blocker

## Waiting On
- Waiting for [person] to [action] — asked [date]
- Waiting for [system] to [complete] — ETA [time]

## Key Decisions Made Today
- Decided to [X] because [Y] — reversible: yes/no

## Context for Next Session
[What does future-you need to know to pick up where you left off?]
```

### Rules
- **Max 50 lines** — if it's longer, you're hoarding. Move completed items to daily notes.
- **Update before ending session** — your gift to future-you
- **One priority** — if everything is priority, nothing is
- **Delete completed items** — this is NOT an archive

---

## 3. Layer 2: Long-Term Memory (MEMORY.md)

Your curated brain. Distilled knowledge, not raw logs.

### Structure Template

```markdown
# MEMORY.md — Long-Term Memory

## About [Human]
- Name, preferences, timezone, communication style
- What motivates them, what frustrates them
- Key relationships, roles, goals

## About Me [Agent]
- Name, personality, capabilities
- Operating preferences learned over time

## Active Projects
### Project Name
- Status, key decisions, blockers
- Links to relevant topic files

## Key People
- [Name] — role, relationship, communication notes

## Lessons Learned
- [Date] — [What happened] → [What I learned]

## Preferences & Patterns
- [Human prefers X over Y]
- [This approach works better than that one]

## Important Dates
- [Event] — [Date] — [Context]
```

### Curation Rules

1. **Only curated insights** — not raw events (those go in daily notes)
2. **Review weekly** — scan daily notes, extract what's worth keeping
3. **Prune quarterly** — remove outdated info, archive completed projects
4. **Max 500 lines** — if it's longer, you need topic files
5. **Security** — never store secrets, API keys, passwords
6. **Main session only** — don't load MEMORY.md in group chats or shared contexts

### What Goes In vs What Doesn't

| ✅ Goes in MEMORY.md | ❌ Stays in daily notes |
|----------------------|------------------------|
| "Kalin prefers being told, not asked" | "Today Kalin said he prefers being told" |
| "Apollo.io free plan doesn't support API" | "Tried Apollo.io API, got 403 error" |
| "Client AcmeCo — $50K deal, Q2 close" | "Sent AcmeCo the proposal at 3pm" |
| "Always verify prospect names with live search" | "Found 6/18 prospect names were wrong" |

---

## 4. Layer 3: Daily Notes (memory/YYYY-MM-DD.md)

Raw event log. Everything that happened today.

### Template

```markdown
# 2026-01-15 — Daily Notes

## Morning
- [08:15] Started session, reviewed ACTIVE-CONTEXT
- [08:30] Received task from [human]: [summary]
- [09:00] Completed [task] — result: [outcome]

## Afternoon
- [14:00] [Event/conversation summary]
- [15:30] Decision: [what was decided and why]

## Key Takeaways
- [Anything worth remembering beyond today]

## Tomorrow
- [ ] Follow up on [X]
- [ ] Check [Y]
```

### Rules
- **One file per day** — `memory/YYYY-MM-DD.md`
- **Append-only** during the day — don't edit earlier entries
- **Timestamps** for important events
- **Summarize, don't transcribe** — capture essence, not every word
- **Auto-create** the `memory/` directory if it doesn't exist
- **Retention**: Keep 30 days of daily notes. Archive older ones quarterly.

---

## 5. Layer 4: Topic Files (memory/topics/*.md)

Deep context on specific subjects that span many days.

### When to Create a Topic File

- A project lasts more than 2 weeks
- A client/person comes up frequently
- A technical area needs accumulated knowledge
- You keep searching daily notes for the same information

### Template

```markdown
# [Topic Name]

Created: YYYY-MM-DD
Last updated: YYYY-MM-DD

## Summary
[2-3 sentences: what is this about?]

## Key Facts
- [Fact 1]
- [Fact 2]

## Decision Log
| Date | Decision | Reasoning | Outcome |
|------|----------|-----------|---------|
| | | | |

## Open Questions
- [Question 1]

## Related
- memory/topics/[related-topic].md
- [External link]
```

### Rules
- **Name descriptively** — `project-alpha.md` not `topic-1.md`
- **One topic per file** — if it covers two things, split it
- **Link from MEMORY.md** — topic files are extensions of long-term memory
- **Update when you learn** — don't let them go stale

---

## 6. Layer 5: Archive (memory/archive/*.md)

Historical summaries for completed projects and past quarters.

### Quarterly Archive Process

Every quarter (or when daily notes exceed 30 files):

1. Read all daily notes older than 30 days
2. Extract key events, decisions, outcomes, lessons
3. Write `memory/archive/YYYY-QN.md` (e.g., `2025-Q4.md`)
4. Delete or move archived daily notes
5. Update MEMORY.md if any long-term insights emerged

### Archive Template

```markdown
# Q4 2025 Archive

## Summary
[3-5 sentences: what defined this quarter?]

## Major Events
- [Event 1] — [outcome]
- [Event 2] — [outcome]

## Projects
### [Project Name]
- Started: [date], Ended: [date]
- Outcome: [result]
- Lesson: [what we learned]

## Metrics
- [Key metric 1]: [value]
- [Key metric 2]: [value]

## Lessons Carried Forward
- [Lesson added to MEMORY.md: yes/no]
```

---

## 7. Session Startup Protocol

What to read at the start of every session, in order:

### Main Session (Direct Chat with Human)

```
1. SOUL.md          — Who am I? (personality, values)
2. USER.md          — Who am I helping? (human context)
3. MEMORY.md        — Long-term memory (full brain)
4. ACTIVE-CONTEXT.md — Hot working memory (current state)
5. memory/today.md  — Today's daily notes (if exists)
6. memory/yesterday.md — Yesterday's notes (recent context)
```

### Shared/Group Session (Discord, Slack, Group Chats)

```
1. SOUL.md          — Who am I?
2. USER.md          — Who am I helping?
3. ACTIVE-CONTEXT.md — Current priorities only
4. memory/today.md  — Today's notes
⚠️ DO NOT load MEMORY.md — contains private context
```

### Sub-Agent / Isolated Session

```
1. Task-specific context only
2. Relevant topic file if applicable
3. ACTIVE-CONTEXT.md for current state
⚠️ Minimal context = focused output + lower token cost
```

---

## 8. Memory Write Protocol

### When to Write (Triggers)

| Event | Action | Target File |
|-------|--------|-------------|
| Session starts | Log start time | Daily notes |
| Task completed | Log result + outcome | Daily notes |
| Decision made | Log decision + reasoning | Daily notes + topic file |
| Lesson learned | Log lesson | Daily notes → MEMORY.md |
| Person mentioned with new info | Update person section | MEMORY.md or topic file |
| Human says "remember this" | Write immediately | MEMORY.md |
| Session ends | Update ACTIVE-CONTEXT | ACTIVE-CONTEXT.md |
| Weekly review | Curate MEMORY.md | MEMORY.md |
| Quarterly | Archive old daily notes | Archive |

### Write-Ahead Protocol

For critical information, write BEFORE acting:

```
1. Human gives important instruction
2. IMMEDIATELY write to daily notes or MEMORY.md
3. THEN execute the instruction
4. Update with results after

Why: If the session crashes mid-execution, the instruction is preserved.
```

### Conflict Resolution

When information conflicts between layers:
- **ACTIVE-CONTEXT.md wins** for current state (most recent)
- **MEMORY.md wins** for long-term facts (curated)
- **Daily notes** are evidence — use to resolve disputes
- **Topic files** win for deep domain knowledge

---

## 9. Memory Search Strategy

When you need to find something:

### Search Order (Fast to Slow)

```
1. ACTIVE-CONTEXT.md    — Is it current? (instant)
2. MEMORY.md            — Is it a known fact? (quick scan)
3. memory/today.md      — Did it happen today? (quick)
4. memory/yesterday.md  — Did it happen recently? (quick)
5. memory/topics/*.md   — Is it a deep topic? (targeted)
6. memory_search tool   — Semantic search across all files
7. memory/archive/*.md  — Is it historical? (slow)
```

### Search Tips
- Use `memory_search` tool for fuzzy/semantic queries
- Use `memory_get` with line numbers for precise retrieval after search
- Check daily notes in reverse chronological order
- If you can't find it after 3 searches, ask the human

---

## 10. Memory Hygiene Schedule

### Daily (During Session)
- [ ] Read ACTIVE-CONTEXT.md at session start
- [ ] Create/append to today's daily notes
- [ ] Update ACTIVE-CONTEXT.md before session ends
- [ ] Move completed ACTIVE-CONTEXT items to daily notes

### Weekly (Pick One Heartbeat)
- [ ] Read last 7 daily notes
- [ ] Extract significant events/lessons to MEMORY.md
- [ ] Prune ACTIVE-CONTEXT.md (remove stale items)
- [ ] Check topic files for staleness
- [ ] Review MEMORY.md for outdated information

### Monthly
- [ ] MEMORY.md line count check (target: <500 lines)
- [ ] Topic files audit — any need merging or archiving?
- [ ] Daily notes older than 30 days → archive
- [ ] Check if any topic files should be promoted to MEMORY.md sections

### Quarterly
- [ ] Full archive process (see Layer 5)
- [ ] MEMORY.md deep review — still accurate?
- [ ] Topic files — archive completed projects
- [ ] Update AGENTS.md with any process improvements learned

---

## 11. Heartbeat Integration

Use heartbeats (periodic agent wake-ups) for memory maintenance:

### heartbeat-state.json

```json
{
  "last_memory_review": "2026-01-15",
  "last_archive": "2025-12-31",
  "last_active_context_prune": "2026-01-14",
  "daily_notes_count": 12,
  "memory_md_lines": 287,
  "next_scheduled": {
    "weekly_review": "2026-01-19",
    "monthly_audit": "2026-02-01",
    "quarterly_archive": "2026-03-31"
  }
}
```

### Heartbeat Memory Tasks (Rotate)

```
Heartbeat 1: Check daily notes count, prune ACTIVE-CONTEXT
Heartbeat 2: Scan recent daily notes, update MEMORY.md
Heartbeat 3: Check topic files for staleness
Heartbeat 4: Token guard — how much are memory reads costing?
```

---

## 12. Context Window Management

### Token Budget Rules

| File | Max Size | If Over Limit |
|------|----------|---------------|
| ACTIVE-CONTEXT.md | 50 lines / 2KB | Move items to daily notes |
| MEMORY.md | 500 lines / 25KB | Split into topic files |
| Daily notes | 200 lines / 10KB | Summarize, stop transcribing |
| Topic files | 300 lines / 15KB | Split or archive |

### Smart Loading Strategy

Don't load everything every session. Use progressive disclosure:

```
Level 1: Always load (every session)
  → ACTIVE-CONTEXT.md (tiny, essential)
  → SOUL.md, USER.md (identity)

Level 2: Load in main sessions
  → MEMORY.md (the brain)
  → Today's daily notes

Level 3: Load on demand
  → Topic files (when topic comes up)
  → Yesterday's notes (if needed)
  → Archive (only on explicit search)
```

### Context Overflow Protocol

When context gets too large mid-session:

1. Write ACTIVE-CONTEXT.md with full current state
2. Write `HANDOFF.md` with: what was done, in progress, next steps, key decisions, gotchas
3. Start fresh session
4. New session reads HANDOFF.md → picks up seamlessly
5. Delete HANDOFF.md after successful handoff

---

## 13. Security Rules

### Never Store in Memory Files
- API keys, tokens, passwords, secrets
- Full credit card or bank account numbers
- Social security numbers or government IDs
- Private encryption keys
- Anything that would cause harm if the file were shared

### Safe Storage Pattern
```markdown
# ✅ Safe
- API keys: stored in 1Password vault "MyVault"
- Database password: see secrets manager, item "prod-db"

# ❌ Dangerous
- API key: sk-abc123def456...
- Password: MyS3cretP@ss!
```

### Privacy in Shared Contexts
- MEMORY.md contains personal context — **never load in group chats**
- Topic files may contain sensitive business data — check before sharing
- Daily notes may reference private conversations — don't share
- When in doubt, ask before exposing any memory content

---

## 14. Memory Patterns & Anti-Patterns

### ✅ Good Patterns

| Pattern | Why It Works |
|---------|-------------|
| Write immediately when told "remember" | Captures before you forget |
| One fact per line in MEMORY.md | Easy to find, update, delete |
| Date-prefix important entries | Enables chronological search |
| Link between files | Creates a knowledge web |
| Prune regularly | Keeps context fresh and cheap |

### ❌ Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Giant MEMORY.md (1000+ lines) | Expensive to load, hard to find things | Split into topic files |
| Never pruning ACTIVE-CONTEXT | Stale items cause confusion | Prune daily, archive weekly |
| Transcribing conversations verbatim | Wastes tokens, buries signal | Summarize: essence, not every word |
| Storing secrets in memory files | Security risk | Use secrets manager, reference by name |
| Reading all files every session | Token burn, slow startup | Progressive loading strategy |
| No daily notes | History is lost | Discipline: one file per day |
| Multiple sources of truth | Conflicts, confusion | Single source per fact type |

---

## 15. Migration Guide

### From No Memory System

```
Day 1: Create MEMORY.md with basic info about human + agent
Day 2: Start daily notes (memory/YYYY-MM-DD.md)
Day 3: Create ACTIVE-CONTEXT.md
Week 2: First weekly review — extract lessons to MEMORY.md
Month 2: Create first topic files for recurring subjects
Quarter 2: First archive cycle
```

### From MEMORY.md-Only System

```
1. Create memory/ directory
2. Start daily notes — stop putting raw events in MEMORY.md
3. Create ACTIVE-CONTEXT.md — move "current" stuff out of MEMORY.md
4. Review MEMORY.md — what's curated vs what's raw? Move raw to daily notes.
5. Identify topics that deserve their own files — split them out
```

### From External Tool (Database, API, Cloud)

```
1. Export key data to markdown files
2. Structure into the 5-layer architecture
3. Set up heartbeat maintenance schedule
4. Gradually reduce dependency on external tool
5. Benefits: zero cost, zero dependencies, works offline, no vendor lock-in
```

---

## 16. Natural Language Commands

- `/memory-status` — Show memory system health: file sizes, line counts, staleness, next maintenance
- `/memory-review` — Run weekly review: scan daily notes, extract to MEMORY.md, prune active context
- `/memory-search [query]` — Search across all memory layers for a topic
- `/memory-archive` — Run quarterly archive: summarize old daily notes, create archive file
- `/remember [fact]` — Immediately write a fact to MEMORY.md
- `/active-context` — Show current ACTIVE-CONTEXT.md contents
- `/daily-summary` — Generate summary of today's daily notes
- `/topic-create [name]` — Create a new topic file with template
- `/memory-prune` — Audit all memory files for staleness and bloat
- `/handoff` — Write HANDOFF.md for session transition
- `/memory-migrate` — Guided migration from current system to this architecture
- `/memory-debug` — Diagnose memory issues: missing files, conflicts, outdated info
