# Tool Setup Guide

## DanSUGC — UGC B-Roll Reaction Library

**What it is:** A marketplace of UGC reaction videos (shocked, crying, happy, frustrated, etc.) perfect for hook clips in short-form content.

**Setup:**
1. Go to [dansugc.com](https://dansugc.com) and create an account
2. Navigate to **Developers** section in your dashboard
3. Generate an API key (starts with `dsk_`)
4. Add the MCP server to Claude Code:

```bash
claude mcp add --transport http -s user dansugc https://dansugc.com/api/mcp \
  -H "Authorization: Bearer dsk_YOUR_API_KEY_HERE"
```

5. Restart Claude Code after adding

**Available MCP Tools:**
- `mcp__dansugc__search_videos` — Search by emotion, keyword, or semantic description
- `mcp__dansugc__get_video` — Get details for a specific video by ID
- `mcp__dansugc__purchase_videos` — Purchase videos (deducts credits, returns download URLs)
- `mcp__dansugc__list_purchases` — List previously purchased videos
- `mcp__dansugc__get_balance` — Check remaining credits
- `mcp__dansugc__tiktok_search_videos` — Search TikTok videos by keyword
- `mcp__dansugc__tiktok_user_videos` — Get a TikTok user's videos
- `mcp__dansugc__tiktok_search_users` — Search for TikTok users
- `mcp__dansugc__instagram_search_reels` — Search Instagram reels
- `mcp__dansugc__instagram_user_reels` — Get an Instagram user's reels
- `mcp__dansugc__scrapecreators_raw` — Raw proxy to any ScrapCreators endpoint
- **Posting tools** (requires Posting subscription): `check_posting_subscription`, `list_posting_accounts`, `create_post`, `list_posts`, `update_post`, `delete_post`, `get_posting_analytics`

**Important:** You must **purchase** videos before downloading them. The `purchase_videos` tool returns download URLs after successful purchase. Always check your balance first with `get_balance`.

**Pricing:** Credit-based. Each video costs credits. Check your balance before bulk purchases.

---

## DanSUGC Posting — TikTok & Instagram Publishing

**What it is:** Native social media scheduling built into DanSUGC. Same API key, same MCP server — no extra tools needed. Supports TikTok and Instagram.

**Requirements:**
- Active DanSUGC Posting subscription (separate from B-Roll credits — activate at [dansugc.com/dashboard](https://dansugc.com/dashboard))
- TikTok and/or Instagram accounts connected in your DanSUGC dashboard

**No extra setup needed** — posting tools are included in the same DanSUGC MCP server you already have.

**Available MCP Tools:**
- `mcp__dansugc__check_posting_subscription` — Verify posting plan is active
- `mcp__dansugc__list_posting_accounts` — List connected TikTok/Instagram accounts with IDs
- `mcp__dansugc__create_post` — Create, schedule, or publish immediately
- `mcp__dansugc__list_posts` — List all posts with status (draft/scheduled/published/failed)
- `mcp__dansugc__update_post` — Update caption, scheduled time, or status
- `mcp__dansugc__delete_post` — Delete a post
- `mcp__dansugc__get_posting_analytics` — Cross-platform metrics (followers, views, engagement)
- `mcp__dansugc__list_social_sets` — List account groupings
- `mcp__dansugc__create_social_set` — Create a new account grouping

**Usage:**
```
# Check subscription before posting
mcp__dansugc__check_posting_subscription()

# List connected accounts
mcp__dansugc__list_posting_accounts()
# → Returns: id, platform, username, followers, total_views

# Schedule a post
mcp__dansugc__create_post(
  content="Hook text...\n\n#hashtag1 #hashtag2 #fyp",
  media_urls=["PUBLIC_VIDEO_URL"],
  account_ids=["ACCOUNT_ID"],
  scheduled_for="2026-03-25T18:00:00Z",
  timezone="America/New_York"
)

# Publish immediately
mcp__dansugc__create_post(
  content="Caption...",
  media_urls=["PUBLIC_VIDEO_URL"],
  account_ids=["ACCOUNT_ID"],
  publish_now=true
)

# Check post status
mcp__dansugc__list_posts()

# View analytics
mcp__dansugc__get_posting_analytics(range="30d")
```

**Key rules:**
- ONE unique video per account — never post the same video to multiple accounts
- Currently supports TikTok and Instagram only
- Videos need a public URL — use tmpfiles.org for temporary hosting (use `/dl/` prefix)

---

## Social Media Analytics — DanSUGC Proxy (powered by ScrapCreators)

**What it is:** Real-time social media analytics for tracking video performance across TikTok, Instagram, YouTube, and 25+ platforms. Included with your DanSUGC API key — no extra setup needed.

**Setup:** None! Analytics are proxied through DanSUGC. Uses the same MCP server you already have — no extra configuration needed.

**Pricing:** $0.02 per request, deducted from your DanSUGC balance.

**Available MCP Tools:**
- `mcp__dansugc__tiktok_search_videos` — Search TikTok videos by keyword
- `mcp__dansugc__tiktok_user_videos` — Get a TikTok user's videos
- `mcp__dansugc__tiktok_search_users` — Search for TikTok users
- `mcp__dansugc__instagram_search_reels` — Search Instagram reels
- `mcp__dansugc__instagram_user_reels` — Get an Instagram user's reels
- `mcp__dansugc__scrapecreators_raw` — Raw proxy to any ScrapCreators endpoint

**Usage (MCP tool calls):**
```
# Search TikTok videos by keyword
mcp__dansugc__tiktok_search_videos(query="KEYWORD", sort_by="relevance")

# Get a TikTok user's videos (sorted by popular)
mcp__dansugc__tiktok_user_videos(handle="USERNAME", sort_by="popular")

# Search for TikTok users
mcp__dansugc__tiktok_search_users(query="KEYWORD")

# Search Instagram reels
mcp__dansugc__instagram_search_reels(query="KEYWORD")

# Get an Instagram user's reels
mcp__dansugc__instagram_user_reels(handle="USERNAME")

# Raw proxy — use for any ScrapCreators endpoint not covered above
mcp__dansugc__scrapecreators_raw(path="v1/tiktok/video", params={"url": "VIDEO_URL"})
```

**Path mapping:** Prepend `https://app.dansugcmodels.com/api/v1/scrapecreators/` to any ScrapCreators path. All query params and request bodies are forwarded as-is. Response format is identical.

**Error codes:**
- `402` — Insufficient DanSUGC balance (tell user to top up credits)
- `403` — API key not linked to a user account
- `502` — ScrapCreators unreachable (auto-refunded, safe to retry)

---

## Gemini — Video Intelligence

**What it is:** Google's Gemini AI model used for analyzing demo screen recordings — identifying the best segments, UI transitions, and emotional moments.

**Setup:**
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create an API key
3. Set it as an environment variable:

```bash
export GEMINI_API_KEY="your_key_here"
```

**Always use model: `gemini-3.1-flash-lite-preview`** — optimized for video understanding tasks.

**Direct video upload for analysis:**
```bash
# Step 1: Upload video file
FILE_URI=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/upload/v1beta/files?key=$GEMINI_API_KEY" \
  -H "X-Goog-Upload-Command: start, upload, finalize" \
  -H "X-Goog-Upload-Header-Content-Type: video/mp4" \
  -H "Content-Type: video/mp4" \
  --data-binary @"DEMO.mp4" | python3 -c "import sys,json; print(json.load(sys.stdin)['file']['uri'])")

# Step 2: Analyze
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{
      \"parts\": [
        {\"text\": \"YOUR ANALYSIS PROMPT HERE\"},
        {\"file_data\": {\"file_uri\": \"$FILE_URI\", \"mime_type\": \"video/mp4\"}}
      ]
    }],
    \"generationConfig\": {\"temperature\": 0.2, \"response_mime_type\": \"application/json\"}
  }"
```
