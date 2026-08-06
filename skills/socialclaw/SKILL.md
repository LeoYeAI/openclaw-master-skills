---
name: socialclaw
description: "When the user wants to schedule, publish, or manage social media posts across X, LinkedIn, Instagram, Facebook Pages, TikTok, Discord, Telegram, YouTube, Reddit, WordPress, or Pinterest through an AI agent via SocialClaw. Also use when the user mentions 'connect social accounts,' 'publish to X,' 'schedule LinkedIn post,' 'social media campaign,' 'multi-platform publishing,' 'SocialClaw,' 'social media API key,' or 'post to social.' For writing social content only, use social-content instead."
metadata:
  version: 1.0.0
---

# SocialClaw

SocialClaw is a workspace-scoped social publishing service at `https://getsocialclaw.com`. This skill teaches an OpenClaw-compatible agent how to publish across 13 social platforms through one workspace API key.

## What This Skill Does

- Authenticate with a SocialClaw workspace API key
- Connect and disconnect social accounts via browser OAuth
- Upload media assets and get SocialClaw-hosted delivery URLs
- Validate, preview, apply, and inspect scheduled posts and campaigns
- Inspect account capabilities, analytics, and workspace health

## Defaults

- Base URL: `https://getsocialclaw.com`
- Auth: workspace API key in `Authorization: Bearer <key>`
- Preferred interface: `socialclaw` CLI when installed
- Fallback interface: SocialClaw HTTP API

## Runtime Requirements

- Required env: `SC_API_KEY`
- Optional CLI: `socialclaw` (install with `npm install -g socialclaw`)
- Active trial or paid plan required for execution

## Quick Start

```bash
# Get a workspace API key at getsocialclaw.com/dashboard
export SC_API_KEY="<workspace-key>"

# Optionally install CLI
npm install -g socialclaw
socialclaw login --api-key <workspace-key>

# Connect a social account
socialclaw accounts connect --provider x --open

# List connected accounts
socialclaw accounts list --json

# Upload media
socialclaw assets upload --file ./image.png --json

# Validate and publish
socialclaw validate -f schedule.json --json
socialclaw apply -f schedule.json --json
```

## Supported Providers

X, LinkedIn (profile + page), Instagram (Business + standalone), Facebook Pages, TikTok, Discord, Telegram, YouTube, Reddit, WordPress, Pinterest

## Operating Rules

1. Start by confirming the user has a workspace API key
2. Never ask users for provider app secrets — they connect accounts inside SocialClaw
3. If billing errors appear (`plan_required`), route to `https://getsocialclaw.com/pricing`
4. Inspect `accounts capabilities` before generating provider-specific schedules
5. Be explicit about provider limitations instead of guessing

## Resources

- GitHub: https://github.com/ndesv21/socialclaw
- Dashboard: https://getsocialclaw.com/dashboard
- npm: https://www.npmjs.com/package/socialclaw
- Install skill: `npx skills add ndesv21/socialclaw`
