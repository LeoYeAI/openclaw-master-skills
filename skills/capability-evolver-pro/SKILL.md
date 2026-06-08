---
name: Capability Evolver
description: >
  Meta-skill for AI agent self-improvement. Analyzes runtime
  logs to detect error patterns, regressions, and inefficiencies, then generates
  structured improvement proposals. Use when the user or agent asks to analyze
  logs, diagnose failures, improve agent reliability, generate evolution proposals,
  or assess system health. Supports analyze, evolve, and status actions.
---

# Capability Evolver

**Local skill by [Claw0x](https://claw0x.com)** — runs entirely in your OpenClaw agent.

> **Runs locally.** No external API calls, no API key required. Complete privacy.

Analyze agent runtime logs, detect patterns, compute health scores, and generate structured improvement proposals. Pure deterministic logic — no LLM, no external dependencies.

## Quick Reference

| When This Happens | Use Action | What You Get |
|-------------------|------------|--------------|
| Agent keeps failing | `analyze` | Error patterns + health score |
| Same error repeats | `analyze` | Root cause identification |
| Need improvement plan | `evolve` | Prioritized recommendations |
| System health check | `status` | Health score + summary |
| Post-deployment review | `analyze` | Regression detection |
| Fleet-wide diagnostics | `analyze` (batch) | Cross-agent patterns |

**Why deterministic?** Reproducible results, no hallucination risk, sub-100ms processing, zero token costs.

---

## Prerequisites

**None.** Just install and use.

## 5-Minute Quickstart

### Step 1: Install (30 seconds)
```bash
openclaw skill add capability-evolver
```

### Step 2: Analyze Your First Logs (1 minute)
```typescript
const result = await agent.run('capability-evolver', {
  action: 'analyze',
  logs: [
    {timestamp: '2025-01-15T10:00:00Z', level: 'error', message: 'ETIMEDOUT', context: 'payment-api.ts'},
    {timestamp: '2025-01-15T10:01:00Z', level: 'error', message: 'ETIMEDOUT', context: 'payment-api.ts'},
    {timestamp: '2025-01-15T10:02:00Z', level: 'error', message: 'ETIMEDOUT', context: 'payment-api.ts'}
  ]
});
```

### Step 3: Get Actionable Insights (instant)
```json
{
  "patterns": [
    {
      "type": "repeated_error",
      "severity": "high",
      "description": "ETIMEDOUT appeared 3 times in payment-api.ts",
      "affected_contexts": ["payment-api.ts"]
    }
  ],
  "health_score": 45,
  "recommendations": [
    "Add timeout configuration to payment-api.ts",
    "Implement retry logic with exponential backoff",
    "Monitor payment API response times"
  ]
}
```

### Step 3: Generate Evolution Plan (instant)
```typescript
const evolution = await agent.run('capability-evolver', {
  action: 'evolve',
  logs: result.logs,
  strategy: 'harden'
});
```

**Done.** You now have a prioritized improvement roadmap, all processed locally.

---

## Real-World Use Cases

### Scenario 1: Production Incident Response
**Problem**: Your agent crashed in production and you need to understand why

**Solution**:
1. Export last 1000 log entries
2. Run analyze action
3. Get error patterns and cascades
4. Identify root cause in minutes

**Example**:
```typescript
const logs = await db.logs.findMany({ 
  where: { timestamp: { gte: incidentStart } },
  orderBy: { timestamp: 'asc' }
});

const analysis = await agent.run('capability-evolver', {
  action: 'analyze',
  logs: logs.map(l => ({
    timestamp: l.timestamp,
    level: l.level,
    message: l.message,
    context: l.context
  }))
});

// analysis.patterns shows: "auth-service.ts failed, then payment-api.ts failed"
// Root cause: auth service timeout cascaded to payment failures
```

### Scenario 2: Continuous Improvement Pipeline
**Problem**: You want your agent to automatically improve based on production data

**Solution**:
1. Schedule daily log analysis
2. Generate evolution proposals
3. Review and apply recommendations
4. Track improvement over time

**Example**:
```javascript
// Cron job: every day at 2am
async function dailyEvolution() {
  const logs = await getLast24HoursLogs();
  
  const evolution = await agent.run('capability-evolver', {
    action: 'evolve',
    logs,
    strategy: 'balanced'
  });
  
  // Store recommendations for review
  for (const rec of evolution.recommendations.filter(r => r.priority === 'critical')) {
    await db.recommendations.create({
      title: `${rec.category}: ${rec.description}`,
      priority: rec.priority,
      affected_files: rec.affected_files,
      approach: rec.suggested_approach
    });
  }
  
  // Track health score trend
  await db.metrics.create({
    date: new Date(),
    health_score: evolution.estimated_improvement
  });
}
// Result: Health score improved from 45 to 85 over 3 months
```

### Scenario 3: Multi-Agent Fleet Management
**Problem**: Managing 50+ agent instances, need to identify systemic issues

**Solution**:
1. Aggregate logs from all agents
2. Batch analyze to find common patterns
3. Fix once, deploy to all agents
4. Reduce fleet-wide error rate

**Example**:
```python
# Collect logs from all agents
all_logs = []
for agent_id in agent_fleet:
    logs = fetch_agent_logs(agent_id, last_24h)
    all_logs.extend(logs)

# Analyze fleet-wide
result = client.call("capability-evolver", {
    "action": "analyze",
    "logs": all_logs
})

# result.patterns shows: "40 of 50 agents failing on auth-service.ts"
# Fix auth-service.ts once, deploy to all agents
# Result: 80% reduction in fleet-wide errors
```

### Scenario 4: Pre-Deployment Health Check
**Problem**: Want to ensure new deployment doesn't introduce regressions

**Solution**:
1. Analyze logs from staging environment
2. Compare health score to production baseline
3. Block deployment if health score drops
4. Catch regressions before production

**Example**:
```javascript
// Pre-deployment health check script
async function preDeploymentCheck() {
  const stagingLogs = await fetchStagingLogs();
  
  const result = await agent.run('capability-evolver', {
    action: 'analyze',
    logs: stagingLogs
  });
  
  const BASELINE = 75;
  
  if (result.health_score < BASELINE) {
    console.error(`Health score ${result.health_score} below baseline ${BASELINE}`);
    console.error('Critical patterns:', result.patterns.filter(p => p.severity === 'critical'));
    process.exit(1);
  }
  
  console.log(`✓ Health check passed: ${result.health_score}`);
}
// Result: Zero regression-related incidents in 6 months
```

---

## Integration Recipes

### OpenClaw Agent
```typescript
// Analyze logs after each run
agent.onComplete(async () => {
  const logs = agent.getRecentLogs();
  
  const analysis = await agent.run('capability-evolver', {
    action: 'analyze',
    logs
  });
  
  if (analysis.health_score < 70) {
    console.warn('⚠️ Health score low:', analysis.health_score);
    console.log('Recommendations:', analysis.recommendations);
  }
});
```

### LangChain Agent
```python
def analyze_agent_health(logs):
    result = agent.run("capability-evolver", {
        "action": "analyze",
        "logs": logs
    })
    
    return {
        "health_score": result["health_score"],
        "patterns": result["patterns"],
        "recommendations": result["recommendations"]
    }

# Use in monitoring
health = analyze_agent_health(agent.logs)
if health["health_score"] < 70:
    alert_team(health)
```

### Custom Monitoring Dashboard
```javascript
// Real-time health monitoring
async function updateHealthDashboard() {
  const logs = await db.logs.findMany({
    where: { timestamp: { gte: Date.now() - 3600000 } } // last hour
  });
  
  const result = await agent.run('capability-evolver', {
    action: 'analyze',
    logs
  });
  
  // Update dashboard
  dashboard.update({
    healthScore: result.health_score,
    errorRate: result.summary.error_count / result.summary.total_logs,
    topPatterns: result.patterns.slice(0, 5)
  });
}

setInterval(updateHealthDashboard, 60000); // every minute
```

### Evolution Strategy Comparison
```typescript
// Compare different evolution strategies
const logs = await getProductionLogs();

const strategies = ['balanced', 'innovate', 'harden', 'repair-only'];

const results = await Promise.all(
  strategies.map(strategy =>
    agent.run('capability-evolver', {
      action: 'evolve',
      logs,
      strategy
    })
  )
);

// Compare estimated improvements
for (let i = 0; i < strategies.length; i++) {
  console.log(`${strategies[i]}: ${results[i].estimated_improvement}`);
}

// Choose best strategy for current situation
const best = results.reduce((a, b) => 
  parseFloat(a.estimated_improvement) > parseFloat(b.estimated_improvement) ? a : b
);
```

---

## How It Works — Under the Hood

Capability Evolver is a deterministic analysis engine that processes structured log data and produces actionable diagnostics. No LLM is involved �?the analysis is rule-based, which means results are reproducible and fast.

### Analysis Engine

The core engine processes log entries through several analysis passes:

1. **Pattern detection** �?logs are grouped by `context` (file/module) and `level` (error/warn/info/debug). The engine looks for:
   - **Repeated errors** �?the same error message appearing multiple times indicates a systemic issue, not a transient failure
   - **Error cascades** �?errors in module A followed by errors in module B within a short time window suggest a dependency chain failure
   - **Regression signals** �?errors that appear after a period of clean logs suggest a recent change broke something
   - **Inefficiency patterns** �?excessive warn-level logs or repeated retries indicate performance issues

2. **Health scoring** �?a system health score (0�?00) is computed based on:
   - Error rate (errors / total logs)
   - Error diversity (unique error messages / total errors)
   - Warn-to-error ratio
   - Time distribution (clustered errors score worse than spread-out errors)

3. **Recommendation generation** �?based on detected patterns, the engine generates specific, actionable recommendations. These aren't generic advice �?they reference the actual files, error messages, and patterns found in your logs.

### Evolution Strategies

When using the `evolve` action, you can choose a strategy that shapes the recommendations:

| Strategy | Focus | Best For |
|----------|-------|----------|
| `auto` | Balanced based on health score | Default �?let the engine decide |
| `balanced` | Equal weight to reliability and features | Stable systems with moderate issues |
| `innovate` | Prioritize new capabilities | Healthy systems ready to grow |
| `harden` | Prioritize reliability and error reduction | Systems with frequent failures |
| `repair-only` | Fix critical issues only | Systems in crisis |

### Evolution Proposals

The `evolve` action produces structured improvement proposals with:
- A unique `evolution_id` for tracking
- Prioritized recommendations with category labels (reliability, performance, architecture)
- Risk assessment (how risky is each proposed change)
- Estimated improvement (projected health score after implementing recommendations)

### Why Deterministic (Not LLM)?

- **Reproducible** �?same logs always produce the same analysis. Critical for debugging and auditing.
- **Fast** �?sub-100ms processing. No API call to an AI provider.
- **No hallucination risk** �?the engine only reports patterns it actually found in the data.
- **Cost-effective** �?pure computation, no token costs.

The tradeoff: the engine can't understand semantic meaning in log messages the way an LLM could. It relies on structural patterns (frequency, timing, severity) rather than understanding what the error message means in context.

## About Claw0x

This skill is provided by [Claw0x](https://claw0x.com), the native skills layer for AI agents.

**Cloud version available**: For users who need centralized analytics and cross-agent insights, a cloud version is available at [claw0x.com/skills/capability-evolver](https://claw0x.com/skills/capability-evolver).

**Explore more skills**: [claw0x.com/skills](https://claw0x.com/skills)

**GitHub**: [github.com/kennyzir/capability-evolver](https://github.com/kennyzir/capability-evolver)

## When to Use

- User says "analyze these logs", "what's failing", "improve my agent", "check system health"
- Agent pipeline needs automated diagnostics after a run
- User wants structured recommendations for fixing recurring errors
- Building a self-healing agent that adapts based on its own failure patterns

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.action` | string | yes | `"analyze"`, `"evolve"`, or `"status"` |
| `input.logs` | array | yes (for analyze/evolve) | Array of log entries |
| `input.logs[].timestamp` | string | yes | ISO timestamp |
| `input.logs[].level` | string | yes | `"error"`, `"warn"`, `"info"`, or `"debug"` |
| `input.logs[].message` | string | yes | Log message |
| `input.logs[].context` | string | no | File or module name |
| `input.strategy` | string | no | `"auto"`, `"balanced"`, `"innovate"`, `"harden"`, `"repair-only"` |
| `input.target_file` | string | no | Focus analysis on a specific file |

## Output (Analyze)

| Field | Type | Description |
|-------|------|-------------|
| `patterns` | array | Detected error/regression/inefficiency patterns with severity |
| `health_score` | number | System health 0�?00 |
| `recommendations` | string[] | Actionable improvement suggestions |
| `summary` | object | Counts: total_logs, error_count, warn_count, unique_patterns |

## Output (Evolve)

| Field | Type | Description |
|-------|------|-------------|
| `evolution_id` | string | Unique proposal ID |
| `strategy` | string | Effective strategy used |
| `recommendations` | array | Prioritized improvements with category and approach |
| `risk_assessment` | object | Risk level and contributing factors |
| `estimated_improvement` | string | Projected health score improvement |

## Error Codes

- `400` — Invalid action or missing logs array
- `500` — Processing failed

## About Claw0x

[Claw0x](https://claw0x.com) is the native skills layer for AI agents — providing unified API access, atomic billing, and quality control.

**Explore more skills**: [claw0x.com/skills](https://claw0x.com/skills)

**GitHub**: [github.com/kennyzir/capability-evolver](https://github.com/kennyzir/capability-evolver)

---

## Deterministic vs LLM Analysis: Which is Right for You?

| Feature | LLM-Based (GPT-4, Claude) | Capability Evolver (Local) |
|---------|---------------------------|---------------------------|
| **Setup Time** | 5-10 min (prompt engineering) | 30 seconds (install skill) |
| **Processing Speed** | 5-30 seconds | Sub-100ms |
| **Reproducibility** | ❌ Varies per run | ✅ Same logs = same results |
| **Hallucination Risk** | ⚠️ Can invent patterns | ✅ Only reports real patterns |
| **Cost** | $0.10-0.50 per analysis | Free (runs locally) |
| **Semantic Understanding** | ✅ Understands context | ❌ Pattern-based only |
| **Audit Trail** | ❌ Hard to explain | ✅ Rule-based, explainable |
| **Privacy** | ⚠️ Sends data to API | ✅ Runs entirely locally |

### When to Use LLM-Based
- Need semantic understanding of log messages
- Want natural language explanations
- Logs contain unstructured text
- Willing to trade speed for insight depth

### When to Use Capability Evolver (Local)
- Need reproducible results for compliance
- Want sub-second processing
- Building automated pipelines
- Require explainable AI for audits
- Processing millions of logs
- Privacy-sensitive applications
- Zero-cost operations

---

## How It Fits Into Your Agent Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                  Agent Development Lifecycle                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─ Development
                            │  • Write agent code
                            │  • Local testing
                            │
                            ├─ Staging Deployment
                            │  agent.run('capability-evolver', 
                            │    {action: "analyze", logs: staging_logs})
                            │  → Health check before production
                            │
                            ├─ Production Monitoring
                            │  agent.run('capability-evolver', 
                            │    {action: "analyze", logs: recent_logs})
                            │  → Real-time health tracking (every hour)
                            │
                            ├─ Incident Response
                            │  agent.run('capability-evolver',
                            │    {action: "analyze", logs: incident_logs})
                            │  → Root cause analysis
                            │
                            └─ Continuous Improvement
                               agent.run('capability-evolver',
                                 {action: "evolve", strategy: "balanced"})
                               → Auto-generate improvement tasks (daily)
```

### Integration Points

1. **Pre-Deployment** — Health check before releasing
2. **Real-Time Monitoring** — Continuous health tracking
3. **Incident Response** — Fast root cause analysis
4. **Daily Reviews** — Automated improvement proposals
5. **Fleet Management** — Cross-agent pattern detection

---

## Why Use Capability Evolver?

### Zero-Cost Operations
- **Runs locally** — no API calls, no billing
- **Complete privacy** — logs never leave your system
- **Offline capable** — works without internet connection

### Agent-Optimized
- **Deterministic analysis** — reproducible, auditable results
- **Fast processing** — sub-100ms, suitable for real-time monitoring
- **Structured output** — JSON format, easy to integrate
- **Evolution strategies** — tailored recommendations based on context

### Production-Ready
- **No dependencies** — pure logic, no external services
- **Scales to millions** — handle enterprise-scale log analysis
- **Cloud-native** — works in Lambda, Cloud Run, containers
- **Zero maintenance** — no model updates or API keys to manage

