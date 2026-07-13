# HEARTBEAT.md - Token-Optimized Template

## 🔥 Model Override (CRITICAL!)
**This heartbeat should ALWAYS run on Quick tier** — never Standard/Deep.

Set model override for this session:
```
session_status model=openrouter/stepfun/step-3.5-flash:free
```

Or in OpenClaw config, set heartbeat sessions to use Quick tier by default.

**Rationale:** Heartbeat checks are routine monitoring — don't waste expensive model tokens!

## Overview
This heartbeat is optimized to minimize token usage while maintaining useful monitoring.

## Check Schedule
Run `heartbeat_optimizer.py plan` to determine which checks should run now.

## Checks to Perform

### Email Check (every 60 minutes)
- Only check if `heartbeat_optimizer.py check email` returns `should_check: true`
- Look for URGENT messages only (not all unread)
- Record check: `heartbeat_optimizer.py record email`

### Calendar Check (every 2 hours)
- Only check if `heartbeat_optimizer.py check calendar` returns `should_check: true`
- Only events in next 24 hours
- Record check: `heartbeat_optimizer.py record calendar`

### Weather Check (every 4 hours)
- Only check if `heartbeat_optimizer.py check weather` returns `should_check: true`
- Only if significant change (>10°F or precipitation)
- Record check: `heartbeat_optimizer.py record weather`

### Monitoring Check (every 30 minutes)
- Only check if `heartbeat_optimizer.py check monitoring` returns `should_check: true`
- Server health, disk space, critical alerts only
- Record check: `heartbeat_optimizer.py record monitoring`

## Quiet Hours
Between 23:00-08:00, skip ALL checks unless explicitly urgent.

## Token Budget
- Target: <5K tokens per heartbeat
- If nothing needs attention: reply `HEARTBEAT_OK` (saves tokens)
- Batch multiple alerts into single message

## Response Protocol

**If nothing needs attention:**
```
HEARTBEAT_OK
```

**If something needs attention:**
```
🔔 [Type] Alert
[Brief description]
[Action item if applicable]
```

**Never:**
- Narrate what you checked ("I checked email, calendar...")
- Explain why you didn't find anything
- Apologize for lack of updates
- Include timestamps unless relevant

## Customization

To adjust check intervals:
```bash
# Email every 2 hours instead of 1
heartbeat_optimizer.py interval email 7200

# Calendar every 4 hours
heartbeat_optimizer.py interval calendar 14400
```

To force a check:
```bash
heartbeat_optimizer.py check email --force
```

## Example Good Heartbeats

**Nothing to report:**
```
HEARTBEAT_OK
```

**Single alert:**
```
🔔 Calendar
Meeting with Asif in 45 minutes (10:00 AM)
```

**Multiple alerts (batched):**
```
🔔 Email: 2 urgent messages from clients
🔔 Monitoring: Disk space on server-3 at 85%
🔔 Calendar: Team standup in 30 min
```

## Integration with token_tracker.py

Before every heartbeat, check budget:
```python
result = token_tracker.py check
if result["status"] == "exceeded":
    # Skip all non-critical checks
    # Or switch to cheaper model for this heartbeat
```
