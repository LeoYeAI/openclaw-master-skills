# HEARTBEAT-CONFIG.md - Autonomous Operation Patterns

**Purpose:** Guide for setting up autonomous background work using heartbeat cron patterns and the proactive-tasks skill.

---

## Overview

Proactive agents work in two modes:

| Mode | Trigger | Use Case | Interruption |
|------|---------|----------|-------------|
| **Interactive (systemEvent)** | User request, prompt | Handle user queries, make decisions requiring context | ✅ Full context, interrupts main session |
| **Autonomous (isolated agentTurn)** | Heartbeat cron, scheduled | Background work, velocity checks, recurring tasks | ❌ No main session, background only |

### Key Principle
**Don't use `systemEvent` for background work.** When a cron job fires during main session, the prompt is ignored and work doesn't happen. Use `isolated agentTurn` instead.

---

## Heartbeat Pattern (Recommended)

Heartbeat is a periodic "check-in" that batches multiple background tasks together.

### Setup

1. **Create cron job** (fires every 30 minutes):
```bash
*/30 * * * * /path/to/send-heartbeat.sh
```

2. **send-heartbeat.sh** sends this message to your OpenClaw session:
```
💓 Heartbeat check: Read HEARTBEAT.md if it exists (workspace context). 
Follow it strictly. Do not infer or repeat old tasks from prior chats. 
If nothing needs attention, reply HEARTBEAT_OK.
```

3. **Create HEARTBEAT.md** in workspace root:
```markdown
## Proactive Tasks (Every heartbeat)

Check and work on next task from Phase 2 goal:

- [ ] Run: `python3 skills/proactive-tasks/scripts/task_manager.py next-task --goal goal_11e3159a`
- [ ] If task returned, spend 10-15 min working on it
- [ ] Update task status: mark-progress, log-time, or mark-blocked
- [ ] Message human if milestone reached or blocked

**Quiet pattern:** Only message for significant completions, blockers, or discoveries.
```

4. **Handle heartbeat in your main agent loop:**
```python
# In main agent session
if "Heartbeat check:" in message:
    read_heartbeat_md()
    # Process proactive tasks
    while has_time_budget():
        result = run_next_task()
        if not result:
            break
    
    if nothing_done:
        reply("HEARTBEAT_OK")
    else:
        reply(summary_of_work)
```

### Why Heartbeat Works Best

✅ **Batch checks together** - One message handles email + calendar + tasks + proactive work  
✅ **Natural breaks** - Every 30 min is a natural checkpoint  
✅ **Minimal overhead** - If nothing to do, just "HEARTBEAT_OK"  
✅ **Full context** - You're in your main session, can make decisions  
✅ **Human-friendly** - You still control when/how often you check  

---

## Autonomous Cron Patterns (Advanced)

For work that should never interrupt your main session:

### Pattern 1: Isolated agentTurn (Background Subprocess)

**When:** Weekly velocity reports, auto-cleanup, metadata updates  
**How:** Run agent in isolated subprocess, no main session context

```bash
# /etc/cron.d/proactive-velocity-weekly
0 9 * * MON /path/to/openclaw-runner \
  --mode isolated \
  --agent proactive-tasks-velocity \
  --task "Calculate weekly velocity and log to memory/velocity-YYYY-W##.md"
```

**Agent behavior:**
```python
# This runs in isolation, no main session interference
weekly_velocity = calculate_velocity(data_dir)
log_to_memory_file(f"velocity-{week}.md", weekly_velocity)
# No user context, no decision-making, just data processing
```

### Pattern 2: Scheduled systemEvent (Exact Time Critical)

**When:** Daily reminders at specific time ("9:00 AM sharp")  
**How:** Send systemEvent to main session at precise time

```bash
# /etc/cron.d/proactive-daily-reminder
0 9 * * * /path/to/send-system-event \
  --target "main:main:main" \
  --message "Daily reminder: Check important deadlines"
```

**When NOT to use:** Background cron work. systemEvent won't fire if agent is busy.

---

## Proactive Tasks Integration

### With Heartbeat (Recommended)

Add to your `HEARTBEAT.md`:

```markdown
## Proactive Tasks - Phase 2 Work

- [ ] `python3 skills/proactive-tasks/scripts/task_manager.py next-task --goal goal_11e3159a`
- [ ] Work on returned task for 10-15 minutes
- [ ] Log progress: `python3 skills/proactive-tasks/scripts/task_manager_phase2.py log-time <id> <mins>`
- [ ] If blocked, use mark-blocked command
- [ ] Message Imran on completion or blockers only
```

### With Isolated agentTurn (Velocity Checks)

```bash
# Every Monday 10 AM
0 10 * * MON /path/to/openclaw-runner \
  --mode isolated \
  --task "Calculate velocity for Phase 2 goals and log results"
```

**Isolated agent behavior:**
```python
# No user context, pure computation
data = load_tasks_json()
velocity = calculate_phase2_velocity(data)
log_to_memory(f"velocity-{week}.md", velocity)
print(json.dumps({"success": True, "velocity": velocity}))
```

---

## Task Manager Phase 2 Commands

### Interactive (During main session)

```bash
# Check next task
python3 scripts/task_manager.py next-task --goal <goal_id>

# Log progress
python3 scripts/task_manager_phase2.py mark-progress <task_id> <percent>

# Log time spent
python3 scripts/task_manager_phase2.py log-time <task_id> <minutes>

# Mark blocked
python3 scripts/task_manager_phase2.py mark-blocked <task_id> "reason"

# Health check
python3 scripts/task_manager_phase2.py health-check
```

### Autonomous (Heartbeat/Cron)

```bash
# Same commands work in heartbeat/cron context
# Just remember: use isolated agentTurn for heavy lifting
# Use heartbeat for interactive checking + decision-making
```

---

## Example: Phase 2 Autonomous Setup

**Goal:** Keep working on Phase 2 tasks autonomously with periodic human updates.

### Heartbeat Schedule
```markdown
# HEARTBEAT.md - Every 30 minutes

## Proactive Tasks - Phase 2 Work
- Run next-task for goal_11e3159a
- Work 10-15 min if task available
- Update progress with log-time
- Message Imran: "Completed [Task] in [time]"
- If blocked: Message reason + next steps needed
```

### Cron Additions
```bash
# Daily health check (isolated, no main session interference)
0 6 * * * /openclaw isolated -- \
  "python3 skills/proactive-tasks/scripts/task_manager_phase2.py health-check >> memory/daily-health.log 2>&1"

# Weekly velocity report (isolated)
0 9 * * MON /openclaw isolated -- \
  "python3 scripts/calculate_velocity.py goal_11e3159a"
```

---

## Anti-Patterns ❌

### Don't:
- Use `systemEvent` for heartbeat work (it won't fire when busy)
- Run long-running tasks during main session (blocks conversation)
- Interrupt user with every tiny update (only milestone messages)
- Create new goals/tasks during heartbeat (do in main session)
- Log to WAL from isolated cron (causes permission conflicts)

### Instead:
- Use heartbeat for periodic checks + decisions
- Use isolated agentTurn for computation + logging
- Message only on milestones (complete task, blocked, discovery)
- Create goals in main session, work on them in heartbeat
- Keep isolated work stateless (read inputs, write outputs, done)

---

## Testing Your Setup

1. **Verify heartbeat fires:**
   ```bash
   crontab -l  # Should show your heartbeat job
   ```

2. **Test heartbeat message locally:**
   ```bash
   # Simulate heartbeat
   echo "💓 Heartbeat check: Read HEARTBEAT.md..." | \
   openclaw message send --channel main
   ```

3. **Verify SESSION-STATE updates:**
   ```bash
   # After heartbeat runs
   cat SESSION-STATE.md  # Should show current task
   ```

4. **Check WAL logs:**
   ```bash
   # During work
   tail -f memory/WAL-*.log
   ```

---

## Benefits

- **Resilient:** Background work never interrupts main session
- **Productive:** Heartbeat batches checks, reducing message spam
- **Transparent:** WAL + SESSION-STATE show exactly what happened
- **Safe:** Isolated mode prevents permission/context conflicts
- **Scalable:** Works same for 1 goal or 100 concurrent goals

---

**Created for Proactive Tasks v1.2.0 - Phase 2 Production Ready Architecture**

See SKILL.md for full proactive-tasks documentation.
