# ClawHub

> Source: https://docs.openclaw.ai/tools/clawhub

## What ClawHub Is

- A public registry for OpenClaw skills.
- A versioned store of skill bundles and metadata.
- A discovery surface for search, tags, and usage signals.

## How It Works

1. A user publishes a skill bundle (files + metadata).
2. ClawHub stores the bundle, parses metadata, and assigns a version.
3. The registry indexes the skill for search and discovery.
4. Users browse, download, and install skills in OpenClaw.

## Install the CLI

```bash
npm i -g clawhub
# or
pnpm add -g clawhub
```

## How It Fits into OpenClaw

- Skills live in `<workspace>/skills` or `~/.openclaw/skills`.
- `clawhub --workdir <dir>` or `CLAWHUB_WORKDIR` overrides the working directory.
- Default skills directory relative to workdir: `skills`.

## Skill System Overview

- A `SKILL.md` file with the primary description and usage.
- Optional configs, scripts, or supporting files used by the skill.
- Metadata such as tags, summary, and install requirements.

## Features

- Public browsing of skills and their `SKILL.md` content.
- Search powered by embeddings (vector search), not just keywords.
- Versioning with semver, changelogs, and tags (including `latest`).
- Downloads as a zip per version.
- Stars and comments for community feedback.
- Moderation hooks for approvals and audits.

## Security and Moderation

- Any signed-in user can report a skill.
- Skills with more than 3 unique reports are auto-hidden by default.
- Moderators can view hidden skills, unhide, delete, or ban users.
- Abusing the report feature can result in account bans.

## CLI Commands

### Auth

```bash
clawhub login                       # Browser flow
clawhub login --token <token>       # API token
clawhub logout
clawhub whoami
```

### Discovery

```bash
clawhub search "query"              # Search for skills
clawhub search "query" --limit <n>  # Limit results
```

### Install & Update

```bash
clawhub install <slug>              # Install a skill
clawhub install <slug> --version <v> --force
clawhub update <slug>               # Update specific skill
clawhub update --all                # Update all skills
clawhub list                        # List installed (reads .clawhub/lock.json)
```

### Publish & Sync

```bash
clawhub publish <path>              # Publish a skill
  --slug <slug>                     # Skill slug
  --name <name>                     # Display name
  --version <version>               # Semver version
  --changelog <text>                # Changelog text
  --tags <tags>                     # Comma-separated (default: latest)

clawhub sync                        # Sync all local skills
  --root <dir...>                   # Extra scan roots
  --all                             # Upload everything
  --dry-run                         # Preview only
  --bump <type>                     # patch|minor|major (default: patch)

clawhub delete <slug> --yes
clawhub undelete <slug> --yes
```

### Global Options

| Flag | Description |
|---|---|
| `--workdir <dir>` | Working directory (default: cwd or OpenClaw workspace) |
| `--dir <dir>` | Skills dir relative to workdir (default: `skills`) |
| `--site <url>` | Site base URL (browser login) |
| `--registry <url>` | Registry API base URL |
| `--no-input` | Non-interactive mode |
| `-V, --cli-version` | Print CLI version |

## Storage and Lockfile

- Installed skills tracked in `.clawhub/lock.json`.
- Each entry stores slug, version, installed path, and checksum.

## Environment Variables

- `CLAWHUB_WORKDIR` — override working directory
- `CLAWHUB_REGISTRY` — registry API URL override
- `CLAWHUB_TOKEN` — API token for CI/automation
