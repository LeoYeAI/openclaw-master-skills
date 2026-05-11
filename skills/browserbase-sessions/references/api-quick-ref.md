# Browserbase API Quick Reference

## Authentication
All REST endpoints require: `X-BB-API-Key: <your-api-key>`
Base URL: `https://api.browserbase.com/v1`

## Sessions

### Create Session
`POST /v1/sessions`
```json
{
  "projectId": "<string>",
  "browserSettings": {
    "context": { "id": "<context-id>", "persist": true },
    "blockAds": true,
    "recordSession": true,
    "logSession": true,
    "solveCaptchas": true,
    "viewport": { "width": 1280, "height": 720 }
  },
  "timeout": 3600,
  "keepAlive": true,
  "proxies": true,
  "region": "us-west-2"
}
```
Response includes `id`, `connectUrl` (CDP WebSocket), `status`.

### List Sessions
`GET /v1/sessions` → Array of session objects

### Get Session
`GET /v1/sessions/{id}` → Single session object

### Terminate Session
`POST /v1/sessions/{id}` with `{"projectId": "...", "status": "REQUEST_RELEASE"}`

### Debug / Live URLs
`GET /v1/sessions/{id}/debug` → Debug connection URL, WebSocket URL, and page list

### Session Logs
`GET /v1/sessions/{id}/logs`

### Session Recording
`GET /v1/sessions/{id}/recording` → rrweb event array (JSON; primary tab)

## Contexts (Authentication Persistence)

### Create Context
`POST /v1/contexts` with `{"projectId": "<project-id>"}`
Returns object with `id`.

### Delete Context
`DELETE /v1/contexts/{id}` → 204 No Content (permanent)

### Session Logs
`GET /v1/sessions/{id}/logs` → Array of log entries (timestamps, methods, params)

### Session Recording
`GET /v1/sessions/{id}/recording` → rrweb event array (JSON; primary tab)

### Session Downloads
`GET /v1/sessions/{id}/downloads` → Binary archive of downloaded files

## Key Details
- **Connection timeout**: 5 min after creation
- **Session timeout**: 60–21600 seconds (max 6 hours)
- **Regions**: us-west-2, us-east-1, eu-central-1, ap-southeast-1
- **Statuses**: RUNNING, ERROR, TIMED_OUT, COMPLETED
- **Contexts never expire** on Browserbase's side
- **persist: true** saves cookies/storage changes back to context on close
- **keepAlive: true** lets sessions survive disconnections (must terminate manually)

## Python SDK
```python
from browserbase import Browserbase
client = Browserbase(api_key="...")
session = client.sessions.create(project_id="...", browser_settings={...})
print(session.connect_url)  # CDP WebSocket URL
```
