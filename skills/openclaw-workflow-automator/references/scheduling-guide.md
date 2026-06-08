# Scheduling Guide

## Overview

OpenClaw supports cron-based scheduling for workflows. The agent converts
natural language schedule descriptions into cron expressions and manages
the full lifecycle of scheduled workflows.

## Cron Syntax Reference

```
┌───────── minute (0-59)
│ ┌─────── hour (0-23)
│ │ ┌───── day of month (1-31)
│ │ │ ┌─── month (1-12)
│ │ │ │ ┌─ day of week (0-7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * *
```

### Common Expressions

| Natural Language | Cron Expression |
|-----------------|-----------------|
| Every Monday at 8am | `0 8 * * 1` |
| Daily at midnight | `0 0 * * *` |
| Every 6 hours | `0 */6 * * *` |
| First of every month at 10am | `0 10 1 * *` |
| Weekdays at 9am | `0 9 * * 1-5` |
| Every Sunday at 6pm | `0 18 * * 0` |
| Every 15 minutes | `*/15 * * * *` |
| Every hour on the half-hour | `30 * * * *` |
| Quarterly (Jan, Apr, Jul, Oct 1st) | `0 9 1 1,4,7,10 *` |

### Special Strings

| String | Equivalent |
|--------|-----------|
| `@hourly` | `0 * * * *` |
| `@daily` | `0 0 * * *` |
| `@weekly` | `0 0 * * 0` |
| `@monthly` | `0 0 1 * *` |
| `@yearly` | `0 0 1 1 *` |

## Schedule Types

### Run Now
No cron expression. Execute immediately, no schedule file created.

### One-Time Schedule
The agent creates a cron job that fires once and then removes itself.
Example: "Run this tomorrow at 3pm" creates a one-shot entry that
auto-deletes after execution.

### Recurring Schedule
Standard cron job that fires repeatedly. The agent creates the schedule
file and registers it with OpenClaw's cron system.

### Conditional Recurring
A recurring schedule where the first step of the workflow is a condition
check. If the condition is false, the workflow skips silently.
Example: "Every Monday, but skip holidays" — Step 1 checks a holiday
calendar before proceeding.

## Schedule File Format

Stored in `~/.openclaw/workflow-automator/schedules/<workflow-slug>.json`:

```json
{
  "workflow_name": "Monday Report",
  "workflow_slug": "monday-report",
  "description": "Generate weekly sales report from Stripe dashboard",
  "cron_expression": "0 8 * * 1",
  "timezone": "America/Chicago",
  "steps": [
    {
      "number": 1,
      "description": "Navigate to Stripe dashboard",
      "type": "browser-navigate",
      "input": "https://dashboard.stripe.com",
      "output": "page loaded"
    }
  ],
  "last_run": "2026-03-17T08:00:00Z",
  "last_run_status": "success",
  "next_run": "2026-03-24T08:00:00Z",
  "status": "active",
  "notification_channel": "telegram",
  "escalation": null,
  "approval_mode": false,
  "created_at": "2026-03-10T14:30:00Z",
  "updated_at": "2026-03-10T14:30:00Z"
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `active` | Cron is registered and will fire on schedule |
| `paused` | Cron is disabled but schedule file preserved |
| `cancelled` | Cron removed, schedule file kept for history |
| `awaiting-auth` | Paused because credentials expired; waiting for user |
| `failed` | Last run failed and awaiting user response |

## Schedule Management Commands

The agent responds to these conversational commands:

| User Says | Agent Does |
|-----------|-----------|
| "What workflows are scheduled?" | Lists all schedule files with status and next run |
| "Pause the Monday report" | Sets status to `paused`, disables cron |
| "Resume the Monday report" | Sets status to `active`, re-enables cron |
| "Change it to Tuesday at 9am" | Updates cron expression, recalculates next_run |
| "Cancel the daily check" | Sets status to `cancelled`, removes cron |
| "Run the Monday report now" | Executes workflow immediately, schedule unchanged |
| "Switch Monday report to approval mode" | Sets `approval_mode: true` |

## Timezone Handling

- The agent asks for timezone during workflow setup if schedule involves
  a specific time of day
- Stored as IANA timezone string (e.g., "America/Chicago")
- Cron expressions are evaluated in the specified timezone
- The agent shows both local time and UTC when presenting schedules

## Run Logs

Each execution (scheduled or manual) creates a log file in
`~/.openclaw/workflow-automator/runs/<workflow-slug>/<timestamp>.json`:

```json
{
  "workflow_name": "Monday Report",
  "trigger": "scheduled",
  "started_at": "2026-03-17T08:00:01Z",
  "completed_at": "2026-03-17T08:02:45Z",
  "status": "success",
  "steps": [
    {
      "number": 1,
      "status": "success",
      "duration_seconds": 3.2,
      "output_summary": "Page loaded: Stripe Dashboard"
    }
  ],
  "notification_sent": true,
  "notification_channel": "telegram"
}
```
