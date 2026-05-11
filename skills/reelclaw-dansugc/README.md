# ReelClaw

UGC reel production engine for AI coding agents. Create scroll-stopping short-form videos at scale.

```
npx skills add dansugc/reelclaw --all
```

## What It Does

ReelClaw is an AI agent skill that automates the entire UGC reel production pipeline:

1. **Source hooks** — Search and purchase UGC reaction clips from [DanSUGC](https://dansugc.com)
2. **Analyze demos** — Use Gemini AI to find the best segments in screen recordings
3. **Assemble reels** — FFmpeg-powered editing with text overlays, music, and transitions
4. **Publish** — Schedule to TikTok & Instagram natively via [DanSUGC Posting](https://dansugc.com)
5. **Track & replicate** — Monitor performance via DanSUGC's built-in analytics proxy and double down on winners
6. **Format research** — Find viral format ideas in any niche by analyzing top TikTok/Instagram content
7. **Hook research** — Discover proven text hooks from high-performing videos in your niche

## Requirements

- **ffmpeg** + **ffprobe** — Video processing
- **DanSUGC API key** — UGC clips, analytics, and TikTok/Instagram posting ([dansugc.com](https://dansugc.com))
- **Gemini API key** — Video intelligence ([aistudio.google.com](https://aistudio.google.com/apikey))

## Quick Setup

### 1. Install the skill

```bash
npx skills add dansugc/reelclaw --all
```

### 2. Connect MCP servers

```bash
# DanSUGC — UGC reaction clips + analytics + posting (TikTok + Instagram)
claude mcp add --transport http -s user dansugc https://dansugc.com/api/mcp \
  -H "Authorization: Bearer dsk_YOUR_API_KEY"
```

> DanSUGC handles everything — UGC clips, analytics, and posting to TikTok/Instagram. A Posting subscription is required for the publishing step.

### 3. Set environment variables

```bash
export GEMINI_API_KEY="your_gemini_key"
```

> **Note:** Social media analytics (TikTok/Instagram tracking) are included with your DanSUGC API key — no extra setup needed.

### 4. Use it

Tell your AI agent:
> "Use ReelClaw to create 5 UGC reels for my app using shocked reaction hooks"

> "Find me format ideas for beef liver supplements on TikTok"

> "Find hooks for my meditation app"

Or invoke directly with `/reelclaw` in Claude Code.

## The Pipeline

```
DanSUGC (hooks + analytics + posting) + Demos (Gemini AI) + Text + Music
    | FFmpeg Assembly (1080x1920, 15s max)
    | DanSUGC Posting (TikTok + Instagram)
    | DanSUGC Analytics Proxy (tracking)
    | Replicate Winners
```

## Key Rules

- **15 seconds max** per reel (non-negotiable for virality)
- **TikTok Sans font** for all text overlays
- **Green Zone positioning** — text placed only in platform-safe areas
- **One video per account** — unique content per social account

## Compatible Agents

Works with any agent that supports the Skills format:
- Claude Code
- Cursor
- Cline
- Codex
- Gemini CLI
- Continue
- Windsurf
- OpenCode

## License

MIT
