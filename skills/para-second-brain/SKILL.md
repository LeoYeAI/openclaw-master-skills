---
name: para-second-brain
version: 2.0.1
description: Organize your agent's knowledge using PARA (Projects, Areas, Resources, Archive) — then make it ALL searchable. The symlink trick enables full semantic search across your entire knowledge base, not just MEMORY.md. Includes session transcript indexing and memory flush protocol. Your agent finally has a real second brain.
---

# PARA Second Brain

Your agent's memory just got a massive upgrade. Full semantic search across your entire knowledge base — not just MEMORY.md.

## What's New in v2.0

**Before v2.0:** `memory_search` only found content in MEMORY.md and daily logs. Your entire `notes/` folder was invisible to search. You had to manually know where to look.

**After v2.0:** One symlink command makes your entire PARA knowledge base searchable. Ask about anything in your notes — it finds it. Plus session transcripts and memory flush protocol to prevent context loss.

| Before | After |
|--------|-------|
| Search only MEMORY.md + daily logs | Search EVERYTHING |
| "I don't have that information" | Finds it instantly |
| Context compaction = lost information | Flush protocol saves critical context |
| Conversations forgotten | Session transcripts indexed |

## What This Does

Creates a "second brain" structure that separates:
- **Raw capture** (daily logs) from **curated knowledge** (MEMORY.md)
- **Active work** (projects) from **ongoing responsibilities** (areas)
- **Reference material** (resources) from **completed work** (archive)

## How This Differs from Other Second Brain Skills

There's another popular [second-brain skill](https://clawdhub.com/christinetyip/second-brain) powered by Ensue. Both are great — they solve different problems:

| | **PARA Second Brain** (this skill) | **Ensue Second Brain** |
|---|---|---|
| **Storage** | Local files in your workspace | Cloud API (Ensue) |
| **Cost** | Free, self-hosted | Requires Ensue API key |
| **Best for** | Work context, agent continuity, project tracking | Evergreen knowledge base, semantic queries |
| **Search** | Clawdbot's `memory_search` | Ensue's vector search |
| **Structure** | PARA (Projects/Areas/Resources/Archive) | Namespaces (concepts/toolbox/patterns) |
| **Use case** | "What did we decide yesterday?" | "How does recursion work?" |

**Use this skill if:** You want file-based memory that works offline, costs nothing, and tracks ongoing work context.

**Use Ensue's skill if:** You want a cloud-hosted knowledge base optimized for semantic "what do I know about X" queries.

**Use both if:** You want PARA for work context + Ensue for evergreen knowledge. They complement each other.

## Quick Setup

### 1. Create Directory Structure

```
workspace/
├── MEMORY.md              # Curated long-term memory
├── memory/
│   └── YYYY-MM-DD.md      # Daily raw logs
└── notes/
    ├── projects/          # Active work with end dates
    ├── areas/             # Ongoing life responsibilities  
    ├── resources/         # Reference material
    │   └── templates/     # Content templates
    └── archive/           # Completed/inactive items
```

Run this to scaffold:
```bash
mkdir -p memory notes/projects notes/areas notes/resources/templates notes/archive
```

### 2. Make Notes Searchable (The Symlink Trick)

By default, `memory_search` only indexes `MEMORY.md` and `memory/*.md`. Your entire `notes/` folder is invisible to semantic search!

**Fix this with one command:**
```bash
ln -s /path/to/your/workspace/notes /path/to/your/workspace/memory/notes
```

Example:
```bash
ln -s /Users/yourname/clawd/notes /Users/yourname/clawd/memory/notes
```

**What this does:** Creates a symbolic link so `memory/notes/` points to your actual `notes/` folder. Now Clawdbot's memory_search sees all your PARA notes.

**Verify it worked:**
```bash
ls -la memory/notes  # Should show: memory/notes -> /path/to/notes
```

**Test the search:**
Ask your agent something that's in your notes but NOT in MEMORY.md. If it finds it, the symlink is working.

**Why this matters:**
| Before | After |
|--------|-------|
| Search only finds MEMORY.md + daily logs | Search finds ALL your notes |
| Must manually know where to look | Semantic search across everything |
| "I don't have that information" | Finds connections you forgot existed |

### 3. Enable Session Transcript Indexing

Make your past conversations searchable too. Add this to your Clawdbot config:

```json
"memorySearch": {
  "sources": ["memory", "sessions"],
  "query": {
    "minScore": 0.3,
    "maxResults": 20
  }
}
```

**What this does:** Indexes your conversation transcripts alongside your notes. Now when you ask "what did we discuss about X last week?" — it can actually find it.

### 4. Initialize MEMORY.md

Create `MEMORY.md` in workspace root - this is your curated long-term memory:

```markdown
# MEMORY.md — Long-Term Memory

## About [Human's Name]
- Role/occupation
- Key goals and motivations
- Communication preferences
- Important relationships

## Active Context
- Current focus areas
- Ongoing projects (summaries, not details)
- Deadlines or time-sensitive items

## Preferences & Patterns
- Tools and workflows they prefer
- Decision-making style
- Pet peeves and likes

## Lessons Learned
- What worked
- What didn't
- Principles discovered

## Key Dates
- Birthdays, anniversaries
- Recurring events
- Important milestones
```

### 5. Add to AGENTS.md

Add these instructions to your AGENTS.md:

```markdown
## Memory

You wake up fresh each session. These files are your continuity:
- **Daily notes:** `memory/YYYY-MM-DD.md` — raw logs of what happened
- **Long-term:** `MEMORY.md` — curated memories (like human long-term memory)
- **Topic notes:** `notes/` — organized by PARA structure (all searchable via memory_search)

### Writing Rules
- If it has future value, write it down NOW
- Don't rely on "mental notes" — they don't survive restarts
- Text > Brain 📝

### PARA Structure
- **Projects** (`notes/projects/`) — Active work with end dates
- **Areas** (`notes/areas/`) — Ongoing responsibilities (health, finances, relationships)
- **Resources** (`notes/resources/`) — Reference material, how-tos, research
- **Archive** (`notes/archive/`) — Completed or inactive items

### Memory Flush Protocol
Monitor your context usage with `session_status`. Before compaction wipes your memory, flush important context to files:

| Context % | Action |
|-----------|--------|
| < 50% | Normal operation |
| 50-70% | Write key points after substantial exchanges |
| 70-85% | Active flushing — write everything important NOW |
| > 85% | Emergency flush — full summary before next response |
| After compaction | Note what context may have been lost |

**The rule:** Act on thresholds, not vibes. If it's important, write it down NOW.
```

## Memory Flush Protocol (Critical!)

Your agent's context window is finite. When it fills up, older context gets compacted or lost. **Don't lose important information.**

### How to Monitor
Run `session_status` periodically. Look for:
```
📚 Context: 36k/200k (18%) · 🧹 Compactions: 0
```

### Threshold-Based Actions

| Context % | What to Do |
|-----------|------------|
| **< 50%** | Normal operation. Write decisions as they happen. |
| **50-70%** | Increased vigilance. Write key points after each substantial exchange. |
| **70-85%** | Active flushing. Write everything important to daily notes NOW. |
| **> 85%** | Emergency flush. Stop and write full context summary before responding. |
| **After compaction** | Immediately note what context may have been lost. Check continuity. |

### What to Flush
1. **Decisions made** — what was decided and why
2. **Action items** — who's doing what
3. **Open threads** — anything unfinished → `notes/areas/open-loops.md`
4. **Working changes** — if you discussed changes to files, make them NOW

### Memory Flush Checklist
Before a long session ends or context gets high:
- [ ] Key decisions documented?
- [ ] Action items captured?
- [ ] New learnings written to appropriate files?
- [ ] Open loops noted for follow-up?
- [ ] Could future-me continue this conversation from notes alone?

## Knowledge Quality

**The core question:** "Will future-me thank me for this?"

### What to Save
- Concepts you actually understand (not half-learned ideas)
- Tools you've actually used (not just heard about)
- Patterns that worked (with concrete examples)
- Lessons learned from mistakes

### What NOT to Save
- Half-understood concepts (learn first, save after)
- Tools you haven't tried yet (bookmarks ≠ knowledge)
- Shallow entries without the WHY
- Duplicates of existing notes

### Quality Gates
Before saving any curated note:
1. Written for future self who forgot context?
2. Includes WHY, not just WHAT?
3. Has concrete examples or key insight?
4. Structured for retrieval (scannable)?

## Content Templates

Use these for structured, high-quality entries in `notes/resources/`:

### Concept Template
```markdown
# [CONCEPT NAME]

## What It Is
[One-line definition]

## Why It Matters
[What problem it solves, when you'd need it]

## How It Works
[Explanation with examples]

## Key Insight
[The "aha" moment — what makes this click]
```

### Tool Template
```markdown
# [TOOL NAME]

**Category:** [devtools | productivity | etc.]

## What It Does
[Brief description]

## Why I Use It
[What problem it solved for YOU]

## When to Reach For It
[Scenarios where this is the right choice]

## Gotchas
- [Things that tripped you up]
```

### Pattern Template
```markdown
# [PATTERN NAME]

## Problem
[What situation triggers this pattern]

## Solution
[The approach]

## Trade-offs
**Pros:** [Why this works]
**Cons:** [When NOT to use it]
```

## PARA Explained

PARA is a knowledge organization system created by [Tiago Forte](https://fortelabs.com/), author of *Building a Second Brain*. It organizes everything into four categories based on actionability:

### Projects
**What:** Work with a deadline or end state
**Examples:** "Launch website", "Plan trip to Japan", "Finish client proposal"
**File as:** `notes/projects/website-launch.md`

### Areas
**What:** Ongoing responsibilities with no end date
**Examples:** Health, finances, relationships, career development
**File as:** `notes/areas/health.md`, `notes/areas/dating.md`

### Resources
**What:** Reference material for future use
**Examples:** Research, tutorials, templates, interesting articles
**File as:** `notes/resources/tax-guide.md`, `notes/resources/api-docs.md`

### Archive
**What:** Inactive items from the other categories
**Examples:** Completed projects, outdated resources, paused areas
**Move to:** `notes/archive/` when done

## Daily Log Format

Create `memory/YYYY-MM-DD.md` for each day:

```markdown
# YYYY-MM-DD

## Key Events
- [What happened, decisions made]

## Learnings
- [What worked, what didn't]

## Open Threads
- [Carry-forward items]
```

## The Curation Workflow

### Daily (5 min)
- Log notable events to `memory/YYYY-MM-DD.md`
- File topic-specific notes to appropriate `notes/` folder

### Weekly (15 min)
- Review the week's daily logs
- Extract patterns and learnings to MEMORY.md
- Move completed projects to archive

### Monthly (30 min)
- Review MEMORY.md for outdated info
- Consolidate or archive old project notes
- Ensure areas reflect current priorities

## Decision Tree: Where Does This Go?

```
Is it about today specifically?
  → memory/YYYY-MM-DD.md

Is it a task with an end date?
  → notes/projects/

Is it an ongoing responsibility?
  → notes/areas/

Is it reference material for later?
  → notes/resources/

Is it done or no longer relevant?
  → notes/archive/

Is it a distilled lesson or preference?
  → MEMORY.md
```

## Why Two Memory Layers?

| Daily Logs | MEMORY.md |
|------------|-----------|
| Raw, timestamped | Curated, organized |
| Everything captured | Only what matters |
| Chronological | Topical |
| High volume | Condensed |
| "What happened" | "What I learned" |

Daily logs are your journal. MEMORY.md is your wisdom.

## Principles

1. **Quality over quantity** — Curated notes beat note hoarding
2. **Capture fast, curate deliberately** — Daily logs are loose; curated notes are high quality
3. **Text > brain** — If it matters, write it down
4. **Future-me test** — "Will future-me thank me for this?"
5. **One home per item** — Don't duplicate; link instead
6. **Include the WHY** — Facts without context are useless
7. **Flush before you lose** — Monitor context, write before compaction

---

*Pairs well with [memory-setup](https://clawdhub.com/jrbobbyhansen-pixel/memory-setup) for technical config and [proactive-agent](https://clawdhub.com/halthelobster/proactive-agent) for behavioral patterns.*
