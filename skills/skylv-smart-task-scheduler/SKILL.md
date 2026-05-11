---
description: Context-aware task scheduling with priority management
keywords: openclaw, skill, automation, ai-agent
name: skylv-context-aware-scheduler
triggers: context aware scheduler
---

# skylv-context-aware-scheduler

> Schedule tasks based on conditions, not just time. Run when a file changes, API rate limit resets, or time window opens.

## Skill Metadata

- **Slug**: skylv-context-aware-scheduler
- **Version**: 1.0.0
- **Description**: Context-aware task scheduler. Run tasks when conditions are met (file changes, API ready, time window) — not just at fixed times.
- **Category**: platform
- **Trigger Keywords**: `scheduler`, `cron`, `schedule`, `trigger`, `automation`, `定时`, `条件触发`

---

## What It Does

Unlike a regular cron that runs at fixed times, this scheduler runs tasks **when conditions are met**:

```bash
# Run tasks when triggers are due
node scheduler.js run tasks.json

# Run all tasks immediately (ignore triggers)
node scheduler.js now tasks.json

# Start daemon (checks every 30s)
node scheduler.js watch tasks.json

# List all tasks
node scheduler.js list tasks.json
```

### Example: ClawHub Auto-Publisher

```json
{
  "name": "Publish next skill",
  "trigger": { "kind": "cron", "spec": "0 * * * *" },
  "condition": { "kind": "file-exists", "spec": "C:/Users/Administrator/.qclaw/pending-publish.txt" },
  "action": { "command": "clawhub publish . --slug skylv-x --version 1.0.0" }
}
```
→ Runs every hour, but **only if** `pending-publish.txt` exists.

### Example: API Rate Limit Aware

```json
{
  "name": "Publish after rate limit reset",
  "trigger": { "kind": "interval", "spec": "5m" },
  "condition": { "kind": "api-ready", "spec": "" },
  "action": { "command": "clawhub publish . --slug skylv-x --version 1.0.0" }
}
```
→ Checks every 5 minutes, but **only executes** when rate limit has reset.

---

## Trigger Kinds

| Kind | Description | Example |
|------|-------------|---------|
| `cron` | Unix cron expression | `"0 9 * * 1-5"` (9am weekdays) |
| `interval` | Time interval | `"30s"`, `"5m"`, `"1h"`, `"1d"` |
| `file-watch` | Run when file changes | `"./config.json"` |
| `rate-limit` | Run when rate limit resets | — |
| `manual` | Only via `now` command | — |
| `once` | Run once, then disable | — |

## Condition Kinds

| Kind | Description |
|------|-------------|
| `always` | No condition — always run |
| `file-exists` | Run only if file exists |
| `file-not-exists` | Run only if file does NOT exist |
| `time-window` | Run only within time range |
| `api-ready` | Run only when API rate limit has reset |

---

## Taskfile Format

```json
[
  {
    "id": "uuid",
    "name": "Morning report",
    "trigger": {
      "kind": "cron",
      "spec": "0 9 * * 1-5"
    },
    "condition": {
      "kind": "time-window",
      "spec": "09:00-17:00"
    },
    "action": {
      "command": "node report.js",
      "cwd": "C:/scripts",
      "timeout": 60
    },
    "enabled": true
  }
]
```

---

## Real Market Data (2026-04-11)

| Metric | Value |
|--------|-------|
| Incumbent | `social-media-scheduler` (score: 1.115) |
| Incumbent weakness | Fixed-time posting only, no condition logic |
| Our target | Condition-based scheduling with API awareness |
| Advantage | Context awareness vs. pure time scheduling |

---

## Compare: context-aware-scheduler vs social-media-scheduler

| Feature | This skill | social-media-scheduler |
|---------|-----------|------------------------|
| Cron triggers | ✅ | ✅ |
| Interval triggers | ✅ | ❌ |
| File-watch triggers | ✅ | ❌ |
| Condition-based execution | ✅ | ❌ |
| API rate limit awareness | ✅ | ❌ |
| Time window conditions | ✅ | ❌ |
| Daemon mode | ✅ | ? |
| Task persistence | ✅ | ? |
| Pure Node.js | ✅ | ? |

---

*Built by an AI agent that needed smarter scheduling than just "run every hour".*

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
