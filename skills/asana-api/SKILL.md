---
name: asana
description: |
  Asana API integration with managed OAuth. Access tasks, projects, workspaces, users, and manage webhooks. Use this skill when users want to manage work items, track projects, or integrate with Asana workflows. For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Asana

Access the Asana API with managed OAuth authentication. Manage tasks, projects, workspaces, users, and webhooks for work management.

## Quick Start

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/tasks?project=PROJECT_GID')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/asana/{native-api-path}
```

Replace `{native-api-path}` with the actual Asana API endpoint path. The gateway proxies requests to `app.asana.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Asana OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=asana&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'asana'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "asana",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Asana connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/tasks?project=PROJECT_GID')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Tasks

#### Get Multiple Tasks

```bash
GET /asana/api/1.0/tasks
```

Query parameters:
- `project` - Project GID to filter tasks
- `assignee` - User GID or "me" for assigned tasks
- `workspace` - Workspace GID (required if no project specified)
- `completed_since` - ISO 8601 date to filter tasks completed after this date
- `opt_fields` - Comma-separated list of fields to include

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/tasks?project=1234567890&opt_fields=name,completed,due_on')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "gid": "1234567890",
      "name": "Review quarterly report",
      "completed": false,
      "due_on": "2025-03-15"
    }
  ]
}
```

#### Get a Task

```bash
GET /asana/api/1.0/tasks/{task_gid}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/tasks/1234567890')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create a Task

```bash
POST /asana/api/1.0/tasks
Content-Type: application/json

{
  "data": {
    "name": "New task",
    "projects": ["PROJECT_GID"],
    "assignee": "USER_GID",
    "due_on": "2025-03-20",
    "notes": "Task description here"
  }
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'data': {'name': 'Complete API integration', 'projects': ['1234567890'], 'due_on': '2025-03-20'}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/tasks', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update a Task

```bash
PUT /asana/api/1.0/tasks/{task_gid}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'data': {'completed': True}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/tasks/1234567890', data=data, method='PUT')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Delete a Task

```bash
DELETE /asana/api/1.0/tasks/{task_gid}
```

#### Get Tasks from a Project

```bash
GET /asana/api/1.0/projects/{project_gid}/tasks
```

#### Get Subtasks

```bash
GET /asana/api/1.0/tasks/{task_gid}/subtasks
```

#### Create Subtask

```bash
POST /asana/api/1.0/tasks/{task_gid}/subtasks
Content-Type: application/json

{
  "data": {
    "name": "Subtask name",
    "assignee": "USER_GID",
    "due_on": "2025-03-20"
  }
}
```

#### Search Tasks (Premium)

**Note:** This endpoint requires an Asana Premium subscription.

```bash
GET /asana/api/1.0/workspaces/{workspace_gid}/tasks/search
```

Query parameters:
- `text` - Text to search for
- `assignee.any` - Filter by assignees
- `projects.any` - Filter by projects
- `completed` - Filter by completion status

### Projects

#### Get Multiple Projects

```bash
GET /asana/api/1.0/projects
```

Query parameters:
- `workspace` - Workspace GID
- `team` - Team GID
- `opt_fields` - Comma-separated list of fields

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/projects?workspace=1234567890&opt_fields=name,owner,due_date')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "gid": "1234567890",
      "name": "Q1 Marketing Campaign",
      "owner": {
        "gid": "0987654321",
        "name": "Alice Johnson"
      },
      "due_date": "2025-03-31"
    }
  ]
}
```

#### Get a Project

```bash
GET /asana/api/1.0/projects/{project_gid}
```

#### Create a Project

```bash
POST /asana/api/1.0/projects
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'data': {'name': 'New Project', 'workspace': '1234567890', 'notes': 'Project description'}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/projects', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update a Project

```bash
PUT /asana/api/1.0/projects/{project_gid}
```

#### Delete a Project

```bash
DELETE /asana/api/1.0/projects/{project_gid}
```

### Workspaces

#### Get Multiple Workspaces

```bash
GET /asana/api/1.0/workspaces
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/workspaces')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "gid": "1234567890",
      "name": "Acme Corp",
      "is_organization": true
    }
  ]
}
```

#### Get a Workspace

```bash
GET /asana/api/1.0/workspaces/{workspace_gid}
```

#### Update a Workspace

```bash
PUT /asana/api/1.0/workspaces/{workspace_gid}
```

#### Add User to Workspace

```bash
POST /asana/api/1.0/workspaces/{workspace_gid}/addUser
```

#### Remove User from Workspace

```bash
POST /asana/api/1.0/workspaces/{workspace_gid}/removeUser
```

### Users

#### Get Multiple Users

```bash
GET /asana/api/1.0/users
```

Query parameters:
- `workspace` - Workspace GID to filter users

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/users?workspace=1234567890&opt_fields=name,email')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "gid": "1234567890",
      "name": "Alice Johnson",
      "email": "alice.johnson@acme.com"
    }
  ]
}
```

#### Get Current User

```bash
GET /asana/api/1.0/users/me
```

#### Get a User

```bash
GET /asana/api/1.0/users/{user_gid}
```

#### Get Users in a Team

```bash
GET /asana/api/1.0/teams/{team_gid}/users
```

#### Get Users in a Workspace

```bash
GET /asana/api/1.0/workspaces/{workspace_gid}/users
```

### Webhooks

#### Get Multiple Webhooks

```bash
GET /asana/api/1.0/webhooks
```

Query parameters:
- `workspace` - Workspace GID (required)
- `resource` - Resource GID to filter by

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/webhooks?workspace=1234567890')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Webhook

**Note:** Asana verifies the target URL is reachable and responds with a 200 status during webhook creation.

```bash
POST /asana/api/1.0/webhooks
Content-Type: application/json

{
  "data": {
    "resource": "PROJECT_OR_TASK_GID",
    "target": "https://example.com/webhook",
    "filters": [
      {
        "resource_type": "task",
        "action": "changed",
        "fields": ["completed", "due_on"]
      }
    ]
  }
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'data': {'resource': '1234567890', 'target': 'https://example.com/webhook'}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/webhooks', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": {
    "gid": "1234567890",
    "resource": {
      "gid": "1234567890",
      "name": "Q1 Project"
    },
    "target": "https://example.com/webhook",
    "active": true
  }
}
```

#### Get a Webhook

```bash
GET /asana/api/1.0/webhooks/{webhook_gid}
```

#### Update a Webhook

```bash
PUT /asana/api/1.0/webhooks/{webhook_gid}
```

#### Delete a Webhook

```bash
DELETE /asana/api/1.0/webhooks/{webhook_gid}
```

Returns `200 OK` with empty data on success.

## Pagination

Asana uses cursor-based pagination. Use `offset` for pagination:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/asana/api/1.0/tasks?project=1234567890&limit=50&offset=OFFSET_TOKEN')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

Response includes `next_page` when more results exist:

```json
{
  "data": [...],
  "next_page": {
    "offset": "eyJ0eXBlIjoib2Zmc2V0IiwidmFsdWUiOjUwfQ",
    "path": "/tasks?project=1234567890&limit=50&offset=eyJ0eXBlIjoib2Zmc2V0IiwidmFsdWUiOjUwfQ",
    "uri": "https://app.asana.com/api/1.0/tasks?project=1234567890&limit=50&offset=eyJ0eXBlIjoib2Zmc2V0IiwidmFsdWUiOjUwfQ"
  }
}
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/asana/api/1.0/tasks?project=1234567890',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/asana/api/1.0/tasks',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'project': '1234567890'}
)
data = response.json()
```

## Notes

- Resource IDs (GIDs) are strings
- Timestamps are in ISO 8601 format
- Use `opt_fields` to specify which fields to return
- Workspaces are the highest-level organizational unit
- Organizations are specialized workspaces representing companies
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets (`fields[]`, `sort[]`, `records[]`) to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments. You may get "Invalid API key" errors when piping.

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or missing Asana connection |
| 401 | Invalid or missing Maton API key |
| 403 | Forbidden - insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Asana API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `asana`. For example:

- Correct: `https://gateway.maton.ai/asana/api/1.0/tasks`
- Incorrect: `https://gateway.maton.ai/api/1.0/tasks`

## Resources

- [Asana API Documentation](https://developers.asana.com)
- [API Reference](https://developers.asana.com/reference)
- [LLM Reference](https://developers.asana.com/llms.txt)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
