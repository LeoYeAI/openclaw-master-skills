# PostFast API Reference

Base URL: `https://api.postfa.st`
Auth: `pf-api-key` header with workspace API key.

## Endpoints

### GET /social-media/my-social-accounts

List all connected social media accounts.

**Response:**
```json
[
  {
    "id": "6a87b56e-ba73-4696-a415-3d524f1a92f8",
    "platform": "FACEBOOK",
    "platformUsername": "johndoe",
    "displayName": "John's Page"
  }
]
```

Platform values: `TIKTOK`, `INSTAGRAM`, `FACEBOOK`, `X`, `YOUTUBE`, `LINKEDIN`, `THREADS`, `BLUESKY`, `PINTEREST`, `TELEGRAM`

### GET /social-media/:id/pinterest-boards

Get Pinterest boards for a connected account.

**Response:**
```json
[{ "boardId": "1234567890123456789", "name": "My Recipes" }]
```

### GET /social-media/:id/youtube-playlists

Get YouTube playlists for a connected account.

**Response:**
```json
[{ "playlistId": "PLrAXtmErZgOe...", "title": "My Tutorials" }]
```

### POST /file/get-signed-upload-urls

Get pre-signed S3 URLs for media upload.

**Request:**
```json
{ "contentType": "image/png", "count": 1 }
```

Supported content types: `image/png`, `image/jpeg`, `image/jpg`, `image/gif`, `image/webp`, `video/mp4`, `video/quicktime`, `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`

**Response:**
```json
[{ "key": "image/a1b2c3d4-e5f6-7890-1234-567890abcdef.png", "signedUrl": "https://s3..." }]
```

Then PUT the raw file to `signedUrl` with matching `Content-Type` header.

### GET /social-posts

List and filter posts. Supports pagination, platform/status filtering, and date ranges.

**Query params:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 0 | 0-based page index |
| `limit` | int | 20 | Items per page (max 50) |
| `platforms` | string | — | Comma-separated: `FACEBOOK,INSTAGRAM,X,TIKTOK,LINKEDIN,YOUTUBE,BLUESKY,THREADS,PINTEREST,TELEGRAM` |
| `statuses` | string | — | Comma-separated: `DRAFT,SCHEDULED,PUBLISHED,FAILED` |
| `from` | ISO 8601 | — | Start date filter (inclusive, on `scheduledAt`) |
| `to` | ISO 8601 | — | End date filter (inclusive, on `scheduledAt`) |

Sorting is fixed to `scheduledAt` ascending. Platform and status values are case-insensitive.

**Response:**
```json
{
  "data": [
    {
      "id": "post-uuid",
      "content": "Post text",
      "status": "DRAFT | SCHEDULED | PUBLISHED | FAILED",
      "approvalStatus": "PENDING_APPROVAL | IN_PROGRESS | APPROVED | REJECTED | NEEDS_WORK",
      "socialMediaId": "account-uuid",
      "mediaItems": [{ "key": "image/...", "type": "IMAGE", "url": "https://...", "sortOrder": 0 }],
      "scheduledAt": "2026-06-15T10:00:00.000Z",
      "publishedAt": "2026-06-15T10:00:05.000Z | null",
      "failedAt": "... | null",
      "platformPostId": "string | null",
      "groupId": "uuid | null",
      "lastError": { "message": "User-friendly error", "code": "platform-code" },
      "firstComment": "string | null",
      "firstCommentError": "string | null"
    }
  ],
  "totalCount": 25,
  "pageInfo": { "page": 1, "hasNextPage": true, "perPage": 20 }
}
```

Rate limit: 200 requests/hour.

### POST /social-posts

Create/schedule one or more posts. Up to 15 posts per request. Rate limit: 350/day.

**Request:**
```json
{
  "posts": [
    {
      "content": "Post text with #hashtags",
      "mediaItems": [
        {
          "key": "image/uuid.png",
          "type": "IMAGE",
          "sortOrder": 0
        }
      ],
      "scheduledAt": "2026-06-15T10:00:00.000Z",
      "socialMediaId": "account-uuid",
      "firstComment": "Check out our link: https://example.com"
    }
  ],
  "status": "SCHEDULED",
  "approvalStatus": "APPROVED",
  "controls": {
    "tiktokPrivacy": "PUBLIC",
    "instagramPublishType": "REEL"
  }
}
```

**Post fields:**
- `content` (string, required): Post text/caption
- `mediaItems` (array): Media attachments. Each has `key` (from upload), `type` (`IMAGE`/`VIDEO`), `sortOrder` (int)
- `scheduledAt` (string): ISO 8601 UTC, must be in the future. Optional for draft posts
- `socialMediaId` (string, required): Target account ID from `/my-social-accounts`
- `firstComment` (string, optional): Auto-posted ~10s after publish. Supported: X, Instagram, Facebook, YouTube, Threads. NOT supported: TikTok, Pinterest, Bluesky, LinkedIn

**Top-level fields:**
- `status` (string): `DRAFT` or `SCHEDULED` (default: `SCHEDULED`). Drafts don't need `scheduledAt`
- `approvalStatus` (string): `APPROVED` or `PENDING_APPROVAL` (default: `APPROVED`)
- `controls` (object): Platform-specific settings. See platform-controls.md for all options

**mediaItems extra fields:**
- `coverTimestamp` (string): Video thumbnail timestamp in seconds (e.g., `"3"`)

**Cross-posting**: Add multiple objects to the `posts` array, each with different `socialMediaId`. The `controls` object applies to all posts in the batch.

**Platform posting limits:** X (Twitter) allows max 5 posts per account per day via API.

**Response:**
```json
{ "postIds": ["uuid-1", "uuid-2"] }
```

One ID per entry in the `posts` array.

### POST /social-media/connect-link

Generate a secure link for clients to connect their social accounts to your workspace — no PostFast account required. Rate limit: 50/hour.

**Request:**
```json
{
  "expiryDays": 7,
  "sendEmail": true,
  "email": "client@example.com"
}
```

- `expiryDays` (int, optional): 1-30, default 7
- `sendEmail` (bool, optional): Send link via email, default false
- `email` (string): Required when `sendEmail` is true

**Response:**
```json
{ "connectUrl": "https://app.postfa.st/connect?token=eyJhbGci..." }
```

Share the `connectUrl` with the client. The token is a JWT — do not truncate it.

### DELETE /social-posts/:id

Delete a scheduled post by ID.

**Response:**
```json
{ "deleted": true }
```

## Error Responses

| Code | Meaning |
|------|---------|
| `400` | Bad request — missing fields, invalid data, scheduledAt in the past |
| `401` | Invalid or missing API key |
| `403` | Forbidden — insufficient permissions |
| `404` | Resource not found |
| `429` | Rate limit exceeded — check `Retry-After-*` header |

## Rate Limits

Per API key (workspace):
- 60 requests/minute
- 150 requests/5 minutes
- 300 requests/hour
- 2,000 requests/day

Response headers: `X-RateLimit-Limit-*`, `X-RateLimit-Remaining-*`, `X-RateLimit-Reset-*`, `Retry-After-*`
