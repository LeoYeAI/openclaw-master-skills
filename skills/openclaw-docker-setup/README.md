# OpenClaw Docker Setup

Install a fully isolated, production-ready [OpenClaw](https://openclaw.ai) instance inside Docker on macOS — from zero to running in one session.

## What This Skill Does

Guides you through installing and configuring a Dockerized OpenClaw instance, including:

- Pulling the official image from GHCR
- Launching a named, isolated container with proper security settings
- Pairing your browser to the dashboard
- Configuring a Discord channel
- (Optional) Gmail via Himalaya — with full attachment support
- (Optional) Google Drive, Docs, Sheets, Calendar via gog

**Supports multiple instances on the same machine.** The skill auto-detects existing containers and suggests the next free name and port.

## Requirements

- macOS (Intel or Apple Silicon)
- Docker Desktop installed and running
- Claude Code CLI (if using Claude Max/Pro subscription)

## Installation

Copy this skill to your OpenClaw shared skills directory:

```bash
gh repo clone chunhualiao/openclaw-skill-docker-setup ~/.openclaw/skills/openclaw-docker-setup
```

Or install via ClawhHub:

```bash
clawhub install openclaw-docker-setup
```

## Usage

Once installed, trigger the skill by saying to your OpenClaw agent:

- "Install OpenClaw in Docker"
- "Set up a dockerized OpenClaw instance"
- "I want to run OpenClaw isolated in Docker"

The agent will walk you through the full setup interactively.

## References

- [Pitfalls and Solutions](references/pitfalls.md) — 14+ real-world issues documented with fixes
- [Gmail Setup via Himalaya](references/gmail-setup.md) — email with attachment support
- [Google Drive Setup via gog](references/google-drive-setup.md) — Drive, Docs, Sheets, Calendar

## Why Docker?

Running OpenClaw in Docker provides:
- **Isolation** — separate config, credentials, and data from your host
- **Multiple instances** — run a personal instance, a demo instance, and a work instance simultaneously
- **Security** — `--cap-drop=ALL` limits container privileges
- **Portability** — same setup works on any Mac

## License

MIT
