# oc-doctor

[English](README.md) | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS | Linux | Windows (WSL)](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows%20(WSL)-lightgrey.svg)](https://github.com/bryant24hao/oc-doctor)

> One command to diagnose your entire OpenClaw setup. Finds problems, explains impact, offers fixes.

<p align="center">
  <img src="assets/demo.svg" alt="oc-doctor demo report" width="800">
</p>

A Claude Code / OpenClaw skill that runs **11 diagnostic sections** on your local OpenClaw installation and generates a structured health report with `CRITICAL` / `WARNING` / `INFO` findings — then offers to fix them interactively, in your language.

## Why

Midnight. Your Telegram bot is responding to every message in a group because `requireMention` was set to `false` weeks ago and nobody noticed. It keeps "forgetting" conversations — turns out a model swap left `contextTokens` at 272k on a 200k model. And now Gateway is down because two processes are fighting over the same port.

You spend two hours digging through config files, grepping logs, searching GitHub Issues. You fix three things but have no idea what else is lurking.

**With oc-doctor, one command finds all of it in 60 seconds — and fixes it in 30 more.**

```
/oc-doctor
→ 12 findings: 1 CRITICAL, 4 WARNING, 7 INFO
→ "Fix all?" → Yes
→ Done. Security patched, models aligned, 282 MB cache cleared, dead files cleaned.
```

What used to take hours of manual troubleshooting now takes 2 minutes. Run it weekly — like a health check for your OpenClaw setup. ([Full story](docs/user-story.en.md))

## Highlights

- **11 diagnostic sections** covering installation, config, sessions, cron, security, resources, gateway, and system instructions
- **Interactive one-click fixes** — batch-fix WARNINGs, confirm CRITICALs individually
- **Cross-reference integrity** — detects when AGENTS.md references files that are missing or empty, and generates practical replacements (e.g., a useful HEARTBEAT.md based on your actual cron jobs and channels)
- **Secret redaction** — API keys and tokens are automatically masked in report output
- **Auto language** — responds in Chinese, English, or any language based on conversation context

## Quick Install

**Via [skills.sh](https://skills.sh)** (recommended):

```bash
npx skills add bryant24hao/oc-doctor -g -y
```

**Via [ClawdHub](https://clawdhub.ai)**:

```bash
clawhub install oc-doctor
```

**Manual**:

```bash
git clone https://github.com/bryant24hao/oc-doctor.git ~/.claude/skills/oc-doctor
```

## Usage

Just say any of these in Claude Code or OpenClaw:

```
/oc-doctor
openclaw doctor
claw health check
openclaw diagnose
```

## What It Finds

| # | Section | Examples |
|---|---------|----------|
| 1 | **Installation & Version** | Outdated version, gateway down, LaunchAgent missing |
| 2 | **Config Consistency** | Invalid model ID, legacy `clawdbot.json`, `.bak` accumulation |
| 3 | **Session Maintenance** | No `pruneAfter`, maintenance mode `"warn"` instead of `"enforce"` |
| 4 | **Compaction Config** | Missing `reserveTokensFloor` (context overflow risk) |
| 5 | **Model Alignment** | Session using 272k contextTokens on a 200k model |
| 6 | **Session Health** | 47 orphan JSONL files (180MB), zombie entries, empty sessions |
| 7 | **Cron Health** | Duplicate enabled jobs, stale schedules, abandoned `.tmp` files |
| 8 | **Security Audit** | `groupPolicy: "open"`, `auth.mode: "none"`, unrestricted `allowFrom` |
| 9 | **Resource Usage** | Browser cache 500MB, logs 80MB, single JSONL 15MB |
| 10 | **Gateway & Process** | Multiple gateway PIDs, port conflict, recent error spikes |
| 11 | **System Instruction Health** | Token budget analysis, empty templates, cross-reference integrity |

## How It Works

**Script + LLM separation**: deterministic data collection via shell scripts, judgment and analysis by the LLM.

```
scripts/sysinstruction-check.sh  → structured JSON  → LLM analyzes
openclaw status --all            → raw output       → LLM interprets
openclaw sessions cleanup --dry-run → candidates    → LLM triages
```

This ensures reproducible data collection while leveraging LLM reasoning for nuanced diagnosis.

## Interactive Fixes

After the report, the skill asks:

> "Would you like me to fix these issues? I can batch-fix all WARNING-level and below. CRITICAL issues will be confirmed individually."

Available fixes:
- **Session cleanup** — orphan/deleted JSONL files, zombie entries
- **Model drift** — align sessions to configured default model
- **Config optimization** — maintenance, compaction, security settings
- **Cron cleanup** — deduplication, tmp file removal, disabled job pruning
- **System instruction** — archive BOOTSTRAP.md, remove empty templates, reduce token bloat
- **Workspace integrity** — generate practical content for referenced but missing files (e.g., HEARTBEAT.md with cron/channel-aware checklist)
- **Resource cleanup** — clear browser cache, rotate logs

## Prerequisites

- **OpenClaw** installed and in PATH
- **[jq](https://jqlang.github.io/jq/)** for the system instruction analysis script

```bash
brew install jq    # macOS
apt install jq     # Debian/Ubuntu/WSL
```

> **Windows users**: Run inside [WSL](https://learn.microsoft.com/en-us/windows/wsl/install). Native Windows (PowerShell/cmd) is not supported.

## Security & Privacy

This skill operates locally and makes no network requests. However, diagnostic output becomes part of the LLM conversation context.

| Aspect | Detail |
|--------|--------|
| Files read | `openclaw.json`, `models.json`, `sessions.json`, workspace `.md` files, cron `jobs.json`, gateway logs |
| Files modified | Only with explicit user confirmation per fix |
| Network | None |
| Secrets | Redacted in report output (first 8 chars + `...`); never logged to disk |

## Directory Structure

```
oc-doctor/
├── SKILL.md                          # Skill definition (loaded by Claude Code)
├── scripts/
│   └── sysinstruction-check.sh       # System instruction token analysis
├── assets/
│   └── demo.svg                      # Terminal demo for README
├── README.md
└── LICENSE
```

## Customization

Override the OpenClaw home directory:

```bash
OPENCLAW_HOME=/custom/path bash scripts/sysinstruction-check.sh
```

## Contributing

Issues and PRs welcome. The skill follows the [Anthropic skill authoring best practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices).

## License

[MIT](LICENSE)
