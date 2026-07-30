# Event Monitoring Guide

## Overview

OpenCode streams real-time events via Server-Sent Events (SSE). Use for:
- Long-running tasks (30+ seconds)
- Progress updates
- Status changes
- File modifications

## Basic Monitoring

Use the monitor script:
```bash
bash ./scripts/monitor_session.sh
```

**What you'll see**:
```
Monitoring session: ses_abc123
Press Ctrl+C to stop
----------------------------------------
⟳ Processing...
Creating React component...
Adding TypeScript types...
✓ Task completed
📊 Tokens: 1500, Cost: $0.025
```

**When it stops**:
- Session becomes "idle"
- Task completes
- You press Ctrl+C

## How It Works

Monitor script:
1. Loads current session from state
2. Connects to event stream
3. Filters events for your session
4. Displays relevant updates
5. Exits when task completes

## Event Types Shown

### Text Updates
```
⟳ Processing...
[streaming text as it's generated]
```

### Status Changes
```
⟳ Processing...  # busy
✓ Task completed  # idle
```

### Completion Stats
```
📊 Tokens: 1500, Cost: $0.025
```

## Usage Patterns

### Pattern 1: Monitor in Background
```bash
# Start task
bash ./scripts/send_message.sh "Complex task" &

# Monitor progress
bash ./scripts/monitor_session.sh
```

### Pattern 2: Check Status Periodically
```bash
# Send task
bash ./scripts/send_message.sh "Build application"

# In another terminal or later
bash ./scripts/check_status.sh
# Output: busy / idle / retry
```

### Pattern 3: Monitor Without Blocking
```bash
# Start monitoring in background, save to file
bash ./scripts/monitor_session.sh > task.log 2>&1 &
MONITOR_PID=$!

# Do other work
# ...

# Check log later
cat task.log

# Or wait for completion
wait $MONITOR_PID
```

## Raw Event Stream

For custom monitoring:
```bash
source ./scripts/load_state.sh

curl -N "$BASE_URL/event?directory=$PROJECT_PATH"
```

**Output format**:
```
event: message.part.updated
data: {"type":"message.part.updated","properties":{...}}

event: session.status
data: {"type":"session.status","properties":{...}}
```

## Important Events

| Event Type | When | Contains |
|------------|------|----------|
| `message.part.updated` | Text streaming | `delta` (new text chunk) |
| `session.status` | State change | `type` (busy/idle) |
| `message.updated` | Task complete | `tokens`, `cost`, `finish` |
| `session.diff` | Files changed | Array of file changes |

## Polling Alternative

If event streaming doesn't work:
```bash
# Poll status every 2 seconds
while true; do
  STATUS=$(bash ./scripts/check_status.sh)
  echo "Status: $STATUS"
  
  if [ "$STATUS" = "idle" ]; then
    echo "✓ Complete"
    break
  fi
  
  sleep 2
done
```

## Monitoring Best Practices

### ✅ DO

1. **Use for long tasks**:
```bash
   # Good use cases
   bash ./scripts/send_message.sh "Build entire application"
   bash ./scripts/monitor_session.sh
```

2. **Save logs for complex workflows**:
```bash
   bash ./scripts/monitor_session.sh > workflow.log 2>&1
```

3. **Monitor in background for parallel work**:
```bash
   bash ./scripts/monitor_session.sh &
   # Continue with other tasks
```

### ❌ DON'T

1. **Don't monitor simple tasks**:
```bash
   # Overkill for quick tasks
   bash ./scripts/send_message.sh "What's 2+2?"
   bash ./scripts/monitor_session.sh  # Unnecessary
```

2. **Don't forget to stop monitoring**:
   - Monitor script stops automatically on completion
   - Or press Ctrl+C manually

3. **Don't monitor multiple sessions simultaneously**:
   - Monitor script uses current session from state
   - Load correct project first

## Troubleshooting

### No events showing

**Cause**: Wrong session or project

**Solution**:
```bash
# Verify state
source ./scripts/load_state.sh
echo $SESSION_ID

# Or reload project
bash ./scripts/load_project.sh "project-name"
bash ./scripts/monitor_session.sh
```

### Monitor exits immediately

**Cause**: Task already completed

**Solution**:
```bash
# Check status
bash ./scripts/check_status.sh
# If "idle", task is done

# Start new task
bash ./scripts/send_message.sh "New task"
bash ./scripts/monitor_session.sh
```

### Too much output

**Cause**: Events from all sessions

**Solution**:
- Monitor script should filter to current session
- If not, update `monitor_session.sh` script

## Advanced: Custom Event Handling

For specific event types, modify monitor script or create custom:
```bash
# Example: Only show file changes
source ./scripts/load_state.sh

curl -N "$BASE_URL/event?directory=$PROJECT_PATH" | \
while read -r line; do
  if [[ $line == data:* ]]; then
    TYPE=$(echo "${line#data:}" | jq -r '.payload.type' 2>/dev/null)
    if [ "$TYPE" = "session.diff" ]; then
      echo "${line#data:}" | jq -r '.payload.properties.diff[] | .file'
    fi
  fi
done
```

## When to Use Monitoring

| Task Duration | Recommendation |
|---------------|----------------|
| < 10 seconds | Don't monitor |
| 10-30 seconds | Optional |
| 30-60 seconds | Recommended |
| 60+ seconds | Highly recommended |
| Unknown duration | Always monitor |
---
**Author:** [Malek RSH](https://github.com/malek262) | **Repository:** [OpenCode-CLI-Controller](https://github.com/malek262/opencode-api-control-skill)
