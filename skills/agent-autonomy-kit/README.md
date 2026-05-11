# 🚀 Agent Autonomy Kit

[![GitHub](https://img.shields.io/badge/GitHub-reflectt-blue?logo=github)](https://github.com/reflectt/agent-autonomy-kit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Part of Team Reflectt](https://img.shields.io/badge/Team-Reflectt-purple)](https://github.com/reflectt)

**Stop waiting for prompts. Keep working.**

Most AI agents sit idle between human messages. This kit turns your agent into a self-directed worker that continuously makes progress on meaningful tasks.

---

## The Problem

Agents waste tokens by waiting:
- Heartbeats check "anything need attention?" and reply `HEARTBEAT_OK`
- Team members sit idle until spawned
- Work stops when the human stops prompting
- Subscription limits (tokens/hour, tokens/day) go unused

## The Solution

A proactive work system:
1. **Task Queue** — Always have work ready to pull
2. **Proactive Heartbeat** — Do work, don't just check for work
3. **Team Coordination** — Agents communicate and hand off tasks
4. **Continuous Operation** — Work until limits hit, then sleep

---

## Core Concepts

### 1. The Task Queue

Instead of waiting for prompts, agents pull from a persistent task queue.

**Location:** `tasks/QUEUE.md` (or GitHub Projects)

```markdown
# Task Queue

## Ready (can be picked up)
- [ ] Research competitor X pricing
- [ ] Write blog post draft on memory systems
- [ ] Review and improve procedure docs

## In Progress
- [ ] @kai: Building autonomy skill
- [ ] @rhythm: Updating process docs

## Blocked
- [ ] Deploy to production (needs: Ryan's approval)

## Done Today
- [x] Memory system shipped
- [x] Team spawning documented
```

**Rules:**
- Any agent can pick up a "Ready" task
- Mark yourself when you start: `@agentname: task`
- Move to Done when complete
- Add new tasks as you discover them

### 2. Proactive Heartbeat

Transform heartbeat from "check for alerts" to "do meaningful work."

**HEARTBEAT.md template:**

```markdown
# Heartbeat Routine

## 1. Check for urgent items (30 seconds)
- Unread messages from human?
- Blocked tasks needing escalation?
- System health issues?

If urgent: handle immediately.
If not: continue to work mode.

## 2. Work Mode (use remaining time)

Pull from task queue:
1. Check `tasks/QUEUE.md` for Ready items
2. Pick the highest-priority task you can do
3. Do meaningful work on it
4. Update status when done or blocked

## 3. Before finishing
- Log what you did to daily memory
- Update task queue
- If task incomplete, note progress for next heartbeat
```

### 3. Team Coordination

Agents communicate through Discord (or configured channel):
- Progress updates
- Handoffs ("@rhythm this is ready for review")
- Blockers ("stuck on X, need help")
- Discoveries ("found interesting thing, adding to queue")

### 4. Token Budget Awareness

Know your limits, use them wisely:

```markdown
## Token Strategy

**Daily budget:** ~X tokens (Claude Max)
**Heartbeat cost:** ~2-5k tokens per run
**Runs available:** ~Y per day

**Priority:**
1. Human requests (always first)
2. Urgent tasks (time-sensitive)
3. High-impact tasks (move needles)
4. Maintenance tasks (improvements)

When approaching limits:
- Wrap up current task
- Write detailed handoff notes
- Sleep until reset
```

---

## Installation

### Git Clone (Recommended)
```bash
# Clone into your skills folder
git clone https://github.com/reflectt/agent-autonomy-kit.git skills/agent-autonomy-kit
```

Then follow the setup steps below.

---

## Setup

### 1. Create the task queue

```bash
mkdir -p tasks
cat > tasks/QUEUE.md << 'EOF'
# Task Queue

## Ready
<!-- Add tasks here that any agent can pick up -->

## In Progress
<!-- Tasks currently being worked on -->

## Blocked
<!-- Tasks waiting on something -->

## Done Today
<!-- Completed tasks (clear daily) -->
EOF
```

### 2. Update HEARTBEAT.md

Replace passive checking with proactive work:

```markdown
# Heartbeat Routine

## Quick Checks (if urgent, handle immediately)
- [ ] Human messages waiting?
- [ ] Critical blockers?

## Work Mode
1. Read `tasks/QUEUE.md`
2. Pick highest-priority Ready task
3. Do the work
4. Update queue and daily memory
5. If time remains, pick another task

## End of Heartbeat
- Log progress to `memory/YYYY-MM-DD.md`
- Post update to team channel if significant
```

### 3. Configure continuous operation

Set heartbeat to run frequently:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "15m",  // More frequent = more work done
        target: "last",
        activeHours: { start: "06:00", end: "23:00" }
      }
    }
  }
}
```

### 4. Set up team channel (optional)

Configure Discord/Slack for team communication:

```json5
{
  channels: {
    discord: {
      // ... existing config ...
      groups: {
        "team-reflectt": {
          policy: "allow",
          channels: ["team-chat-channel-id"]
        }
      }
    }
  }
}
```

---

## Workflow Example

### Morning (6:00 AM)
1. Heartbeat fires
2. Agent checks: no urgent human messages
3. Agent reads task queue: "Research competitor X pricing"
4. Agent does the research, writes findings
5. Agent updates queue: moves task to Done, adds follow-up tasks discovered
6. Agent posts to team channel: "Competitor research done, see tasks/competitor-analysis.md"

### Throughout the Day
- Heartbeat fires every 15-30 minutes
- Each time: check for urgent → do work → update queue → log progress
- Human messages always get priority
- Team coordinates via channel

### Evening (11:00 PM)
- Last heartbeat of active hours
- Agent wraps up current task
- Writes detailed notes for tomorrow
- Goes dormant until morning

---

## Anti-Patterns

❌ **Passive heartbeats** — "HEARTBEAT_OK" wastes the opportunity to work
❌ **No task queue** — Agents don't know what to work on
❌ **Solo operation** — No coordination means duplicated effort
❌ **Ignoring limits** — Getting rate-limited mid-task loses context
❌ **No handoff notes** — Next session starts from scratch

---

## Metrics to Track

In `memory/metrics.md`:

```markdown
# Autonomy Metrics

## This Week
- Tasks completed: X
- Heartbeats used productively: Y%
- Token utilization: Z%
- Human interventions needed: N

## Patterns
- Most productive hours: morning
- Common blockers: waiting for human approval
- Tasks that work well async: research, writing, code review
```

---

## Related Kits

This kit works best with its companions:

### [Agent Memory Kit](https://github.com/reflectt/agent-memory-kit)
**Required foundation.** Provides the memory system this kit builds on:
- Task progress logged to daily memory (episodic)
- Procedures for common tasks (procedural)
- Learnings added to MEMORY.md (semantic)
- Failures tracked in feedback.md (feedback loops)

### [Agent Team Kit](https://github.com/reflectt/agent-team-kit)
**For multi-agent setups.** Coordinates autonomous agents working together:
- Role-based work distribution
- Self-service task queues
- Team communication patterns

---

## Origin

Created by Team Reflectt after realizing their Claude Max subscription tokens were going unused. The agent would complete a task and wait for the next prompt, leaving hours of potential work on the table.

Now the team works continuously, coordinating via Discord, pulling from a shared task queue, and only sleeping when the token limits are reached.

---

## Cron Jobs for Autonomy

Set up automated reporting and work triggers:

### Daily Progress Report (10 PM)
```bash
openclaw cron add \
  --name "Daily Progress Report" \
  --cron "0 22 * * *" \
  --tz "America/Vancouver" \
  --session isolated \
  --message "Generate daily progress report. Read tasks/QUEUE.md for completed tasks. Summarize: completed, in progress, blockers, tomorrow's plan."
```

### Morning Kickoff (7 AM)
```bash
openclaw cron add \
  --name "Morning Kickoff" \
  --cron "0 7 * * *" \
  --tz "America/Vancouver" \
  --session main \
  --system-event "Morning kickoff: Review task queue, pick top priorities, spawn team members for parallel work." \
  --wake now
```

### Overnight Work Check (3 AM)
```bash
openclaw cron add \
  --name "Overnight Work" \
  --cron "0 3 * * *" \
  --tz "America/Vancouver" \
  --session isolated \
  --message "Overnight work session. Pull tasks from queue that don't need human input. Do research, writing, or analysis. Log progress."
```

These run automatically — no human prompt needed.

---

*Idle agents are wasted agents. Keep working.*
