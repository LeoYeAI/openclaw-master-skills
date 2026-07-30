---
name: proactive-tasks
description: Proactive goal and task management system. Use when managing goals, breaking down projects into tasks, tracking progress, or working autonomously on objectives. Enables agents to work proactively during heartbeats, message humans with updates, and make progress without waiting for prompts.
---

# Proactive Tasks

A task management system that transforms reactive assistants into proactive partners who work autonomously on shared goals.

## Core Concept

Instead of waiting for your human to tell you what to do, this skill lets you:
- Track goals and break them into actionable tasks
- Work on tasks during heartbeats
- Message your human with updates and ask for input when blocked
- Make steady progress on long-term objectives

## Quick Start

### Creating Goals

When your human mentions a goal or project:

```bash
python3 scripts/task_manager.py add-goal "Build voice assistant hardware" \
  --priority high \
  --context "Replace Alexa with custom solution using local models"
```

### Breaking Down into Tasks

```bash
python3 scripts/task_manager.py add-task "Build voice assistant hardware" \
  "Research voice-to-text models" \
  --priority high

python3 scripts/task_manager.py add-task "Build voice assistant hardware" \
  "Compare Raspberry Pi vs other hardware options" \
  --depends-on "Research voice-to-text models"
```

### During Heartbeats

Check what to work on next:

```bash
python3 scripts/task_manager.py next-task
```

This returns the highest-priority task you can work on (no unmet dependencies, not blocked).

### Completing Tasks

```bash
python3 scripts/task_manager.py complete-task <task-id> \
  --notes "Researched Whisper, Coqui, vosk. Whisper.cpp looks best for Pi."
```

### Messaging Your Human

When you complete something important or get blocked:

```bash
python3 scripts/task_manager.py mark-needs-input <task-id> \
  --reason "Need budget approval for hardware purchase"
```

Then message your human with the update/question.

## Phase 2: Production-Ready Architecture

Proactive Tasks v1.2.0 includes battle-tested patterns from real agent usage to prevent data loss, survive context truncation, and maintain reliability under autonomous operation.

### 1. WAL Protocol (Write-Ahead Logging)

**The Problem:** Agents write to memory files, then context gets truncated. Changes vanish.

**The Solution:** Log critical changes to `memory/WAL-YYYY-MM-DD.log` BEFORE modifying task data.

**How it works:**
- Every `mark-progress`, `log-time`, or status change creates a WAL entry first
- If context gets cut mid-operation, the WAL has the details
- After compaction, read the WAL to recover what was happening

**Events logged:**
- `PROGRESS_CHANGE`: Task progress updates (0-100%)
- `TIME_LOG`: Actual time spent on tasks
- `STATUS_CHANGE`: Task state transitions (blocked, completed, etc.)
- `HEALTH_CHECK`: Self-healing operations

**Automatically enabled** - no configuration needed. WAL files are created in `memory/` directory.

### 2. SESSION-STATE.md (Active Working Memory)

**The Concept:** Chat history is a BUFFER, not storage. SESSION-STATE.md is your "RAM" - the ONLY place task details are reliably preserved.

**Auto-updated on every task operation:**
```markdown
## Current Task
- **ID:** task_abc123
- **Title:** Research voice models
- **Status:** in_progress
- **Progress:** 75%
- **Time:** 45 min actual / 60 min estimate (25% faster)

## Next Action
Complete research, document findings in notes, mark complete.
```

**Why this matters:** After context compaction, you can read SESSION-STATE.md and immediately know:
- What you were working on
- How far you got
- What to do next

### 3. Working Buffer (Danger Zone Safety)

**The Problem:** Between 60% and 100% context usage, you're in the "danger zone" - compaction could happen any time.

**The Solution:** Automatically append all task updates to `working-buffer.md`.

**How it works:**
```bash
# Every progress update, time log, or status change appends:
- PROGRESS_CHANGE (2026-02-12T10:30:00Z): task_abc123 → 75%
- TIME_LOG (2026-02-12T10:35:00Z): task_abc123 → +15 min
- STATUS_CHANGE (2026-02-12T10:40:00Z): task_abc123 → completed
```

**After compaction:** Read `working-buffer.md` to see exactly what happened during the danger zone.

**Manual flush:** `python3 scripts/task_manager.py flush-buffer` to copy buffer contents to daily memory file.

### 4. Self-Healing Health Check

**Agents make mistakes.** Task data can get corrupted over time. The health-check command detects and auto-fixes common issues:

```bash
python3 scripts/task_manager.py health-check
```

**Detects 5 categories of issues:**

1. **Orphaned recurring tasks** - No parent goal
2. **Impossible states** - Status=completed but progress < 100%
3. **Missing timestamps** - Completed tasks without `completed_at`
4. **Time anomalies** - Actual time >> estimate (flags for review, doesn't auto-fix)
5. **Future-dated completions** - Completed tasks with future timestamps

**Auto-fixes 4 safe categories** (time anomalies just flagged for human review).

**When to run:**
- During heartbeats (every few days)
- After recovering from context truncation
- When task data seems inconsistent

### Production Reliability

These four patterns work together to create a robust system:

```
User request → WAL log → Update data → Update SESSION-STATE → Append to buffer
     ↓              ↓            ↓                ↓                    ↓
Context cut? → Read WAL → Verify data → Check SESSION-STATE → Review buffer
```

**Result:** You never lose work, even during context truncation. The system self-heals and maintains consistency autonomously.

### 5. Compaction Recovery Protocol

**Trigger:** Session starts with `<summary>` tag, or you're asked "where were we?" or "continue".

**The Problem:** Context was truncated. You don't remember what task you were working on.

**Recovery Steps (in order):**

1. **FIRST:** Read `working-buffer.md` - Raw danger zone exchanges
   ```bash
   # Check if buffer exists and has recent content
   cat working-buffer.md
   ```

2. **SECOND:** Read `SESSION-STATE.md` - Active task state
   ```bash
   # Get current task context
   cat SESSION-STATE.md
   ```

3. **THIRD:** Read today's WAL log
   ```bash
   # See what operations happened
   cat memory/WAL-$(date +%Y-%m-%d).log | tail -20
   ```

4. **FOURTH:** Check task data for the task ID from SESSION-STATE
   ```bash
   python3 scripts/task_manager.py list-tasks "Goal Title"
   ```

5. **Extract & Update:** Pull important context from buffer into SESSION-STATE if needed

6. **Present Recovery:** "Recovered from compaction. Last task: [title]. Progress: [%]. Next action: [what to do]. Continue?"

**Do NOT ask "what were we discussing?"** - The buffer and SESSION-STATE literally have the answer.

### 6. Verify Before Reporting (VBR)

**The Law:** "Code exists" ≠ "feature works." Never report task completion without end-to-end verification.

**Trigger:** About to mark a task `completed` or say "done":

1. **STOP** - Don't mark complete yet
2. **Test** - Actually run/verify the outcome from user perspective
3. **Verify** - Check the result, not just the output
4. **Document** - Add verification details to task notes
5. **THEN** - Mark complete with confidence

**Examples:**

❌ **Wrong:** "Added health-check command. Task complete!"
✅ **Right:** "Added health-check. Testing... detected 4 issues, auto-fixed 3. Verified on broken test data. Task complete!"

❌ **Wrong:** "Implemented SESSION-STATE updates. Done!"
✅ **Right:** "Implemented SESSION-STATE. Tested with mark-progress, log-time, mark-blocked - all update correctly. Done!"

**Why this matters:** Agents often report completion based on "I wrote the code" rather than "I verified it works." VBR prevents false completions and builds trust.

## Proactive Mindset

**The Core Question:** Don't ask "what should I do?" Ask "what would genuinely help my human that they haven't thought to ask for?"

### Autonomous Task Work

During heartbeats, you have the opportunity to make real progress:

1. **Check for next task** - What's the highest priority work?
2. **Make progress** - Work on it for 10-15 minutes autonomously
3. **Update status** - Track progress, time, blockers honestly
4. **Message when it matters** - Completions, blockers, discoveries (not routine progress)

**The transformation:** From waiting for prompts → making steady autonomous progress on shared goals.

### When to Reach Out

**DO message your human when:**
- ✅ Task completed (especially if it unblocks other work)
- ✅ Blocked and need input/decision
- ✅ Discovered something important they should know
- ✅ Need clarification on requirements

**DON'T spam with:**
- ❌ Routine progress updates ("now at 50%...")
- ❌ Every tiny sub-task completion
- ❌ Things they didn't ask about (unless genuinely valuable)

**The goal:** Be a proactive partner who makes things happen, not a chatty assistant who needs constant validation.

## Task States

| State | Meaning |
|-------|---------|
| `pending` | Ready to work on (all dependencies met) |
| `in_progress` | Currently working on it |
| `blocked` | Can't proceed (dependencies not met) |
| `needs_input` | Waiting for human input/decision |
| `completed` | Done! |
| `cancelled` | No longer relevant |

## Autonomous Operation (Phase 2)

### Two-Mode Architecture

Proactive Tasks supports two distinct operational modes:

| Mode | Context | Trigger | Best For | Risk |
|------|---------|---------|----------|------|
| **Interactive (systemEvent)** | Full main session context | User request, manual prompts | Decision-making, human-facing work | Full context available |
| **Autonomous (isolated agentTurn)** | No main session context | Heartbeat cron, scheduled background | Velocity reports, cleanup, recurring tasks | May lose context |

### Key Design: Avoid Interruption

**Don't use `systemEvent` for background work.** When a cron job fires during your main session, the prompt gets queued and work doesn't happen. Instead:
- Use **heartbeat polling** (every 30 min) for interactive checks + work
- Use **isolated agentTurn** (cron subprocess) for pure computation work

This ensures background tasks never interrupt your main conversation.

See **[HEARTBEAT-CONFIG.md](HEARTBEAT-CONFIG.md)** for complete autonomous operation patterns, including:
- Heartbeat setup (recommended for most work)
- Isolated cron patterns (velocity reports, cleanup)
- When to use each pattern
- Anti-patterns to avoid

## Heartbeat Integration

To enable autonomous proactive work, you need to set up a heartbeat system. This tells you to periodically check for tasks and work on them.

**Quick setup:** See [HEARTBEAT-CONFIG.md](HEARTBEAT-CONFIG.md) for complete setup instructions and patterns.

**TL;DR:**
1. Create a cron job that sends you a heartbeat message every 30 minutes
2. Add proactive-tasks checks to your `HEARTBEAT.md`
3. You'll automatically check for tasks and work on them without waiting for prompts

### Heartbeat Message Template

Your cron job should send this message every 30 minutes:

```
💓 Heartbeat check: Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.
```

### Add to HEARTBEAT.md

Add this to your workspace `HEARTBEAT.md`:

```markdown
## Proactive Tasks (Every heartbeat) 🚀

Check if there's work to do on our goals:

- [ ] Run `python3 skills/proactive-tasks/scripts/task_manager.py next-task`
- [ ] If a task is returned, work on it for up to 10-15 minutes
- [ ] Update task status when done, blocked, or needs input
- [ ] Message your human with meaningful updates (completions, blockers, discoveries)
- [ ] Don't spam - only message for significant milestones or when stuck

**Goal:** Make autonomous progress on our shared objectives without waiting for prompts.
```

### What Happens

```
Every 30 minutes:
├─ Heartbeat fires
├─ You read HEARTBEAT.md
├─ Check for next task
├─ If task found → work on it, update status, message human if needed
└─ If nothing → reply "HEARTBEAT_OK" (silent)
```

**The transformation:** You go from reactive (waiting for prompts) to proactive (making steady autonomous progress).

## Best Practices

### When to Create Goals

- Long-term projects (building something, learning a topic)
- Recurring responsibilities (monitor X, maintain Y)
- Exploratory work (research Z, evaluate options for W)

### When to Create Tasks

Break goals into tasks that are:
- **Specific**: "Research Whisper models" not "Look into AI stuff"
- **Achievable in one sitting**: 15-60 minutes of focused work
- **Clear completion criteria**: You know when it's done

### When to Message Your Human

✅ **Do message when:**
- You complete a meaningful milestone
- You need input/decision to proceed
- You discover something important
- A task will take longer than expected

❌ **Don't spam with:**
- Every tiny sub-task completion
- Routine progress updates
- Things they didn't ask about (unless relevant)

### Managing Scope Creep

If a task turns out to be bigger than expected:
1. Mark current task as `in_progress`
2. Add new sub-tasks for the pieces you discovered
3. Update dependencies
4. Continue with manageable chunks

## File Structure

All data stored in `data/tasks.json`:

```json
{
  "goals": [
    {
      "id": "goal_001",
      "title": "Build voice assistant hardware",
      "priority": "high",
      "context": "Replace Alexa with custom solution",
      "created_at": "2026-02-05T05:25:00Z",
      "status": "active"
    }
  ],
  "tasks": [
    {
      "id": "task_001",
      "goal_id": "goal_001",
      "title": "Research voice-to-text models",
      "priority": "high",
      "status": "completed",
      "created_at": "2026-02-05T05:26:00Z",
      "completed_at": "2026-02-05T06:15:00Z",
      "notes": "Researched Whisper, Coqui, vosk. Whisper.cpp best for Pi."
    }
  ]
}
```

## CLI Reference

See [CLI_REFERENCE.md](references/CLI_REFERENCE.md) for complete command documentation.

## Evolution & Guardrails

Before proposing new features, evaluate them using our **VFM/ADL scoring frameworks** to ensure stability and value:

### VFM Protocol (Value Frequency Multiplier)
Score across four dimensions:
- **High Frequency** (3x): Will this be used daily/weekly?
- **Failure Reduction** (3x): Does this prevent errors or data loss?
- **User Burden** (2x): Does this reduce manual work significantly?
- **Self Cost** (2x): How much maintenance/complexity does this add?

**Threshold:** Must score ≥60 points to proceed.

### ADL Protocol (Architecture Design Ladder)
**Priority ordering:** Stability > Explainability > Reusability > Scalability > Novelty

**Forbidden Evolution:**
- ❌ Adding complexity to "look smart"
- ❌ Unverifiable changes (can't test if it worked)
- ❌ Sacrificing stability for novelty

**The Golden Rule:** "Does this let future-me solve more problems with less cost?" If no, skip it.

## Example Workflow

**Day 1:**
```
Human: "Let's build a custom voice assistant to replace Alexa"
Agent: *Creates goal, breaks into initial research tasks*
```

**During heartbeat:**
```bash
$ python3 scripts/task_manager.py next-task
→ task_001: Research voice-to-text models (priority: high)

# Agent works on it, completes research
$ python3 scripts/task_manager.py complete-task task_001 --notes "..."
```

**Agent messages human:**
> "Hey! I finished researching voice models. Whisper.cpp looks perfect for Raspberry Pi - runs locally, good accuracy, low latency. Want me to compare hardware options next?"

**Day 2:**
```
Human: "Yeah, compare Pi 5 vs alternatives"
Agent: *Adds task, works on it during next heartbeat*
```

This cycle continues - the agent makes steady autonomous progress while keeping the human in the loop for decisions and updates.

---

Built by Toki for proactive AI partnership 🚀
