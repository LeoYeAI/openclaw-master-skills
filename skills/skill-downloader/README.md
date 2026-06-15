# Skill Downloader

> Discover, compare, and review OpenClaw skills from trusted sources, then guide safe installation when the user explicitly approves it.

## ⚠️ Mandatory Workflow

**This skill is the mandatory entry point for all skill search and installation operations.**

Any other skill that performs skill search, discovery, comparison, or installation — in whole or in part — **must delegate to this skill's workflow** rather than implementing its own parallel flow. See `SKILL.md` for the full declaration.

## Features

- 🔍 **Multi-source search**: Parallel search across ClawHub, GitHub anthropics/skills, and skills.sh simultaneously
- 📊 **Source-labeled results**: Every result clearly shows which source it came from
- 📋 **Information completeness levels**: Results are labeled Full / Partial / Minimal so you know how much data was available
- 🛡️ **Security-first workflow**: Explicit approval, local source review, and trusted-source preference
- 📁 **Flexible installation targets**:
  - Global install to `~/.openclaw/skills/` (when user says "global" or "system-wide")
  - Local install to `{workspace}/skills/` (default)
- 🚫 **No symlink installs**: Uses copied source files for transparent fallback installs
- ⏱️ **Search degraded mode**: Handles rate limits gracefully — reports failures honestly, gives user a choice to wait or proceed

## Trusted Sources (searched in parallel)

| Source | Search command | Install command | Directory control |
|--------|---------------|----------------|-----------------|
| ClawHub | `clawhub search "<query>"` | `clawhub install <slug> --dir <path>` | ✅ Full |
| GitHub anthropics/skills | `curl` GitHub API | File-based (clone → copy) | ✅ Full |
| skills.sh | `npx skills find "<query>"` | File-based (download from GitHub URL) | ✅ Full |

> Note: `npx skills add` is NOT used for installation because it only supports `--global` or `--agent` directories — not arbitrary custom paths. Install always goes through the file-based workflow for full directory control.

## Information Completeness Levels

Every result table is labeled with its completeness level:

- **Full** (✅ Full details available): `clawhub inspect` returned all fields — recommendation is given
- **Partial** (⚠️ Partial information): Some fields marked `unknown` — user chooses to proceed or wait
- **Minimal** (❌ Limited details): Only names available — show names only, do not recommend

**Hard rule**: At Partial or Minimal level, never give a recommendation without first disclosing what is missing and asking the user's consent.

## When to use this skill

Use this skill whenever the user:
- Asks to find, search, or look for a skill
- Requests to download, install, or add a skill
- Asks whether a skill exists for a certain task
- Wants to compare candidates before choosing one to install

## Workflow

### Mode A: Search Only
1. **Detect search intent**
2. **Parallel search**: Fire ClawHub, GitHub, and skills.sh searches simultaneously, aggregate results into one unified table with a **Source** column
3. **Inspect candidates**: Run `clawhub inspect` for ClawHub candidates; if rate limited, enter degraded mode
4. **Present results**: Comparison table with Source, description, ranking signals, best-use-case note, and recommendation (Full only)
5. **Disclose completeness level**: Label the table Full / Partial / Minimal
6. **Wait for user**: Ask if they want to install any result, or wait for full data

### Mode B: Installation
1. **Capture request**: Extract skill name, check if global install requested, confirm intent
2. **Find the skill**: ClawHub → GitHub → skills.sh in priority order
3. **Security check**: Download to temp, inspect for suspicious patterns; if clean, proceed
4. **Install**: Copy to target directory (never symlink), preserve existing user data
5. **Cleanup**: Remove temp files
6. **Done**: Offer to summarize the installed skill's usage

## Search degraded mode (rate limits)

When `clawhub inspect` fails due to rate limit:
1. Report the failure immediately
2. State which fields are unavailable
3. Offer choices: Wait (~30s retry) / Proceed with partial data / Skip
4. Never silently fall back to invented values

## Installation

```bash
# Global install
clawhub install skill-downloader --dir ~/.openclaw/skills

# Local install (default)
clawhub install skill-downloader --dir ./skills
```

If `clawhub` is unavailable, use the file-based installation workflow: download to temp, inspect, copy to target directory.

## Requirements

- network access to trusted registries and repositories
- ability to review downloaded text or source files locally
- standard local command-line tooling when available
- `clawhub` CLI for the preferred ClawHub workflow (when installed)
- `skill-scanner` (optional extra check, when available)
- `skill-vetting` (optional extra check, when available)

## Maintenance

When updating this skill's behavior, keep `SKILL.md` and `README.md` in sync.

## License

MIT
