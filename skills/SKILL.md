---
name: openclaw-guardian
description: Deploy and manage a Guardian watchdog process for OpenClaw Gateway. Provides automated health monitoring, self-repair via `doctor --fix`, git-based workspace rollback, daily snapshots, and optional Discord alerting. Use when a user wants to harden their OpenClaw instance against crashes, config corruption, or bad workspace edits — or when setting up Guardian for the first time on a new server/container.
---

# OpenClaw Guardian

Guardian is a standalone bash watchdog that keeps OpenClaw Gateway alive 24/7.

**Repair ladder:**
1. Detect Gateway down (every 30s)
2. Run `openclaw doctor --fix` (up to 3 attempts)
3. If still down → `git reset --hard` to last stable commit, restart Gateway
4. If all fails → cooldown 300s, resume monitoring
5. Daily automatic git snapshot of workspace

## Setup Steps

### 1. Initialize git (required for rollback)

```bash
cd ~/.openclaw/workspace
git config --global user.email "guardian@example.com"
git config --global user.name "Guardian"
git init && git add -A && git commit -m "initial"
```

Skip if repo already exists. Without git, doctor --fix still works; rollback is skipped.

### 2. Install guardian.sh

Copy `scripts/guardian.sh` from this skill to `~/.openclaw/guardian.sh`:

```bash
cp scripts/guardian.sh ~/.openclaw/guardian.sh
chmod +x ~/.openclaw/guardian.sh
```

### 3. Start Guardian

**Container / no systemd (nohup):**
```bash
nohup ~/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

**Linux VPS with systemd:** See `references/setup.md` → Pattern B.

### 4. Auto-start on container restart

Add to `~/.openclaw/start-gateway.sh` (before the final `exec` line):
```bash
pkill -f "guardian.sh" 2>/dev/null || true
nohup /home/ubuntu/.openclaw/guardian.sh >> /tmp/openclaw-guardian.log 2>&1 &
```

### 5. Optional: Discord alerts

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

Or add to `start-gateway.sh` as a persistent export.

## Verify

```bash
pgrep -a -f "guardian.sh"          # confirm process running
tail -f /tmp/openclaw-guardian.log  # watch live logs
```

## Configuration

All settings via environment variables. Defaults work out of the box.
See `references/setup.md` for full variable reference, systemd config, and architecture diagram.

## Notes

- Guardian coexists with `gw-watchdog.sh` — run both for layered resilience
- Rollback targets the 2nd-newest non-auto commit (skips daily-backup, rollback, auto-backup commits)
- Log path: `/tmp/openclaw-guardian.log`
