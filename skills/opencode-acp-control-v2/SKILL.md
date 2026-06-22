---
name: opencode-acp-control
description: Control OpenCode directly via the Agent Client Protocol (ACP). Start sessions, send prompts, resume conversations, and manage OpenCode updates. Includes automatic recovery, stuck detection, and session management.
metadata: {"version": "2.0.0", "author": "Bastian Berrios <bastianberrios.a@gmail.com>", "license": "MIT", "github_url": "https://github.com/berriosb/Opencode-Acp-Control"}
---

# OpenCode ACP Skill v2.0

Control OpenCode directly via the Agent Client Protocol (ACP) with **automatic recovery** and **stuck detection**.

## 🆕 What's New in v2.0

| Feature | Description |
|---------|-------------|
| **Auto-retry** | Automatically retries on failure (max 3 attempts) |
| **Stuck detection** | Detects when OpenCode is not responding |
| **Lock cleanup** | Automatically removes stale lock files |
| **Adaptive polling** | Polls faster at start, slower when stable |
| **Health checks** | Periodic checks that OpenCode is alive |
| **Configurable timeouts** | Shorter timeouts with escalation |
| **Session recovery** | Can recover from crashes mid-task |

---

## Quick Reference

| Action | How |
|--------|-----|
| Start OpenCode | `exec(command: "opencode acp --cwd /path", background: true)` |
| Send message | `process.write(sessionId, data: "<json-rpc>\n")` |
| Read response | `process.poll(sessionId)` - adaptive polling |
| Health check | `process.poll(sessionId, timeout: 5000)` - only when no output >60s |
| Stop OpenCode | `process.kill(sessionId)` + cleanup locks |
| Clean locks | `exec(command: "rm -f ~/.openclaw/agents/*/sessions/*.lock")` |
| List sessions | `exec(command: "opencode session list", workdir: "...")` |
| Resume session | List sessions → `session/load` |

---

## 🚀 Quick Start (Simple)

For most use cases, use this simple workflow:

```
1. exec(command: "opencode acp --cwd /path/to/project", background: true)
   -> sessionId: "bg_42"

2. process.write(sessionId: "bg_42", data: initialize_json + "\n")
   process.poll(sessionId: "bg_42", timeout: 10000)

3. process.write(sessionId: "bg_42", data: session_new_json + "\n")
   process.poll(sessionId: "bg_42", timeout: 10000)
   -> opencodeSessionId: "sess_xyz"

4. process.write(sessionId: "bg_42", data: prompt_json + "\n")
   adaptivePoll(sessionId: "bg_42", maxWaitMs: 120000)

5. When done: process.kill(sessionId: "bg_42")
   cleanupLocks()
```

---

## 📁 Skill Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This file - main documentation |
| `config.default.json` | Default configuration (copy to `config.json` to customize) |
| `templates.md` | Prompt templates for common tasks |

---

## ⚙️ Configuration

### Option 1: Use defaults
All defaults are built-in. No config file needed.

### Option 2: Customize
Copy `config.default.json` to `config.json` in the same folder and modify:

```bash
cp config.default.json config.json
# Edit config.json with your preferences
```

**Config structure:**
```json
{
  "timeouts": { "initialize": 10000, "prompt": {...} },
  "retry": { "maxAttempts": 3, "initialDelay": 2000 },
  "polling": { "initial": 1000, "active": 2000 },
  "healthCheck": { "noOutputThreshold": 60000 },
  "recovery": { "autoRecover": true },
  "mcpServers": { "default": [], "supabase": ["supabase"] }
}
```

---

### Timeouts (Configurable)

| Operation | Default | Max | When to increase |
|-----------|---------|-----|------------------|
| Initialize | 10s | 30s | Slow machine |
| Session new | 10s | 30s | Large project |
| Prompt (simple) | 60s | 120s | Complex query |
| Prompt (complex) | 120s | 300s | Refactor, code gen |
| Health check | 5s | 10s | Network issues |

### Retry Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Max retries | 3 | How many times to retry on failure |
| Retry delay | 2s | Initial delay between retries |
| Backoff multiplier | 2 | Delay doubles each retry |
| Max retry delay | 10s | Maximum delay between retries |

### Adaptive Polling

| Phase | Interval | Duration |
|-------|----------|----------|
| Initial | 1s | First 10s |
| Active | 2s | 10s - 60s |
| Stable | 3s | 60s - 120s |
| Slow | 5s | 120s+ |

---

## 🔄 Automatic Recovery

### Stuck Detection

OpenCode is considered "stuck" when:
- No response after **2x expected timeout**
- Health check fails 3 times in a row
- Process is still running but not responding to polls

### Recovery Steps

When stuck is detected:

```
1. Cancel current operation: session/cancel
2. Wait 2 seconds
3. If still stuck: process.kill
4. Clean up locks
5. Restart OpenCode
6. Resume from last known session (if available)
```

### Lock Cleanup

Lock files can become stale when OpenCode crashes. Always clean up:

```bash
# Before starting a new session
exec(command: "find ~/.openclaw/agents -name '*.lock' -mmin +30 -delete")

# After killing a stuck process
exec(command: "rm -f ~/.openclaw/agents/*/sessions/*.lock")
```

---

## 📋 Step-by-Step Workflow

### Step 1: Pre-flight Check

Before starting, verify environment:

```bash
# Check OpenCode is installed
exec(command: "opencode --version")

# Clean stale locks (older than 30 minutes)
exec(command: "find ~/.openclaw/agents -name '*.lock' -mmin +30 -delete")
```

### Step 2: Start OpenCode

```bash
exec(
  command: "opencode acp --cwd /path/to/project",
  background: true,
  workdir: "/path/to/project"
)
# Save sessionId for all subsequent operations
```

### Step 3: Initialize (with retry)

```json
// Send initialize
{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{"fs":{"readTextFile":true,"writeTextFile":true},"terminal":true},"clientInfo":{"name":"clawdbot","title":"Clawdbot","version":"2.0.0"}}}
```

**Retry logic:**
```
for attempt in 1..3:
    process.write(sessionId, initialize_json + "\n")
    response = process.poll(sessionId, timeout: 10000)
    
    if response contains protocolVersion:
        break  # Success
    
    if attempt < 3:
        sleep(2 * attempt)  # Backoff: 2s, 4s
    else:
        # Recovery mode
        process.kill(sessionId)
        cleanupLocks()
        restart from Step 2
```

### Step 4: Create Session (with retry)

```json
{"jsonrpc":"2.0","id":1,"method":"session/new","params":{"cwd":"/path/to/project","mcpServers":[]}}
```

**Same retry logic as initialize.**

### Step 5: Send Prompts (with adaptive polling)

```json
{"jsonrpc":"2.0","id":2,"method":"session/prompt","params":{"sessionId":"sess_xyz","prompt":[{"type":"text","text":"Your question here"}]}}
```

**Adaptive polling:**
```
elapsed = 0
interval = 1000  # Start at 1s
maxWait = 120000  # 2 minutes for complex tasks

while elapsed < maxWait:
    response = process.poll(sessionId, timeout: interval)
    
    if response contains stopReason:
        return response  # Done
    
    if response contains error:
        handle_error(response)
        break
    
    # Adaptive interval
    elapsed += interval
    if elapsed < 10000:
        interval = 1000      # First 10s: poll every 1s
    elif elapsed < 60000:
        interval = 2000      # 10-60s: poll every 2s
    elif elapsed < 120000:
        interval = 3000      # 60-120s: poll every 3s
    else:
        interval = 5000      # 120s+: poll every 5s

# Timeout reached - check if stuck
if is_stuck(sessionId):
    recover(sessionId)
```

### Step 6: Health Check (Smart - No Token Waste)

**⚠️ Don't poll constantly - wastes tokens!**

Only do health checks when:
1. No output for >60s (possible stuck)
2. Approaching timeout (verify before declaring stuck)
3. Something looks wrong (partial errors, etc.)

**DO NOT health check when:**
- OpenCode is actively generating output
- <60s since last output

```
# Smart health check - only when needed
if time_since_last_output > 60000:  # 60s
    response = process.poll(sessionId, timeout: 5000)
    
    if response contains new data:
        last_output_time = now()
        continue  # Not stuck, just slow
    
    if response is "Process still running" with no data:
        # Still alive, just thinking - wait more
        continue
    
    if response is "No active session":
        # Process died - recover
        recover(sessionId)
```

### Step 7: Cleanup

When done, always clean up:

```
process.kill(sessionId)
exec(command: "rm -f ~/.openclaw/agents/*/sessions/*.lock")
```

---

## 🛠️ Error Handling

### Common Errors and Solutions

| Error | Detection | Solution |
|-------|-----------|----------|
| Process died | `process.poll` returns "No active session" | Restart OpenCode, resume session |
| Stuck (no response) | No response after 2x timeout | Cancel, kill, clean locks, restart |
| Lock file exists | `.lock` file from previous run | Remove stale locks (>30min old) |
| JSON parse error | Malformed response | Skip line, continue polling |
| Timeout | `elapsed >= maxWait` | Check if stuck, retry or escalate |
| Rate limited | HTTP 429 from OpenCode | Exponential backoff, max 10s |

### Recovery Function

```
function recover(sessionId, opencodeSessionId):
    # Step 1: Try to cancel gracefully
    process.write(sessionId, cancel_json + "\n")
    sleep(2000)
    
    # Step 2: Check if recovered
    response = process.poll(sessionId, timeout: 5000)
    if response is valid:
        return  # Recovered!
    
    # Step 3: Force kill
    process.kill(sessionId)
    
    # Step 4: Clean up
    exec("rm -f ~/.openclaw/agents/*/sessions/*.lock")
    
    # Step 5: Restart
    newSessionId = startOpenCode()
    initialize(newSessionId)
    
    # Step 6: Resume if we had a session
    if opencodeSessionId:
        session_load(newSessionId, opencodeSessionId)
    
    return newSessionId
```

---

## 🔌 Session Management

### Multiple Sessions

OpenCode supports multiple concurrent sessions. Track them:

```json
{
  "sessions": {
    "process_42": {
      "processSessionId": "bg_42",
      "opencodeSessionId": "sess_abc",
      "project": "/path/to/project1",
      "lastActivity": "2026-03-05T10:00:00Z",
      "status": "active"
    },
    "process_43": {
      "processSessionId": "bg_43",
      "opencodeSessionId": "sess_def",
      "project": "/path/to/project2",
      "lastActivity": "2026-03-05T09:30:00Z",
      "status": "idle"
    }
  }
}
```

### Session Recovery

If OpenCode crashes mid-task:

```
1. Find the last opencodeSessionId
2. Start new OpenCode process
3. Initialize
4. session/load with the old sessionId
5. Continue from where it left off
```

---

## 📊 Monitoring

### Health Metrics

Track these to detect problems early:

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Response time | <5s | 5-15s | >15s |
| Polls without data | <10 | 10-30 | >30 |
| Lock file age | <5min | 5-30min | >30min |
| Consecutive errors | 0 | 1-2 | ≥3 |

### Logging

Log important events for debugging:

```
[2026-03-05 10:00:00] Started OpenCode, sessionId=bg_42
[2026-03-05 10:00:02] Initialized successfully
[2026-03-05 10:00:03] Created session sess_abc
[2026-03-05 10:00:05] Sent prompt: "Refactor auth module"
[2026-03-05 10:00:15] Received update (thinking)
[2026-03-05 10:00:45] Received update (tool use)
[2026-03-05 10:01:30] Completed, stopReason=end_turn
```

---

## 🎯 Best Practices

### DO:
- ✅ Always clean up locks before starting
- ✅ Use adaptive polling (saves tokens)
- ✅ Implement retry logic (makes it robust)
- ✅ Track session state (enables recovery)
- ✅ Set appropriate timeouts per task type
- ✅ Kill and restart if stuck >2x timeout

### DON'T:
- ❌ Poll every 2s for 5 minutes (wastes tokens)
- ❌ Health check every 30s when output is active (wastes tokens)
- ❌ Ignore stuck processes (blocks future work)
- ❌ Leave lock files after crashes
- ❌ Use same timeout for all operations
- ❌ Skip health checks when no output for >60s (misses stuck detection)

---

## 📝 Example: Robust Implementation

```
# State tracking
state = {
  processSessionId: null,
  opencodeSessionId: null,
  messageId: 0,
  retries: 0,
  lastActivity: null
}

# Start with cleanup
cleanupStaleLocks()

# Start OpenCode
state.processSessionId = exec("opencode acp --cwd /path", background: true)

# Initialize with retry
for attempt in 1..3:
  process.write(state.processSessionId, initialize())
  response = process.poll(state.processSessionId, timeout: 10000)
  
  if is_valid(response):
    break
  
  if attempt == 3:
    throw Error("Failed to initialize after 3 attempts")

# Create session with retry
for attempt in 1..3:
  process.write(state.processSessionId, session_new())
  response = process.poll(state.processSessionId, timeout: 10000)
  
  if is_valid(response):
    state.opencodeSessionId = response.result.sessionId
    break
  
  if attempt == 3:
    throw Error("Failed to create session after 3 attempts")

# Send prompt with adaptive polling
process.write(state.processSessionId, prompt(state.messageId, "Your task"))

elapsed = 0
interval = 1000
maxWait = 120000

while elapsed < maxWait:
  response = process.poll(state.processSessionId, timeout: interval)
  state.lastActivity = now()
  
  if contains_stop_reason(response):
    return parse_response(response)
  
  elapsed += interval
  interval = get_adaptive_interval(elapsed)
  
  # Smart health check - only if no output for >60s
  if elapsed > 60000 && no_recent_output:
    if is_stuck(state.processSessionId):
      state = recover(state)
      # Re-send prompt
      process.write(state.processSessionId, prompt(state.messageId, "Your task"))
      elapsed = 0

# Timeout
throw Error("Operation timed out after ${maxWait}ms")
```

---

## 🔧 Utility Functions

### cleanupStaleLocks()

```bash
# Remove locks older than 30 minutes
find ~/.openclaw/agents -name '*.lock' -mmin +30 -delete
```

### isStuck(sessionId)

```
# Check if process is alive but not responding
response = process.poll(sessionId, timeout: 5000)
return response == "Process still running" && no_data_for_60s
```

### getAdaptiveInterval(elapsedMs)

```
if elapsedMs < 10000: return 1000
if elapsedMs < 60000: return 2000
if elapsedMs < 120000: return 3000
return 5000
```

---

## 📝 Prompt Templates
---

## 📝 Prompt Templates

See `templates.md` for pre-built prompts for common tasks:

| Category | Templates |
|----------|-----------|
| **Refactoring** | Extract function, convert to TS, improve readability |
| **Features** | Add endpoint, add component, implement feature |
| **Bug fixes** | Debug and fix, TypeScript errors |
| **Testing** | Unit tests, integration tests |
| **Documentation** | JSDoc/TSDoc, README updates |
| **Database** | Migrations, RLS policies |
| **Performance** | Query optimization, bundle size |
| **Security** | Security audit |

**Usage:**
```
1. Read templates.md
2. Find appropriate template
3. Replace placeholders with your specifics
4. Send as prompt
```

---

## 📊 Metrics & Monitoring

### Track these for health monitoring:

| Metric | How to track | Healthy | Warning | Critical |
|--------|--------------|---------|---------|----------|
| **Avg response time** | Log timestamps | <30s | 30-60s | >60s |
| **Polls per request** | Counter | <20 | 20-50 | >50 |
| **Retry rate** | Retries/requests | <5% | 5-15% | >15% |
| **Stuck rate** | Stucks/sessions | <1% | 1-5% | >5% |
| **Success rate** | Completed/started | >95% | 85-95% | <85% |

### Logging format:

```
[2026-03-05 10:00:00] INFO: Started OpenCode, sessionId=bg_42
[2026-03-05 10:00:02] INFO: Initialized successfully
[2026-03-05 10:00:03] INFO: Created session sess_abc
[2026-03-05 10:00:05] INFO: Sent prompt (refactor)
[2026-03-05 10:00:15] DEBUG: Received update (thinking)
[2026-03-05 10:00:45] DEBUG: Received update (tool use)
[2026-03-05 10:01:30] INFO: Completed, stopReason=end_turn
[2026-03-05 10:01:31] INFO: Metrics: duration=91s, polls=15, retries=0
```

### Log levels:
- `ERROR` - Failures, exceptions, stuck detected
- `WARN` - Retries, slow responses, near-timeout
- `INFO` - Start, complete, cleanup
- `DEBUG` - Detailed output, updates received

---

## 📦 Skill Files

```
opencode-acp-control-3/
├── SKILL.md              # This file
├── opencode-session.sh   # Helper script (executable)
├── config.default.json   # Default configuration
├── templates.md          # Prompt templates
├── _meta.json            # Skill metadata
└── .clawhub/             # ClawHub metadata
```

---

## 🚀 Helper Script (Recommended)

**Use `opencode-session.sh` for automatic workflow:**

```bash
# Simple usage
~/.openclaw/workspace/skills/opencode-acp-control-3/opencode-session.sh \
  --project /path/to/project \
  --prompt "Add error handling to the API"

# With template
opencode-session.sh \
  --project ~/myapp \
  --template "Add API endpoint" \
  --prompt "POST /api/users with validation"

# Complex task
opencode-session.sh \
  --project ~/myapp \
  --timeout complex \
  --mcp '["supabase"]' \
  --prompt "Create migration for users table"
```

### Script options:

| Option | Description |
|--------|-------------|
| `--project PATH` | Project directory (required) |
| `--prompt "TEXT"` | Prompt to send (required if no template) |
| `--template NAME` | Use template from templates.md |
| `--timeout TYPE` | simple (60s) \| medium (120s) \| complex (300s) |
| `--mcp SERVERS` | MCP servers as JSON array |
| `--verbose` | Enable debug logging |
| `--dry-run` | Show JSON-RPC without executing |
| `--help` | Show help |

### What the script provides:

The script outputs a **complete workflow** with:
- ✅ Pre-flight cleanup
- ✅ Exact JSON-RPC messages to send
- ✅ Retry logic hints
- ✅ Adaptive polling intervals
- ✅ Health check thresholds
- ✅ Cleanup commands

**CYPHER should:**
1. Execute the script with options
2. Parse the output
3. Execute the steps in order
4. Log metrics at the end

---

*Version 2.2.0 - Released 2026-03-05*
*Changes: Added opencode-session.sh helper script*
