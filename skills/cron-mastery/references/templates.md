# Cron Examples & Templates

## One-Shot Reminder (Push Notification / Reliable)

**Context:** User says "Remind me to check the oven in 15 mins."
**Best for:** Timers that MUST ping the user's phone.

```json
{
  "action": "add",
  "job": {
    "name": "Oven Timer",
    "schedule": {
      "kind": "at",
      "at": "2026-02-16T21:15:00+02:00"
    },
    "payload": {
      "kind": "agentTurn",
      "message": "DELIVER THIS EXACT MESSAGE TO THE USER WITHOUT MODIFICATION OR COMMENTARY:\n\n🔥 OVEN CHECK! It's been 15 minutes."
    },
    "sessionTarget": "isolated",
    "delivery": {
      "mode": "announce",
      "channel": "telegram",
      "to": "1027899060"
    },
    "wakeMode": "now"
  }
}
```

## The Janitor (System Maintenance)

**Context:** Cleaning up finished one-shot jobs daily.
**Best for:** Running with full tool access in the main session.

```json
{
  "action": "add",
  "job": {
    "name": "Daily Cron Sweep",
    "schedule": {
      "kind": "every",
      "everyMs": 86400000
    },
    "payload": {
      "kind": "systemEvent",
      "text": "Time for the 24-hour cron sweep. List all cron jobs (includeDisabled: true). Delete any disabled jobs with lastStatus: ok. Report results."
    },
    "sessionTarget": "main",
    "wakeMode": "now"
  }
}
```

## Complex Task (Recurring/Async)

**Context:** User says "Summarize my emails every morning at 8 AM."

```json
{
  "action": "add",
  "job": {
    "name": "Morning Briefing",
    "schedule": {
      "kind": "cron",
      "expr": "0 8 * * *",
      "tz": "Africa/Cairo"
    },
    "payload": {
      "kind": "agentTurn",
      "message": "Good morning! Search for unread emails and top tech news, then summarize them."
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "delivery": {
      "mode": "announce",
      "channel": "telegram",
      "to": "1027899060"
    }
  }
}
```
