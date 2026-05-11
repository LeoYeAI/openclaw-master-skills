---
name: dropspace
description: Create and publish social media launches via the Dropspace API. Use when user wants to post to social media, create launches, manage personas, generate media, track post analytics, schedule content, or anything Dropspace-related. Supports 10 platforms (Twitter, LinkedIn, Reddit, Instagram, TikTok, Facebook, YouTube, Substack, Product Hunt, Hacker News) with per-post analytics and AI content generation.
homepage: https://www.dropspace.dev/docs
source: https://github.com/joshchoi4881/dropspace-agents
metadata:
  {
    "openclaw":
      {
        "emoji": "🚀",
        "requires": { "env": ["DROPSPACE_API_KEY"] }
      }
  }
---

# Dropspace API Skill

Multi-platform social media publishing with AI-generated content, media generation, per-post analytics, and persona-based writing styles.

## Setup

Set your API key:
```bash
export DROPSPACE_API_KEY="ds_live_..."  # from dropspace.dev/settings/api
```

Base URL: `https://api.dropspace.dev`
Auth header: `-H "Authorization: Bearer $DROPSPACE_API_KEY"`

Also available as MCP server: `npx @jclvsh/dropspace-mcp`
Machine-readable docs: [llms.txt](https://www.dropspace.dev/llms.txt) | [OpenAPI](https://www.dropspace.dev/openapi.json)

## API Key Scopes

Keys can be scoped: `read`, `write`, `delete`, `publish`, `generate`, `admin`.

| Use Case | Recommended Scopes |
|----------|-------------------|
| AI agents / MCP | read, write, generate |
| CI/CD publishing | read, publish |
| Monitoring / dashboards | read |
| Full access (admin tools) | all scopes |

Missing scope returns 403 with `AUTH_002`.

## Audit Logging

Destructive/sensitive API operations are automatically logged: delete launch/persona, publish, create/revoke key, create/delete/rotate webhook.

## Supported Platforms

twitter, linkedin, reddit, instagram, tiktok, facebook, producthunt, hackernews, substack

### Per-Platform Character Limits
Twitter 280/tweet (25,000 for X Premium) × 6 tweets (use `thread` array or `content` string), LinkedIn 3,000, Instagram 2,200, Reddit 3,000, Facebook 3,000, TikTok 4,000, Product Hunt 500, Hacker News 2,000, Substack 3,000

## Core Workflow: Create & Publish

### 1. Check connected platforms
```bash
# User's OAuth connections
curl -s https://api.dropspace.dev/connections \
  -H "Authorization: Bearer $DROPSPACE_API_KEY"

# Official Dropspace accounts available for posting
curl -s https://api.dropspace.dev/dropspace/status \
  -H "Authorization: Bearer $DROPSPACE_API_KEY"
```
Connections: OAuth-connected accounts with platform, username, account_type, is_active, expires_at. Managed via dashboard.
Dropspace status: Shows which official Dropspace accounts (facebook, linkedin, twitter, reddit, instagram, tiktok) are connected and available for the `dropspace_platforms` field.

### 2. Create a launch (AI generates platform-specific content)
```bash
curl -s -X POST https://api.dropspace.dev/launches \
  -H "Authorization: Bearer $DROPSPACE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "launch title",
    "product_description": "what to post about (1-2000 chars)",
    "platforms": ["twitter", "linkedin", "reddit"],
    "product_url": "https://optional-url.com",
    "persona_id": "optional-uuid",
    "scheduled_date": "optional ISO 8601 (≥15 min future)",
    "publish": "optional boolean — immediately publish after creation (returns 202, mutually exclusive with scheduled_date, requires write+publish scopes)",
    "wait": "optional boolean — wait for publishing to complete and return post URLs inline (requires publish: true, returns 200 with posting_status)",
    "dropspace_platforms": ["twitter"],
    "user_platform_accounts": {"twitter": "account-id"},
    "media": [
      {"source": "url", "url": "https://example.com/image.png"},
      {"source": "base64", "data": "iVBOR...", "filename": "slide.png", "mime_type": "image/png"}
    ],
    "media_attach_platforms": ["twitter", "linkedin"],
    "media_mode": "images|video",
    "generate_ai_videos": ["instagram", "tiktok"],
    "custom_content": "single text for all platforms (validated against lowest char limit)",
    "custom_content_reddit_title": "reddit title when using custom_content (max 300 chars)",
    "platform_contents": {
      "twitter": {"thread": ["tweet 1", "tweet 2", "tweet 3"]},
      "reddit": {"title": "...", "content": "..."},
      "linkedin": {"content": "custom post"},
      "tiktok": {
        "content": "caption text",
        "tiktok_settings": {
          "privacy_level": "PUBLIC_TO_EVERYONE",
          "auto_add_music": true,
          "allow_comments": true,
          "allow_duet": true,
          "allow_stitch": true
        }
      }
    }
  }'
```
Content auto-generated via Claude from description + scraped URL + persona.

**Content options (mutually exclusive):**
- Omit both → full AI generation for all platforms
- `platform_contents` → per-platform custom content. Platforms without content get AI-generated. Reddit requires `title`. Product Hunt/HN support optional `title` (max 60/80 chars). **Twitter supports `thread` (string[], each ≤280 chars or ≤25,000 for X Premium, max 6 tweets) instead of `content`** — mutually exclusive with `content`.
- `custom_content` → `string` distributed to all platforms (validated against most restrictive char limit), or `string[]` to create a Twitter thread (each ≤280 chars or ≤25,000 for X Premium, max 6) that joins with double newlines for other platforms. Array form requires Twitter in platforms. Use `custom_content_reddit_title` if Reddit is included.

**`user_platform_accounts` key format:**
- Simple keys: `"twitter"`, `"reddit"`, `"instagram"`, `"tiktok"`
- LinkedIn personal: `"linkedin:personal"` → personal profile
- LinkedIn org: `"linkedin:organization:<org_id>"` → company page
- Facebook page: `"facebook:page:<page_id>"`
- Multiple keys allowed (e.g. post to personal + org simultaneously)

**TikTok settings (`platform_contents.tiktok.tiktok_settings`):**
- `privacy_level` (REQUIRED before publishing): `"PUBLIC_TO_EVERYONE"`, `"FOLLOWER_OF_CREATOR"`, `"MUTUAL_FOLLOW_FRIENDS"`, or `"SELF_ONLY"`
- Optional booleans: `allow_comments`, `allow_duet`, `allow_stitch`, `is_commercial`, `is_your_brand`, `is_branded_content`, `auto_add_music`
- Branded content (`is_branded_content: true`) cannot use `SELF_ONLY` privacy
- Can be set at creation or updated via PATCH (deep-merged)

**Inline media upload (`media` field):** Upload images/videos inline via URL or base64 — server handles storage upload and populates `media_assets` in the response. Max 10 items (9 images + 1 video). Images: jpeg/png/webp/gif (5MB). Videos: mp4/mov (512MB via URL, 4MB via base64). `media_attach_platforms` and `media_mode` auto-inferred if not set. Mutually exclusive with `media_assets`.

**Pre-uploaded media (`media_assets` field):** For files already in storage — requires `id`, `url`, `type`, `filename`, `size`, `mime_type`. Mutually exclusive with `media`.

Media limits: Instagram/Facebook 10, Reddit 20, TikTok 35.

**Inline publish (`publish` + `wait` fields):**
- `publish: true` → immediately publish after creation (returns 202). Mutually exclusive with `scheduled_date`. Requires both `write` and `publish` scopes.
- `wait: true` (requires `publish: true`) → wait for publishing to complete synchronously and return 200 with `posting_status` containing per-platform results and post URLs. Typical wait: 10-30s for text platforms, up to 60s+ with Instagram/TikTok.
- If publish validation fails after creation, returns 201 with `publish_error: { code, message }` — retry via `POST /launches/:id/publish`.

**Publish validation (LAUNCH_007):** When publishing fails validation, the response includes a `details` array listing all blocking issues. Checks include: char limits (all platforms), Reddit title ≤300 chars, Reddit video needs video+thumbnail, Reddit images need images, Instagram reel needs video, Instagram carousel needs ≥2 images, TikTok requires `tiktok_settings.privacy_level`, TikTok video needs video, TikTok photo needs images.
Instagram requires media. TikTok requires video or photos.
`generate_ai_videos`: subset of `["instagram", "tiktok"]` — generates video scripts and starts async rendering.
`media_mode`: `"images"` or `"video"` (auto-inferred when using `media`).

Upload errors: `UPLOAD_001` (unsupported type), `UPLOAD_002` (too large), `UPLOAD_003` (storage upload failed).

### 3. Review & edit content
```bash
# Edit specific platform content:
curl -s -X PATCH https://api.dropspace.dev/launches/LAUNCH_ID \
  -H "Authorization: Bearer $DROPSPACE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"platform_contents": {"twitter": {"thread": ["tweet 1", "tweet 2", "tweet 3"]}}}'

# Or regenerate for specific platforms:
curl -s -X POST https://api.dropspace.dev/launches/LAUNCH_ID/generate-content \
  -H "Authorization: Bearer $DROPSPACE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["twitter"], "generate_video_scripts": ["instagram"]}'
```

### 4. Publish
```bash
curl -s -X POST https://api.dropspace.dev/launches/LAUNCH_ID/publish \
  -H "Authorization: Bearer $DROPSPACE_API_KEY"
```
Returns 202. Async — poll `/status` or use webhooks (`launch.completed`, `launch.failed`, `launch.partial`).

### 5. Check posting status
```bash
curl -s https://api.dropspace.dev/launches/LAUNCH_ID/status \
  -H "Authorization: Bearer $DROPSPACE_API_KEY"
```
Returns per-platform posting logs with `status`, `post_url`, `post_id`, `error_message`, `error_code`, `attempt_count`, `posted_at`.

### 6. Get per-post analytics with engagement metrics
```bash
curl -s https://api.dropspace.dev/launches/LAUNCH_ID/analytics \
  -H "Authorization: Bearer $DROPSPACE_API_KEY"
```
Returns per-platform metrics (live refresh — fetches from platform APIs when stale >5 min):
- **Twitter:** likes, retweets, replies, quotes, bookmarks, impressions, urlClicks, profileClicks
- **LinkedIn:** impressions, uniqueImpressions, likes, comments, shares, clicks, engagement
- **Facebook:** reactions, comments, shares
- **Instagram:** views, engagement, saved, likes, comments, shares
- **Reddit:** score, upvotes, upvoteRatio, comments
- **TikTok:** views, likes, comments, shares

Response includes `fetched_at`, `next_refresh_at` (fetched_at + 5 min), and per-platform `cache_status` (`fresh` | `refreshed` | `stale`). Calling the endpoint triggers a refresh automatically when data is stale.

### Batch Analytics
```bash
# Fetch analytics for up to 100 launches in one request
curl -s "https://api.dropspace.dev/launches/analytics?ids=uuid1,uuid2,uuid3" \
  -H "Authorization: Bearer $DROPSPACE_API_KEY"
```
Returns `{ data: [...], errors: [...] }` with partial success support. Each item includes `launch_id`, `platforms` (with per-platform metrics + deletion info), and `status`. No `fetched_at`/`next_refresh_at` (those are single-launch only). Uses cached metrics — does not trigger live refresh from platforms.

### Post Deletion Detection

Analytics responses include deletion detection fields per platform:
- `is_deleted` (boolean) — true if the post was detected as deleted/removed
- `deleted_detected_at` (ISO 8601) — when deletion was first detected
- `deletion_reason` — one of: `not_found` (404), `gone` (410), `creator_deleted`, `moderation_removed`, `account_deleted`, `spam_filtered`

Platform-specific detection:
- **LinkedIn:** Detects `REMOVED_BY_LINKEDIN_TAKEDOWN`
- **Reddit:** Checks `removed_by_category`
- **Twitter:** Catches authorization errors as possible account deletion
- **TikTok/Instagram/Facebook:** Detects 404/410 responses

Deletion is detected during the analytics cron refresh cycle (runs every 5 minutes for recently active posts).

## First-Touch Attribution (Built-in)

Dropspace has built-in signup attribution via Next.js middleware → httpOnly cookie → profiles table.

**How it works:**
1. First page visit → middleware captures referrer + UTM params into `ds_attr` cookie (30-day expiry)
2. On signup → auth callback writes to `profiles.signup_referrer`, `signup_utm_source`, `signup_utm_medium`, `signup_utm_campaign`

**Add UTM params to links:**
```
https://www.dropspace.dev?utm_source=tiktok&utm_medium=social&utm_campaign=slideshow_feb
```

**Query attribution data via Supabase:**
```sql
SELECT signup_referrer, signup_utm_source, signup_utm_medium, signup_utm_campaign, created_at
FROM profiles
WHERE created_at >= now() - interval '7 days'
AND signup_utm_source IS NOT NULL;
```

## Launch Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /launches | List all (paginated: page, page_size 1-100) |
| POST | /launches | Create with AI-generated content |
| GET | /launches/:id | Get single with posting_status |
| PATCH | /launches/:id | Update draft/scheduled/cancelled (name, content, schedule, status, media, dropspace_platforms, user_platform_accounts) |
| DELETE | /launches/:id | Delete (not running) |
| POST | /launches/:id/publish | Publish (async, 202) |
| POST | /launches/:id/retry | Retry failed platforms only |
| POST | /launches/:id/retry-content | Retry content generation for failed platforms (optional `platforms` filter) |
| POST | /launches/:id/generate-content | Regenerate AI content (optional `platforms`, `generate_video_scripts`) |
| GET | /launches/:id/status | Detailed posting logs |
| GET | /launches/:id/analytics | Per-post engagement metrics (live refresh, 5-min cache) |
| DELETE | /launches/:id/posts/:logId | Delete a single published post from platform (logId from /status) |
| DELETE | /launches/:id/posts | Delete all published posts for a launch |

### Launch Status Lifecycle

Statuses in lifecycle order: `draft` → `manual` → `trigger` → `scheduled` → `running` → `completed` / `partial` / `failed` / `cancelled`

| Status | Cron auto-publishes? | Dashboard action buttons? | Can publish via API? | Use case |
|--------|---------------------|--------------------------|---------------------|----------|
| `draft` | ❌ | ❌ | ✅ | Initial creation, not ready |
| `manual` | ❌ | ✅ | ✅ | Ready, waiting for manual publish |
| `trigger` | ❌ | ✅ | ✅ | Ready, waiting for explicit trigger |
| `scheduled` | ✅ (when `scheduled_date ≤ now`) | ✅ | ✅ | Will auto-publish at scheduled time |
| `running` | — | — | — | Currently publishing |
| `completed` | — | — | — | All platforms succeeded |
| `partial` | — | — | ✅ (retry) | Some platforms failed |
| `failed` | — | — | ✅ (retry) | All platforms failed |
| `cancelled` | — | — | ✅ (retry) | Manually cancelled |

**Key rules:**
- The publish cron **only** picks up `scheduled` launches with `scheduled_date ≤ now`. All other statuses require manual action.
- **Status is auto-derived on PATCH** for editable launches (draft/manual/trigger/scheduled). The server overrides your requested status based on configuration:
  - Has `user_platform_accounts` or `dropspace_platforms` + `scheduled_date` → `scheduled`
  - Has `user_platform_accounts` or `dropspace_platforms` + no `scheduled_date` → `trigger`
  - Has content + no posting accounts → `manual`
  - This means you **cannot force `manual`** on a launch that has posting accounts. It will auto-transition to `trigger`.
- To **unschedule** without losing settings: PATCH with `{"scheduled_date": null}`. The server will auto-set status to `trigger` (since posting accounts exist). Do NOT set to `draft` (loses dashboard action buttons) or DELETE (soft-deletes, hard to recover).
- To **pause** a scheduled launch: PATCH `{"scheduled_date": null}`. Status becomes `trigger` automatically.
- `POST /launches/:id/publish` triggers **immediate** publishing regardless of `scheduled_date`. Never call this on scheduled launches unless you want them published now.
- `manual` = no posting accounts configured (publish manually). `trigger` = has posting accounts but no schedule (publish on demand).

PATCH fields: `name` (1-200 chars), `scheduled_date` (ISO 8601 | null to unschedule), `status`, `platforms`, `product_description` (max 10,000 chars), `product_url` (empty string to clear), `persona_id` (null to clear), `platform_contents` (deep-merged per platform — existing platforms preserved, within a platform included fields replace old values), `user_platform_accounts`, `dropspace_platforms`, `media`/`media_assets` (replaces entirely), `media_attach_platforms`, `media_mode`. All optional but ≥1 required. Running launch can only be `cancelled`. TikTok `tiktok_settings` is deep-merged (can update individual fields without overwriting others).

### Deleting Published Posts
- Requires `delete` scope on API key (enabled)
- **Works on:** Twitter, Facebook, LinkedIn, Reddit
- **Does NOT work on:** Instagram, TikTok (returns DELETE_NOT_SUPPORTED — manual deletion required)
- `logId` is the posting_log UUID from the `/status` endpoint
- If post was already deleted on platform (404), treated as successful deletion
- On success, posting log status updated to `deleted`
- Use Dropspace API: `DELETE /launches/:id/posts/:logId` or `DELETE /launches/:id/posts`

## Personas (Writing Styles)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /personas | List all (paginated) |
| POST | /personas | Create `{"name": "..."}` |
| GET | /personas/:id | Get with all writing samples + analysis |
| PATCH | /personas/:id | Update name/samples (custom, twitter, reddit, facebook, instagram, tiktok, linkedin — max 50 each) |
| DELETE | /personas/:id | Delete (not if used by launches) |
| POST | /personas/:id/analyze | Trigger AI analysis (async, 202). Optional: `platforms`, `include_custom_samples` |

Build statuses: `idle`, `building`, `complete`, `error`

## Media Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /media/generate | Submit job |
| GET | /media/:jobId | Poll status (processing/completed/failed) |

Request body for `/media/generate`:
- `type`: `"image"` | `"video"` | `"script_video"` (required)
- `launch_id`: UUID (required)
- `platform`: string (required for `script_video`: "instagram" or "tiktok")
- `prompt`: string 10-2000 chars (required for `script_video`)
- `product_description`: optional context
- `options.aspect_ratio`: image supports all 10 (`"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"`, `"3:2"`, `"2:3"`, `"5:4"`, `"4:5"`, `"21:9"`); video/script_video only `"16:9"` and `"9:16"`
- `options.duration_seconds`: 4 | 6 | 8 (default 8, video only)
- `reference_image_url`: URL of a reference image for style/composition guidance (image type only, uses edit endpoint)

`script_video` generates video from text script (requires `platform` and `prompt`). `video` generates from visual/cinematic prompt.

## Connections

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /connections | List OAuth platform connections (read-only, paginated) |

Returns: id, platform, entity_id, account_info (username, display_name), account_type, is_active, expires_at.

## Dropspace Official Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /dropspace/status | Check which official Dropspace accounts are connected |

Returns all 6 auto-post platforms (facebook, linkedin, twitter, reddit, instagram, tiktok) with connected status and account_name. Use `connected_platforms` to know valid values for `dropspace_platforms` field.

## API Keys Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /keys | List all API keys |
| GET | /keys/me | Get current API key info (id, name, scopes) — no scope required |
| POST | /keys | Create new key (max 10). Body: `{"name": "...", "scopes": ["read", "write", ...]}` |
| PATCH | /keys/:id | Rename key. Body: `{"name": "..."}` |
| DELETE | /keys/:id | Revoke key permanently |

Key shown only once on creation. Keys begin with `ds_live_`.
Default scopes: read, write, publish, generate. Available: read, write, delete, publish, generate, admin.

## Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /webhooks | List webhook endpoints |
| POST | /webhooks | Create endpoint (max 10). Body: `{"url": "https://...", "events": [...]}` |
| GET | /webhooks/:id | Get endpoint |
| PATCH | /webhooks/:id | Update url, events, or active status |
| DELETE | /webhooks/:id | Delete endpoint |
| POST | /webhooks/:id/rotate-secret | Rotate signing secret (new secret shown once) |
| GET | /webhooks/:id/deliveries | List delivery attempts (paginated) |

### Webhook Events

| Event | Fired when |
|-------|-----------|
| launch.completed | All platforms posted successfully |
| launch.failed | All platforms failed |
| launch.partial | Some succeeded, some failed |
| post.deleted | Post detected as deleted from platform (`deletion_reason`: not_found, gone, creator_deleted, moderation_removed, account_deleted, spam_filtered) |
| media.ready | Image/video generation completed |
| persona.analyzed | AI persona analysis finished |

### Webhook Delivery

Payload envelope: `{ "id": "evt_...", "event": "...", "created_at": "...", "data": { ... } }`

Headers: `Content-Type`, `X-Dropspace-Signature` (HMAC-SHA256), `X-Dropspace-Event`, `X-Dropspace-Delivery` (idempotency key).

Signature format: `sha256=<hex-digest>` of JSON body using webhook secret.

Retries: up to 3 with exponential backoff (QStash), 30s timeout. Return 2xx to acknowledge.

## Usage / Plan Limits

```bash
curl -s https://api.dropspace.dev/usage \
  -H "Authorization: Bearer $DROPSPACE_API_KEY"
```
Returns: plan name, billing period, limits (launches/month, AI images/month, AI videos/month, personas, analyses/persona, regenerations/launch), and features (can_connect_own_accounts, can_post_to_official_accounts, allowed_platforms). Limit/remaining can be `"unlimited"` (string) for higher-tier plans. Personas is a lifetime limit.

## Agent Payments (x402 + MPP)

Autonomous agents can use the API without accounts or subscriptions via two payment protocols:

**x402 (crypto):** USDC on Base via `X-PAYMENT` header (base64-encoded proof)
**MPP (Stripe):** Card charge via `Authorization: Payment <base64url>` header

- Only supported on launch endpoints (create, list, get, update, delete, publish, status)
- **5 free launches/month** using official Dropspace accounts
- Beyond free tier: $0.50 per launch creation (paid at creation, publishing is always free)
- Agent users can only post to official Dropspace accounts (not connected user accounts)
- Rate limit: 30 req/min per agent identity (wallet address for x402, payer credential for MPP)
- On 402 response, body contains both `x402` and `mpp` challenge objects

## Rate Limits

| Limit | Value |
|-------|-------|
| General API | 60 req/min per API key |
| Content generation | 30 req/min per user |
| Media generation | 5 req/min per user |
| Video concurrency | 2 per user / 20 global |

On 429: check `Retry-After` header (seconds). Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (Unix timestamp in milliseconds, not seconds).

## Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| AUTH_001 | 401 | Invalid/revoked key |
| AUTH_002 | 403 | Plan restriction |
| AUTH_003 | 403 | API key missing required scope |
| LAUNCH_001 | 404 | Launch not found |
| LAUNCH_002 | 429 | Launch/regen limit exceeded |
| LAUNCH_003 | 409 | Invalid status for operation |
| LAUNCH_004 | 409 | Not publishable / already publishing |
| LAUNCH_007 | 400 | Platform requirements not met |
| PERSONA_001 | 429 | Persona creation limit |
| PERSONA_002 | 404 | Persona not found |
| PERSONA_003 | 429 | Persona build limit |
| MEDIA_001 | 429 | Monthly media limit |
| UPLOAD_001 | 400 | Unsupported media type (allowed: jpeg, png, webp, gif, mp4, mov) |
| UPLOAD_002 | 400 | Media file too large (images: 5MB, videos: 512MB URL / 4MB base64) |
| UPLOAD_003 | 400 | Media storage upload failed |
| PAYMENT_001 | 402 | Payment required (free tier exceeded) |
| PAYMENT_002 | 402 | Payment verification failed |
| PAYMENT_003 | 402 | MPP credential verification failed |
| RATE_001 | 429 | Rate limited |
| SERVER_001 | 500 | Internal server error |
| SERVER_002 | 400 | Validation error |
| SERVER_003 | 404 | Resource not found |
| SERVER_004 | 405 | Method not allowed |
| SERVER_005 | 400 | Invalid input / business rule violation |
| SERVER_008 | 500 | Database error |
| SERVER_009 | 409 | Conflict (duplicate name, race condition, already building) |

## Open Source Pipeline

For the full automation pipeline (self-improving content engine, DJ clipper, photo slideshows), see the companion skills and repo:

- **dropspace-content-engine** — autonomous content generation + scheduling
- **dropspace-dj-clipper** — long recordings → short-form clips
- **dropspace-photo-slideshows** — event photos → daily TikTok slideshows
- Repo: https://github.com/joshchoi4881/dropspace-agents
