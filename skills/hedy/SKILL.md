---
name: hedy
description: "Access Hedy meeting data: sessions, transcripts, highlights, todos, topics, contexts, and webhooks via the Hedy REST API."
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": ["HEDY_API_KEY"], "bins": ["curl", "jq"]}, "primaryEnv": "HEDY_API_KEY"}}
---

# Hedy

Access a user's Hedy meeting data through the Hedy REST API. Read sessions with transcripts, highlights, and todos. Manage topics, session contexts, and webhooks.

Hedy is an AI-powered meeting coach that provides real-time speech transcription and AI-powered conversation analysis. This skill lets you query the user's meeting history, search for specific sessions, retrieve structured meeting outputs, and manage organizational features like topics and webhooks.

## Setup

### 1. Get your API key

Generate an API key inside the Hedy app under Settings > API. Keys start with `hedy_live_`.

### 2. Configure OpenClaw

Add the following to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "hedy": {
        "enabled": true,
        "apiKey": "hedy_live_YOUR_KEY_HERE",
        "config": {
          "region": "us"
        }
      }
    }
  }
}
```

Set `"region"` to `"eu"` if your Hedy account uses EU data residency. Default is `"us"`.

### 3. Sandbox users

If you run OpenClaw in a Docker sandbox, `apiKey` and `env` values from `openclaw.json` are injected into the host process only. Add the key to your sandbox environment separately:

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "docker": {
          "env": {
            "HEDY_API_KEY": "hedy_live_YOUR_KEY_HERE"
          }
        }
      }
    }
  }
}
```

### 4. Restart OpenClaw

Start a new session so the skill is picked up.

## Region and Base URL

Determine the base URL from the configured region:

| Region | Base URL |
|--------|----------|
| `us` (default) | `https://api.hedy.bot` |
| `eu` | `https://eu-api.hedy.bot` |

If no region is configured, default to `us`.

All endpoints below use `{BASE_URL}` as a placeholder. Replace it with the resolved URL.

## Authentication

Every request requires:

```
Authorization: Bearer {HEDY_API_KEY}
```

The API key is injected via the `HEDY_API_KEY` environment variable. Never display, log, or include the API key in output shown to the user.

## Endpoints

All endpoints return JSON. Response shapes vary by endpoint (documented individually below). Error responses always use:

```json
{
  "success": false,
  "error": { "code": "error_code", "message": "Human-readable message" }
}
```

### GET /me

Returns the authenticated user's profile. Response is a bare JSON object (no wrapper).

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/me" | jq
```

Response:

```json
{
  "id": "uid_123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

### GET /sessions

List recent meeting sessions. Only cloud-synced sessions are returned. Response is wrapped in `{ success, data, pagination }`.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/sessions?limit=20" | jq
```

Query parameters:
- `limit` (int, 1-100, default 50): Number of sessions to return

Note: This endpoint returns the most recent `limit` sessions only. There is no cursor-based pagination. To retrieve more sessions, increase the `limit` value (max 100).

Response:

```json
{
  "success": true,
  "data": [
    {
      "sessionId": "sess_123",
      "title": "Weekly Sync",
      "startTime": "2026-03-15T14:30:00Z",
      "duration": 45,
      "topic": { "id": "topic_1", "name": "Team Meetings" }
    }
  ],
  "pagination": { "hasMore": false, "next": null, "total": 42 }
}
```

### GET /sessions/{sessionId}

Full session detail including transcript, AI outputs, highlights, and todos. Response is a bare JSON object (no wrapper).

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/sessions/{sessionId}" | jq
```

Response:

```json
{
  "sessionId": "sess_123",
  "title": "Weekly Sync",
  "startTime": "2026-03-15T14:30:00Z",
  "endTime": "2026-03-15T15:15:00Z",
  "duration": 45,
  "transcript": "full meeting transcript text",
  "cleaned_transcript": "AI-cleaned version or null",
  "cleaned_at": "2026-03-15T16:00:00Z",
  "conversations": "Q&A structured format",
  "meeting_minutes": "formatted minutes",
  "recap": "brief summary",
  "highlights": [],
  "user_todos": [],
  "topic": { "id": "topic_1", "name": "Team Meetings" }
}
```

### GET /sessions/{sessionId}/highlights

Highlights (key quotes) from a specific session.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/sessions/{sessionId}/highlights" | jq
```

### GET /sessions/{sessionId}/todos

Todos from a specific session.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/sessions/{sessionId}/todos" | jq
```

### GET /sessions/{sessionId}/todos/{todoId}

A specific todo item.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/sessions/{sessionId}/todos/{todoId}" | jq
```

### GET /highlights

List all highlights across all sessions, sorted by timestamp (newest first). Response is wrapped in `{ success, data, pagination }`.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/highlights?limit=20" | jq
```

Query parameters:
- `limit` (int, 1-100, default 50)

Note: This endpoint returns the most recent `limit` highlights only. There is no cursor-based pagination. To retrieve more highlights, increase the `limit` value (max 100).

Response:

```json
{
  "success": true,
  "data": [
    {
      "highlightId": "high_123",
      "sessionId": "sess_456",
      "timestamp": "2026-03-15T14:35:00Z",
      "title": "Key Decision"
    }
  ],
  "pagination": { "hasMore": false, "next": null, "total": 15 }
}
```

### GET /highlights/{highlightId}

Full highlight detail. Response is a bare JSON object (no wrapper).

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/highlights/{highlightId}" | jq
```

Response:

```json
{
  "highlightId": "high_123",
  "sessionId": "sess_456",
  "timestamp": "2026-03-15T14:35:00Z",
  "timeIndex": 300000,
  "title": "Key Decision on Mobile App",
  "rawQuote": "yeah I think we should prioritize the mobile app",
  "cleanedQuote": "We should prioritize the mobile app",
  "mainIdea": "Team agreed to prioritize mobile app development",
  "aiInsight": "Strategic prioritization of mobile platform"
}
```

### GET /todos

All todos across all sessions. Returns a flat array (no pagination wrapper).

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/todos" | jq
```

Response (array of):

```json
{
  "id": "uuid-1234",
  "text": "Follow up with John",
  "dueDate": "Tomorrow",
  "sessionId": "sess_123",
  "completed": false,
  "topic": { "id": "topic_1", "name": "Team Meetings" }
}
```

### GET /topics

List all topics (conversation groupings), sorted by last update. Response is wrapped in `{ success, data }`. No pagination.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/topics" | jq
```

Response `data` (array of):

```json
{
  "id": "topic_123",
  "name": "Project Alpha",
  "description": "All about Project Alpha",
  "color": "#FF5733",
  "iconName": "lightbulb_outline",
  "topicContext": "Custom instructions for this topic",
  "topicContextUpdatedAt": "2026-03-15T16:00:00Z",
  "sessionCount": 12,
  "lastSessionDate": "2026-03-15T14:30:00Z",
  "dominantSessionType": "brainstorm",
  "overview": { "summary": "..." },
  "overviewUpdatedAt": "2026-03-15T16:00:00Z",
  "createdAt": "2026-02-01T10:00:00Z",
  "updatedAt": "2026-03-15T16:00:00Z"
}
```

Fields like `overview`, `overviewUpdatedAt`, `topicContext`, and `dominantSessionType` may be null or absent if not yet generated.

### GET /topics/{topicId}

Full topic detail including overview and insights. Response is wrapped in `{ success, data }`.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/topics/{topicId}" | jq
```

### GET /topics/{topicId}/sessions

Sessions grouped under a topic. This is the only endpoint with cursor-based pagination.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/topics/{topicId}/sessions?limit=20" | jq
```

Query parameters:
- `limit` (int, 1-100, default 50)
- `startAfter` (string): Session ID cursor for next page (from `data.pagination.nextCursor`)

Response:

```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "sessionId": "sess_123",
        "title": "Q1 Planning",
        "startTime": "2026-03-15T14:30:00Z",
        "duration": 45,
        "topicInfo": { "id": "topic_123", "name": "Project Alpha" }
      }
    ],
    "pagination": {
      "count": 20,
      "hasMore": true,
      "nextCursor": "sess_456"
    }
  }
}
```

To paginate: pass `?startAfter={data.pagination.nextCursor}` until `hasMore` is `false`.

### GET /contexts

List session contexts (pre-meeting preparation notes), sorted by most recently updated. Response is wrapped in `{ success, data }`. No pagination.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/contexts" | jq
```

Response `data` (array of):

```json
{
  "id": "ctx_abc123",
  "title": "Sales Call Context",
  "content": "Focus on customer pain points...",
  "isDefault": true,
  "createdAt": "2026-02-01T10:00:00Z",
  "updatedAt": "2026-03-15T16:00:00Z"
}
```

### GET /contexts/{contextId}

A specific session context. Response is wrapped in `{ success, data }`.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/contexts/{contextId}" | jq
```

### POST /topics

Create a new topic. Response is wrapped in `{ success, data }`.

```bash
curl -s -X POST -H "Authorization: Bearer $HEDY_API_KEY" -H "Content-Type: application/json" \
  -d '{"name": "Project Alpha", "description": "All about Project Alpha", "color": "#FF5733"}' \
  "{BASE_URL}/topics" | jq
```

Request body:
- `name` (string, required): 1-100 chars
- `description` (string, optional): 0-500 chars
- `color` (string, optional): Hex format `#RRGGBB`
- `iconName` (string, optional): Material icon name
- `topicContext` (string, optional): Custom instructions, 0-20,000 chars

Returns HTTP 201 with the created topic object.

### PATCH /topics/{topicId}

Update an existing topic. Response is wrapped in `{ success, data }`.

```bash
curl -s -X PATCH -H "Authorization: Bearer $HEDY_API_KEY" -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}' \
  "{BASE_URL}/topics/{topicId}" | jq
```

Request body (all fields optional):
- `name` (string): 1-100 chars
- `description` (string): 0-500 chars
- `color` (string): Hex format `#RRGGBB`
- `iconName` (string)
- `topicContext` (string or null): Set to `null` to clear

Returns HTTP 200 with the updated topic object.

### DELETE /topics/{topicId}

Delete a topic. Sessions under this topic are unlinked (topicId set to null) but not deleted.

```bash
curl -s -X DELETE -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/topics/{topicId}" | jq
```

Returns HTTP 200:

```json
{
  "success": true,
  "message": "Topic deleted"
}
```

**Warning:** Deletion is not fully atomic for large topics. The backend unlinks up to 4,000 sessions in batches. If a topic has more than 4,000 sessions, the request returns `400 deletion_limit_exceeded` after partially unlinking sessions, and the topic is left in a `deletion_failed` state. If this happens, inform the user that manual cleanup may be needed in the Hedy app. A `409 deletion_in_progress` error means another delete is already running for this topic.

### POST /contexts

Create a new session context. Response is wrapped in `{ success, data }`.

```bash
curl -s -X POST -H "Authorization: Bearer $HEDY_API_KEY" -H "Content-Type: application/json" \
  -d '{"title": "Sales Call Context", "content": "Focus on customer pain points..."}' \
  "{BASE_URL}/contexts" | jq
```

Request body:
- `title` (string, required): 1-200 chars
- `content` (string, optional): 0-20,000 chars
- `isDefault` (boolean, optional): If true, clears default from all other contexts

Returns HTTP 201 with the created context object.

Note: Free tier users are limited to 1 session context. Additional contexts require a Pro subscription.

### PATCH /contexts/{contextId}

Update an existing session context. Response is wrapped in `{ success, data }`.

```bash
curl -s -X PATCH -H "Authorization: Bearer $HEDY_API_KEY" -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "isDefault": true}' \
  "{BASE_URL}/contexts/{contextId}" | jq
```

Request body (all fields optional):
- `title` (string): 1-200 chars
- `content` (string): 0-20,000 chars
- `isDefault` (boolean): If true, clears default from all other contexts

Returns HTTP 200 with the updated context object.

### DELETE /contexts/{contextId}

Delete a session context. If the deleted context was the default, the most recently updated remaining context is promoted to default.

```bash
curl -s -X DELETE -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/contexts/{contextId}" | jq
```

Returns HTTP 200:

```json
{
  "success": true,
  "message": "Session context deleted"
}
```

### GET /webhooks

List all configured webhooks. Response is wrapped in `{ success, data }`.

```bash
curl -s -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/webhooks" | jq
```

Response `data` (array of):

```json
{
  "id": "wh_123",
  "url": "https://api.example.com/hedy-webhook",
  "events": ["session.ended", "highlight.created"],
  "createdAt": "2026-02-01T10:00:00Z",
  "updatedAt": "2026-02-01T10:00:00Z"
}
```

### POST /webhooks

Create a webhook. Rate limited to 5 per minute. Maximum 50 webhooks per user. Requires HTTPS URL in production.

```bash
curl -s -X POST -H "Authorization: Bearer $HEDY_API_KEY" -H "Content-Type: application/json" \
  -d '{"url": "https://api.example.com/hedy-webhook", "events": ["session.ended", "highlight.created"]}' \
  "{BASE_URL}/webhooks" | jq
```

Request body:
- `url` (string, required): Valid HTTPS URL
- `event` (string) or `events` (string array): At least one required. Valid event types:
  - `session.created` - New session started
  - `session.ended` - Session finished processing
  - `session.exported` - User manually exported session
  - `highlight.created` - New highlight generated
  - `todo.exported` - Todo marked for export

Returns HTTP 200 with the created webhook object (signing secret is stored but not returned).

### DELETE /webhooks/{webhookId}

Delete a webhook.

```bash
curl -s -X DELETE -H "Authorization: Bearer $HEDY_API_KEY" "{BASE_URL}/webhooks/{webhookId}" | jq
```

Returns HTTP 200:

```json
{
  "success": true,
  "data": {
    "message": "Webhook deleted successfully"
  }
}
```

## Pagination

Most endpoints do NOT support cursor-based pagination. They return up to `limit` items (max 100) sorted by recency. The `/todos`, `/topics`, and `/contexts` endpoints return all items with no pagination at all.

The only endpoint with true cursor pagination is **GET /topics/{topicId}/sessions**, which uses `startAfter` (documented above).

For `/sessions` and `/highlights`, if the user needs more than 100 items, inform them that only the most recent 100 are available via the API.

## Error Handling

| HTTP Status | Error Code | Meaning | Action |
|---|---|---|---|
| 400 | `validation_error` | Request body failed validation | Show the error message; check field constraints |
| 400 | `invalid_webhook_url` | Webhook URL is invalid | Ask user to provide a valid HTTPS URL |
| 400 | `missing_event` | Neither `event` nor `events` provided | Ask user which events to subscribe to |
| 400 | `invalid_event` | Single event type is invalid | Show the list of valid events |
| 400 | `invalid_events` | One or more event types invalid | Show the list of valid events |
| 400 | `webhook_limit_exceeded` | User has 50 webhooks already | Suggest deleting unused webhooks first |
| 400 | `deletion_limit_exceeded` | Topic has too many sessions (>4,000) for full cleanup | Inform user; partial unlink occurred, manual cleanup needed |
| 401 | `missing_api_key` | Authorization header missing | Check that `HEDY_API_KEY` is set |
| 401 | `invalid_api_key` | Key not found or wrong format | Ask user to verify their API key in Hedy app settings |
| 403 | `tier_limit_exceeded` | Feature requires Hedy Pro subscription | Inform user this feature requires a Pro plan |
| 404 | `session_not_found` | Session ID does not exist | Inform user; suggest listing sessions first |
| 404 | `highlight_not_found` | Highlight ID does not exist | Inform user |
| 404 | `not_found` | Topic or context does not exist | Inform user; suggest listing topics or contexts first |
| 404 | `todo_not_found` | Todo ID does not exist | Inform user |
| 404 | `webhook_not_found` | Webhook ID does not exist | Inform user; suggest listing webhooks first |
| 409 | `deletion_in_progress` | Topic deletion already running | Wait and retry later |
| 429 | `rate_limit_exceeded` | Too many requests (200/min global, 5/min for webhooks) | Wait 30 seconds before retrying. Do NOT retry immediately. |
| 500 | `internal_error` | Server error | Inform user and suggest trying again later |

For user-actionable errors (401, 403, 404), show the `error.message` from the response. For 429 and 500 errors, show a friendly summary instead (e.g., "The server is busy, please try again in a moment") since raw server messages may contain technical details. Never retry more than once on 429 or 500 errors.

## Safety Rules

1. **Confirm before writing.** Before any POST, PATCH, or DELETE request, show the user exactly what will be created, changed, or deleted and wait for explicit confirmation.
2. **Confirm deletions twice.** For DELETE requests, state the target (topic name, context title, webhook URL) and ask "Are you sure?" before proceeding.
3. **Extra caution for webhooks.** Creating a webhook causes Hedy to send future meeting event data (session metadata, highlight titles, todo text) to an external URL. Before creating a webhook, explicitly confirm: (a) the exact destination host, (b) which events will be sent, and (c) warn the user that meeting-derived data will be sent outside Hedy to that URL.
3. **Never display, log, or include the API key** in any output, message, file, or code block shown to the user.
4. **Never prompt the user to paste their API key in chat.** Direct them to configure it in `~/.openclaw/openclaw.json`.
5. **Respect rate limits.** On 429 responses, wait before retrying. Do not loop.
6. **Present data clearly.** Format session transcripts, highlights, and todos in a readable way. Use markdown tables or lists as appropriate.
7. **Handle missing data gracefully.** Some fields (transcript, cleaned_transcript, recap, topic) may be null or empty. Do not treat this as an error.
8. **Protect user privacy.** Meeting transcripts and notes contain sensitive content. Do not send this data to any external service, tool, or URL beyond the Hedy API itself.

## Usage Examples

**"Show me my recent meetings"**
-> GET /sessions with limit=10, display as a table with title, date, duration, and topic.

**"What were the key takeaways from my last meeting?"**
-> GET /sessions with limit=1 to find the most recent session, then GET /sessions/{id} for full detail. Present the recap and highlights.

**"Do I have any open todos?"**
-> GET /todos, filter where completed is false, present as a checklist.

**"Show me everything about Project Alpha"**
-> GET /topics to find the topic by name, then GET /topics/{id}/sessions to list all sessions under it.

**"What did we discuss last Tuesday?"**
-> GET /sessions, scan startTime fields for the matching date, then GET /sessions/{id} for that session's detail.

**"Show my session contexts"**
-> GET /contexts, present as a list with title and whether it's the default.

**"Create a topic called Client Calls with a blue color"**
-> Confirm with user, then POST /topics with name "Client Calls" and color "#4A90D9".

**"Delete the Project Alpha topic"**
-> GET /topics to find the ID, confirm with user showing the topic name and session count, then DELETE /topics/{id}.

**"Set up a webhook for new highlights"**
-> Confirm the URL with user, then POST /webhooks with events ["highlight.created"].

**"Create a context for investor meetings"**
-> Confirm with user, then POST /contexts with title "Investor Meetings" and relevant content.
