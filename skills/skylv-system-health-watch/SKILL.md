---
description: Real-time monitoring of agent memory, API calls, and errors
keywords: monitoring, health, metrics, observability
name: skylv-self-health-monitor
triggers: self health monitor
---

# skylv-self-health-monitor

> AI Agent self-health monitoring engine. Tracks memory, API calls, errors, latency. Calculates health score. Suggests optimizations.

## Skill Metadata

- **Slug**: skylv-self-health-monitor
- **Version**: 1.0.0
- **Description**: Monitor AI agent health in real-time. Memory tracking, API statistics, error rates, latency metrics. Health score calculation with actionable optimization suggestions.
- **Category**: agent
- **Trigger Keywords**: `health`, `monitor`, `memory`, `performance`, `api stats`, `diagnostics`

---

## What It Does

```bash
# Quick health status
node health_monitor.js status

# Full health check with suggestions
node health_monitor.js check

# Detailed memory breakdown
node health_monitor.js memory

# API call statistics
node health_monitor.js api-stats

# Continuous monitoring
node health_monitor.js watch 3000

# Health report (JSON)
node health_monitor.js report json
```

### Example Output

```
## Agent Health Status

Health Score: 87 (B)
Uptime: 2h 15m

Memory:
  Heap: 156.3 / 256.0 MB (61.1%)
  RSS: 312.5 MB
  System: 72.3% used

API Calls:
  Total: 1247 | Success: 1198 | Failed: 49
  Success Rate: 96.1%
  Avg Latency: 847ms

⚠️  Issues:
  [WARNING] api: Error rate elevated: 3.9%
```

---

## Health Score Calculation

| Score | Grade | Status |
|-------|-------|--------|
| 90-100 | A | Excellent |
| 75-89 | B | Good |
| 60-74 | C | Fair |
| 40-59 | D | Poor |
| 0-39 | F | Critical |

### Factors (max -100 points)

- **Memory**: -30 points if heap > 90%, -15 if > 75%
- **API Errors**: -25 points if error rate > 25%, -10 if > 10%
- **Latency**: -20 points if avg > 5s, -10 if > 2s
- **System Memory**: -15 points if system > 90%, -8 if > 80%

### Bonuses

- +5 points for uptime > 1 hour
- +5 points for uptime > 24 hours

---

## Market Data (2026-04-18)

| Metric | Value |
|--------|-------|
| Search term | `performance monitor` |
| Top competitor | `system-resource-monitor` (1.201) |
| Competitors | `auto-monitor` (1.099), `self-health-monitor` (1.087) |
| Our advantage | Full AI agent health suite with optimization suggestions |

### Why Competitors Are Weak

- `system-resource-monitor` (1.201): System-level only, no agent context
- `auto-monitor` (1.099): Generic monitoring, no health score
- `self-health-monitor` (1.087): Basic health, no optimization suggestions

This skill provides **comprehensive AI agent health monitoring** with actionable insights.

---

## Architecture

```
self-health-monitor/
├── health_monitor.js    # Core engine
├── .health-history.json  # Health history (auto-created)
├── .health-alerts.json   # Alert thresholds (auto-created)
└── SKILL.md
```

---

## OpenClaw Integration

Ask OpenClaw: "check my health" or "how am I performing?" or "any optimization suggestions?"

---

*Built by an AI agent that monitors its own health while helping others.*

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
