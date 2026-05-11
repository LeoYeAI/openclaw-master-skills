# Restore OpenClaw from Backup

## Quick Restore

```bash
# 1. Stop OpenClaw
openclaw gateway stop

# 2. Backup current (safety)
mv ~/.openclaw ~/.openclaw-old

# 3. Extract backup
cd ~
tar -xzf ~/openclaw-backups/openclaw-YYYY-MM-DD_HHMM.tar.gz

# 4. Start OpenClaw
openclaw gateway start

# 5. Verify
openclaw status
```

## Rollback if Restore Fails

```bash
rm -rf ~/.openclaw
mv ~/.openclaw-old ~/.openclaw
openclaw gateway start
```

## What's in a Backup

```
~/.openclaw/
├── openclaw.json      # Main config
├── credentials/       # API keys, tokens
├── agents/            # Agent configs, auth
├── workspace/         # Memory, SOUL.md, files
├── telegram/          # Telegram session
└── cron/              # Scheduled tasks
```

## Excluded from Backup

- `completions/` — API response cache (regenerated)
- `*.log` — Log files
