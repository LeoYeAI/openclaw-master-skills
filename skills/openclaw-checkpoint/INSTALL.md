# Installation

## Git Clone (Recommended)

```bash
git clone https://github.com/AnthonyFrancis/openclaw-checkpoint.git ~/.openclaw/skills/openclaw-checkpoint

mkdir -p ~/.openclaw/workspace/tools
cp ~/.openclaw/skills/openclaw-checkpoint/scripts/checkpoint* ~/.openclaw/workspace/tools/
chmod +x ~/.openclaw/workspace/tools/checkpoint*

export PATH="${HOME}/.openclaw/workspace/tools:${PATH}"

checkpoint-setup
```

Add the `export PATH` line to your `~/.zshrc` or `~/.bashrc` for persistence.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/AnthonyFrancis/openclaw-checkpoint/main/scripts/install-openclaw-checkpoint.sh | bash
```

This runs the install script -- review it first if you prefer to inspect before executing.

## Requirements

- macOS or Linux (Windows not supported)
- Git
- GitHub account (for private backup repository)

## After Installation

### New Setup (First Time)

Run the setup wizard to create a new backup:

```bash
checkpoint-setup
```

This guides you through creating a private GitHub repo and configuring automatic backups.

### Restore from Existing Backup

If you already have a checkpoint backup on GitHub (e.g., setting up a new machine):

```bash
checkpoint-restore
```

This launches an interactive restore wizard that:
- Helps you authenticate with GitHub
- Connects to your existing backup repository
- Lets you pick the most recent or any previous checkpoint to restore
- Restores your OpenClaw state
- Offers to restore your cron jobs (scheduled tasks) automatically

To skip selection and restore the latest checkpoint automatically:

```bash
checkpoint-restore --latest
```

## Commands Available After Install

| Command | Description |
|---------|-------------|
| `checkpoint` | Show all available commands |
| `checkpoint-setup` | Interactive first-time setup |
| `checkpoint-backup` | Backup now |
| `checkpoint-restore` | Restore from backup (select checkpoint) |
| `checkpoint-status` | Check backup health |
| `checkpoint-schedule` | Configure auto-backup |
| `checkpoint-stop` | Stop automatic backups |
| `checkpoint-auth` | Fix authentication |
| `checkpoint-reset` | Reset for fresh setup |

## More Information

Full documentation: [GitHub Repository](https://github.com/AnthonyFrancis/openclaw-checkpoint)
