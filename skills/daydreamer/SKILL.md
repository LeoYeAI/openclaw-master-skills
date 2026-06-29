---
name: daydreamer
description: Use this skill when the user says "daydream", "start daydreaming", "force a daydream", "run daydream cycles", or when a scheduled daydream is triggered. Also activates on first install to configure daydream frequency and cycles. Use when maintaining the Daydreams.MD memory log or writing new memories. This skill emulates the human act of daydreaming by randomly traversing accumulated memories and web searches to generate novel ideas.
version: 2.2.0
tools: Read, Write, Edit, Bash, WebSearch
env:
  DAYDREAM_WORKSPACE:
    description: Path to the workspace root where Daydreams.MD and related files are stored. Defaults to the current working directory if not set.
    required: false
---

# Daydreamer Skill

This skill emulates the human act of daydreaming. A Python conductor script (`daydream.py`, bundled with this skill) handles all mechanical work — cycle counting, random number generation, memory parsing, and state tracking. The agent handles only the creative work: semantic matching, hypothetical reasoning, web searches, analytical questioning, and final synthesis.

**Architecture: Script as conductor, agent as musician.**

Each cycle's prompt contains the **full accumulated context** from every previous cycle. The script reads the agent's response after each step, folds it into the running context, and generates the next prompt with everything included. The agent never has to reconstruct state or re-read old files.

---

## Files

The conductor script (`daydream.py`) is bundled in this skill's directory. All other files are created in the **current working directory** (workspace root):

| File | Purpose |
|------|---------|
| `Daydreams.MD` | Numbered list of daily memories. Each line is one memory entry. |
| `Daydreamlog.MD` | Chronological log of completed daydream sessions and their outcomes. |
| `daydreamer-config.json` | Persisted configuration (frequency, cycles per session, default daydream type). |
| `ideas/NNN-title.md` | Standalone idea files — one per daydream session. Auto-numbered. |
| `.daydream-session/` | Temporary directory for script↔agent JSON exchange during a session. Cleaned up after finalization. |

---

## Prerequisites

- **Python 3.8+** must be installed and available.

---

## Locating the Script

The conductor script `daydream.py` is in the same directory as this SKILL.md file. To find it at runtime, resolve the path relative to this skill's installation directory. For example:

```bash
# If the skill is installed at ~/.claude/skills/daydreamer/
python ~/.claude/skills/daydreamer/daydream.py status
```

Throughout this document, `$SCRIPT` refers to the full path to `daydream.py` in this skill's directory. When executing commands, replace `$SCRIPT` with the actual resolved path.

---

## Daydream Types

| Type | Name | Output |
|------|------|--------|
| `full` | Full Daydream | Open-ended — can produce an idea, recommendation, question, observation, warning, analogy, or anything else that emerges naturally. No constraints. |
| `idea` | Idea Generation | Focused on producing a novel, actionable idea — something that could be built, implemented, or pursued. |

The default type is set in `daydreamer-config.json` (`default_daydream_type`). The user can override it per-session.

The traversal mechanics (modes 1–4) are identical for both types. The difference is entirely in the **synthesis step** — the synthesis prompt includes type-specific instructions telling the agent what kind of output to produce.

---

## First Install

On first use, check whether `daydreamer-config.json` exists in the workspace root. If it does **not** exist, perform first-install setup:

1. Run the init command to create the files:
   ```bash
   python $SCRIPT init
   ```

2. **Ask about daydream type** (this is its own question — do not bundle with other settings):
   > "What kind of daydreams would you like as your default?
   >
   > - **Full** — open-ended. Each session can produce anything: an idea, a recommendation, a question, an observation, or something unexpected.
   > - **Idea** — focused. Each session is specifically aimed at generating a novel, actionable idea.
   >
   > You can always run the other kind on demand — this just sets what happens by default."

3. Wait for the user's answer. Update `daydreamer-config.json` with their choice:
   ```bash
   # For idea mode:
   # Set "default_daydream_type": "idea" in daydreamer-config.json
   # For full mode (already the default):
   # No change needed
   ```

4. **Ask about schedule and cycles:**
   > "How often should I daydream, and how many cycles per session?
   >
   > **Defaults:** Once per day, 10 cycles per session.
   > Reply with **default** to accept, or specify your preferences (e.g., 'twice a day, 15 cycles')."

5. Wait for the user's answer. Update `daydreamer-config.json` if they specified custom values.

6. Confirm setup to the user and explain:
   - Memories will be written here each day as you work.
   - A daydream session can be triggered at any time with `/daydream`.
   - Automated sessions will run on the configured schedule.
   - To run a different type than the default, say `/daydream idea` or `/daydream full`.

7. **Seed starter memories** (only when `Daydreams.MD` is empty or has fewer than 2 entries):

   ```bash
   python $SCRIPT seed-memories
   ```

   The script outputs a list of Claude Code session log files (JSONL) and how many memories are needed. Read each file and extract meaningful events — decisions made, things built, bugs fixed, requests fulfilled, insights gained. Skip heartbeat checks, empty status polls, and trivial exchanges.

   Write each event as a memory (aim for 50 total):

   ```bash
   python $SCRIPT add-memory "<memory text>"
   ```

   **What counts as a meaningful event:**
   - A feature or tool the user asked to build
   - A bug diagnosed or fixed
   - A design decision or trade-off made
   - A configuration or workflow set up
   - An insight or pattern observed during the session

   Read log files in reverse-chronological order (most recent first). Stop when you have 50 memories or have exhausted the logs. Tell the user how many memories were seeded.

---

## Slash Command: /daydream

Users can trigger a forced daydream session with `/daydream`. Parse arguments flexibly:

- `/daydream` → default type and cycles
- `/daydream 5` → 5 cycles, default type
- `/daydream idea` → default cycles, idea type
- `/daydream idea 5` → 5 cycles, idea type
- `/daydream full 20` → 20 cycles, full type

Recognize `full` and `idea` as type keywords. Any number is the cycle count.

When triggered via `/daydream`, always pass `--forced` to both `start` and `finalize`. This ensures the daily schedule is not affected.

---

## Writing Memories

Memory writing happens **once per calendar day** (tracked via `last_memory_write_date` in config).

### What to write

Write a memory entry for each **meaningful event** that occurred during the session. A memory is a single, self-contained observation, experience, decision, or insight.

### Memory format

Each memory should be **1–2 sentences** capturing WHO, WHAT (the action or request), and WHY (if clear). No timestamps, no verbose detail.

**Format:** `[WHO] [WHAT]. [WHY if clear.]`

**Good examples:**

- `User asked Claude to debug an off-by-one error in the pagination logic; root cause was 0-indexed vs 1-indexed page numbers.`
- `User and Claude designed the Daydreamer skill's conductor/musician architecture to separate randomness from creativity.`
- `Claude refactored the payment pipeline into smaller services at user's request to improve testability.`
- `User asked for database query optimization for large result sets; Claude suggested index-based pagination over OFFSET.`
- `Claude observed that the team prefers explicit error types over generic exceptions based on PR review patterns.`

**Aim for:** one clear subject (who), one clear verb (what they did or asked), and context that would help connect this memory to others.

### What NOT to write

Do **not** write entries for:
- Heartbeat checks that returned no work.
- Polling loops with no result.
- Empty status checks.
- Duplicate or trivially similar entries already in the list.

### How to write

Use the conductor script:

```bash
python $SCRIPT add-memory "User asked Claude to debug an off-by-one error in the pagination logic; root cause was 0-indexed vs 1-indexed page numbers."
```

The script handles numbering, dating, and appending automatically.

---

## Daydream Procedure

A daydream session is a conversation between the **conductor script** and the **agent**, one cycle at a time. Each cycle builds on the full accumulated context of every previous cycle.

### Flow Diagram

```
Agent                          Script
  |                              |
  |  start --cycles 10           |
  |----------------------------->|  Picks seed, rolls mode 1
  |  prompt_cycle_001.json       |  Writes prompt with seed context
  |<-----------------------------|
  |                              |
  |  [does creative work]        |
  |  response_cycle_001.json     |
  |----------------------------->|
  |                              |
  |  next-cycle                  |
  |----------------------------->|  Reads response 1
  |                              |  Folds into context: seed + cycle 1
  |                              |  Rolls mode 2
  |  prompt_cycle_002.json       |  Writes prompt with FULL context
  |<-----------------------------|
  |                              |
  |  [does creative work]        |
  |  response_cycle_002.json     |
  |----------------------------->|
  |                              |
  |  next-cycle                  |
  |----------------------------->|  Reads response 2
  |                              |  Context: seed + cycle 1 + cycle 2
  |          ...                 |  ...repeats...
  |                              |
  |  next-cycle (after last)     |
  |----------------------------->|  All cycles done
  |  prompt_synthesis.json       |  Writes synthesis with EVERYTHING
  |<-----------------------------|
  |                              |
  |  [writes synthesis]          |
  |  response_synthesis.json     |
  |----------------------------->|
  |                              |
  |  finalize                    |
  |----------------------------->|  Writes log, updates config, cleans up
  |<-----------------------------|
```

### Step 1 — Start the session

```bash
python $SCRIPT start --cycles 10
```

To specify a type:
```bash
python $SCRIPT start --cycles 10 --type idea
python $SCRIPT start --cycles 10 --type full
```

For forced daydreams (won't update schedule):
```bash
python $SCRIPT start --cycles 10 --forced
python $SCRIPT start --cycles 5 --type idea --forced
```

The script outputs JSON with the seed memory, cycle 1's mode, and file paths.

### Step 2 — Process cycle 1

Read `.daydream-session/prompt_cycle_001.json`. It contains:

- `mode` / `mode_name`: Which mode to execute (1–4)
- `accumulated_context`: The seed memory text
- `visited_memory_indices`: Which memories have been visited
- `all_memories`: The full memory bank
- For Mode 3: `target_result_rank` (which web search result to use)

Execute the mode (see mode descriptions below). Write a response file:

```json
{
  "selected_memory_index": 15,
  "text": "Brief description of what was found/thought and the memory content",
  "log_entry": "[Cycle 1 | Mode 2] Hypothetical: \"What if X?\" → memory #15"
}
```

### Step 3 — Advance to next cycle

```bash
python $SCRIPT next-cycle
```

The script:
1. Reads your response for the current cycle
2. Folds it into the accumulated context
3. Rolls a new random mode
4. Writes the next prompt with the **full accumulated context from all previous cycles**

Read the new prompt and repeat Step 2.

### Step 4 — Synthesis

After the last cycle, `next-cycle` writes `prompt_synthesis.json` instead of another cycle prompt. This contains the complete accumulated context from every cycle.

Review everything. Think creatively:

- What unexpected connections emerge between the memories visited?
- Does the combination suggest a solution, idea, pattern, or question?
- Consider the original context of each memory — why did it matter?

The synthesis prompt includes a `synthesis_instructions` field that tells you what kind of output to produce based on the daydream type:
- **Full:** Output is unconstrained — report whatever emerged honestly.
- **Idea:** Focus on producing a specific, actionable idea.

Follow those instructions when writing your synthesis.

Write `.daydream-session/response_synthesis.json`:

```json
{
  "synthesis": "2–5 sentences. Content depends on daydream type.",
  "status": "Complete"
}
```

Use `"Inconclusive"` if no clear output emerged — describe recurring themes instead.

### Step 5 — Finalize

```bash
python $SCRIPT finalize
```

For forced daydreams:
```bash
python $SCRIPT finalize --forced
```

This:
1. Writes the session report to `Daydreamlog.MD`
2. Writes a standalone idea file to `ideas/NNN-title.md` with the synthesis, memory trail, and cycle log
3. Updates `last_daydream_date` (unless forced)
4. Cleans up `.daydream-session/`

The finalize output includes an `idea_file` path pointing to the new idea file.

### Step 6 — Present results to the user

**This is the most important step.** After finalizing, tell the user what you concluded. Present the synthesis directly and conversationally — not as a log entry, but as an idea worth thinking about. Example:

```
Daydream complete (10 cycles).

Starting from a memory about [seed topic], I wandered through [brief path description]
and arrived at this:

[Synthesis — the actual idea, stated clearly in 2–4 sentences]

Full details saved to ideas/001-the-idea-slug.md and logged in Daydreamlog.MD.
```

If the session was inconclusive, say so honestly and describe what themes kept recurring — these may be worth exploring deliberately.

---

## Mode Descriptions

### Mode 1 — Semantic Association

- Review the `accumulated_context` from the prompt.
- Create a short semantic search query from the most salient concepts.
- Scan `all_memories` for the entry most conceptually similar.
- Prefer memories not in `visited_memory_indices`.
- Write response with the matched memory index, text, and log entry.

### Mode 2 — Hypothetical Exploration

- Generate a brief "what if" question inspired by the accumulated context.
- Think through the hypothetical, drawing on 2–3 thematically related memories from the memory bank.
- Select the memory most relevant to your conclusion.
- Write response with the hypothetical, reasoning, selected memory, and log entry.

### Mode 3 — Web Search Excursion

- Construct a focused web search query from the core themes of accumulated context.
- Perform the search using WebSearch.
- The prompt includes `target_result_rank` — use the search result at that position.
- Summarize the key insight from that result.
- Find the memory in the bank that most closely matches the web insight.
- Write response with the search query, insight, selected memory, and log entry.
- **If web search is unavailable:** Write a skip response. Note it in the log.

### Mode 4 — Analytical Question

- Formulate a direct, analytical question about the accumulated context. Not a "what if" (that's Mode 2) — instead, ask something that interrogates what's already there: "How does X actually work?", "Does X apply in this context?", "Why did X lead to Y?", "What's the mechanism behind X?"
- Think through the answer carefully, drawing on the accumulated context and related memories from the memory bank.
- The answer becomes part of the accumulated context — it deepens understanding rather than branching to new territory.
- Select the memory most relevant to the answer you arrived at.
- Write response with the question, your answer, the selected memory, and log entry formatted as: `[Cycle N | Mode 4] Question: "{question}" → memory #{index}`

---

## Forced Daydream

The user may trigger a daydream at any time with `/daydream` or "force a daydream". Optional cycle count and type:

```
/daydream              → default cycles and type
/daydream 5            → 5 cycles, default type
/daydream idea         → default cycles, idea type
/daydream idea 5       → 5 cycles, idea type
/daydream full 20      → 20 cycles, full type
```

Always pass `--forced` to both `start` and `finalize`.

---

## Scheduled Daydream

Check the schedule:

```bash
python $SCRIPT status
```

If "Daydream is DUE", run a full session (without `--forced`).

| Value | Meaning |
|-------|---------|
| `once_daily` | One session per calendar day |
| `twice_daily` | Two sessions per day |
| `every_N_hours` | Every N hours |
| `manual` | Only on explicit user request |

---

## Utility Commands

```bash
python $SCRIPT status                  # Check status
python $SCRIPT add-memory "Description" # Add a memory (WHO + WHAT + WHY format)
python $SCRIPT init                     # First-time setup
python $SCRIPT seed-memories            # Populate starter memories from session logs
```

---

## Edge Cases

- **Fewer than 2 memories:** The script returns an error. Tell the user more memories are needed.
- **Web search unavailable (Mode 3):** Write a skip response for the cycle.
- **Same memory selected twice:** Accept it — note the repetition in the log.
- **Gaps in memory numbering:** The script handles this automatically.
- **Python not installed:** Inform the user Python 3.8+ is required.
