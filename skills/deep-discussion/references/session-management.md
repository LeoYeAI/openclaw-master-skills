# Session Management Guide (True Multi-Agent Coordination)

Managing **independent persistent sessions** for TRUE interactive multi-agent deep discussion.

---

## ⚠️ Pre-flight Checks (MANDATORY - Before Creating Sessions)

**DO NOT create any sessions until all checks pass.**

**As the assistant, YOU must perform these checks automatically using `exec` tool.**

---

### Check 1: maxSpawnDepth (Auto-run by Assistant)

**YOU must run this exact command using `exec` tool:**

```bash
exec(command: "openclaw config get agents.defaults.subagents.maxSpawnDepth")
```

**Parse the output:**
| Output | Status | Action |
|--------|--------|--------|
| `2` or higher | ✅ Pass | Proceed to Check 2 |
| `1` | ⚠️ Warning | Can spawn subagents but Orchestrator cannot spawn further subagents |
| `0` | ❌ Blocked | **Abort** - cannot spawn any subagents |
| `command not found` or error | ⚠️ Warning | Assume 1, proceed with caution |

---

### Check 2: User Confirmation

**Always required** (sequential spawn is the default mode):

```
🎯 Multi-agent deep discussion will use sequential spawn mode:

- Each expert is spawned one-by-one (not in parallel)
- Each expert sees all previous experts' responses
- Mode: mode="run" (one-shot per expert)
- Estimated time: ~75-175 minutes

Proceed? [y/N]
```

---

### Pre-flight Checklist
```
[ ] Check 1: exec("openclaw config get agents.defaults.subagents.maxSpawnDepth") completed
[ ] Check 1 Result: {value} (≥2 ✅ | 1 ⚠️ | 0 ❌)
[ ] Check 2: User confirmation obtained
[ ] Mode: run-sequential (default)
[ ] Proceeding to session creation
```

---

## Core Architecture

```
┌─────────────────┐
│  Orchestrator   │ (persistent session, mode="session")
│   Coordinator   │
└────────┬────────┘
         │
    ┌────┴────┬───────────┬───────────┬───────────┐
    │         │           │           │           │
┌───▼───┐ ┌──▼────┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐
│Expert 1│ │Expert 2│ │Expert 3│ │Expert 4│ │Expert 5│
│Session │ │Session │ │Session │ │Session │ │Session │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

**关键**：每个专家都是独立的 session，Orchestrator 协调对话流程

## Session Modes

### `mode="session"` (Optimal for Experts)
- **Behavior**: Session stays alive until explicitly ended
- **Use case**: Multi-round discussions where experts need to see each other's responses
- **Timeout**: No auto-expire (stays alive indefinitely)
- **Requirement**: `thread=true` (not available in all environments)

### `mode="run"` (Fallback for Experts)
- **Behavior**: Session ends when task completes
- **Use case**: Environments without `thread=true` support (e.g., Feishu/webchat)
- **CRITICAL**: Must use **sequential spawn** pattern (see below)
- **Trade-off**: Each expert response is one-shot, but Orchestrator maintains discussion history

## Creating Sessions

### Step 1: Spawn Orchestrator

```python
orchestrator = sessions_spawn({
  label: "deep-discussion-orchestrator-{topic}",
  runtime: "subagent",
  mode: "session",  # CRITICAL: persistent
  model: "bailian/qwen3.5-plus",
  task: "You are the Orchestrator for a deep discussion session about {topic}..."
})
```

### Step 2: Orchestrator Spawns Experts

```python
expert_sessions = []
for i, expert_role in enumerate(expert_roles, 1):
  expert_session = sessions_spawn({
    label: f"deep-discussion-expert-{i}-{expert_role}",
    runtime: "subagent",
    mode: "session",  # CRITICAL: persistent
    model: "bailian/qwen3.5-plus",
    task: f"""You are Expert #{i}: {expert_role}.

Topic: {topic}
Your perspective: {expert_perspective}

You will participate in a real-time discussion with other experts.
You will see their responses and respond to them.
Wait for the Orchestrator to send you prompts."""
  })
  expert_sessions.append(expert_session.sessionKey)
```

## Communication Pattern

### Sequential Spawn Pattern (CRITICAL for `mode="run"`)

When using `mode="run"` (environment doesn't support `thread=true`), **MUST spawn experts sequentially**:

```python
# ✅ CORRECT: Sequential spawn with context passing
discussion_history = []

for i, expert_role in enumerate(expert_roles):
  # Build context from all previous experts
  context = "\n\n".join(discussion_history) if discussion_history else ""
  
  # Spawn expert with full context
  expert = sessions_spawn({
    label: f"expert-{i}-{expert_role}",
    runtime: "subagent",
    mode: "run",  # Fallback mode
    task: f"""You are {expert_role}.

Previous experts' views:
{context if context else "(You are the first to speak)"}

Task: Share your perspective and respond to previous experts' points."""
  })
  
  # Wait for completion (push-based)
  response = wait_for_completion(expert.sessionKey)
  discussion_history.append(f"## {expert_role}\n{response}")
  
  # Append to discussion file immediately
  append_to_file(discussion_file, f"## {expert_role}\n{response}\n")

# ✅ Result: Each expert sees and responds to previous experts
```

```python
# ❌ WRONG: Parallel spawn (batch processing)
expert_sessions = []
for i, expert_role in enumerate(expert_roles):
  expert = sessions_spawn({...})  # All spawned at once
  expert_sessions.append(expert)

# All experts respond in isolation - NO REAL INTERACTION!
```

**Key Difference**:
- Sequential: Expert 5 sees Expert 1-4's responses → real dialogue
- Parallel: All experts respond independently → no interaction

---

### Sequential Dialogue (关键！)

```python
# Round 1: Expert 1 speaks first
sessions_send({
  sessionKey: expert_sessions[0],
  message: "Round 1: Please share your initial view on this topic."
})
expert1_response = wait_for_completion(expert_sessions[0])

# Append to discussion file
append_to_file(discussion_file, f"## Expert 1 ({expert_role_1})\n{expert1_response}\n")

# Round 1: Expert 2 sees Expert 1's response
sessions_send({
  sessionKey: expert_sessions[1],
  message: f"""Round 1: Please share your view.

Expert 1 ({expert_role_1}) said:
{expert1_response}

Please respond to their points and share your perspective."""
})
expert2_response = wait_for_completion(expert_sessions[1])

# Append to discussion file
append_to_file(discussion_file, f"## Expert 2 ({expert_role_2})\n{expert2_response}\n")

# Continue sequence...
```

### Parallel Collection (for Agenda Setting)

```python
# Send to all experts in parallel
for session_key in expert_sessions:
  sessions_send({
    sessionKey: session_key,
    message: "Please review this agenda draft and provide feedback."
  })

# Collect all responses
responses = []
for session_key in expert_sessions:
  response = wait_for_completion(session_key)
  responses.append(response)
```

## Keeping Sessions Alive

Persistent sessions stay alive as long as:
1. No explicit end command
2. Periodic activity (sending/receiving messages)

```python
# For long discussions (>30 min), send keep-alive if needed
sessions_send({
  sessionKey: expert_session,
  message: "Discussion ongoing, please stand by..."
})
```

## Session Cleanup

```python
# After discussion complete
for session_key in expert_sessions:
  sessions_send({
    sessionKey: session_key,
    message: "Discussion complete! Thank you for your contributions."
  })
# Sessions will naturally expire after inactivity
```

## Timeout Handling

### Detecting Timeout

```python
try:
  response = sessions_send({
    sessionKey: session_key,
    message: "Please respond...",
    timeout: 300  # 5 minutes
  })
except TimeoutError:
  log(f"Expert {session_key} timed out")
  # Option 1: Recreate session
  # Option 2: Continue without this expert
```

### Recovery Strategy

```python
def recover_expert_session(expert_role, previous_context):
  """Recreate expert session with full context"""
  new_session = sessions_spawn({
    label: f"deep-discussion-expert-{expert_role}-recovered",
    runtime: "subagent",
    mode: "session",
    task: f"""You are {expert_role}.

Previous discussion:
{previous_context}

Please continue the discussion from where you left off."""
  })
  return new_session.sessionKey
```

## Best Practices

### 1. Always Use `mode="session"`

```python
# ✅ Good
sessions_spawn({mode: "session", ...})

# ❌ Bad - will timeout
sessions_spawn({mode: "run", ...})
```

### 2. Track All Session Keys

```python
# ✅ Good
expert_sessions = {}
for i, role in enumerate(expert_roles):
  session = sessions_spawn(...)
  expert_sessions[role] = session.sessionKey

# ❌ Bad - lose track
for role in expert_roles:
  sessions_spawn(...)  # Session keys lost!
```

### 3. Sequential Dialogue for Real Interaction

```python
# ✅ Good - Expert 2 sees Expert 1's response
expert1 = sessions_send({sessionKey: experts[0], message: "Your view?"})
expert2 = sessions_send({
  sessionKey: experts[1],
  message: f"Expert 1 said: {expert1}. Your response?"
})

# ❌ Bad - Parallel, no interaction
for expert in experts:
  sessions_send({sessionKey: expert, message: "Your view?"})
# All experts respond in isolation, no real dialogue
```

### 4. Save Discussion History

```python
# After each expert responds
append_to_file(discussion_file, f"""
## Round {round_num}: {expert_role}

{response}

""")
```

## Common Issues

### Issue 1: Experts Don't See Each Other's Responses

**Symptom**: All experts respond in parallel, no interaction

**Cause**: Sending prompts to all experts at once

**Fix**: Use sequential dialogue pattern

```python
# Sequential (correct)
for i, expert in enumerate(experts):
  previous_responses = get_all_previous_responses(i)
  sessions_send({
    sessionKey: expert,
    message: f"Previous experts said: {previous_responses}. Your response?"
  })
```

### Issue 2: Sessions Timeout

**Symptom**: Expert doesn't respond after ~10-15 minutes

**Cause**: Using `mode="run"` instead of `mode="session"`

**Fix**: Use `mode="session"` for all expert sessions

### Issue 3: Lost Session Keys

**Symptom**: Cannot send messages to experts

**Cause**: Did not track session keys

**Fix**: Always store session keys in a dictionary/list

## Example: Full Lifecycle

```python
# 1. Create Orchestrator
orchestrator = sessions_spawn({
  label: "orchestrator",
  runtime: "subagent",
  mode: "session",
  task: "You are the Orchestrator..."
})

# 2. Orchestrator creates experts
expert_sessions = []
for i in range(5):
  expert = sessions_spawn({
    label: f"expert-{i}",
    runtime: "subagent",
    mode: "session",
    task: f"You are Expert #{i}..."
  })
  expert_sessions.append(expert.sessionKey)

# 3. Facilitate REAL dialogue (5 rounds)
for round_num in range(1, 6):
  # Sequential dialogue
  all_previous_responses = []
  for i, session_key in enumerate(expert_sessions):
    # Build context from previous experts
    context = "\n".join(all_previous_responses) if all_previous_responses else ""
    
    # Send prompt with context
    prompt = f"Round {round_num}: {round_topic}"
    if context:
      prompt += f"\n\nPrevious experts said:\n{context}"
    
    sessions_send({
      sessionKey: session_key,
      message: prompt
    })
    
    # Wait for response
    response = wait_for_completion(session_key, timeout=300)
    all_previous_responses.append(f"Expert {i+1}: {response}")
    
    # Append to file
    append_to_file(discussion_file, f"## Round {round_num}, Expert {i+1}\n{response}\n")
  
  # Assess convergence
  if assess_convergence(all_previous_responses):
    break

# 4. Generate final report
final_report = synthesize_report(discussion_file)
save_report(final_report)

# 5. Clean up
for session_key in expert_sessions:
  sessions_send({
    sessionKey: session_key,
    message: "Discussion complete! Thank you!"
  })
```

## Performance Considerations

| Aspect | Recommendation |
|--------|---------------|
| Session count | 5-7 experts optimal |
| Timeout per expert | 5 minutes (300 seconds) |
| Total round time | ~25-35 minutes per round (5 experts × 5 min) |
| Expected rounds | 3-5 rounds for convergence |
| **Total time** | **~75-175 minutes** for full session |

## Debugging

### List Active Sessions

```python
active = subagents(action="list", recentMinutes=30)
print(f"Active sessions: {len(active['active'])}")
```

### Session Health Check

```python
def check_session_health(session_key):
  try:
    result = sessions_send({
      sessionKey: session_key,
      message: "Health check - please respond with 'OK'",
      timeout: 10
    })
    return "OK" in result.reply
  except:
    return False
```
