# 🎬 Medeo Video Generator

Generate AI-powered videos from text. Tell your AI assistant "make me a video about XX" and it will automatically create the video using the [Medeo](https://medeo.app) platform, sending you the result in a few minutes.

---

## Installation

### Option A: Install via OpenClaw (Recommended)

Tell your AI assistant:

```
Install the medeo-video skill from https://github.com/one2x-ai/medeo-video-skill
```

### Option B: Manual Install

```bash
cd ~/.agents/skills/
git clone https://github.com/one2x-ai/medeo-video-skill.git medeo-video
openclaw gateway restart
```

---

## Setup (One-Time)

The first time you use the skill, your assistant will prompt you to set up an API key:

1. Go to 👉 **https://medeo.app/dev/apikey**
   - No account? The page will guide you through registration
2. Copy your API key (starts with `mk_`)
3. Send it to your assistant — it will handle the rest

That's it. One-time setup, works forever.

---

## Usage

### Text to Video

Just describe what you want:

```
Make me a video about the coffee brewing process with a cozy vibe
```

```
Create a 30-second product launch video for new running shoes
```

### Image + Text to Video

Send an image (or paste a URL) along with your description:

```
Use this image to create a product promo video
[send your image]
```

```
Make a video using this photo: https://example.com/photo.jpg
```

Your assistant will automatically upload your image and ensure the video uses your provided assets.

### Vertical / Short-Form Video

Want TikTok / Reels / Shorts format? Just say so:

```
Make a vertical short video of a sunset timelapse
```

---

## What You Can Do

| What You Say | What Happens |
|-------------|-------------|
| "Make me a XX video" | Full auto video generation |
| "Use this image to make a video" + image | Uses your image as assets |
| "Make it vertical" / "9:16" | Portrait short-form video |
| "What video templates are available?" | Browse preset recipes |
| "Is my last video done?" | Check recent job status |
| "Show my video history" | View past generations |

---

## FAQ

### How long does generation take?

Typically 5–15 minutes. Complex scripts may take longer. Generation runs in the background — your assistant will send you the video when it's ready.

### What image/video formats are supported?

`.jpg`, `.png`, `.webp`, `.mp4`, `.mov`, `.gif`

### What if I run out of credits?

Your assistant will let you know and provide a link to top up. After recharging, just say "credits topped up, please retry."

### Which chat platforms are supported?

All platforms supported by OpenClaw: Feishu, Telegram, Discord, WhatsApp, Signal, and more. The video will be delivered directly to your chat.

---

## Technical Details

- **Requirements**: Python 3.6+ with `requests` library (`pip install requests`)
- **Data Storage**: `~/.openclaw/workspace/medeo-video/` (config + job history)
- **API Docs**: https://docs.prd.medeo.app/

### Feishu Video Delivery

The optional `feishu_send_video.py` script reads Feishu app credentials (`appId` + `appSecret`) from your local `~/.openclaw/openclaw.json` to obtain a `tenant_access_token` for sending videos. **No credentials are uploaded or transmitted to third parties** — they are only used locally to call the Feishu Open API. If you don't use Feishu, this script is not invoked.

---

## Links

- [Medeo Platform](https://medeo.app)
- [OpenClaw](https://github.com/openclaw/openclaw)
- [ClawhHub Skill Marketplace](https://clawhub.com)

---

MIT License
