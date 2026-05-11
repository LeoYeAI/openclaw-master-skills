# personal-brand-builder v1.0.0

Transforms any OpenClaw agent into a personal brand authority engine
for entrepreneurs at the intersection of business, trading, and AI automation.

## What it does

- **Identity Engine** — Defines positioning, story, pillars, and brand promise
- **Presence Engine** — Manages 6 platforms (Twitter/X, LinkedIn, Instagram, YouTube, TikTok, Podcast)
- **Authority Engine** — Builds trust through social proof, networking, and credibility content

## Credentials required

- `TELEGRAM_BOT_TOKEN` — already in agent .env
- `TELEGRAM_CHAT_ID` — already in agent .env
- `TWITTER_API_KEY` — for Twitter/X automation (developer.twitter.com)
- `TWITTER_API_SECRET` — for Twitter/X automation
- `TWITTER_ACCESS_TOKEN` — for Twitter/X automation
- `TWITTER_ACCESS_SECRET` — for Twitter/X automation

> Twitter credentials are optional — the skill works in manual mode
> without them (generates content, no auto-posting).

## Quick start

```bash
python3 /workspace/brand/scripts/brand_manager.py init
python3 /workspace/brand/scripts/brand_manager.py status
```

## Integrates with

`content-creator-pro` · `acquisition-master` · `funnel-builder`
`voice-agent-pro-v3` · `agent-shark-mindset` · `proof-engine`

## Files

```
SKILL.md                       ← This skill's instructions
README.md                      ← This file
scripts/brand_manager.py       ← CLI: init, content, audit, network, proof
templates/identity.json        ← Brand identity template
templates/platform_config.json ← Platform config template
templates/voice_guide.md       ← Brand voice template
references/positioning.md      ← Positioning frameworks reference
.learnings/LEARNINGS.md        ← Auto-populated by the skill
AUDIT.md                       ← Auto-populated by the skill
```
