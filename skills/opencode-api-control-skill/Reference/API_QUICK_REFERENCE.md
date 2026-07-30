# API Quick Reference

## Essential Endpoints

### Health Check
```bash
curl -s http://127.0.0.1:4099/global/health
# Returns: {"healthy": true, "version": "x.x.x"}
```

### Get Path Info
```bash
curl -s http://127.0.0.1:4099/path
# Returns: {"directory": "/path/to/project", "worktree": "...", ...}
```

### List Sessions
```bash
curl -s "http://127.0.0.1:4099/session?directory=$PROJECT_PATH"
# Returns: [{id, title, time: {created, updated}, ...}, ...]
```

### Create Session
```bash
curl -s -X POST "http://127.0.0.1:4099/session?directory=$PROJECT_PATH" \
  -H "Content-Type: application/json" \
  -d '{"title": "Session Name"}'
# Returns: {id: "ses_...", title, directory, ...}
```

### Send Message
```bash
curl -s -X POST "http://127.0.0.1:4099/session/ses_123/message?directory=$PROJECT_PATH" \
  -H "Content-Type: application/json" \
  -d '{
    "model": {"providerID": "opencode", "modelID": "gpt-5.1-codex"},
    "parts": [{"type": "text", "text": "Your prompt"}]
  }'
# Returns: {info: {role, tokens, cost, ...}, parts: [{type, text, ...}]}
```

### Get Messages
```bash
curl -s "http://127.0.0.1:4099/session/ses_123/message?directory=$PROJECT_PATH"
# Returns: [{info: {...}, parts: [...]}, ...]
```

### Get Session Diff
```bash
curl -s "http://127.0.0.1:4099/session/ses_123/diff?directory=$PROJECT_PATH"
# Returns: [{file, status, additions, deletions, before, after}, ...]
```

### Subscribe to Events
```bash
curl -N "http://127.0.0.1:4099/event?directory=$PROJECT_PATH"
# Streams: event: type\ndata: {...}\n\n
```

### Get Session Status
```bash
curl -s "http://127.0.0.1:4099/session/status?directory=$PROJECT_PATH"
# Returns: {"ses_123": {type: "idle|busy|retry", ...}, ...}
```

### List Providers
```bash
curl -s "http://127.0.0.1:4099/provider?directory=$PROJECT_PATH"
# Returns: {all: [{id, name, models: {...}}, ...], connected: [...]}
```

### Get File Content
```bash
curl -s "http://127.0.0.1:4099/file/content?directory=$PROJECT_PATH&path=src/App.tsx"
# Returns: {type: "text|binary", content: "...", ...}
```

### List Directory
```bash
curl -s "http://127.0.0.1:4099/file?directory=$PROJECT_PATH&path=src"
# Returns: [{name, path, absolute, type: "file|directory", ignored}, ...]
```

### Search Text
```bash
curl -s "http://127.0.0.1:4099/find?directory=$PROJECT_PATH&pattern=TODO"
# Returns: [{path: {text}, lines: {text}, line_number, ...}, ...]
```

### Find Files
```bash
curl -s "http://127.0.0.1:4099/find/file?directory=$PROJECT_PATH&query=component&type=file"
# Returns: ["path/to/file1.tsx", "path/to/file2.tsx", ...]
```

### Delete Session
```bash
curl -s -X DELETE "http://127.0.0.1:4099/session/ses_123?directory=$PROJECT_PATH"
# Returns: true
```

## Authentication Patterns



### Without Password
Normal curl requests:
```bash
curl -s "$URL"
```

## Common Response Structures

### Message Response
```json
{
  "info": {
    "id": "msg_123",
    "role": "assistant",
    "tokens": {"total": 1500, "input": 800, "output": 700},
    "cost": 0.025,
    "finish": "stop"
  },
  "parts": [
    {"type": "text", "text": "Response text"},
    {"type": "reasoning", "text": "Thinking process"},
    {"type": "tool", "tool": "edit", "state": {...}}
  ]
}
```

### Error Response
```json
{
  "data": {},
  "errors": [{"message": "Error description", "path": [...]}],
  "success": false
}
```

## Query Parameters

### Required
- `directory` - Project path (required for all project-scoped endpoints)

### Optional
- `limit` - Limit results (e.g., `?limit=10`)
- `roots` - Only root sessions (e.g., `?roots=true`)
- `search` - Search filter (e.g., `?search=dashboard`)
- `start` - Timestamp filter (e.g., `?start=1707312000000`)

## Request Body Examples

### Minimal Message
```json
{
  "parts": [
    {"type": "text", "text": "Your prompt"}
  ]
}
```

### Full Message Options
```json
{
  "agent": "build",
  "model": {
    "providerID": "anthropic",
    "modelID": "claude-sonnet-4-5"
  },
  "parts": [
    {"type": "text", "text": "Your prompt"}
  ],
  "system": "Custom system prompt",
  "noReply": false
}
```

### With File Attachment
```json
{
  "model": {...},
  "parts": [
    {
      "type": "file",
      "mime": "image/png",
      "url": "data:image/png;base64,iVBORw0KG..."
    },
    {
      "type": "text",
      "text": "Analyze this image"
    }
  ]
}
```

## One-Liners

### Quick Task
```bash
curl -s -X POST "http://127.0.0.1:4099/session/$(curl -s -X POST 'http://127.0.0.1:4099/session?directory='$(curl -s http://127.0.0.1:4099/path | jq -r .directory) -H 'Content-Type: application/json' -d '{"title":"Quick"}' | jq -r .id)/message?directory=$(curl -s http://127.0.0.1:4099/path | jq -r .directory)" -H 'Content-Type: application/json' -d '{"model":{"providerID":"opencode","modelID":"gpt-5.1-codex"},"parts":[{"type":"text","text":"Create Hello World"}]}' | jq -r '.parts[].text'
```

### List All Sessions with Details
```bash
curl -s "http://127.0.0.1:4099/session?directory=$(curl -s http://127.0.0.1:4099/path | jq -r .directory)" | jq -r '.[] | "\(.id): \(.title) - Updated: \(.time.updated | todate)"'
```

### Get Latest Message
```bash
curl -s "http://127.0.0.1:4099/session/ses_123/message?directory=$PROJECT_PATH&limit=1" | jq -r '.[0].parts[] | select(.type=="text") | .text'
```

## HTTP Status Codes

- `200` - Success
- `204` - Success (no content)
- `400` - Bad request (validation error)

- `404` - Not found (session/message doesn't exist)
- `500` - Server error

## Rate Limits

- Generally no rate limits on self-hosted server
- Model provider limits apply (e.g., Anthropic, OpenAI)
- Event streams can be resource-intensive
---
**Author:** [Malek RSH](https://github.com/malek262) | **Repository:** [OpenCode-CLI-Controller](https://github.com/malek262/opencode-api-control-skill)
