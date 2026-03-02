# OpenClaw Guardian - Setup & Configuration Reference

## Environment Variables

All variables are optional with sensible defaults:

| Variable | Default | Description |
|---|---|---|
| `GUARDIAN_WORKSPACE` | `$HOME/.openclaw/workspace` | Path to workspace git repo |
| `GUARDIAN_LOG` | `/tmp/openclaw-guardian.log` | Log file path |
| `GUARDIAN_CHECK_INTERVAL` | `30` | Health check interval in seconds |
| `GUARDIAN_MAX_REPAIR` | `3` | Max doctor --fix attempts before rollback |
| `GUARDIAN_COOLDOWN` | `300` | Cooldown period (seconds) after all repairs fail |
| `DISCORD_WEBHOOK_URL` | _(unset)_ | Discord webhook URL for alerts (optional) |
| `OPENCLAW_CMD` | `openclaw` | OpenClaw CLI command |

## Deployment Patterns

### Pattern A: nohup (container / no systemd)
Used when systemd user sessions are unavailable (e.g., Docker containers).

```bash
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

Integrate into `start-gateway.sh` so it auto-starts on container restart:
```bash
pkill -f "guardian.sh" 2>/dev/null || true
nohup /home/ubuntu/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### Pattern B: systemd user service (Linux desktop / VPS)

Create `~/.config/systemd/user/openclaw-guardian.service`:
```ini
[Unit]
Description=OpenClaw Guardian

[Service]
ExecStart=/path/to/guardian.sh
Restart=always

[Install]
WantedBy=default.target
```

Enable:
```bash
systemctl --user daemon-reload
systemctl --user enable --now openclaw-guardian.service
```

## Git Initialization (Required for Rollback)

Guardian's rollback feature requires a git repo in the workspace:

```bash
cd ~/.openclaw/workspace
git config --global user.email "guardian@example.com"
git config --global user.name "Guardian"
git init && git add -A && git commit -m "initial"
```

Without git, Guardian still monitors and runs `doctor --fix` — rollback is simply skipped.

## How Repair Works

```
Gateway down detected
        │
        ▼
  doctor --fix  ──→ success? ──→ Done ✅
  (up to N times)
        │ all failed
        ▼
   git rollback  ──→ success? ──→ Done ✅
        │ failed
        ▼
  cooldown period
        │
        ▼
  resume monitoring
```

## Daily Backup

Guardian creates a daily git snapshot automatically:
- Commit message: `daily-backup: auto snapshot YYYY-MM-DD`
- Tracked in `/tmp/guardian-last-backup`
- These commits are excluded from rollback targets

## Coexistence with gw-watchdog

Guardian is designed to complement, not replace, `gw-watchdog.sh`:

| | gw-watchdog | guardian |
|---|---|---|
| Check interval | 15s | 30s |
| Action | Fast restart | doctor --fix → rollback |
| Git rollback | No | Yes |
| Discord alerts | No | Yes |
| Daily backup | No | Yes |

Run both for layered resilience.

## Viewing Logs

```bash
tail -f /tmp/openclaw-guardian.log
```

## Checking Status

```bash
pgrep -a -f "guardian.sh"
```
