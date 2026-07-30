# Proactive Tasks v1.1.0 - ReadyforClawdHub

**Status:** Ready for ClawdHub submission  
**Version:** 1.1.0  
**Last updated:** 2026-02-12  

## Overview

Proactive Tasks is a production-ready autonomous task management system for AI agents. Unlike simple to-do lists, it enables:

- **Progress tracking** — 0-100% completion, not binary done/not-done
- **Time tracking** — Measure actual vs estimated time, build velocity
- **Velocity prediction** — "At 2.5 tasks/day, you'll finish in 6 days"
- **Recurring automation** — Daily standup, weekly reviews run themselves
- **Specific blockers** — Know exactly why a task is stuck
- **Autonomous heartbeat integration** — Check tasks, work on them, report back

## Key Features

### Task Management
- Create goals and break them into tasks
- Set priorities (low, medium, high)
- Track dependencies between tasks
- Update status (pending, in_progress, blocked, needs_input, completed)

### Progress & Time
- Track progress from 0-100%
- Log actual time spent vs estimates
- Auto-calculate variance and build velocity data
- Predict completion dates

### Recurring Tasks
- Daily, weekly, monthly automation
- Auto-create next occurrence on completion
- Estimate time for recurring work

### Intelligent Status
- Mark tasks as blocked with specific reasons
- Auto-unblock when ready
- Distinguish "stuck" from "waiting for input"

### Velocity Tracking
- Tasks completed per day
- Estimated completion time based on velocity
- Data for improving estimates

## Technical Details

**Storage:** JSON (tasks.json)  
**Scripts:** Python 3.7+  
**Dependencies:** None (standard library only)  

## Commands

### Core
```bash
# Create goal
python3 scripts/task_manager.py add-goal "Build voice assistant"

# Add task
python3 scripts/task_manager.py add-task "Build voice assistant" "Research models"

# Get next task
python3 scripts/task_manager.py next-task

# Complete task
python3 scripts/task_manager.py complete-task <task-id> --notes "..."

# List status
python3 scripts/task_manager.py status
```

### Phase 1 (Enhanced)
```bash
# Track progress
python3 scripts/task_manager_phase1.py mark-progress <task-id> 50

# Log time
python3 scripts/task_manager_phase1.py log-time <task-id> 45

# Block with reason
python3 scripts/task_manager_phase1.py mark-blocked <task-id> "Waiting on API key"

# Create recurring
python3 scripts/task_manager_phase1.py create-recurring <goal-id> "Weekly review" --recurring weekly

# Show velocity
python3 scripts/task_manager_phase1.py show-velocity <goal-id>
```

## Heartbeat Integration

Add to HEARTBEAT.md:

```markdown
## Proactive Tasks (Every heartbeat) 🚀

- [ ] Run `python3 skills/proactive-tasks/scripts/task_manager.py next-task`
- [ ] If task returned, work for 10-15 minutes
- [ ] Log progress and time: `mark-progress` + `log-time`
- [ ] If blocked, explain: `mark-blocked <id> "<reason>"`
- [ ] Message human with meaningful updates only
```

## Philosophy

**Don't wait to be told what to do.** Instead:

1. Check what needs work
2. Do it autonomously
3. Report progress periodically
4. Know when you're stuck and ask for help

This transforms agents from reactive tools into proactive partners.

## Comparison

| Feature | proactive-tasks | Excel | Notion | Jira |
|---------|-----------------|-------|--------|------|
| Goal/Task hierarchy | ✅ | ❌ | ✅ | ✅ |
| Progress 0-100% | ✅ | ✅ | ✅ | ✅ |
| Time tracking | ✅ | ✅ | ⚠️ | ✅ |
| Velocity prediction | ✅ | ❌ | ❌ | ✅ |
| Recurring tasks | ✅ | ❌ | ⚠️ | ✅ |
| Blocking reasons | ✅ | ❌ | ⚠️ | ✅ |
| **JSON (portable)** | ✅ | ❌ | ❌ | ❌ |
| **CLI (automation)** | ✅ | ❌ | ❌ | ⚠️ |
| **No dependencies** | ✅ | ❌ | ❌ | ❌ |

## Use Cases

**Autonomous agents:**
- Work on goals without waiting for prompts
- Report progress via heartbeat
- Handle dependencies and blockers gracefully
- Know exactly when work will be done

**Team coordination:**
- Team lead assigns goals
- Agents work autonomously
- Velocity predicts timeline
- Blockages surface quickly

**Long-term projects:**
- Break goals into achievable tasks
- Track progress week-by-week
- Improve estimates over time
- Celebrate milestones

## Architecture

Inspired by **Proactive Agent v3.1.0**:
- Clean separation of concerns (CLI, data, logic)
- JSON storage for portability
- Minimal dependencies
- Extensible command structure

**Phase 1** adds production features:
- Progress granularity
- Time metrics
- Velocity prediction
- Recurring automation

**Phase 2** (planned):
- WAL Protocol (context preservation)
- SESSION-STATE.md (active working memory)
- Self-healing (auto-fix failed tasks)
- Evolution guardrails (VFM/ADL)

## Getting Started

1. **Install:** Copy to ~/.openclaw/workspace/skills/proactive-tasks
2. **Run:** `python3 scripts/task_manager.py add-goal "My first goal"`
3. **Integrate:** Add to HEARTBEAT.md and start working

## Testing

```bash
# Test basic workflow
python3 scripts/task_manager.py add-goal "Test goal"
python3 scripts/task_manager.py add-task "Test goal" "Test task"
python3 scripts/task_manager.py next-task
python3 scripts/task_manager.py complete-task <id>

# Test Phase 1
python3 scripts/task_manager_phase1.py mark-progress <id> 50
python3 scripts/task_manager_phase1.py log-time <id> 30
python3 scripts/task_manager_phase1.py show-velocity <goal-id>
```

## Support

**Documentation:**
- SKILL.md — Full guide
- PHASE1-UPDATE.md — What's new
- CLI_REFERENCE.md — All commands

**Author:** Toki (toki@openclaw.ai)  
**License:** MIT  
**Repository:** github.com/ImrKhn03/proactive-tasks (upcoming)

---

## Version History

**v1.1.0** (2026-02-12)
- ✨ Progress tracking (0-100%)
- ✨ Time logging and variance
- ✨ Recurring tasks (daily/weekly/monthly)
- ✨ Blocking with reasons
- ✨ Velocity prediction
- 📝 Phase 1 documentation

**v1.0.0** (2026-02-05)
- ✨ Goal and task management
- ✨ Task dependencies
- ✨ Priority levels
- ✨ Status tracking
- ✨ Heartbeat integration

---

**Ready for production. Battle-tested with autonomous agents. Inspired by industry leaders.**
