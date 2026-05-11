# OpenClaw Checkpoint - Personal AI Assistant Backup & Recovery

> Backup and disaster recovery for [OpenClaw](https://github.com/openclaw/openclaw) workspaces

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS | Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey.svg)]()

**Platform:** macOS and Linux only. Windows is not supported.

Automatically sync your OpenClaw agent's identity, memory, and configuration to GitHub. Never lose your agent's state again.

## What Gets Backed Up

| Backed Up | Not Backed Up (Security) |
|-----------|-------------------------|
| ✅ SOUL.md, IDENTITY.md, USER.md | ❌ API keys (.env.*) |
| ✅ MEMORY.md, memory/*.md | ❌ OAuth tokens |
| ✅ TOOLS.md, AGENTS.md, HEARTBEAT.md | ❌ Credentials |
| ✅ Custom scripts and tools | ❌ Temporary files |
| ✅ Cron jobs (memory/cron-jobs-backup.json) | |

## Quick Start

### Install (Recommended)

```bash
# Clone this repo
git clone https://github.com/AnthonyFrancis/openclaw-checkpoint.git ~/.openclaw/skills/openclaw-checkpoint

# Copy scripts to your tools directory
mkdir -p ~/.openclaw/workspace/tools
cp ~/.openclaw/skills/openclaw-checkpoint/scripts/checkpoint* ~/.openclaw/workspace/tools/
chmod +x ~/.openclaw/workspace/tools/checkpoint*

# Add to PATH (add to ~/.zshrc or ~/.bashrc for persistence)
export PATH="${HOME}/.openclaw/workspace/tools:${PATH}"

# Run setup
checkpoint-setup
```

The interactive wizard will:
1. Guide you through creating a **private** GitHub repo
2. Set up SSH authentication
3. Configure automatic backups
4. Test the backup system

### Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/AnthonyFrancis/openclaw-checkpoint/main/scripts/install-openclaw-checkpoint.sh | bash
```

This runs the install script -- review it first if you prefer to inspect before executing.

## Commands

| Command | Description |
|---------|-------------|
| `checkpoint` | Show all available commands |
| `checkpoint-setup` | Interactive first-time setup wizard |
| `checkpoint-backup` | Backup now |
| `checkpoint-restore` | Restore from backup (select checkpoint) |
| `checkpoint-auth` | Fix authentication issues |
| `checkpoint-status` | Check backup health |
| `checkpoint-schedule` | Configure auto-backup frequency |
| `checkpoint-stop` | Stop automatic backups |
| `checkpoint-reset` | Reset for fresh setup |

### Auto-Backup Options

```bash
checkpoint-schedule 15min    # Every 15 minutes
checkpoint-schedule 30min    # Every 30 minutes
checkpoint-schedule hourly   # Every hour (default)
checkpoint-schedule 2hours   # Every 2 hours
checkpoint-schedule daily    # Once per day
checkpoint-schedule disable  # Turn off
```

## Disaster Recovery

When your machine dies:

```bash
# On new machine:

# 1. Install checkpoint skill and restore interactively
curl -fsSL https://raw.githubusercontent.com/AnthonyFrancis/openclaw-checkpoint/main/scripts/install-openclaw-checkpoint.sh | bash
checkpoint-restore

# 2. Restore API keys from your password manager
# (secrets are not backed up for security)

# 3. Start OpenClaw
openclaw gateway start
```

`checkpoint-restore` guides you through authentication, lets you pick which checkpoint to restore, and offers to restore your cron jobs automatically.

### Restoring an Older Checkpoint

If you need to roll back to a previous checkpoint:

```bash
checkpoint-restore
```

You'll see a numbered list of recent checkpoints and can select the one to restore. Use `checkpoint-restore --latest` to skip the selection and restore the most recent checkpoint automatically.

## ⚠️ Security: Use a PRIVATE Repository

Your backup contains personal data:
- Agent identity and personality
- Conversation history and memories
- Personal notes and configurations

**Always use a private GitHub repository for your backup.**

## Requirements

- macOS or Linux (Windows is not supported)
- Git
- SSH key or GitHub Personal Access Token
- A **private** GitHub repository for storing backups

## Cron Job Backup & Restore

Each time you run `checkpoint-backup`, your OpenClaw cron jobs are automatically exported to `memory/cron-jobs-backup.json`. This means your scheduled tasks (morning briefs, daily syncs, automated workflows, etc.) are preserved alongside your workspace.

**Backup** happens automatically -- no extra steps needed. The checkpoint-backup command calls `openclaw cron list --json`, cleans the output to keep only configuration (not runtime state), and saves it to the backup file.

**Restore** happens automatically during `checkpoint-restore` -- it detects the backup file and offers to restore your cron jobs. If you prefer to restore manually:

```bash
# Manually inspect and recreate jobs:
cat ~/.openclaw/workspace/memory/cron-jobs-backup.json
```

**Requirements:**
- The `openclaw` CLI must be available on PATH
- The OpenClaw gateway must be running for cron backup and restore to succeed
- If either is unavailable, checkpoint-backup continues without cron backup (non-blocking)

## How It Works

1. **checkpoint-init** creates a git repo in `~/.openclaw/workspace`
2. **checkpoint-backup** exports cron jobs to JSON, then commits and pushes changes to GitHub
3. **checkpoint-schedule** sets up cron (Linux) or launchd (macOS) for auto-backups
4. **checkpoint-restore** lets you select and restore from any recent checkpoint on GitHub

## Security and Permissions

This skill uses standard system scheduling to automate backups:

- **macOS**: Creates a launchd plist at `~/Library/LaunchAgents/com.openclaw.checkpoint.plist`
- **Linux**: Adds a user-level cron job (visible via `crontab -l`)

Auto-backup is **opt-in only** -- it is never enabled unless you explicitly run `checkpoint-schedule`. You can disable it at any time with `checkpoint-stop` or `checkpoint-schedule disable`.

The skill does **not** install any background daemons, system services, or root-level processes. All scheduling runs under your user account.

**File access scope**: The skill only reads and writes within `~/.openclaw/workspace`. It does not access files outside this directory. Sensitive files (.env.*, credentials, OAuth tokens) are excluded from backups via .gitignore.

## Troubleshooting

<details>
<summary><strong>"Not a git repository"</strong></summary>

Run `checkpoint-setup` for guided setup, or `checkpoint-init` to initialize manually.
</details>

<details>
<summary><strong>"Failed to push checkpoint"</strong></summary>

Another machine pushed changes. Run `checkpoint-restore` first, then `checkpoint-backup`.

If you restored an older checkpoint and then ran `checkpoint-backup`, the push will detect the diverged history and ask if you want to force push.
</details>

<details>
<summary><strong>GitHub prompting for password</strong></summary>

GitHub no longer accepts passwords. Switch to SSH:
```bash
cd ~/.openclaw/workspace
git remote set-url origin git@github.com:USER/REPO.git
```
</details>

<details>
<summary><strong>"Permission denied (publickey)"</strong></summary>

Your SSH key isn't added to GitHub. Run `checkpoint-auth` to set up SSH authentication.
</details>

## About

This is a community skill for [OpenClaw](https://github.com/openclaw/openclaw), an AI agent framework. It's not officially affiliated with the OpenClaw project.

## License

MIT
