---
name: memory-fortress
description: Complete memory management system for OpenClaw agents. Combines compaction-aware saving, a formalized boot sequence, domain-based organization, memory scoring, and bloat prevention. Use when: a session starts, an important decision is made, a task arrives, compaction is approaching, memory needs reorganization, or a "do you remember" question arises.
---

# Memory Fortress 🏰

A unified memory management system that prevents agents from forgetting what they did yesterday.

**Built from five proven patterns:**
- **Compaction-aware saving** → disk is truth, write before you lose it
- **Boot sequence + state files** → Dory-proof pattern
- **Domain organization** → bloat prevention, ≤10KB MEMORY.md
- **Memory types + priority** → contradiction detection, scoring
- **Promote / demote** → natural memory decay over time

---

## Mental model

```
┌─────────────────────────────────────────────────────┐
│                   MEMORY FORTRESS                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🔴 SESSION RAM                                     │
│  Short-term, lost on compaction                     │
│  → Write important things to files IMMEDIATELY      │
│                                                     │
│  🟡 STATE FILES (state/)                            │
│  Active task, blockers, recent decisions            │
│  → Load at the start of every session               │
│                                                     │
│  🟢 DAILY LOG (memory/YYYY-MM-DD.md)                │
│  Raw append-only journal                            │
│  → Load today + yesterday at boot                   │
│                                                     │
│  🔵 MEMORY.md (≤10KB!)                              │
│  Curated, durable knowledge — facts, decisions      │
│  → Main session only; use search + get              │
│                                                     │
│  ⚪ DOMAIN FILES (memory/domains/*.md)              │
│  Topic-specific details                             │
│  → On-demand via memory_search                      │
│                                                     │
│  📦 ARCHIVE (memory/archive/)                       │
│  Daily logs older than 14 days                      │
│  → Rarely needed                                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 1. Boot sequence — run at the start of every session

**Order matters. Agents execute this automatically.**

```
1. state/HOLD.md        — what is BLOCKED? (do NOT do these!)
2. state/ACTIVE.md      — is there an active task?
3. state/DECISIONS.md   — recent decisions (last 48h)
4. memory/YYYY-MM-DD.md — today's + yesterday's log
5. MEMORY.md            — long-term knowledge (main session ONLY!)
```

Post-boot status line:
```
🏰 Boot: ACTIVE=[task|none] | HOLD=[n] | DECISIONS=[n last 48h]
```

### What is NOT a boot step
- Domain files → only via `memory_search`, on-demand
- Archive → rarely, on explicit request
- Other agents' memory → NEVER

---

## 2. Dory-proof pattern — when a task arrives

When the user gives you a task:

1. **IMMEDIATELY** write their **EXACT words** → `state/ACTIVE.md`
2. Then interpret what it means
3. Then do the work
4. Done → mark complete, remove from ACTIVE

**Why:** Paraphrasing causes drift. Exact words preserve intent even after context flush.

### state/ACTIVE.md format
```markdown
## Active task
**User said:** "[exact quote]"
**Interpretation:** [what you think it means]
**Status:**
- [ ] Step 1
- [ ] Step 2
**Updated:** YYYY-MM-DD HH:MM
```

### state/HOLD.md format
```markdown
[YYYY-MM-DD HH:MM | session] Item — reason for blocking
```
⚠️ **Every agent checks this at boot — FIRST step!** If something is on HOLD, do NOT proceed.

### state/DECISIONS.md format
```markdown
[YYYY-MM-DD HH:MM | session] Decision description — context/rationale
```
Archive after 48 hours → daily log or MEMORY.md (if durable).

---

## 3. Compaction-aware saving — "Write Before Lose"

Session RAM is lost on compaction. **Save before that happens.**

### When to write to files immediately (don't wait for compaction):

| Event | Where to write |
|-------|---------------|
| Decision made | `state/DECISIONS.md` + daily log |
| User preference discovered | `MEMORY.md` (if durable) or daily log |
| Task received | `state/ACTIVE.md` (Dory-proof) |
| Something is blocked | `state/HOLD.md` |
| Error occurred + lesson learned | Daily log + `MEMORY.md` if generalizable |
| Important fact discovered | Daily log, promote if durable |
| Work completed | `state/ACTIVE.md` update + log entry |

### Rule: if it matters → write to file IMMEDIATELY. Don't defer to end of session.

---

## 4. Memory scoring — what goes into MEMORY.md?

Not every memory deserves a spot in MEMORY.md. Score it on 4 axes (0–3):

| Axis | 0 | 1 | 2 | 3 |
|------|---|---|---|---|
| **Durability** | Invalid tomorrow | Valid for weeks | Valid for months | Valid for years+ |
| **Reuse** | One-time | Occasional | Frequent | Every session |
| **Impact** | Trivial | Good to know | Changes output | Changes decisions |
| **Uniqueness** | Obvious | Slightly useful | Hard to re-derive | Impossible without it |

**Goes into MEMORY.md if:**
- Sum ≥ 8, OR
- Any axis = 3 AND sum ≥ 6

**Everything else** → daily log (and from there to a domain file if it fits thematically).

---

## 5. Domain organization — keeping MEMORY.md ≤10KB

MEMORY.md **must stay ≤10KB**. If it grows larger:

### Split into domain files

```
memory/
├── domains/
│   ├── projects.md        — active project details
│   ├── infrastructure.md  — servers, deploys, networking
│   ├── people.md          — contacts, preferences
│   ├── skills-tools.md    — tools, skills, configs
│   └── lessons.md         — lessons learned, anti-patterns
├── archive/
│   └── YYYY-MM/           — daily logs older than 14 days
└── YYYY-MM-DD.md          — daily logs
```

### Rules:
- **MEMORY.md** = summaries, references, most important facts
- **domains/*.md** = details, searched via `memory_search`
- **archive/** = old logs, rarely needed

### MEMORY.md section format (with domain references):
```markdown
## Projects
→ Details: memory/domains/projects.md

- **Project Alpha** — ESP32 firmware, active development
- **ERP Deploy** — ✅ deployed, 12 containers
- **Pipeline v2** — planning in progress
```

### Maintenance (weekly or during heartbeat):
1. Check MEMORY.md size — if >10KB, split
2. Remove or archive stale entries
3. Find duplicates (daily log vs MEMORY.md)
4. Update domain files from daily logs

---

## 6. Memory types and priority

Every saved memory gets a type and priority.

### Types (ID prefixes)
| Prefix | Type | Example |
|--------|------|---------|
| `DEC` | Decision | "We use PostgreSQL in production" |
| `PREF` | Preference | "English, direct tone" |
| `FACT` | Durable fact | "Voice PE = ESP32-S3, 16MB flash" |
| `POLICY` | Rule/invariant | "MEMORY.md never >10KB" |
| `LESSON` | Lesson learned | "VLA unsafe on 4KB stack" |
| `ERR` | Known error | "OIDC trailing slash incompatible" |

### Priority (1–10)
| Level | Meaning | Example |
|-------|---------|---------|
| 1–3 | Low, good to know | A tool version number |
| 4–6 | Medium, useful | Project status |
| 7–8 | High, important | Architectural decision |
| 9–10 | Critical, never forget | Security rule, user preference |

---

## 7. Promote / Demote — memory lifecycle

### Promote (strengthen)
A memory is promoted when:
- It becomes relevant again (found and used in search)
- The user references it
- It grounds a decision

**Promote action:** raise priority, move from domain file → MEMORY.md summary

### Demote (decay)
A memory weakens when:
- Not referenced in >30 days
- Outdated (project closed, tool replaced)
- Contradicted by a newer memory

**Demote action:** MEMORY.md → domain file, or domain → archive

### Contradiction handling
When two memories contradict each other:
1. The **newer** one takes priority (unless explicitly overridden)
2. Mark the old one `[STALE]`
3. Daily log note: why it changed

---

## 8. Search strategy

### Core rule: always `memory_search` → `memory_get`

1. `memory_search(query)` — max 6 results
2. Pick the best 1–2 matches
3. `memory_get(path, from, lines)` — exact line range
4. Inject only the **minimum necessary** text into context

### Search order:
1. `state/` files (loaded at boot, no search needed)
2. `MEMORY.md` (loaded at boot in main session)
3. `memory/domains/*.md` (memory_search)
4. `memory/YYYY-MM-DD.md` (memory_search)
5. `memory/archive/` (last resort)

### Don't do this:
- ❌ Read entire files "just in case"
- ❌ Load all domain files at boot
- ❌ Answer questions about the past without searching first

---

## 9. Multi-agent rules

When multiple agents share a workspace, memory stays isolated.

| Rule | Details |
|------|---------|
| **Own workspace** | Every agent writes to its own workspace |
| **No cross-read** | Don't read another agent's MEMORY.md |
| **Communication** | Use `sessions_send`, not memory files |
| **Shared state** | Only explicitly shared folders (e.g. `shared/roundtable/`) |
| **Private context** | DM-originated info stays private, not placed in shared locations |

---

## 10. Anti-patterns — don't do this

| ❌ Anti-pattern | ✅ Instead |
|----------------|-----------|
| "I'll mentally remember this" | Write to file IMMEDIATELY |
| Paste chat transcript into MEMORY.md | Daily log + summary |
| MEMORY.md >10KB | Split into domain files |
| Answer questions about the past without searching | `memory_search` → `memory_get` |
| 10 tasks in ACTIVE.md | 1 active task, rest in STAGING or project files |
| Paraphrase in ACTIVE.md | User's EXACT words |
| Store a secret key | Store only that it *exists*, not its value |
| Never archive daily logs | 14+ days old → `memory/archive/YYYY-MM/` |
| Every memory priority 10 | Score it! Most things are 4–6 |
| Skip HOLD.md at boot | It's the FIRST step at every boot |

---

## 11. .learnings/ — error and lesson logging

The `memory/.learnings/` folder provides structured logging for continuous agent improvement.

### Detection triggers — watch for these

| User says | Action |
|-----------|--------|
| "No, that's wrong..." / "Actually..." | LEARNINGS.md, category: `correction` |
| "Can you also..." / "I wish you could..." | FEATURE_REQUESTS.md |
| "That's outdated..." / "It changed since..." | LEARNINGS.md, category: `knowledge_gap` |
| Command exits with non-zero code | ERRORS.md |
| Found a better approach | LEARNINGS.md, category: `best_practice` |

### When to write here (direct append, not memory_search):

| Event | File | Category |
|-------|------|----------|
| Tool/command fails | `ERRORS.md` | — |
| User corrects you | `LEARNINGS.md` | `correction` |
| Something didn't work, you fixed it | `LEARNINGS.md` | `best_practice` |
| Missing capability requested | `FEATURE_REQUESTS.md` | — |
| Knowledge was outdated | `LEARNINGS.md` | `knowledge_gap` |

### Structured ID format

Every entry gets a unique ID:

```
TYPE-YYYYMMDD-XXX
```
- TYPE: `LRN` (learning), `ERR` (error), `FEAT` (feature request)
- YYYYMMDD: current date
- XXX: sequential number or 3 random chars (`001`, `A7B`)

**Entry header:**
```markdown
## [LRN-20260322-001] best_practice

**Logged**: 2026-03-22T14:30:00Z
**Priority**: medium        ← low | medium | high | critical
**Status**: pending         ← pending | resolved | promoted | wont_fix
**Area**: infra             ← frontend | backend | infra | config | docs

### Summary
One-line description

### Details
What happened, what was wrong, what's correct

### Suggested Action
Concrete next step

### Metadata
- Source: conversation | error | user_feedback
- Pattern-Key: harden.api_retry (optional, for recurring pattern tracking)
- Recurrence-Count: 1
- See Also: ERR-20260310-003 (if related)
```

**When resolved:**
```markdown
### Resolution
- **Resolved**: 2026-03-22T16:00:00Z
- **Notes**: What was done
- **Status**: resolved
```

### Quick review commands

```bash
# Count pending items
grep -h "Status\*\*: pending" memory/.learnings/*.md | wc -l

# High-priority open errors
grep -B5 "Priority\*\*: high" memory/.learnings/ERRORS.md | grep "^## \["

# Search by topic
grep -n "keyword" memory/.learnings/LEARNINGS.md
```

### Promotion logic (after 3 occurrences):
- Behavioral pattern → agent personality file (e.g. `SOUL.md`)
- Workflow improvement → operational manual (e.g. `AGENTS.md`)
- Tool gotcha → tool config file (e.g. `TOOLS.md`)
- Generally useful → `MEMORY.md` (with scoring)

### Pattern-Key tracking:
If the same error/pattern recurs: add `See Also: ERR-YYYYMMDD-XXX` link + increment `Recurrence-Count`.
3+ occurrences in 2+ different contexts → **mandatory promotion**.

### Skill extraction — when to turn a learning into a skill?

A learning qualifies for skill extraction when ANY of these apply:

| Criterion | Description |
|-----------|-------------|
| **Recurring** | 2+ `See Also` links to similar entries |
| **Verified** | Status is `resolved`, solution works |
| **Non-obvious** | Required actual debugging/investigation |
| **Broadly applicable** | Not project-specific; useful elsewhere |
| **User-flagged** | User says "save this as a skill" or similar |

**Quality gates (check before extraction):**
- [ ] Solution is tested and working
- [ ] Description is clear without original context
- [ ] No hardcoded values (paths, API keys, names)
- [ ] Lowercase, hyphenated filename (e.g. `api-retry-pattern`)
- [ ] Single SKILL.md file — no README.md alongside

**Extraction steps:**
1. Create `skills/<skill-name>/SKILL.md` from the learning
2. Proper frontmatter: `name` + single-line `description`
3. Update original entry: `Status: promoted_to_skill`
4. Publish if broadly useful

---

## 12. Maintenance schedule

| Frequency | Task |
|-----------|------|
| **Every session** | Execute boot sequence |
| **Every task** | Dory-proof pattern (ACTIVE.md) |
| **On important events** | Immediate file write |
| **Daily** | Review daily log, clean state files |
| **Weekly** | MEMORY.md size check, update domain files |
| **Biweekly** | Archive old daily logs |
| **Monthly** | Demote stale memories, resolve contradictions |
| **On error** | `.learnings/ERRORS.md` entry immediately |
| **On correction** | `.learnings/LEARNINGS.md` correction entry immediately |

---

## Installation

### 1. Create the state folder
```bash
mkdir -p ~/.openclaw/workspace/state
touch ~/.openclaw/workspace/state/ACTIVE.md
touch ~/.openclaw/workspace/state/HOLD.md
touch ~/.openclaw/workspace/state/DECISIONS.md
```

### 2. Create the memory folder structure
```bash
mkdir -p ~/.openclaw/workspace/memory/domains
mkdir -p ~/.openclaw/workspace/memory/archive
mkdir -p ~/.openclaw/workspace/memory/.learnings
```

### 3. Add to your agent's operational manual
Add the boot sequence to your `AGENTS.md` (or equivalent config file):
- Load `state/HOLD.md`, `state/ACTIVE.md`, `state/DECISIONS.md` first
- Load `memory/YYYY-MM-DD.md` (today + yesterday)
- Load `MEMORY.md` only in the main/direct session

### 4. Add the "Write Before Lose" rule
Ensure your agent config instructs writing to files immediately on: decisions, preferences, task receipt, blockers, errors.

---

*"Memory is what separates a tool from an ally."*
