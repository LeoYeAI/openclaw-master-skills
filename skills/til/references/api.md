# API Reference

Base URL: `https://opentil.ai/api/v1`

All requests require a Bearer token:

```
Authorization: Bearer $OPENTIL_TOKEN
```

## POST /entries -- Create Entry

### Request Body

All fields are nested under `entry`. Additionally, `tag_names` and `category_name` are accepted at the `entry` level as convenience parameters.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | yes | Markdown body (max 100,000 chars) |
| `title` | string | no | Entry title (max 200 chars). Auto-generates slug if omitted. |
| `slug` | string | no | Custom URL slug. Auto-generated from title if omitted. |
| `tag_names` | array | no | 1-3 lowercase tags, e.g. `["go", "concurrency"]` |
| `category_name` | string | no | Category name. Only include if the user explicitly specifies one. |
| `category_id` | integer | no | Category ID (alternative to `category_name`). |
| `published` | boolean | no | `false` for draft (default), `true` to publish immediately. |
| `published_at` | datetime | no | ISO 8601 timestamp. Only relevant when publishing. |
| `visibility` | string | no | `public` (default), `unlisted`, or `private` |
| `summary` | string | no | AI-generated summary for listing pages (max 500 chars) |
| `meta_description` | string | no | SEO meta description |
| `meta_image` | string | no | URL for social sharing image |
| `lang` | string | no | Language code (see Supported Languages below) |

### Supported Languages

`en`, `zh-CN`, `zh-TW`, `ja`, `ko`, `es`, `fr`, `de`, `pt-BR`, `pt`, `ru`, `ar`, `bs`, `da`, `nb`, `pl`, `th`, `tr`, `it`

### 201 Response (EntrySerializer)

```json
{
  "id": "1234567890",
  "title": "Go interfaces are satisfied implicitly",
  "slug": "go-interfaces-are-satisfied-implicitly",
  "content": "In Go, a type implements an interface...",
  "content_html": "<p>In Go, a type implements an interface...</p>",
  "published": false,
  "published_at": null,
  "first_published_at": null,
  "visibility": "public",
  "hidden": false,
  "summary": null,
  "meta_description": null,
  "meta_image": null,
  "lang": "en",
  "views_count": 0,
  "unique_views_count": 0,
  "category_id": null,
  "category": null,
  "tag_names": ["go", "interfaces"],
  "source": "human",
  "agent_name": "Claude Code",
  "agent_model": "Claude Opus 4.6",
  "url": "https://opentil.ai/@username/go-interfaces-are-satisfied-implicitly",
  "created_at": "2026-02-10T14:30:22Z",
  "updated_at": "2026-02-10T14:30:22Z"
}
```

Use the `url` field for the Review link in result messages.

## GET /entries -- List Entries

List entries for the authenticated user. Requires `read:entries` scope.

```
GET /entries?status=published&per_page=20&q=go
```

| Param | Description |
|-------|-------------|
| `status` | `published`, `draft`, or `scheduled` |
| `q` | Search by title (case-insensitive partial match) |
| `tag` | Filter by tag slug |
| `category_id` | Filter by category ID |
| `uncategorized` | `true` to filter uncategorized entries |
| `per_page` | Results per page (max 100, default 20) |
| `page` | Page number |

### Response (EntryListSerializer)

```json
{
  "data": [
    {
      "id": "1234567890",
      "title": "Go interfaces are satisfied implicitly",
      "slug": "go-interfaces-are-satisfied-implicitly",
      "excerpt": "In Go, a type implements an interface by implementing...",
      "published": true,
      "published_at": "2026-02-10T14:30:22Z",
      "first_published_at": "2026-02-10T14:30:22Z",
      "visibility": "public",
      "views_count": 42,
      "unique_views_count": 35,
      "category_id": null,
      "category_name": null,
      "tag_names": ["go", "interfaces"],
      "source": "human",
      "agent_name": "Claude Code",
      "agent_model": "Claude Opus 4.6",
      "created_at": "2026-02-10T14:30:22Z",
      "updated_at": "2026-02-10T14:30:22Z"
    }
  ],
  "meta": {
    "current_page": 1,
    "total_pages": 1,
    "total_count": 1,
    "per_page": 20
  }
}
```

## GET /entries/drafts

Shorthand for listing draft entries. Requires `read:entries` scope.

Returns the same response format as `GET /entries` but filtered to drafts, ordered by `updated_at` descending.

## GET /entries/:id -- Show Entry

Fetch a single entry. Requires `read:entries` scope.

Returns the full EntrySerializer response (same as 201 response above).

## PATCH /entries/:id -- Update Entry

Update an entry. Requires `write:entries` scope.

### Request Body

Same fields as POST, all optional. Only include fields that are changing.

```json
{
  "entry": {
    "title": "Updated title",
    "content": "Updated content...",
    "tag_names": ["go", "interfaces", "type-system"]
  }
}
```

### 200 Response

Returns the full EntrySerializer response with updated fields.

## DELETE /entries/:id -- Delete Entry

Permanently delete an entry. Requires `delete:entries` scope.

### 200 Response

```json
{
  "message": "Entry deleted"
}
```

## POST /entries/:id/publish

Publish a draft entry. Requires `write:entries` scope. No request body needed.

Returns the full EntrySerializer response with `published: true`.

## POST /entries/:id/unpublish

Unpublish a published entry (revert to draft). Requires `write:entries` scope. No request body needed.

Returns the full EntrySerializer response with `published: false`.

## Error Handling

### Error Response Format

```json
{
  "error": {
    "type": "validation_error",
    "code": "validation_failed",
    "message": "Validation failed",
    "details": [{"field": "title", "message": "Title can't be blank"}]
  }
}
```

### Error Codes

| Status | Code | Action |
|--------|------|--------|
| 401 | `unauthorized` | Token invalid or expired. Save locally (for capture commands). Then follow the inline re-authentication flow defined in SKILL.md Error Handling — prompt to reconnect if token is from `~/.til/credentials`, or show env var guidance if from `$OPENTIL_TOKEN`. |
| 403 | `insufficient_scope` | Token lacks required scope. Show which scope is needed. |
| 404 | `not_found` | Entry does not exist or belongs to another user. |
| 422 | `validation_failed` | Parse `details` array, auto-fix, and retry once. Save locally if retry fails. |
| 429 | `rate_limited` | Rate limit exceeded. Save locally. Retry after `X-RateLimit-Reset`. |
| 5xx | -- | Server error. Save locally. |

### 422 Auto-Fix Retry Logic

When a 422 is returned, inspect the `details` array and attempt to fix:

1. `title` too long -> truncate to 200 chars
2. `lang` invalid -> fall back to `en`
3. `slug` already taken -> append `-2` (or increment)
4. `tag_names` invalid -> remove offending tags, keep valid ones
5. `content` too long -> truncate to 100,000 chars

After fixing, retry the POST **once**. If the retry also returns 422, save locally and report the error.

## GET /site -- Site Info

Fetch the authenticated user's site details. Requires `read:entries` scope.

### Response (SiteDetailSerializer)

```json
{
  "username": "hong",
  "title": "Hong's TIL",
  "bio": "Learning something new every day",
  "timezone": "Asia/Shanghai",
  "locale": "en",
  "entries_count": 28,
  "published_entries_count": 15,
  "categories_count": 3,
  "custom_domain": null,
  "domain_verified": false,
  "discoverable": true,
  "theme_slug": "default",
  "theme_mode": "auto",
  "last_posted_at": "2026-02-10T14:30:22Z",
  "created_at": "2025-06-01T00:00:00Z",
  "updated_at": "2026-02-10T14:30:22Z"
}
```

- `entries_count`: total entries (including drafts)
- `published_entries_count`: published entries only

Used by `/til status` to display site info.

## GET /tags -- List Tags

List tags for the authenticated user's site. Requires `read:entries` scope.

```
GET /tags?sort=popular&per_page=20
```

| Param | Description |
|-------|-------------|
| `sort` | `popular` (default, by taggings count) or `alphabetical` |
| `per_page` | Results per page (max 100, default 20) |
| `page` | Page number |
| `with_entries` | `true` to only return tags that have entries |

### Response (TagSerializer)

```json
{
  "data": [
    {
      "id": "123",
      "name": "go",
      "slug": "go",
      "taggings_count": 8,
      "created_at": "2025-06-15T10:00:00Z"
    }
  ],
  "meta": {
    "current_page": 1,
    "total_pages": 1,
    "total_count": 12,
    "per_page": 20
  }
}
```

Note: `taggings_count` is the global usage count across all entries on the site.

Used by `/til tags` to display tag usage.

## GET /categories -- List Categories

List categories (topics) for the authenticated user's site. Requires `read:entries` scope.

```
GET /categories
```

### Response (CategorySerializer)

```json
{
  "data": [
    {
      "id": "456",
      "name": "Backend",
      "slug": "backend",
      "description": "Server-side topics",
      "entries_count": 12,
      "position": 0,
      "created_at": "2025-06-15T10:00:00Z"
    }
  ]
}
```

Note: `entries_count` is the site-level count of entries in that category.

Used by `/til categories` to display category listing.

## Rate Limits

- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour

Rate limit info is returned in response headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per window |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when the window resets |

When `429` is received, save the draft locally and inform the user. Do not retry automatically -- the user's workflow should not be blocked by rate limits.

## Device Flow (OAuth)

These endpoints do not require a Bearer token. Used by `/til auth` to obtain a token via browser authorization.

### POST /oauth/device/code

Create a device authorization code.

```
POST /api/v1/oauth/device/code
Content-Type: application/json

{ "scopes": ["read", "write"] }
```

**200 Response:**

```json
{
  "device_code": "uuid-string",
  "user_code": "XXXX-YYYY",
  "verification_uri": "https://opentil.ai/device",
  "expires_in": 900,
  "interval": 5
}
```

| Field | Description |
|-------|-------------|
| `device_code` | Opaque code used to poll for the token |
| `user_code` | Human-readable code displayed to the user |
| `verification_uri` | URL where the user authorizes the device |
| `expires_in` | Seconds until the device code expires |
| `interval` | Minimum polling interval in seconds |

### POST /oauth/device/token

Poll for an access token after the user authorizes.

```
POST /api/v1/oauth/device/token
Content-Type: application/json

{ "device_code": "uuid-string", "grant_type": "urn:ietf:params:oauth:grant-type:device_code" }
```

**200 Response (authorized):**

```json
{
  "access_token": "til_xxx...",
  "token_type": "bearer",
  "scope": "read write"
}
```

**400 Response (pending):**

```json
{
  "error": {
    "code": "authorization_pending",
    "message": "The user has not yet authorized this device"
  }
}
```

**Error codes:**

| Code | Meaning | Action |
|------|---------|--------|
| `authorization_pending` | User hasn't authorized yet | Continue polling |
| `slow_down` | Polling too fast | Increase interval by 5 seconds |
| `expired_token` | Device code expired | Stop polling, show timeout message |
| `invalid_grant` | Invalid device code | Stop polling, show error |

## Credential Storage

After a successful device flow, credentials are stored locally in `~/.til/credentials` as YAML.

### File Format

```yaml
active: personal
profiles:
  personal:
    token: til_abc...
    nickname: hong
    site_url: https://opentil.ai/@hong
    host: https://opentil.ai
  work:
    token: til_xyz...
    nickname: hong-corp
    site_url: https://opentil.ai/@hong-corp
    host: https://opentil.ai
```

### Field Reference

| Field | Level | Description |
|-------|-------|-------------|
| `active` | top | Name of the currently active profile |
| `profiles` | top | Map of profile name → profile object |
| `token` | profile | Bearer token (starts with `til_`) |
| `nickname` | profile | Username from `GET /site` response (`username` field) |
| `site_url` | profile | Public site URL, e.g. `https://opentil.ai/@hong` |
| `host` | profile | API host, e.g. `https://opentil.ai` |

### Backward Compatibility

Old format (`~/.til/credentials` containing only a plain text token):

```
til_abc123...
```

On first read, detect the old format (file content starts with `til_` and contains no YAML structure). Migrate automatically:

1. Read the token string
2. `GET /site` with the token to fetch `username`
   - On success: use `username` as profile name, populate `nickname` and `site_url`
   - On failure (401/network): use `default` as profile name, leave `nickname` and `site_url` empty
3. Write back as YAML with the single profile set as `active`
4. Preserve file permissions (`chmod 600`)

### File Permissions

Always set `~/.til/credentials` to `chmod 600` (owner read/write only) after any write operation. Create `~/.til/` directory with `chmod 700` if it doesn't exist.
