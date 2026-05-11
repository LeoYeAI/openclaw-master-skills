---
name: openclaw-backup
description: Backup and restore OpenClaw data. Use when user asks to create backups, set up automatic backup schedules, restore from backup, or manage backup rotation. Handles ~/.openclaw directory archiving with proper exclusions.
---

# OpenClaw Backup

Backup and restore OpenClaw configuration, credentials, and workspace.

## Create Backup

Run the backup script:

```bash
./scripts/backup.sh [backup_dir]
```

Default backup location: `~/openclaw-backups/`

Output: `openclaw-YYYY-MM-DD_HHMM.tar.gz`

## What Gets Backed Up

- `openclaw.json` — main config
- `credentials/` — API keys, tokens
- `agents/` — agent configs, auth profiles
- `workspace/` — memory, SOUL.md, user files
- `telegram/` — session data
- `cron/` — scheduled tasks

## Excluded

- `completions/` — cache, regenerated automatically
- `*.log` — logs

## Setup Daily Backup with Cron

Use OpenClaw cron for daily backups with notification:

```json
{
  "name": "daily-backup",
  "schedule": {"kind": "cron", "expr": "0 3 * * *", "tz": "UTC"},
  "payload": {
    "kind": "agentTurn",
    "message": "Run ~/.openclaw/backup.sh and report result to user."
  },
  "sessionTarget": "isolated",
  "delivery": {"mode": "announce"}
}
```

## Restore

See [references/restore.md](references/restore.md) for step-by-step restore instructions.

Quick restore:

```bash
openclaw gateway stop
mv ~/.openclaw ~/.openclaw-old
tar -xzf ~/openclaw-backups/openclaw-YYYY-MM-DD_HHMM.tar.gz -C ~
openclaw gateway start
```

## Rotation

Script keeps last 7 backups automatically.
