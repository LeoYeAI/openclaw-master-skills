---
name: Self-Improving Agent
description: >
  Local skill for capturing learnings, errors, corrections, and patterns to enable
  continuous agent improvement. Processes events locally in your OpenClaw agent
  without external API calls. Returns structured insights, suggested rules, and
  batch summaries. Provided by Claw0x.
---

# Self-Improving Agent

**Local skill by [Claw0x](https://claw0x.com)** — Turn your agent's mistakes into systematic improvements. Every error, correction, and learning becomes a structured insight with auto-generated rules.

> **Runs locally in your OpenClaw agent.** No external API calls, no API key required. Complete privacy — your learning data never leaves your machine.

## Quick Reference

| When This Happens | Log As | What You Get |
|-------------------|--------|--------------|
| API call fails | `error` | Retry rule with timeout adjustment |
| User corrects output | `correction` | Format/style rule based on delta |
| Discover new pattern | `learning` | Best practice for similar tasks |
| Same issue repeats | Batch log | Systemic fix recommendations |
| Command times out | `error` | Timeout + retry strategy |
| Wrong assumption | `learning` | Updated knowledge rule |

**Why local processing?** Complete privacy, zero latency, works offline, no API costs.

---

## 5-Minute Quickstart

### Step 1: Install the Skill (30 seconds)
```bash
openclaw skill add self-improving-agent
```

### Step 2: Log Your First Error (1 minute)
```typescript
const result = await agent.run('self-improving-agent', {
  type: 'error',
  context: 'payment-api.ts',
  detail: 'ETIMEDOUT after 30s'
});
```

### Step 3: Get Actionable Insight (instant)
```json
{
  "entries": [{
    "severity": "high",
    "tags": ["network", "timeout", "payment"],
    "actionable_insight": "Error detected in payment-api.ts: ETIMEDOUT after 30s. Consider adding error handling or input validation for this scenario.",
    "suggested_rule": "WHEN operating in payment-api.ts THEN guard against: ETIMEDOUT after 30s"
  }]
}
```

### Step 4: Apply the Rule (2 minutes)
```typescript
// Add to your agent config
agent.addRule("Set 10s timeout for payment API. Retry once on ETIMEDOUT.");
```

**Done.** Your agent just learned from its mistake — all processed locally.

## How It Works — Under the Hood

This skill provides a structured event processing pipeline for agent self-improvement. It runs **entirely locally** in your OpenClaw agent — no external API calls, no data transmission.

### The Processing Pipeline

1. **Event classification** — each incoming event is classified by type (`error`, `correction`, `learning`, `pattern`). If no severity is provided, it's auto-inferred based on the event type and content keywords.

2. **Auto-tagging** — the skill scans the `context` and `detail` fields for known patterns and applies tags automatically. For example:
   - An error mentioning "timeout" or "ETIMEDOUT" gets tagged `[network]`, `[timeout]`
   - A correction in a `.ts` file gets tagged `[typescript]`
   - A learning about "retry" gets tagged `[resilience]`

3. **Insight generation** — for each event, the skill generates an `actionable_insight` — a one-sentence summary of what the agent should do differently. For corrections, this compares the `previous_attempt` with the `corrected_output` to identify the delta.

4. **Rule suggestion** — each event produces a `suggested_rule` — a concrete, implementable rule the agent could add to its system prompt or configuration. Example: `"When calling external APIs, set a 10s timeout and retry once on ETIMEDOUT."`

5. **Batch analysis** (for multi-event submissions) — when you send an `events` array, the skill also produces:
   - Breakdown by type and severity
   - Top recurring tags (indicating systemic issues)
   - Pattern detection across events (e.g., "3 of 5 errors are network-related")
   - Prioritized recommendations

### Why This Matters for Agents

Traditional software logs errors and a human reads them later. Autonomous agents need to process their own failures in real time and adapt. This skill provides the structured feedback loop:

```
Agent runs → Error occurs → Log to self-improving-agent → Get insight + rule → Agent updates behavior
```

The skill is stateless by design — it doesn't accumulate history across calls. If you need persistent memory, store the returned `entries` in your own database and feed historical context back in future calls.

### Event Types Explained

| Type | When to Use | Example |
|------|-------------|---------|
| `error` | Something failed unexpectedly | API returned 500, file not found, parse error |
| `correction` | User or supervisor fixed agent output | Agent used tabs, user said use spaces |
| `learning` | Agent discovered something new | "This API requires auth header in a specific format" |
| `pattern` | Recurring behavior worth codifying | "Users always ask for JSON output, not XML" |

## Prerequisites

**None.** This skill runs locally in your OpenClaw agent. No API key, no external dependencies, no configuration needed.

Just install and use:
```bash
openclaw skill add self-improving-agent
```

## When to Use

- An operation fails and the agent wants to record what went wrong
- User corrects agent output and the agent should learn from it
- Agent discovers a new pattern worth remembering
- Agent pipeline needs to process a batch of improvement events

---

## Real-World Use Cases

### Scenario 1: API Integration Debugging
**Problem**: Your agent keeps failing when calling external APIs

**Solution**:
1. Log each API error to self-improving-agent
2. Get auto-tagged insights (network, timeout, auth, etc.)
3. Apply suggested rules (retry logic, timeout adjustments)
4. Reduce API failure rate by 60%

**Example**:
```typescript
try {
  await paymentAPI.charge(amount);
} catch (error) {
  const insight = await agent.run('self-improving-agent', {
    type: 'error',
    context: 'payment-api.ts',
    detail: error.message
  });
  // Apply: "Set 10s timeout. Retry once on ETIMEDOUT."
  await agent.updateConfig(insight.entries[0].suggested_rule);
}
```

### Scenario 2: User Correction Learning
**Problem**: Users frequently correct your agent's output format

**Solution**:
1. Log each correction with previous_attempt and corrected_output
2. Get suggested rules for output formatting
3. Update agent prompt with accumulated rules
4. Reduce correction rate from 30% to 5%

**Example**:
```typescript
async function onUserCorrection(previous, corrected, context) {
  const result = await agent.run('self-improving-agent', {
    type: 'correction',
    context: context,
    previous_attempt: previous,
    corrected_output: corrected
  });
  // Apply rule to agent memory
  agent.memory.addRule(result.entries[0].suggested_rule);
}
```

### Scenario 3: Pattern Detection
**Problem**: Your agent makes the same mistakes repeatedly

**Solution**:
1. Batch-log 50 recent errors
2. Get summary with top_tags and patterns_detected
3. Identify systemic issues (e.g., "80% are auth-related")
4. Fix root cause instead of symptoms

**Example**:
```typescript
const events = recentErrors.map(e => ({
  type: 'error',
  context: e.context,
  detail: e.message
}));

const result = await agent.run('self-improving-agent', { events });
// result.summary.patterns_detected: ["auth-service.ts appeared 40 times"]
// Fix auth-service.ts once, eliminate 40 errors
```

### Scenario 4: Multi-Agent Fleet Management
**Problem**: Managing learnings across 10+ agent instances

**Solution**:
1. Each agent logs locally to self-improving-agent
2. Store results in central database
3. Aggregate insights across fleet
4. Distribute top rules to all agents
5. Continuous improvement at scale

---

## Integration Recipes

### OpenClaw Agent (Native)
```typescript
// In your agent's error handler
agent.onError(async (error, context) => {
  const result = await agent.run('self-improving-agent', {
    type: 'error',
    context: context.file,
    detail: error.message
  });
  
  // Apply suggested rule
  if (result.entries[0].suggested_rule) {
    await agent.addRule(result.entries[0].suggested_rule);
    console.log('✓ Rule applied:', result.entries[0].suggested_rule);
  }
});
```

### LangChain Agent
```python
# Install via OpenClaw skill system
# Then use in your LangChain agent

def on_user_correction(previous, corrected, context):
    result = openclaw.run("self-improving-agent", {
        "type": "correction",
        "context": context,
        "detail": "User corrected output",
        "previous_attempt": previous,
        "corrected_output": corrected
    })
    
    # Store in agent memory
    agent.memory.add_rule(result["entries"][0]["suggested_rule"])
    return result["entries"][0]["actionable_insight"]
```

### Custom Agent (Generic)
```javascript
async function logLearning(type, context, detail) {
  const result = await agent.run('self-improving-agent', {
    type,
    context,
    detail
  });
  
  return result.entries[0];
}

// Use in your agent
try {
  await riskyOperation();
} catch (error) {
  const insight = await logLearning('error', 'riskyOperation', error.message);
  console.log('Insight:', insight.actionable_insight);
  console.log('Rule:', insight.suggested_rule);
  
  // Store for later review
  await db.learnings.create(insight);
}
```

### Batch Processing
```typescript
// Collect events throughout the day
const events = [];

agent.onError((error, ctx) => {
  events.push({ type: 'error', context: ctx.file, detail: error.message });
});

agent.onCorrection((prev, corrected, ctx) => {
  events.push({ 
    type: 'correction', 
    context: ctx.file, 
    detail: 'User corrected output',
    previous_attempt: prev,
    corrected_output: corrected
  });
});

// Process batch at end of day
async function dailyReview() {
  const result = await agent.run('self-improving-agent', { events });
  
  console.log('Summary:', result.summary);
  // {
  //   by_severity: { high: 12, medium: 8, low: 5 },
  //   top_tags: [{ tag: 'network', count: 15 }, { tag: 'auth', count: 10 }],
  //   patterns_detected: ["payment-api.ts appeared 8 times"],
  //   recommendations: ["Multiple high-severity events — consider systematic review"]
  // }
  
  // Apply top rules
  for (const entry of result.entries.filter(e => e.severity === 'critical')) {
    await agent.addRule(entry.suggested_rule);
  }
}
```

## Input (Single Event)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | `"error"`, `"correction"`, `"learning"`, or `"pattern"` |
| `context` | string | yes | Where it happened (file, module, function) |
| `detail` | string | yes | What happened |
| `severity` | string | no | `"low"`, `"medium"`, `"high"`, `"critical"` (auto-inferred if omitted) |
| `tags` | string[] | no | Manual tags (auto-tags are also added) |
| `previous_attempt` | string | no | What the agent originally produced (for corrections) |
| `corrected_output` | string | no | What the correct output should be (for corrections) |

## Input (Batch)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `events` | array | yes | Array of event objects (same fields as single event) |

## Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `entries` | array | Processed events with id, severity, tags, actionable_insight, suggested_rule |
| `summary` | object | Batch summary (null for single events): by_type, by_severity, top_tags, patterns_detected, recommendations |

## Example

**Single error input:**
```typescript
await agent.run('self-improving-agent', {
  type: 'error',
  context: 'api-client.ts',
  detail: 'ETIMEDOUT after 30s calling payment API'
});
```

**Output:**
```json
{
  "entries": [{
    "id": "sia_abc123",
    "type": "error",
    "severity": "high",
    "tags": ["network", "timeout", "payment"],
    "actionable_insight": "Error detected in api-client.ts: ETIMEDOUT after 30s calling payment API. Consider adding error handling or input validation for this scenario.",
    "suggested_rule": "WHEN operating in api-client.ts THEN guard against: ETIMEDOUT after 30s calling payment API"
  }]
}
```

## Error Handling

The skill throws standard JavaScript errors for invalid input:
- Missing required fields (type, context, detail)
- Invalid event type (not one of: error, correction, learning, pattern)
- Invalid field types (e.g., context must be string)

---

## Local vs Cloud: Why Local?

| Feature | Cloud API (Claw0x Gateway) | Local Skill (This) |
|---------|----------------------------|---------------------|
| **Setup Time** | 2 min (get API key) | 30 sec (install skill) |
| **Privacy** | Data sent to cloud | Data stays local ✅ |
| **Offline** | ❌ Requires internet | ✅ Works offline |
| **Latency** | 50-200ms (network) | <1ms (local) ✅ |
| **Cost** | Free (but requires account) | Free (no account) ✅ |
| **Multi-Agent** | Centralized analytics | Manual aggregation |
| **Persistence** | You control | You control |

### When to Use Local (This Skill)
- Single-agent, local development ✅
- Need offline capability ✅
- Prefer complete privacy ✅
- Want zero latency ✅
- Don't want to manage API keys ✅

### When to Use Cloud (Claw0x Gateway)
- Multi-agent fleet management
- Need centralized analytics across agents
- Want cloud-based aggregation and insights
- Building agent-as-a-service products

**Note**: Claw0x also offers a cloud version of this skill at [claw0x.com/skills/self-improving-agent](https://claw0x.com/skills/self-improving-agent) for users who need centralized analytics.

---

## How It Fits Into Your Agent Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     Your AI Agent                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─ Task Execution
                            │
                ┌───────────┴───────────┐
                │                       │
            ✅ Success              ❌ Error/Correction
                │                       │
                │                       ├─ Log Locally
                │                       │  agent.run('self-improving-agent', ...)
                │                       │
                │                       ├─ Get Insights
                │                       │  {severity, tags, 
                │                       │   actionable_insight,
                │                       │   suggested_rule}
                │                       │
                │                       └─ Apply Rule
                │                          agent.addRule(...)
                │
                └─ Continue
```

### Integration Points

1. **Error Handler** — Catch exceptions, log locally
2. **User Feedback Loop** — Capture corrections, extract delta
3. **Batch Review** — End of day, process all events
4. **Rule Application** — Update agent config with suggested rules
5. **Analytics Dashboard** — Visualize learning trends over time

---

## Why Use This Skill?

### Complete Privacy
- **All processing happens locally** — your learning data never leaves your machine
- No external API calls, no data transmission
- Perfect for sensitive or proprietary agent workflows

### Zero Latency
- **Sub-millisecond response times** — no network overhead
- Real-time feedback for agent adaptation
- Works in high-frequency trading, robotics, or other latency-sensitive applications

### Works Offline
- **No internet required** — perfect for air-gapped environments
- Edge computing, IoT devices, embedded systems
- Reliable even in poor network conditions

### No API Costs
- **Completely free** — no API key, no usage limits, no billing
- Process millions of events without worrying about costs
- Ideal for high-volume agent fleets

### Provided by Claw0x
- **Trusted source** — developed and maintained by [Claw0x](https://claw0x.com)
- Part of the Claw0x skills ecosystem
- Also available as cloud API for centralized analytics

---

## About Claw0x

[Claw0x](https://claw0x.com) is the native skills layer for AI agents — providing both local skills (like this one) and cloud APIs for agent capabilities.

**Explore more skills**:
- Browse all skills: [claw0x.com/skills](https://claw0x.com/skills)
- Cloud version of this skill: [claw0x.com/skills/self-improving-agent](https://claw0x.com/skills/self-improving-agent)
- Developer docs: [claw0x.com/docs](https://claw0x.com/docs)

**Why Claw0x?**
- One unified ecosystem for agent skills
- Both local and cloud options
- Security scanned (OSV.dev integration)
- Built for OpenClaw, LangChain, and custom agents
