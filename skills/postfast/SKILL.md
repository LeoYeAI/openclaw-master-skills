---
name: postfast
description: Schedule and manage social media posts across TikTok, Instagram, Facebook, X (Twitter), YouTube, LinkedIn, Threads, Bluesky, Pinterest, and Telegram using the PostFast API. Use when the user wants to schedule social media posts, manage social media content, upload media for social posting, list connected social accounts, check scheduled posts, delete scheduled posts, cross-post content to multiple platforms, or automate their social media workflow. PostFast is a SaaS tool — no self-hosting required.
homepage: https://postfa.st
metadata: {"openclaw":{"emoji":"⚡","primaryEnv":"POSTFAST_API_KEY","requires":{"env":["POSTFAST_API_KEY"]}}}
---

# PostFast

Schedule social media posts across 10 platforms from one API. SaaS — no self-hosting needed.

## Setup

1. Sign up at https://app.postfa.st/register (7-day free trial, no credit card)
2. Go to Workspace Settings → generate an API key
3. Set the environment variable:
   ```bash
   export POSTFAST_API_KEY="your-api-key"
   ```

Base URL: `https://api.postfa.st`
Auth header: `pf-api-key: $POSTFAST_API_KEY`

## Core Workflow

### 1. List connected accounts

```bash
curl -s -H "pf-api-key: $POSTFAST_API_KEY" https://api.postfa.st/social-media/my-social-accounts
```

Returns array of `{ id, platform, platformUsername, displayName }`. Save the `id` — it's the `socialMediaId` required for every post.

Platform values: `TIKTOK`, `INSTAGRAM`, `FACEBOOK`, `X`, `YOUTUBE`, `LINKEDIN`, `THREADS`, `BLUESKY`, `PINTEREST`, `TELEGRAM`

### 2. Schedule a text post (no media)

```bash
curl -X POST https://api.postfa.st/social-posts \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "content": "Your post text here",
      "mediaItems": [],
      "scheduledAt": "2026-06-15T10:00:00.000Z",
      "socialMediaId": "ACCOUNT_ID_HERE"
    }],
    "controls": {}
  }'
```

Returns `{ "postIds": ["uuid-1"] }`.

### 3. Schedule a post with media (3-step flow)

**Step A** — Get signed upload URLs:
```bash
curl -X POST https://api.postfa.st/file/get-signed-upload-urls \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "contentType": "image/png", "count": 1 }'
```
Returns `[{ "key": "image/uuid.png", "signedUrl": "https://..." }]`.

**Step B** — Upload file to S3:
```bash
curl -X PUT "SIGNED_URL_HERE" \
  -H "Content-Type: image/png" \
  --data-binary @/path/to/file.png
```

**Step C** — Create post with media key:
```bash
curl -X POST https://api.postfa.st/social-posts \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "content": "Post with image!",
      "mediaItems": [{ "key": "image/uuid.png", "type": "IMAGE", "sortOrder": 0 }],
      "scheduledAt": "2026-06-15T10:00:00.000Z",
      "socialMediaId": "ACCOUNT_ID_HERE"
    }],
    "controls": {}
  }'
```

For video: use `contentType: "video/mp4"`, `type: "VIDEO"`, key prefix `video/`.

### 4. List scheduled posts

```bash
curl -s -H "pf-api-key: $POSTFAST_API_KEY" "https://api.postfa.st/social-posts?page=0&limit=20"
```

Returns `{ "data": [...], "totalCount": 25, "pageInfo": { "page": 1, "hasNextPage": true, "perPage": 20 } }`.

**Query parameters:**
- `page` (int, default 0) — 0-based page index. Response shows 1-based display page in `pageInfo.page`
- `limit` (int, default 20, max 50) — items per page
- `platforms` (string) — comma-separated filter: `FACEBOOK,INSTAGRAM,X`
- `statuses` (string) — comma-separated: `DRAFT`, `SCHEDULED`, `PUBLISHED`, `FAILED`
- `from` / `to` (ISO 8601 UTC) — date range filter on `scheduledAt`

Example: `GET /social-posts?page=0&limit=50&platforms=X,LINKEDIN&statuses=SCHEDULED&from=2026-06-01T00:00:00Z&to=2026-06-30T23:59:59Z`

### 5. Delete a scheduled post

```bash
curl -X DELETE -H "pf-api-key: $POSTFAST_API_KEY" https://api.postfa.st/social-posts/POST_ID
```

### 6. Cross-post to multiple platforms

Include multiple entries in the `posts` array, each with a different `socialMediaId`. They share the same `controls` and `mediaItems` keys.

### 7. Generate a connect link (for clients)

Let clients connect their social accounts to your workspace without creating a PostFast account:

```bash
curl -X POST https://api.postfa.st/social-media/connect-link \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "expiryDays": 7, "sendEmail": true, "email": "client@example.com" }'
```

Returns `{ "connectUrl": "https://app.postfa.st/connect?token=..." }`. Share the URL — they can connect accounts directly. Rate limit: 50/hour.

### 8. Create a draft post

Omit `scheduledAt` and set `status: "DRAFT"` to save without scheduling:

```bash
curl -X POST https://api.postfa.st/social-posts \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{ "content": "Draft idea...", "mediaItems": [], "socialMediaId": "ACCOUNT_ID" }],
    "status": "DRAFT",
    "controls": {}
  }'
```

### 9. Get post analytics

Fetch published posts with their performance metrics:

```bash
curl -s -H "pf-api-key: $POSTFAST_API_KEY" \
  "https://api.postfa.st/social-posts/analytics?startDate=2026-03-01T00:00:00.000Z&endDate=2026-03-31T23:59:59.999Z&platforms=TIKTOK,INSTAGRAM"
```

**Query parameters:**
- `startDate` (ISO 8601, required) — start of date range
- `endDate` (ISO 8601, required) — end of date range
- `platforms` (string, optional) — comma-separated filter
- `socialMediaIds` (string, optional) — comma-separated account UUIDs

Returns `{ "data": [{ id, content, socialMediaId, platformPostId, publishedAt, latestMetric }] }`.

`latestMetric` fields: `impressions`, `reach`, `likes`, `comments`, `shares`, `totalInteractions`, `fetchedAt`, `extras`. All numbers are strings (bigint). `latestMetric` is null if metrics haven't been fetched yet. LinkedIn personal accounts are excluded.

Rate limit: 350/hour.

## Common Patterns

### Pattern 1: Cross-platform campaign

Post the same content to LinkedIn, X, and Threads at the same time:

```bash
curl -X POST https://api.postfa.st/social-posts \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [
      { "content": "Big announcement!", "mediaItems": [], "scheduledAt": "2026-06-15T09:00:00.000Z", "socialMediaId": "LINKEDIN_ID" },
      { "content": "Big announcement!", "mediaItems": [], "scheduledAt": "2026-06-15T09:00:00.000Z", "socialMediaId": "X_ID" },
      { "content": "Big announcement!", "mediaItems": [], "scheduledAt": "2026-06-15T09:00:00.000Z", "socialMediaId": "THREADS_ID" }
    ],
    "controls": {}
  }'
```

See [examples/cross-platform-post.json](examples/cross-platform-post.json) for a complete example.

### Pattern 2: Instagram Reel with upload

1. Get signed URL with `contentType: "video/mp4"`
2. PUT video to signed URL
3. Create post with `instagramPublishType: "REEL"`

See [examples/instagram-reel.json](examples/instagram-reel.json) for the request body.

### Pattern 3: TikTok video with privacy settings

Upload video, then post with privacy controls:

```bash
# controls object:
{
  "tiktokPrivacy": "PUBLIC",
  "tiktokAllowComments": true,
  "tiktokAllowDuet": false,
  "tiktokAllowStitch": false,
  "tiktokBrandContent": true
}
```

See [examples/tiktok-video.json](examples/tiktok-video.json).

### Pattern 4: Pinterest pin (board required)

Always fetch boards first, then post:

```bash
# Step 1: Get boards
curl -s -H "pf-api-key: $POSTFAST_API_KEY" \
  https://api.postfa.st/social-media/PINTEREST_ACCOUNT_ID/pinterest-boards

# Step 2: Post with board ID
# controls: { "pinterestBoardId": "BOARD_ID", "pinterestLink": "https://yoursite.com" }
```

See [examples/pinterest-pin.json](examples/pinterest-pin.json).

### Pattern 5: YouTube Short with tags and playlist

Upload video, then post with YouTube controls:

```bash
# controls object:
{
  "youtubeIsShort": true,
  "youtubeTitle": "Quick Tip: Batch Your Content",
  "youtubePrivacy": "PUBLIC",
  "youtubePlaylistId": "PLxxxxxx",
  "youtubeTags": ["tips", "productivity", "social media"],
  "youtubeMadeForKids": false
}
```

See [examples/youtube-short.json](examples/youtube-short.json).

### Pattern 6: LinkedIn document post

Documents (PDF, PPTX, DOCX) display as swipeable carousels on LinkedIn.

1. Get signed URL with `contentType: "application/pdf"`
2. PUT the file to signed URL
3. Create post using `linkedinAttachmentKey` instead of `mediaItems`

```bash
# controls: { "linkedinAttachmentKey": "file/uuid.pdf", "linkedinAttachmentTitle": "Q1 Marketing Playbook" }
# Note: mediaItems should be [] when using linkedinAttachmentKey
```

See [examples/linkedin-document.json](examples/linkedin-document.json).

### Pattern 7: First comment (auto-posted after publish)

Add a `firstComment` to any post — it's auto-posted ~10 seconds after the main post goes live (up to 3 retries):

```json
{
  "posts": [{ "content": "Main post text", "firstComment": "Link: https://postfa.st", "mediaItems": [], "scheduledAt": "...", "socialMediaId": "X_ID" }],
  "controls": {}
}
```

Supported on: X, Instagram, Facebook, YouTube, Threads. NOT supported on: TikTok, Pinterest, Bluesky, LinkedIn.

See [examples/x-first-comment.json](examples/x-first-comment.json).

### Pattern 8: X (Twitter) retweet

Schedule a retweet — content and media are ignored:

```json
{
  "posts": [{ "content": "", "scheduledAt": "...", "socialMediaId": "X_ID" }],
  "controls": { "xRetweetUrl": "https://x.com/username/status/1234567890" }
}
```

See [examples/x-retweet.json](examples/x-retweet.json). For quote tweets with your own commentary, use `xQuoteTweetUrl` instead. See [examples/x-quote-tweet.json](examples/x-quote-tweet.json).

### Pattern 9: Batch scheduling (a week of posts)

Schedule multiple posts at different times in a single API call (up to 15 posts per request):

See [examples/batch-scheduling.json](examples/batch-scheduling.json).

## Platform-Specific Controls

Pass these in the `controls` object. See [references/platform-controls.md](references/platform-controls.md) for full details.

| Platform | Key Controls |
|---|---|
| **TikTok** | `tiktokPrivacy`, `tiktokAllowComments`, `tiktokAllowDuet`, `tiktokAllowStitch`, `tiktokIsDraft`, `tiktokBrandOrganic`, `tiktokBrandContent`, `tiktokAutoAddMusic` |
| **Instagram** | `instagramPublishType` (TIMELINE/STORY/REEL), `instagramPostToGrid`, `instagramCollaborators` |
| **Facebook** | `facebookContentType` (POST/REEL/STORY), `facebookReelsCollaborators` |
| **YouTube** | `youtubeIsShort`, `youtubeTitle`, `youtubePrivacy`, `youtubePlaylistId`, `youtubeTags`, `youtubeMadeForKids`, `youtubeCategoryId` |
| **LinkedIn** | `linkedinAttachmentKey`, `linkedinAttachmentTitle` (for document posts) |
| **X (Twitter)** | `xQuoteTweetUrl` (quote tweet), `xRetweetUrl` (retweet), `xCommunityId` (post to community) |
| **Pinterest** | `pinterestBoardId` (required), `pinterestLink` |
| **Bluesky** | No platform-specific controls — text + images only |
| **Threads** | No platform-specific controls — text + images/video |
| **Telegram** | No platform-specific controls — text + images/video/mixed media |

## Helper Endpoints

- **Pinterest boards**: `GET /social-media/{id}/pinterest-boards` → returns `[{ boardId, name }]`
- **YouTube playlists**: `GET /social-media/{id}/youtube-playlists` → returns `[{ playlistId, title }]`
- **Connect link**: `POST /social-media/connect-link` → returns `{ connectUrl }`. Let clients connect accounts without a PostFast account. Params: `expiryDays` (1-30, default 7), `sendEmail` (bool), `email` (required if sendEmail=true)

## Rate Limits

**Global** (per API key): 60/min, 150/5min, 300/hour, 2000/day

**Per-endpoint:**
- `POST /social-posts`: 350/day
- `GET /social-posts`: 200/hour
- `GET /social-posts/analytics`: 350/hour
- `POST /social-media/connect-link`: 50/hour

**Platform limits:**
- X (Twitter) via API: **5 posts per account per day** — do not exceed this

Check `X-RateLimit-Remaining-*` headers. 429 = rate limited, check `Retry-After-*` header. For batch operations, add a 1-second delay between API calls.

## Media Specs Quick Reference

| Platform | Images | Video | Carousel |
|---|---|---|---|
| TikTok | Carousels only | ≤250MB, MP4/MOV, 3s-10min | 2-35 images |
| Instagram | JPEG/PNG | ≤1GB, 3-90s (Reels) | Up to 10 |
| Facebook | ≤30MB, JPG/PNG | 1 per post | Up to 10 images |
| YouTube | — | Shorts ≤3min, H.264 | — |
| LinkedIn | Up to 9 | ≤10min | Up to 9, or documents (PDF/PPTX/DOCX) |
| X (Twitter) | Up to 4 | — | — |
| Pinterest | 2:3 ratio ideal | Supported | 2-5 images |
| Bluesky | Up to 4 | Not supported | — |
| Threads | Supported | Supported | Up to 10 |
| Telegram | Up to 10 | Supported | Up to 10 mixed media |

## Common Gotchas

1. **Always fetch accounts first** — `socialMediaId` is a UUID, not a platform name. Call `GET /social-media/my-social-accounts` to get valid IDs.
2. **Media MUST go through 3-step upload** — No external URLs. Always: get signed URL → PUT to S3 → use the `key` in `mediaItems`.
3. **`scheduledAt` must be in the future** — ISO 8601 UTC format. Past dates return 400.
4. **Pinterest ALWAYS requires `pinterestBoardId`** — Fetch boards first with `GET /social-media/{id}/pinterest-boards`.
5. **TikTok requires video for standard posts** — Images only work in carousels (2-35 images).
6. **LinkedIn documents use `linkedinAttachmentKey`** — NOT `mediaItems`. Set `mediaItems: []` when posting documents.
7. **Content-Type on S3 PUT must match** — The `Content-Type` header in your S3 PUT must match what you requested in `get-signed-upload-urls`.
8. **Instagram Reels need video 3-90 seconds** — Outside this range returns an error.
9. **YouTube Shorts need video under 3 minutes** — H.264 codec with AAC audio recommended.
10. **X (Twitter) has a 280 character limit** — Longer content is silently truncated.
11. **Cross-posting shares controls** — The `controls` object applies to ALL posts in the batch. Platform-irrelevant controls are ignored.
12. **X (Twitter) API limit is 5 posts/account/day** — Exceeding this risks account restrictions.
13. **`firstComment` only works on 5 platforms** — X, Instagram, Facebook, YouTube, Threads. TikTok, Pinterest, Bluesky, LinkedIn return a validation error.
14. **Cannot use `xQuoteTweetUrl` and `xRetweetUrl` together** — Pick one. Retweets ignore content/media.
15. **LinkedIn documents support PDF, DOC, DOCX, PPT, PPTX** — Max 60MB. Cannot mix with regular media.
16. **Pagination is 0-based** — `page=0` returns the first page. Response `pageInfo.page` shows 1-based display number.

## Supporting Resources

**Reference docs:**
- [references/api-reference.md](references/api-reference.md) — Complete API endpoint reference with response examples
- [references/platform-controls.md](references/platform-controls.md) — All platform-specific controls with types and defaults
- [references/media-specs.md](references/media-specs.md) — Media size, format, and dimension limits per platform
- [references/upload-flow.md](references/upload-flow.md) — Detailed media upload walkthrough

**Ready-to-use examples:**
- [examples/EXAMPLES.md](examples/EXAMPLES.md) — Index of all 18 examples
- [examples/cross-platform-post.json](examples/cross-platform-post.json) — Multi-platform posting
- [examples/tiktok-video.json](examples/tiktok-video.json) — TikTok with privacy settings
- [examples/tiktok-carousel.json](examples/tiktok-carousel.json) — TikTok image carousel
- [examples/tiktok-draft.json](examples/tiktok-draft.json) — TikTok saved as draft
- [examples/instagram-reel.json](examples/instagram-reel.json) — Instagram Reel
- [examples/instagram-story.json](examples/instagram-story.json) — Instagram Story
- [examples/instagram-carousel.json](examples/instagram-carousel.json) — Instagram carousel
- [examples/facebook-reel.json](examples/facebook-reel.json) — Facebook Reel
- [examples/facebook-story.json](examples/facebook-story.json) — Facebook Story
- [examples/youtube-short.json](examples/youtube-short.json) — YouTube Short with tags
- [examples/pinterest-pin.json](examples/pinterest-pin.json) — Pinterest with board
- [examples/linkedin-document.json](examples/linkedin-document.json) — LinkedIn document post
- [examples/x-quote-tweet.json](examples/x-quote-tweet.json) — X quote tweet
- [examples/x-retweet.json](examples/x-retweet.json) — X scheduled retweet
- [examples/x-first-comment.json](examples/x-first-comment.json) — X post with auto first comment
- [examples/threads-carousel.json](examples/threads-carousel.json) — Threads image carousel
- [examples/batch-scheduling.json](examples/batch-scheduling.json) — Week of scheduled posts
- [examples/telegram-mixed-media.json](examples/telegram-mixed-media.json) — Telegram mixed media

## Quick Reference

```
# Auth
Header: pf-api-key: $POSTFAST_API_KEY

# List accounts
GET /social-media/my-social-accounts

# Schedule post
POST /social-posts  { posts: [{ content, mediaItems, scheduledAt, socialMediaId, firstComment? }], status?, approvalStatus?, controls: {} }

# Draft post (no scheduledAt needed)
POST /social-posts  { posts: [...], status: "DRAFT", controls: {} }

# List posts (page is 0-based, limit max 50)
GET /social-posts?page=0&limit=20
GET /social-posts?page=0&limit=50&platforms=X,LINKEDIN&statuses=SCHEDULED&from=2026-06-01T00:00:00Z&to=2026-06-30T23:59:59Z

# Delete post
DELETE /social-posts/:id

# Upload media (3 steps)
POST /file/get-signed-upload-urls  { contentType, count }
PUT  <signedUrl>  (raw file, matching Content-Type)
# then use key in mediaItems

# Pinterest boards
GET /social-media/:id/pinterest-boards

# YouTube playlists
GET /social-media/:id/youtube-playlists

# Post analytics (published posts with metrics)
GET /social-posts/analytics?startDate=...&endDate=...&platforms=...

# Connect link (for clients)
POST /social-media/connect-link  { expiryDays?, sendEmail?, email? }
```

## Tips for the Agent

- Always call `my-social-accounts` first to get valid `socialMediaId` values.
- For media posts, complete the full 3-step upload flow (signed URL → S3 PUT → create post).
- `scheduledAt` must be ISO 8601 UTC and in the future.
- Pinterest always requires `pinterestBoardId` — fetch boards first.
- LinkedIn documents use `linkedinAttachmentKey` instead of `mediaItems`.
- For carousels, include multiple items in `mediaItems` with sequential `sortOrder`.
- TikTok video thumbnails: set `coverTimestamp` (seconds) in `mediaItems`.
- When cross-posting, adjust content length for each platform's limits (X: 280, Bluesky: 300, TikTok: 2200).
- If the user doesn't specify a time, suggest tomorrow at 9:00 AM in their timezone.
- Batch up to 15 posts per API call for efficiency.
- Use `firstComment` for CTAs and links — keeps the main post clean and gets better engagement.
- X (Twitter) allows only 5 posts per account per day via API — warn the user if they're batching many X posts.
- For draft posts, set `status: "DRAFT"` and omit `scheduledAt` — the user can finalize in the PostFast dashboard.
- Use `GET /social-posts` with `from`/`to` filters to check what's already scheduled before adding more.
