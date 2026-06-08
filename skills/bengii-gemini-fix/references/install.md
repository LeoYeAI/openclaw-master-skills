# OpenClaw Installation Reference

## Table of Contents

- [System Requirements](#system-requirements)
- [Install Methods](#install-methods)
- [After Install](#after-install)
- [Troubleshooting](#troubleshooting)
- [Updating](#updating)
- [Rollback / Pinning](#rollback--pinning)
- [Migrating](#migrating)
- [Uninstall](#uninstall)

## System Requirements

- **Node 22+** (the installer script installs it if missing)
- **macOS, Linux, or Windows** (WSL2 recommended for Windows)
- `pnpm` only needed for building from source

## Install Methods

### Installer Script (Recommended)

```bash
# macOS / Linux / WSL2
curl -fsSL https://openclaw.ai/install.sh | bash

# Windows (PowerShell)
iwr -useb https://openclaw.ai/install.ps1 | iex
```

Skip the onboarding wizard with `--no-onboard`:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard
```

### npm / pnpm

```bash
# npm
npm install -g openclaw@latest
openclaw onboard --install-daemon

# pnpm
pnpm add -g openclaw@latest
pnpm approve-builds -g    # approve openclaw, node-llama-cpp, sharp, etc.
openclaw onboard --install-daemon
```

**sharp build errors?**

```bash
SHARP_IGNORE_GLOBAL_LIBVIPS=1 npm install -g openclaw@latest
```

If you see `sharp: Please add node-gyp`:

```bash
npm install -g node-gyp
```

### From Source

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build
pnpm build
pnpm link --global       # Link the CLI
openclaw onboard --install-daemon
```

### Other Install Methods

| Method | Description |
|---|---|
| **Docker** | Containerized or headless deployments |
| **Podman** | Rootless container via `setup-podman.sh` |
| **Nix** | Declarative install via Nix |
| **Ansible** | Automated fleet provisioning |
| **Bun** | CLI-only usage via Bun runtime |

See: https://docs.openclaw.ai/install/docker, /podman, /nix, /ansible, /bun

## After Install

```bash
openclaw doctor     # Check config issues + apply migrations
openclaw status     # Gateway status
openclaw dashboard  # Open browser UI
```

Key environment variables:
- `OPENCLAW_HOME` — home directory for internal paths
- `OPENCLAW_STATE_DIR` — mutable state location
- `OPENCLAW_CONFIG_PATH` — config file location

## Troubleshooting

### `openclaw` not found

#### PATH Diagnosis

```bash
node -v
npm -v
npm prefix -g
echo "$PATH"
```

If `$(npm prefix -g)/bin` is not in `$PATH`:

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$(npm prefix -g)/bin:$PATH"
```

Then: `rehash` (zsh) or `hash -r` (bash).

## Updating

### Re-run Installer (Recommended)

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### Before You Update

1. Note current version: `openclaw --version`
2. Check release notes for breaking changes
3. Backup config: `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak`

### Update Global Install

```bash
npm install -g openclaw@latest
# Or:
openclaw update          # Self-update command
```

### Auto-Updater (Optional)

```json5
{
  gateway: {
    autoUpdate: {
      enabled: true,
      // check interval, etc.
    },
  },
}
```

### Update Control UI / RPC

Control UI updates come with package updates. No separate step needed.

### Update From Source

```bash
cd openclaw
git pull
pnpm install
pnpm ui:build
pnpm build
```

### Always Run After Update

```bash
openclaw doctor          # Config migrations + health check
openclaw gateway restart # Apply changes
```

## Rollback / Pinning

### Pin Global Install

```bash
npm install -g openclaw@<version>
```

### Pin Source by Date

```bash
git checkout <commit-hash>
pnpm install && pnpm ui:build && pnpm build
```

### If You're Stuck

1. Pin to last known good version
2. Run `openclaw doctor --fix`
3. Check GitHub Issues / Releases

## Migrating

To move OpenClaw to a new machine:

1. Install OpenClaw on the new machine
2. Copy `~/.openclaw/` directory (config, state, sessions)
3. Run `openclaw doctor` on the new machine
4. Re-pair mobile devices and re-login channels

## Uninstall

```bash
openclaw uninstall       # Guided removal
```

Or manually:
1. `openclaw gateway stop` — stop the daemon
2. `npm uninstall -g openclaw`
3. Remove `~/.openclaw/` directory
4. Remove launchd/systemd service files
