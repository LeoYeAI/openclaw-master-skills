# Xquik REST API Endpoints

Base URL: `https://xquik.com/api/v1`

All requests require the `x-api-key` header. All responses are JSON. HTTPS only.

## Table of Contents

- [Account](#account)
- [API Keys](#api-keys)
- [Monitors](#monitors)
- [Events](#events)
- [Webhooks](#webhooks)
- [Draws](#draws)
- [Extractions](#extractions)
- [X API (Direct Lookups)](#x-api-direct-lookups)
- [X Media (Download)](#x-media-download)
- [Trends](#trends)
- [Radar](#radar)
- [Compose](#compose)
- [Drafts](#drafts)
- [Tweet Style Cache](#tweet-style-cache)
- [Account Identity](#account-identity)
- [Subscribe](#subscribe)
- [X Accounts (Connected)](#x-accounts-connected)
- [X Write](#x-write)
- [Integrations](#integrations)

---

## Account

### Get Account

```
GET /account
```

Returns subscription status, monitor allocation, and current period usage.

**Response:**
```json
{
  "plan": "active",
  "monitorsAllowed": 1,
  "monitorsUsed": 0,
  "currentPeriod": {
    "start": "2026-02-01T00:00:00.000Z",
    "end": "2026-03-01T00:00:00.000Z",
    "usagePercent": 45
  }
}
```

### Update Account

```
PATCH /account
```

Update account locale. Session auth only (not API key).

**Body:** `{ "locale": "en" | "tr" | "es" }`

---

## API Keys

Session auth only. These endpoints do not accept API key auth.

### Create API Key

```
POST /api-keys
```

**Body:** `{ "name": "My Key" }` (optional)

**Response:** Returns `fullKey` (shown only once), `prefix`, `name`, `id`, `createdAt`.

### List API Keys

```
GET /api-keys
```

Returns all keys with `id`, `name`, `prefix`, `isActive`, `createdAt`, `lastUsedAt`. Full key is never exposed.

### Revoke API Key

```
DELETE /api-keys/{id}
```

Permanent and irreversible. The key stops working immediately.

---

## Monitors

### Create Monitor

```
POST /monitors
```

**Body:**
```json
{
  "username": "elonmusk",
  "eventTypes": ["tweet.new", "tweet.reply", "tweet.quote"]
}
```

**Response:**
```json
{
  "id": "7",
  "username": "elonmusk",
  "xUserId": "44196397",
  "eventTypes": ["tweet.new", "tweet.reply", "tweet.quote"],
  "createdAt": "2026-02-24T10:30:00.000Z"
}
```

Event types: `tweet.new`, `tweet.quote`, `tweet.reply`, `tweet.retweet`, `follower.gained`, `follower.lost`.

Returns `409 monitor_already_exists` if the username is already monitored.

### List Monitors

```
GET /monitors
```

Returns all monitors (up to 200, no pagination). Response includes `monitors` array and `total` count.

### Get Monitor

```
GET /monitors/{id}
```

### Update Monitor

```
PATCH /monitors/{id}
```

**Body:** `{ "eventTypes": [...], "isActive": true|false }` (both optional)

### Delete Monitor

```
DELETE /monitors/{id}
```

Stops tracking and deletes all associated data.

---

## Events

### List Events

```
GET /events
```

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `monitorId` | string | Filter by monitor ID |
| `eventType` | string | Filter by event type |
| `limit` | number | Results per page (1-100, default 50) |
| `after` | string | Cursor for next page |

**Response:**
```json
{
  "events": [
    {
      "id": "9010",
      "type": "tweet.new",
      "monitorId": "7",
      "username": "elonmusk",
      "occurredAt": "2026-02-24T16:45:00.000Z",
      "data": {
        "tweetId": "1893556789012345678",
        "text": "Hello world",
        "metrics": { "likes": 3200, "retweets": 890, "replies": 245 }
      }
    }
  ],
  "hasMore": true,
  "nextCursor": "MjAyNi0wMi0yNFQxNjozMDowMC4wMDBa..."
}
```

### Get Event

```
GET /events/{id}
```

Returns a single event with full details.

---

## Webhooks

### Create Webhook

```
POST /webhooks
```

**Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "eventTypes": ["tweet.new", "tweet.reply"]
}
```

**Response** includes a `secret` field (shown only once). Store it for signature verification.

### List Webhooks

```
GET /webhooks
```

Returns all webhooks (up to 200). Secret is never exposed in list responses.

### Update Webhook

```
PATCH /webhooks/{id}
```

**Body:** `{ "url": "...", "eventTypes": [...], "isActive": true|false }` (all optional)

### Delete Webhook

```
DELETE /webhooks/{id}
```

Permanently removes the webhook. All future deliveries are stopped.

### Test Webhook

```
POST /webhooks/{id}/test
```

Sends a `webhook.test` event to the webhook endpoint, HMAC-signed with the webhook's secret. Returns success or failure status with HTTP response details.

**Payload delivered to your endpoint:**
```json
{
  "eventType": "webhook.test",
  "data": {
    "message": "Test delivery from Xquik"
  },
  "timestamp": "2026-02-27T12:00:00.000Z"
}
```

The delivery includes the `X-Xquik-Signature` header, identical to production deliveries.

Returns `400 webhook_inactive` if the webhook is disabled. Reactivate via `PATCH /webhooks/{id}` before testing.

### List Deliveries

```
GET /webhooks/{id}/deliveries
```

View delivery attempts and statuses for a webhook. Statuses: `pending`, `delivered`, `failed`, `exhausted`.

---

## Draws

### Create Draw

```
POST /draws
```

Run a giveaway draw from a tweet. Picks random winners from replies.

**Body:**
```json
{
  "tweetUrl": "https://x.com/user/status/1893456789012345678",
  "winnerCount": 3,
  "backupCount": 2,
  "uniqueAuthorsOnly": true,
  "mustRetweet": true,
  "mustFollowUsername": "burakbayir",
  "filterMinFollowers": 100,
  "filterAccountAgeDays": 30,
  "filterLanguage": "en",
  "requiredKeywords": ["giveaway"],
  "requiredHashtags": ["#contest"],
  "requiredMentions": ["@xquik"]
}
```

All filter fields are optional. Only `tweetUrl` is required.

**Response:**
```json
{
  "id": "42",
  "tweetId": "1893456789012345678",
  "tweetUrl": "https://x.com/user/status/1893456789012345678",
  "tweetText": "Like & RT to enter! Picking 3 winners tomorrow.",
  "tweetAuthorUsername": "xquik",
  "tweetLikeCount": 4200,
  "tweetRetweetCount": 1800,
  "tweetReplyCount": 1500,
  "tweetQuoteCount": 120,
  "status": "completed",
  "totalEntries": 1500,
  "validEntries": 890,
  "createdAt": "2026-02-24T10:00:00.000Z",
  "drawnAt": "2026-02-24T10:01:00.000Z"
}
```

### List Draws

```
GET /draws
```

Cursor-paginated. Returns compact draw objects.

### Get Draw

```
GET /draws/{id}
```

Returns full draw details including winners.

### Export Draw

```
GET /draws/{id}/export?format=csv&type=winners
```

Formats: `csv`, `xlsx`, `md`. Types: `winners` (default), `entries`. Entry exports capped at 50,000 rows.

---

## Extractions

### Create Extraction

```
POST /extractions
```

Run a bulk data extraction job. See `references/extractions.md` for all 20 tool types.

**Body:**
```json
{
  "toolType": "reply_extractor",
  "targetTweetId": "1893704267862470862",
  "resultsLimit": 500
}
```

`resultsLimit` (optional): Maximum results to extract. Stops early instead of fetching all data. Useful for controlling costs.

**Response:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "toolType": "reply_extractor",
  "status": "running"
}
```

### Estimate Extraction

```
POST /extractions/estimate
```

Preview the cost before running. Same body as create.

**Response:**
```json
{
  "allowed": true,
  "source": "replyCount",
  "estimatedResults": 150,
  "usagePercent": 45,
  "projectedPercent": 48
}
```

### List Extractions

```
GET /extractions
```

Cursor-paginated. Filter by `status` and `toolType`.

### Get Extraction

```
GET /extractions/{id}
```

Returns job details with paginated results (up to 1,000 per page).

### Export Extraction

```
GET /extractions/{id}/export?format=csv
```

Formats: `csv`, `xlsx`, `md`. 50,000 row limit. Exports include enrichment columns not in the API response.

---

## X API (Direct Lookups)

Metered operations that count toward the monthly quota.

### Get Tweet

```
GET /x/tweets/{id}
```

Returns full tweet with engagement metrics (likes, retweets, replies, quotes, views, bookmarks), author info (username, followers, verified status, profile picture), and optional attached media (photos/videos with URLs).

### Search Tweets

```
GET /x/tweets/search?q={query}
```

Search using X syntax: keywords, `#hashtags`, `from:user`, `to:user`, `"exact phrases"`, `OR`, `-exclude`.

Returns tweet info with optional engagement metrics (likeCount, retweetCount, replyCount) and optional attached media. Some fields may be omitted if unavailable.

### Get User

```
GET /x/users/{username}
```

Returns profile info. Fields `id`, `username`, `name` are always present. All other fields (`description`, `followers`, `following`, `verified`, `profilePicture`, `location`, `createdAt`, `statusesCount`) are optional and omitted when unavailable.

### Check Follower

```
GET /x/followers/check?source={username}&target={username}
```

Returns `isFollowing` and `isFollowedBy` for both directions.

---

## X Media (Download)

### Download Media

```
POST /x/media/download
```

Download images, videos, and GIFs from tweets. Single or bulk (up to 50). Returns a shareable gallery URL.

**Body:** Provide either `tweetInput` (single tweet) or `tweetIds` (bulk). Exactly 1 is required.

| Field | Type | Description |
|-------|------|-------------|
| `tweetInput` | string | Tweet URL or numeric tweet ID for a single download. Accepts `x.com` and `twitter.com` URL formats |
| `tweetIds` | string[] | Array of tweet URLs or IDs for bulk download. Maximum 50 items. Returns a single combined gallery |

**Response (single):**
```json
{
  "tweetId": "1893456789012345678",
  "galleryUrl": "https://xquik.com/gallery/abc123",
  "cacheHit": false
}
```

**Response (bulk):**
```json
{
  "galleryUrl": "https://xquik.com/gallery/def456",
  "totalTweets": 3,
  "totalMedia": 7
}
```

First download is metered (counts toward monthly quota). Subsequent requests for the same tweet return cached URLs at no cost (`cacheHit: true`). All downloads are saved to the gallery at `https://xquik.com/gallery`.

Returns `400 no_media` if the tweet has no downloadable media. Returns `400 too_many_tweets` if bulk array exceeds 50 items.

---

## Trends

### List Trends

```
GET /trends?woeid=1&count=30
```

Metered. Subscription required. Cached, refreshes every 15 minutes.

**WOEIDs:** 1 (Worldwide), 23424977 (US), 23424975 (UK), 23424969 (Turkey), 23424950 (Spain), 23424829 (Germany), 23424819 (France), 23424856 (Japan), 23424848 (India), 23424768 (Brazil), 23424775 (Canada), 23424900 (Mexico).

**Response:**
```json
{
  "trends": [
    { "name": "#AI", "description": "...", "rank": 1, "query": "#AI" }
  ],
  "total": 30,
  "woeid": 1
}
```

---

## Radar

### List Radar Items

```
GET /radar
```

Get trending topics and news from 7 sources: Google Trends, Hacker News, Polymarket, TrustMRR, Wikipedia, GitHub Trending, Reddit. Free.

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `source` | string | Filter by source: `google_trends`, `hacker_news`, `polymarket`, `trustmrr`, `wikipedia`, `github`, `reddit` |
| `category` | string | Filter by category: `general`, `tech`, `dev`, `science`, `culture`, `politics`, `business`, `entertainment` |
| `limit` | number | Items per page (1-100, default 50) |
| `hours` | number | Look-back window in hours (1-72, default 6) |
| `region` | string | Region code: `US`, `GB`, `TR`, `ES`, `DE`, `FR`, `JP`, `IN`, `BR`, `CA`, `MX`, `global` (default) |

**Response:**
```json
{
  "items": [
    {
      "id": "12345",
      "title": "Claude 4.6 Released",
      "description": "Anthropic releases Claude 4.6...",
      "url": "https://example.com/article",
      "imageUrl": "https://example.com/image.png",
      "source": "hacker_news",
      "sourceId": "hn_12345",
      "category": "tech",
      "region": "global",
      "language": "en",
      "score": 450,
      "metadata": { "points": 450, "numberComments": 132, "author": "pgdev" },
      "publishedAt": "2026-03-05T10:00:00.000Z",
      "createdAt": "2026-03-05T10:05:00.000Z"
    }
  ],
  "hasMore": true,
  "nextCursor": "NDUwfDIwMjYtMDMtMDRUMDg6MzA6MDAuMDAwWnwxMjM0NQ=="
}
```

Fields: `id`, `title`, `description?`, `url?`, `imageUrl?`, `source`, `sourceId`, `category`, `region`, `language`, `score`, `metadata`, `publishedAt`, `createdAt`. Response includes `hasMore` and `nextCursor` for pagination.

---

## Compose

### Compose Tweet

```
POST /compose
```

Compose, refine, and score tweets using X algorithm data. Free, 3-step workflow.

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `step` | string | Yes | `compose`, `refine`, or `score` |
| `topic` | string | No | Tweet topic (compose, refine) |
| `goal` | string | No | `engagement`, `followers`, `authority`, `conversation` |
| `styleUsername` | string | No | Cached style username for voice matching (compose) |
| `tone` | string | No | Desired tone (refine) |
| `additionalContext` | string | No | Extra context or URLs (refine) |
| `callToAction` | string | No | Desired CTA (refine) |
| `mediaType` | string | No | `photo`, `video`, `none` (refine) |
| `draft` | string | No | Tweet text to evaluate (score) |
| `hasLink` | boolean | No | Link attached (score) |
| `hasMedia` | boolean | No | Media attached (score) |

**Response (step=compose):** Returns `contentRules`, `scorerWeights`, `followUpQuestions`, `algorithmInsights`, `engagementMultipliers`, `topPenalties`.

**Response (step=refine):** Returns `compositionGuidance`, `examplePatterns`.

**Response (step=score):** Returns `totalChecks`, `passedCount`, `topSuggestion`, `checklist[]` with `factor`, `passed`, `suggestion`.

---

## Drafts

### Create Draft

`POST /drafts`

Save a tweet draft for later.

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The draft tweet text |
| `topic` | string | No | Topic the tweet is about |
| `goal` | string | No | Optimization goal: `engagement`, `followers`, `authority`, `conversation` |

**Response (201):**

```json
{
  "id": "123",
  "text": "draft text",
  "topic": "product launch",
  "goal": "engagement",
  "createdAt": "2026-02-24T10:30:00.000Z",
  "updatedAt": "2026-02-24T10:30:00.000Z"
}
```

---

### List Drafts

`GET /drafts`

List saved tweet drafts with cursor pagination.

**Query parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | number | No | 50 | Results per page (max 50) |
| `afterCursor` | string | No | - | Pagination cursor from previous response |

**Response (200):**

```json
{
  "drafts": [
    {
      "id": "123",
      "text": "draft text",
      "topic": "product launch",
      "goal": "engagement",
      "createdAt": "2026-02-24T10:30:00.000Z",
      "updatedAt": "2026-02-24T10:30:00.000Z"
    }
  ],
  "afterCursor": "cursor_string",
  "hasMore": true
}
```

---

### Get Draft

`GET /drafts/{id}`

Get a specific draft by ID.

**Response (200):** Single draft object.

**Errors:** `400 invalid_id`, `404 draft_not_found`

---

### Delete Draft

`DELETE /drafts/{id}`

Delete a draft. Returns `204 No Content`.

**Errors:** `400 invalid_id`, `404 draft_not_found`

---

## Tweet Style Cache

### Analyze & Cache Style

`POST /styles`

Fetch recent tweets from an X account and cache them for style analysis. **Consumes API usage credits.**

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | X username to analyze (without @) |

**Response (201):**

```json
{
  "xUsername": "elonmusk",
  "tweetCount": 20,
  "isOwnAccount": false,
  "fetchedAt": "2026-02-24T10:30:00.000Z",
  "tweets": [
    {
      "id": "1893456789012345678",
      "text": "The future is now.",
      "authorUsername": "elonmusk",
      "createdAt": "2026-02-24T14:22:00.000Z"
    }
  ]
}
```

---

### List Cached Styles

`GET /styles`

List all cached tweet style profiles. Max 200 results, ordered by fetch date.

**Response (200):**

```json
{
  "styles": [
    {
      "xUsername": "elonmusk",
      "tweetCount": 20,
      "isOwnAccount": false,
      "fetchedAt": "2026-02-24T10:30:00.000Z"
    }
  ]
}
```

---

### Save Custom Style

`PUT /styles/{username}`

Save a custom style profile from tweet texts. Free, no usage cost. Replaces existing style if one exists with the same label.

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Style label name (1-30 characters) |
| `tweets` | object[] | Yes | Array of tweet objects (1-100). Each must have a `text` field |

**Response (200):** Style object with label, `tweetCount`, `isOwnAccount: false`, `fetchedAt`, and `tweets` array.

**Errors:** `400 invalid_input`

---

### Get Cached Style

`GET /styles/{username}`

Get a cached style profile with full tweet data.

**Response (200):** Full style object with `tweets` array.

**Errors:** `404 style_not_found`

---

### Delete Cached Style

`DELETE /styles/{username}`

Delete a cached style. Returns `204 No Content`.

**Errors:** `404 style_not_found`

---

### Compare Styles

`GET /styles/compare?username1=A&username2=B`

Compare two cached tweet style profiles side by side.

**Query parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username1` | string | Yes | First X username |
| `username2` | string | Yes | Second X username |

**Response (200):**

```json
{
  "style1": { "xUsername": "user1", "tweetCount": 20, "isOwnAccount": true, "fetchedAt": "...", "tweets": [...] },
  "style2": { "xUsername": "user2", "tweetCount": 15, "isOwnAccount": false, "fetchedAt": "...", "tweets": [...] }
}
```

**Errors:** `400 missing_params`, `404 style_not_found`

---

### Analyze Performance

`GET /styles/{username}/performance`

Get live engagement metrics for cached tweets. **Consumes API usage credits.**

**Response (200):**

```json
{
  "xUsername": "elonmusk",
  "tweetCount": 20,
  "tweets": [
    {
      "id": "1893456789012345678",
      "text": "The future is now.",
      "likeCount": 42000,
      "retweetCount": 8500,
      "replyCount": 3200,
      "quoteCount": 1100,
      "viewCount": 5000000,
      "bookmarkCount": 2400
    }
  ]
}
```

**Errors:** `404 style_not_found`

---

## Account Identity

### Set X Identity

`PUT /account/x-identity`

Link your X username to your Xquik account. Required for own-account detection in style analysis.

**Request body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | Your X username (without @) |

**Response (200):**

```json
{
  "success": true,
  "xUsername": "elonmusk"
}
```

**Errors:** `400 invalid_input`

---

## Subscribe

### Get Subscription Link

```
POST /subscribe
```

Returns a Stripe Checkout URL for subscribing or managing the subscription. If already subscribed, returns the billing portal URL.

**Response:**
```json
{
  "url": "https://checkout.stripe.com/c/pay/..."
}
```

---

## X Accounts (Connected)

Manage connected X accounts for write actions. All endpoints are free (no usage cost).

### List X Accounts

```
GET /x/accounts
```

Returns all connected X accounts. Response: `{ accounts: [{ id, username, displayName, isActive, createdAt }] }`.

### Connect X Account

```
POST /x/accounts
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | X username (`@` auto-stripped) |
| `email` | string | Yes | Email associated with the X account |
| `password` | string | Yes | Account password (encrypted at rest) |
| `totp_secret` | string | No | TOTP base32 secret for 2FA accounts |
| `proxy_country` | string | No | Preferred proxy region (e.g. `"US"`, `"TR"`) |

**Response (201):** `{ id, username, isActive, createdAt }`

**Errors:** `409 account_already_connected`, `422 connection_failed`

### Get X Account

```
GET /x/accounts/{id}
```

Returns `{ id, username, displayName, isActive, createdAt }`.

### Disconnect X Account

```
DELETE /x/accounts/{id}
```

Permanently removes the account and deletes stored credentials. Returns `{ success: true }`.

### Re-authenticate X Account

```
POST /x/accounts/{id}/reauth
```

Use when a session expires or X requires re-verification.

**Body:** `{ "password": "...", "totp_secret": "..." }` (password required, totp_secret optional)

**Response:** `{ success: true }`

**Errors:** `422 reauth_failed`

---

## X Write

Write actions performed through connected X accounts. All endpoints are metered. Every request requires an `account` field (username or account ID) identifying which connected account to use.

### Create Tweet

```
POST /x/tweets
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account` | string | Yes | Connected X username or account ID |
| `text` | string | Yes | Tweet text (280 chars, or 25,000 if `is_note_tweet` is true) |
| `reply_to_tweet_id` | string | No | Tweet ID to reply to |
| `attachment_url` | string | No | URL to attach as a card |
| `community_id` | string | No | Community ID to post into |
| `is_note_tweet` | boolean | No | Long-form note tweet (up to 25,000 chars) |
| `media_ids` | string[] | No | Media IDs from `POST /x/media` (max 4 images or 1 video) |

**Response:** `{ tweetId, success: true }`

**Errors:** `502 x_write_failed`

### Delete Tweet

```
DELETE /x/tweets/{id}
```

**Body:** `{ "account": "username" }`

**Response:** `{ success: true }`

### Like Tweet

```
POST /x/tweets/{id}/like
```

**Body:** `{ "account": "username" }`

### Unlike Tweet

```
DELETE /x/tweets/{id}/like
```

**Body:** `{ "account": "username" }`

### Retweet

```
POST /x/tweets/{id}/retweet
```

**Body:** `{ "account": "username" }`

### Follow User

```
POST /x/users/{id}/follow
```

**Body:** `{ "account": "username" }`

**Errors:** `502 upstream_error`

### Unfollow User

```
DELETE /x/users/{id}/follow
```

**Body:** `{ "account": "username" }`

### Send DM

```
POST /x/dm/{userId}
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account` | string | Yes | Connected X username or account ID |
| `text` | string | Yes | Message text |
| `media_ids` | string[] | No | Media IDs to attach |
| `reply_to_message_id` | string | No | Message ID to reply to |

### Update Profile

```
PATCH /x/profile
```

**Body:** `{ "account": "username", "name": "...", "description": "...", "location": "...", "url": "..." }` (account required, others optional)

### Update Avatar

```
PATCH /x/profile/avatar
```

**Body:** FormData with `account` (required) and `file` (required, max 700 KB).

### Update Banner

```
PATCH /x/profile/banner
```

**Body:** FormData with `account` (required) and `file` (required, max 2 MB).

### Upload Media

```
POST /x/media
```

**Body:** FormData with `account` (required), `file` (required), and `is_long_video` (optional boolean).

**Response:** Returns a media ID to pass in `media_ids` when creating a tweet.

### Create Community

```
POST /x/communities
```

**Body:** `{ "account": "username", "name": "...", "description": "..." }` (all required)

### Delete Community

```
DELETE /x/communities/{id}
```

**Body:** `{ "account": "username", "community_name": "..." }` (name required for confirmation)

### Join Community

```
POST /x/communities/{id}/join
```

**Body:** `{ "account": "username" }`

**Errors:** `409 already_member`

### Leave Community

```
DELETE /x/communities/{id}/join
```

**Body:** `{ "account": "username" }`

---

## Integrations

Manage third-party integrations (currently Telegram) that receive monitor event notifications. All endpoints are free (no usage cost).

### Create Integration

```
POST /integrations
```

**Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Integration type: `"telegram"` |
| `name` | string | Yes | Human-readable name |
| `config` | object | Yes | Type-specific config. Telegram: `{ chatId: "-1001234567890" }` |
| `eventTypes` | string[] | Yes | Event types: `tweet.new`, `tweet.quote`, `tweet.reply`, `tweet.retweet`, `follower.gained`, `follower.lost` |

**Response (201):** `{ id, type, name, config, eventTypes, isActive, createdAt }`

### List Integrations

```
GET /integrations
```

Returns all integrations. Response: `{ integrations: [...] }`.

### Get Integration

```
GET /integrations/{id}
```

Returns a single integration with full details.

### Update Integration

```
PATCH /integrations/{id}
```

**Body:** `{ "name": "...", "eventTypes": [...], "isActive": true|false, "silentPush": false, "scopeAllMonitors": true, "filters": {}, "messageTemplate": {} }` (all optional, at least 1 required)

### Delete Integration

```
DELETE /integrations/{id}
```

Permanently removes the integration. Returns `204 No Content`.

### Test Integration

```
POST /integrations/{id}/test
```

Sends a test notification. Returns success or failure status.

**Errors:** `502 delivery_failed`

### List Deliveries

```
GET /integrations/{id}/deliveries
```

View delivery attempts and statuses. Statuses: `pending`, `delivered`, `failed`, `exhausted`.

**Query:** `limit` (default 50).

---

## Error Codes

| Status | Code | Meaning |
|--------|------|---------|
| 400 | `invalid_input` | Request body failed validation |
| 400 | `invalid_id` | Path parameter is not a valid ID |
| 400 | `invalid_tweet_url` | Tweet URL format is invalid |
| 400 | `invalid_tweet_id` | Tweet ID is empty or invalid |
| 400 | `invalid_username` | X username is empty or invalid |
| 400 | `invalid_tool_type` | Extraction tool type not recognized |
| 400 | `invalid_format` | Export format not `csv`, `xlsx`, or `md` |
| 400 | `invalid_params` | Export query parameters are missing or invalid |
| 400 | `missing_query` | Required query parameter is missing |
| 400 | `missing_params` | Required query parameters are missing |
| 400 | `no_media` | Tweet has no downloadable media |
| 400 | `webhook_inactive` | Webhook is disabled (test-webhook only) |
| 401 | `unauthenticated` | Missing or invalid API key |
| 402 | `no_subscription` | No active subscription |
| 402 | `subscription_inactive` | Subscription is not active |
| 402 | `usage_limit_reached` | Monthly usage cap exceeded |
| 402 | `extra_usage_disabled` | Extra usage not enabled |
| 402 | `extra_usage_requires_v2` | Extra usage requires the new pricing plan |
| 402 | `frozen` | Extra usage paused, outstanding payment required |
| 402 | `overage_limit_reached` | Overage spending limit reached |
| 403 | `monitor_limit_reached` | Plan monitor limit exceeded |
| 403 | `api_key_limit_reached` | API key limit reached (100 max) |
| 402 | `no_addon` | No monitor addon on subscription |
| 404 | `not_found` | Resource does not exist |
| 404 | `user_not_found` | X user not found |
| 404 | `tweet_not_found` | Tweet not found |
| 404 | `style_not_found` | No cached style found |
| 404 | `draft_not_found` | Draft not found |
| 404 | `account_not_found` | Connected X account not found |
| 409 | `monitor_already_exists` | Duplicate monitor for same username |
| 409 | `account_already_connected` | X account already connected |
| 409 | `already_member` | Already a member of the community |
| 422 | `connection_failed` | X credential verification failed |
| 422 | `reauth_failed` | X re-authentication failed |
| 429 | - | Rate limited. Retry with backoff |
| 429 | `x_api_rate_limited` | X data source rate limited. Retry |
| 500 | `internal_error` | Server error |
| 502 | `stream_registration_failed` | Stream registration failed. Retry |
| 502 | `x_api_unavailable` | X data source temporarily unavailable |
| 502 | `x_api_unauthorized` | X data source authentication failed. Retry |
| 502 | `x_write_failed` | Write action failed (tweet, delete, like, retweet) |
| 502 | `upstream_error` | Upstream action failed (follow, DM, profile update) |
| 502 | `delivery_failed` | Integration test delivery failed |
