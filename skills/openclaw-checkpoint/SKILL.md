---
name: openclaw-checkpoint
description: Backup and restore OpenClaw workspace state and agents across machines using git. Enables disaster recovery by syncing SOUL.md, MEMORY.md, memory files, cron jobs, agents (~/.openclaw/agents/), and configuration to a remote repository. Use when user wants to checkpoint their OpenClaw state, restore on a new machine, migrate between computers, or protect against data loss. Provides commands checkpoint (help overview), checkpoint-setup (interactive onboarding), checkpoint-backup, checkpoint-restore (with interactive checkpoint selection or --latest for most recent), checkpoint-schedule (auto-backup), checkpoint-stop, checkpoint-status, checkpoint-init, and checkpoint-reset. Supports multi-agent backup with flags --workspace-only, --agents-only, and --agent <name>. Automatically backs up cron jobs to memory/cron-jobs-backup.json on each checkpoint-backup.
---

# OpenClaw Checkpoint Skill

Backup and restore your OpenClaw identity, memory, agents, and configuration across machines.

**Platform:** macOS and Linux only. Windows is not supported.

## Overview

This skill provides disaster recovery for OpenClaw by syncing your workspace and agents to a git repository. It preserves:

- **Identity**: SOUL.md, IDENTITY.md, USER.md (who you and the assistant are)
- **Memory**: MEMORY.md and memory/*.md files (conversation history and context)
- **Cron Jobs**: Scheduled tasks exported to memory/cron-jobs-backup.json (morning briefs, daily syncs, automations)
- **Configuration**: TOOLS.md, AGENTS.md, HEARTBEAT.md (tool setups and conventions)
- **Scripts**: Custom tools and automation you've built
- **Agents**: All agent folders from ~/.openclaw/agents/ (alex, blake, etc.)

**Not synced** (security): API keys (.env.*), credentials, OAuth tokens

## Installation

### Option 1: Git Clone (Recommended)

```bash
# Clone the skill repo
git clone https://github.com/AnthonyFrancis/openclaw-checkpoint.git ~/.openclaw/skills/openclaw-checkpoint

# Copy scripts to tools directory
mkdir -p ~/.openclaw/workspace/tools
cp ~/.openclaw/skills/openclaw-checkpoint/scripts/checkpoint* ~/.openclaw/workspace/tools/
chmod +x ~/.openclaw/workspace/tools/checkpoint*

# Add to PATH (also add to ~/.zshrc or ~/.bashrc for persistence)
export PATH="${HOME}/.openclaw/workspace/tools:${PATH}"

# Run setup wizard
checkpoint-setup
```

### Option 2: Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/AnthonyFrancis/openclaw-checkpoint/main/scripts/install-openclaw-checkpoint.sh | bash
```

This runs the install script -- review it first if you prefer to inspect before executing.

## Commands

### checkpoint
**Show all available commands and usage examples.**

```bash
checkpoint
```

**What it does:**
- Displays a quick reference of all checkpoint commands with descriptions and examples

**When to use:**
- When you can't remember the exact command name
- Quick reference for available options

### checkpoint-setup
**Interactive onboarding flow for first-time setup.**

```bash
checkpoint-setup
```

**What it does:**
- Guides you through creating a PRIVATE GitHub repository
- Sets up SSH authentication (recommended) or Personal Access Token
- Automatically detects if SSH key is already authorized on GitHub
- Detects agents in `~/.openclaw/agents/` and reports they will be included in backups
- Generates a README.md with recovery instructions and commands
- Commits workspace files within `~/.openclaw/workspace` (secrets excluded via .gitignore)
- Configures automatic backups
- Tests the backup system
- Shows final status

**When to use:**
- First time setting up checkpoint system
- After installing the skill
- After running `checkpoint-reset`
- Recommended starting point for new users

### checkpoint-auth
**Authenticate with GitHub (browser-based).**

```bash
checkpoint-auth
```

**What it does:**
- Option 1: GitHub CLI (opens browser automatically)
- Option 2: Personal Access Token (expires, needs renewal)
- Option 3: SSH Key (recommended - no token expiry)
- Automatically adds GitHub to known_hosts
- Tests authentication after setup

**When to use:**
- Authentication expired or failed
- Switching authentication methods
- Setting up on a new machine

**SSH is recommended** because:
- No token expiration to worry about
- Works reliably without password prompts
- GitHub no longer accepts password authentication for HTTPS

### checkpoint-backup
Save current state to remote repository.

```bash
checkpoint-backup                     # Backup workspace + all agents
checkpoint-backup --workspace-only    # Backup workspace only (skip agents)
checkpoint-backup --agents-only       # Backup agents only (skip workspace/cron)
checkpoint-backup --agent alex        # Backup only the 'alex' agent (+ workspace)
```

**What it does:**
- Backs up OpenClaw cron jobs to `memory/cron-jobs-backup.json` (requires `openclaw` CLI and running gateway)
- Copies agent folders from `~/.openclaw/agents/` into `agents/` in the workspace repo (strips nested `.git` dirs)
- Normalizes home-directory paths (`$HOME` -> `{{HOME}}`) for cross-machine portability
- Commits all changes in ~/.openclaw/workspace
- Pushes to origin/main
- Shows commit hash and timestamp

**Agent backup details:**
- Auto-detects agents in `~/.openclaw/agents/` (e.g., alex, blake)
- Each agent folder is copied to `agents/<name>/` in the backup repo
- Nested `.git` directories are removed to avoid submodule issues
- If no agents exist, skips gracefully with an info message
- Uses `rsync --exclude='.git'` when available, falls back to `cp -r` + manual `.git` removal

**Cron job backup details:**
- Runs `openclaw cron list --json` to export all scheduled tasks
- Strips runtime state, keeps only configuration (name, schedule, target, payload)
- Non-blocking: if the CLI or gateway is unavailable, checkpoint-backup continues without cron backup

**Flags:**
- `--workspace-only` — skip agent backup
- `--agents-only` — skip workspace and cron backup, only back up agents
- `--agent <name>` — back up a single named agent only

**When to use:**
- Before switching computers
- After significant changes (new memory, updated SOUL.md)
- Any time you want to ensure changes are saved

### checkpoint-schedule
Set up automatic backups with configurable frequency.

```bash
checkpoint-schedule 15min      # Every 15 minutes
checkpoint-schedule 30min      # Every 30 minutes
checkpoint-schedule hourly     # Every hour (default)
checkpoint-schedule 2hours     # Every 2 hours
checkpoint-schedule 4hours     # Every 4 hours
checkpoint-schedule daily      # Once per day at 9am
checkpoint-schedule disable    # Turn off auto-backup
```

**What it does:**
- macOS: Creates launchd plist for reliable background backups
- Linux: Adds cron job for scheduled backups
- Logs all activity to ~/.openclaw/logs/checkpoint.log

**When to use:**
- First time setup: `checkpoint-schedule hourly`
- Change frequency: `checkpoint-schedule 15min`
- Stop backups: `checkpoint-schedule disable`

### checkpoint-status
Check backup health and status.

```bash
checkpoint-status
```

**What it shows:**
- Last backup time and commit
- Whether local is behind remote
- Uncommitted changes
- Agent backup status (which agents are backed up, which are missing)
- Auto-backup schedule status
- Recent backup activity log

**When to use:**
- Before switching machines (verify synced)
- Troubleshooting backup issues
- Regular health checks

### checkpoint-restore
Restore state from remote repository, with checkpoint selection and first-time onboarding.

```bash
checkpoint-restore                    # Select from recent checkpoints (interactive)
checkpoint-restore --latest           # Restore most recent checkpoint (skip selection)
checkpoint-restore --force            # Discard local changes before restoring
checkpoint-restore --workspace-only   # Restore workspace only (skip agents)
checkpoint-restore --agents-only      # Restore agents only (skip workspace/cron)
checkpoint-restore --agent alex       # Restore only the 'alex' agent
```

**What it does:**
- **First-time users:** Launches interactive restore onboarding flow
  - Guides you through GitHub authentication (SSH, GitHub CLI, or PAT)
  - Lets you specify your existing backup repository
  - Verifies access and restores your checkpoint
  - Handles merge/replace options if local files exist
  - Shows available checkpoints to pick from (if the repo has more than one commit)
  - Offers to restore cron jobs from backup
  - Offers to restore agents from backup
- **Returning users:** Shows a list of the 10 most recent checkpoints to choose from
  - Pick the latest or any older checkpoint to restore
  - Current checkpoint is marked in the list
  - Restoring an older checkpoint warns that the next backup will overwrite newer remote checkpoints
  - Use `--latest` flag to skip the interactive selection and restore the most recent checkpoint automatically
- **Uncommitted changes:** If you have local uncommitted changes, you're prompted to:
  1. Save changes first (runs `checkpoint-backup`)
  2. Discard local changes and continue restoring
  3. Cancel
- **Path portability:** Automatically expands `{{HOME}}` placeholders and rewrites old home-directory paths for the current machine
- **Cron jobs:** Automatically offers to restore cron jobs from `memory/cron-jobs-backup.json` after restoring (requires OpenClaw gateway to be running)
- **Agents:** Offers to restore agents from `agents/` directory in the backup to `~/.openclaw/agents/`

**Flags:**
- `--latest` — skip selection, restore most recent checkpoint
- `--force` — discard local changes without prompting
- `--workspace-only` — skip agent restore
- `--agents-only` — skip workspace and cron restore, only restore agents
- `--agent <name>` — restore a single named agent only

**When to use:**
- Starting OpenClaw on a new machine
- After hardware failure/disaster
- When resuming work on different computer
- First-time restore from an existing backup
- Rolling back to a previous checkpoint after unwanted changes

**Onboarding flow triggers when:**
- No workspace exists
- Workspace exists but not a git repository
- Git repository exists but no remote configured

### checkpoint-init
Initialize workspace for checkpoint system.

```bash
checkpoint-init
```

**What it does:**
- Creates git repository in ~/.openclaw/workspace
- Generates .gitignore (excludes secrets and ephemeral files)
- Creates initial commit

**When to use:**
- First time setting up checkpoint system
- After restoring from backup to new machine

### checkpoint-reset
Reset checkpoint system for fresh setup.

```bash
checkpoint-reset
```

**What it does:**
- Option 1: Removes local git repository only (keeps SSH keys)
- Option 2: Removes everything (git repo + SSH keys + GitHub from known_hosts)
- Offers to remove backed-up agent copies from workspace `agents/` folder
- Reminds you to delete the GitHub repo manually

Note: Reset never touches your actual agent folders in `~/.openclaw/agents/` -- only the backup copies.

**When to use:**
- Starting over with a fresh setup
- Switching to a different GitHub repository
- Troubleshooting persistent authentication issues

### checkpoint-stop
Stop automatic backups.

```bash
checkpoint-stop
```

**What it does:**
- Disables scheduled automatic backups
- Removes cron job (Linux) or launchd agent (macOS)

**When to use:**
- Temporarily pausing backups
- Before making major workspace changes
- If backups are causing issues

**To restart:** `checkpoint-schedule hourly` (or any frequency)

## Setup

### Easy Setup (Recommended)

Just run the interactive wizard:

```bash
checkpoint-setup
```

This handles everything: git init, SSH keys, GitHub setup, and first backup.

### First Time Setup (Manual)

```bash
# 1. Initialize checkpoint system
checkpoint-init

# 2. Create PRIVATE GitHub repository
# Go to https://github.com/new
# Name: openclaw-state
# ⚠️  Visibility: PRIVATE (important - contains your personal data!)

# 3. Add remote (use SSH, not HTTPS)
cd ~/.openclaw/workspace
git remote add origin git@github.com:YOURUSER/openclaw-state.git
checkpoint-backup
```

### Setup on Second Machine

**Option 1: Interactive Restore (Recommended)**

```bash
# Install the checkpoint skill first
curl -fsSL https://raw.githubusercontent.com/AnthonyFrancis/openclaw-checkpoint/main/scripts/install-openclaw-checkpoint.sh | bash

# Run checkpoint-restore - it will guide you through the entire process
checkpoint-restore
```

This will:
- Help you authenticate with GitHub (if not already)
- Ask for your backup repository details
- Clone/restore your checkpoint automatically

**Option 2: Manual Clone**

```bash
# 1. Clone repository (use SSH)
git clone git@github.com:YOURUSER/openclaw-state.git ~/.openclaw/workspace

# 2. Restore secrets from 1Password/password manager
# Create ~/.openclaw/workspace/.env.thisweek
# Create ~/.openclaw/workspace/.env.stripe
# (Copy from secure storage)

# 3. Start OpenClaw
openclaw gateway start
```

## Automated Backups

### Easy Setup (Recommended)

```bash
# Enable hourly backups
checkpoint-schedule hourly

# Or choose your frequency:
checkpoint-schedule 15min   # Every 15 minutes - high activity
checkpoint-schedule 30min   # Every 30 minutes - medium activity  
checkpoint-schedule 2hours  # Every 2 hours - low activity
checkpoint-schedule daily   # Once per day - minimal activity
```

### Check Status

```bash
checkpoint-status
```

Shows:
- Last backup time
- Whether synced with remote
- Auto-backup schedule
- Recent activity log

## Multi-Agent Backup

The checkpoint system automatically detects and backs up all agents from `~/.openclaw/agents/`.

### How It Works

- On **backup**: Agent folders are copied from `~/.openclaw/agents/` into `agents/` inside the backup repo, with nested `.git` directories stripped
- On **restore**: Agent folders are copied from `agents/` in the backup repo back to `~/.openclaw/agents/`
- If no agents exist, all commands skip agent handling gracefully

### File Structure in Backup Repo

```
~/.openclaw/workspace/          (backup repo root)
  SOUL.md
  MEMORY.md
  memory/
  agents/                       (auto-created when agents exist)
    alex/                       (copied from ~/.openclaw/agents/alex/)
    blake/                      (copied from ~/.openclaw/agents/blake/)
```

### Agent Flags

These flags work on `checkpoint-backup` and `checkpoint-restore`:

| Flag | Description |
|------|-------------|
| `--workspace-only` | Skip agent backup/restore entirely |
| `--agents-only` | Skip workspace and cron, only operate on agents |
| `--agent <name>` | Operate on a single named agent only |

### Examples

```bash
# Backup everything (default)
checkpoint-backup

# Backup only agents
checkpoint-backup --agents-only

# Backup only the 'alex' agent
checkpoint-backup --agent alex

# Restore workspace but skip agents
checkpoint-restore --latest --workspace-only

# Restore only agents from backup
checkpoint-restore --agents-only

# Check which agents are backed up
checkpoint-status
```

### Backwards Compatibility

- If `~/.openclaw/agents/` does not exist or is empty, all commands skip agent handling with an info message
- Old backup repos without an `agents/` directory work fine -- restore simply skips agents
- No existing behavior changes when no agents are present

## Cross-Machine Portability

When you back up on one machine (e.g. `/Users/jerry`) and restore on another (e.g. `/Users/tom`), hardcoded absolute home-directory paths in workspace files would break. The checkpoint system handles this automatically.

### How It Works

- **On backup:** All occurrences of your `$HOME` path (e.g. `/Users/jerry`) are replaced with the placeholder `{{HOME}}` in text files. A `.checkpoint-meta.json` file is written with the source machine's details.
- **On restore:** The `{{HOME}}` placeholder is expanded to the current machine's `$HOME` (e.g. `/Users/tom`). For backwards compatibility with older backups that were created before normalization, any remaining literal old home paths are also rewritten.

### What Gets Processed

Only text files likely to contain paths are scanned:
- `*.md`, `*.json`, `*.sh`, `*.txt`, `*.yaml`, `*.yml`, `*.toml`, `*.cfg`, `*.conf`

Binary files, `.git/`, and `node_modules/` are never touched.

### .checkpoint-meta.json

This file is auto-generated on each backup and records the source machine:

```json
{
  "source_home": "/Users/jerry",
  "source_user": "jerry",
  "hostname": "Jerrys-MacBook-Pro"
}
```

On restore, this metadata tells the script which old paths to rewrite. The file is updated after restore to reflect the current machine.

### Manual Cron Setup (Advanced)

If you prefer manual cron:

```bash
# Edit crontab
crontab -e

# Add line for hourly backups:
0 * * * * /Users/$(whoami)/.openclaw/workspace/skills/openclaw-checkpoint/scripts/checkpoint-backup >> ~/.openclaw/logs/checkpoint.log 2>&1
```

## Disaster Recovery Workflow

**Scenario: Home server dies**

```bash
# On new machine:

# 1. Install OpenClaw
brew install openclaw  # or your install method

# 2. Install checkpoint skill and run interactive restore
curl -fsSL https://raw.githubusercontent.com/AnthonyFrancis/openclaw-checkpoint/main/scripts/install-openclaw-checkpoint.sh | bash
checkpoint-restore
# Follow the interactive prompts to:
# - Authenticate with GitHub
# - Enter your backup repository (e.g., YOURUSER/openclaw-state)
# - Restore your checkpoint

# 3. Restore secrets from 1Password (API keys are not backed up for security)
cat > ~/.openclaw/workspace/.env.thisweek << 'EOF'
THISWEEK_API_KEY=your_key_here
EOF

# 4. Start OpenClaw
openclaw gateway start

# 5. Cron jobs are restored automatically during checkpoint-restore
# (if the gateway is running and cron backup exists)

# 6. Enable automatic backups on this machine
checkpoint-schedule hourly

# 7. Verify
# Ask assistant: "What were we working on?"
# Should recall everything up to last checkpoint, with all scheduled tasks restored
```

## Security Considerations

### ⚠️ CRITICAL: Repository MUST be PRIVATE

Your backup contains sensitive personal data:
- SOUL.md, MEMORY.md (your identity & memories)
- Personal notes and conversation history
- Custom scripts and configurations

**If you make the repo public, anyone can see your data!**

**What gets backed up:**
- ✅ Memory files (conversation history)
- ✅ Identity files (SOUL.md, etc.)
- ✅ Cron jobs (memory/cron-jobs-backup.json)
- ✅ Scripts and tools
- ✅ Configuration
- ✅ Agents (~/.openclaw/agents/ -> agents/ in backup repo)

**What does NOT get backed up:**
- ❌ API keys (.env.*) — keep in 1Password
- ❌ OAuth tokens — re-authenticate on new machine
- ❌ Downloaded media — ephemeral
- ❌ Temporary files — ephemeral

**Best practices:**
- **Always use a PRIVATE repository**
- Use SSH authentication (no token expiry)
- Store API keys in password manager, not in backed-up files
- Enable 2FA on GitHub account
- Consider encrypting sensitive notes before adding to memory

### Permissions and Scheduling

This skill uses standard system scheduling to automate backups:

- **macOS**: Creates a launchd plist at `~/Library/LaunchAgents/com.openclaw.checkpoint.plist`
- **Linux**: Adds a user-level cron job (visible via `crontab -l`)

Auto-backup is **opt-in only** -- it is never enabled unless you explicitly run `checkpoint-schedule`. You can disable it at any time with `checkpoint-stop` or `checkpoint-schedule disable`.

The skill does **not** install any background daemons, system services, or root-level processes. All scheduling runs under your user account.

**File access scope**: The skill reads from `~/.openclaw/workspace` and `~/.openclaw/agents/` (for multi-agent backup). It writes backup copies of agents into `~/.openclaw/workspace/agents/`. On restore, it copies agents back to `~/.openclaw/agents/`. Sensitive files (.env.*, credentials, OAuth tokens) are excluded from backups via .gitignore.

## Troubleshooting

### "Not a git repository" or "'origin' does not appear to be a git repository"
Running `checkpoint-restore` will now automatically start the interactive restore onboarding flow to help you connect to your backup repository. Alternatively, run `checkpoint-setup` to create a new backup from scratch.

### "Failed to push checkpoint"
Another machine pushed changes. Run `checkpoint-restore` first, then `checkpoint-backup`.

### "You have uncommitted changes"
`checkpoint-restore` will prompt you to choose:
1. Save changes first (runs `checkpoint-backup`)
2. Discard local changes and continue
3. Cancel

You can also skip the prompt with `checkpoint-restore --force` to discard changes directly.

### Behind remote after restore
This is expected if another machine checkpointed since you last synced.

### GitHub prompting for username/password
GitHub no longer accepts password authentication for HTTPS. Switch to SSH:
```bash
cd ~/.openclaw/workspace
git remote set-url origin git@github.com:YOURUSER/REPO.git
```

### "Host key verification failed"
GitHub's SSH host key isn't in your known_hosts. Fix with:
```bash
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts
```

### "Permission denied (publickey)"
Your SSH key isn't added to GitHub. Run `checkpoint-auth` and choose SSH option.

### GitHub repo is empty after setup
The old `checkpoint-init` only committed `.gitignore`. This is fixed now. Run:
```bash
cd ~/.openclaw/workspace && git add -A && git commit -m "Full backup" && git push
```

### Starting fresh
Run `checkpoint-reset` to remove local git repo and optionally SSH keys, then `checkpoint-setup`.

### Agents not being backed up
Check that your agents are in `~/.openclaw/agents/` (not somewhere else). Run `checkpoint-status` to see which agents are detected and which are backed up. Make sure you're not passing `--workspace-only`.

### Agent has nested .git errors
The backup process automatically strips `.git` directories from agent copies. If you see submodule warnings, run a fresh backup:
```bash
rm -rf ~/.openclaw/workspace/agents
checkpoint-backup
```

### Restored agents missing files
Agent restore copies the backup as-is. If the backup was taken before certain files were added to the agent, those files won't be present. Run `checkpoint-backup` on the source machine first to capture the latest state.

### "Permission denied, mkdir '/Users/olduser'" after restoring on a new machine
This means files contain hardcoded paths from the original machine. If the backup was created before path normalization was added, run:
```bash
cd ~/.openclaw/workspace
grep -rl "/Users/olduser" --include="*.md" --include="*.json" --include="*.sh" | \
  xargs sed -i '' "s|/Users/olduser|$HOME|g"
```
Future backups will normalize paths automatically.

### Files show {{HOME}} instead of real paths
This is expected **in the backup repo on GitHub**. The `{{HOME}}` placeholder is replaced with the real `$HOME` path on each restore. If you see `{{HOME}}` in your local workspace after a restore, run `checkpoint-restore --latest` again.

## Limitations

- **Single machine at a time**: Don't run OpenClaw on multiple machines simultaneously
- **Max data loss**: 1 hour if using hourly backups (cron)
- **Secrets not synced**: Must restore API keys manually on new machine
- **Large files**: GitHub has 100MB file limit (your text files are fine)

## File Reference

See [references/setup.md](references/setup.md) for detailed setup instructions.
