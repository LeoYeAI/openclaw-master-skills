---
name: clickup
description: |
  ClickUp API integration with managed OAuth. Access tasks, lists, folders, spaces, workspaces, users, and manage webhooks. Use this skill when users want to manage work items, track projects, or integrate with ClickUp workflows. For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
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

# ClickUp

Access the ClickUp API with managed OAuth authentication. Manage tasks, lists, folders, spaces, workspaces, users, and webhooks for work management.

## Quick Start

```bash
# List workspaces (teams)
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/team')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/clickup/{native-api-path}
```

Replace `{native-api-path}` with the actual ClickUp API endpoint path. The gateway proxies requests to `api.clickup.com` and automatically injects your OAuth token.

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

Manage your ClickUp OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=clickup&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'clickup'}).encode()
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
    "app": "clickup",
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

If you have multiple ClickUp connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/team')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## ClickUp Hierarchy

ClickUp organizes data in a hierarchy:
- **Workspace** (team) → **Space** → **Folder** → **List** → **Task**

Note: In the API, Workspaces are referred to as "teams".

## API Reference

### Workspaces (Teams)

#### Get Authorized Workspaces

```bash
GET /clickup/api/v2/team
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/team')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "teams": [
    {
      "id": "1234567",
      "name": "Acme Corp",
      "color": "#7B68EE",
      "avatar": null,
      "members": [
        {
          "user": {
            "id": 123,
            "username": "Alice Johnson",
            "email": "alice@acme.com"
          }
        }
      ]
    }
  ]
}
```

### Spaces

#### Get Spaces

```bash
GET /clickup/api/v2/team/{team_id}/space
```

Query parameters:
- `archived` - Include archived spaces (true/false)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/team/1234567/space')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "spaces": [
    {
      "id": "90120001",
      "name": "Engineering",
      "private": false,
      "statuses": [
        {"status": "to do", "type": "open"},
        {"status": "in progress", "type": "custom"},
        {"status": "done", "type": "closed"}
      ]
    }
  ]
}
```

#### Get a Space

```bash
GET /clickup/api/v2/space/{space_id}
```

#### Create a Space

```bash
POST /clickup/api/v2/team/{team_id}/space
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'name': 'New Space', 'multiple_assignees': True, 'features': {'due_dates': {'enabled': True}, 'time_tracking': {'enabled': True}}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/team/1234567/space', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update a Space

```bash
PUT /clickup/api/v2/space/{space_id}
```

#### Delete a Space

```bash
DELETE /clickup/api/v2/space/{space_id}
```

### Folders

#### Get Folders

```bash
GET /clickup/api/v2/space/{space_id}/folder
```

Query parameters:
- `archived` - Include archived folders (true/false)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/space/90120001/folder')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "folders": [
    {
      "id": "456789",
      "name": "Sprint 1",
      "orderindex": 0,
      "hidden": false,
      "space": {"id": "90120001", "name": "Engineering"},
      "task_count": "12",
      "lists": []
    }
  ]
}
```

#### Get a Folder

```bash
GET /clickup/api/v2/folder/{folder_id}
```

#### Create a Folder

```bash
POST /clickup/api/v2/space/{space_id}/folder
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'name': 'New Folder'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/space/90120001/folder', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update a Folder

```bash
PUT /clickup/api/v2/folder/{folder_id}
```

#### Delete a Folder

```bash
DELETE /clickup/api/v2/folder/{folder_id}
```

### Lists

#### Get Lists

```bash
GET /clickup/api/v2/folder/{folder_id}/list
```

Query parameters:
- `archived` - Include archived lists (true/false)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/folder/456789/list')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "lists": [
    {
      "id": "901234",
      "name": "Backlog",
      "orderindex": 0,
      "status": {"status": "active", "color": "#87909e"},
      "task_count": 25,
      "folder": {"id": "456789", "name": "Sprint 1"}
    }
  ]
}
```

#### Get Folderless Lists

```bash
GET /clickup/api/v2/space/{space_id}/list
```

#### Get a List

```bash
GET /clickup/api/v2/list/{list_id}
```

#### Create a List

```bash
POST /clickup/api/v2/folder/{folder_id}/list
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'name': 'New List'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/folder/456789/list', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Folderless List

```bash
POST /clickup/api/v2/space/{space_id}/list
```

#### Update a List

```bash
PUT /clickup/api/v2/list/{list_id}
```

#### Delete a List

```bash
DELETE /clickup/api/v2/list/{list_id}
```

### Tasks

#### Get Tasks

```bash
GET /clickup/api/v2/list/{list_id}/task
```

Query parameters:
- `archived` - Include archived tasks (true/false)
- `page` - Page number (0-indexed)
- `order_by` - Sort by field (created, updated, due_date)
- `reverse` - Reverse sort order (true/false)
- `subtasks` - Include subtasks (true/false)
- `statuses[]` - Filter by status
- `include_closed` - Include closed tasks (true/false)
- `assignees[]` - Filter by assignee IDs
- `due_date_gt` - Due date greater than (Unix ms)
- `due_date_lt` - Due date less than (Unix ms)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/list/901234/task?include_closed=true')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "abc123",
      "name": "Implement login feature",
      "status": {"status": "in progress", "type": "custom", "color": "#4194f6"},
      "priority": {"id": "2", "priority": "high", "color": "#f9d900"},
      "due_date": "1709251200000",
      "assignees": [{"id": 123, "username": "Alice Johnson", "email": "alice@acme.com"}],
      "description": "Add OAuth login flow",
      "date_created": "1707436800000",
      "date_updated": "1708646400000"
    }
  ]
}
```

#### Get a Task

```bash
GET /clickup/api/v2/task/{task_id}
```

Query parameters:
- `custom_task_ids` - Use custom task IDs (true/false)
- `team_id` - Required when using custom_task_ids
- `include_subtasks` - Include subtasks (true/false)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/task/abc123')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create a Task

```bash
POST /clickup/api/v2/list/{list_id}/task
Content-Type: application/json

{
  "name": "Task name",
  "description": "Task description",
  "assignees": [123],
  "status": "to do",
  "priority": 2,
  "due_date": 1709251200000,
  "tags": ["api", "backend"],
  "parent": null
}
```

Fields:
- `name` (required) - Task title
- `description` - Task description (supports markdown)
- `assignees` - Array of user IDs
- `status` - Status name (must match a status in the list)
- `priority` - Priority level (1=urgent, 2=high, 3=normal, 4=low, null=none)
- `due_date` - Unix timestamp in milliseconds
- `due_date_time` - Include time in due date (true/false)
- `start_date` - Unix timestamp in milliseconds
- `time_estimate` - Time estimate in milliseconds
- `tags` - Array of tag names
- `parent` - Parent task ID (for subtasks)
- `custom_fields` - Array of custom field objects

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'name': 'Complete API integration', 'description': 'Integrate with the new payment API', 'priority': 2, 'due_date': 1709251200000, 'assignees': [123]}).encode()
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/list/901234/task', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update a Task

```bash
PUT /clickup/api/v2/task/{task_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'status': 'complete', 'priority': None}).encode()
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/task/abc123', data=data, method='PUT')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Delete a Task

```bash
DELETE /clickup/api/v2/task/{task_id}
```

#### Get Filtered Team Tasks

```bash
GET /clickup/api/v2/team/{team_id}/task
```

Query parameters:
- `page` - Page number (0-indexed)
- `order_by` - Sort field
- `statuses[]` - Filter by statuses
- `assignees[]` - Filter by assignees
- `list_ids[]` - Filter by list IDs
- `space_ids[]` - Filter by space IDs
- `folder_ids[]` - Filter by folder IDs

### Users

#### Get Current User

```bash
GET /clickup/api/v2/user
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/user')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "user": {
    "id": 123,
    "username": "Alice Johnson",
    "email": "alice@acme.com",
    "color": "#7B68EE",
    "profilePicture": "https://...",
    "initials": "AJ",
    "week_start_day": 0,
    "timezone": "America/New_York"
  }
}
```

### Webhooks

#### Get Webhooks

```bash
GET /clickup/api/v2/team/{team_id}/webhook
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/team/1234567/webhook')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Webhook

```bash
POST /clickup/api/v2/team/{team_id}/webhook
Content-Type: application/json

{
  "endpoint": "https://example.com/webhook",
  "events": ["taskCreated", "taskUpdated", "taskDeleted"],
  "space_id": "90120001",
  "folder_id": "456789",
  "list_id": "901234",
  "task_id": "abc123"
}
```

Events:
- `taskCreated`, `taskUpdated`, `taskDeleted`
- `taskPriorityUpdated`, `taskStatusUpdated`
- `taskAssigneeUpdated`, `taskDueDateUpdated`
- `taskTagUpdated`, `taskMoved`
- `taskCommentPosted`, `taskCommentUpdated`
- `taskTimeEstimateUpdated`, `taskTimeTrackedUpdated`
- `listCreated`, `listUpdated`, `listDeleted`
- `folderCreated`, `folderUpdated`, `folderDeleted`
- `spaceCreated`, `spaceUpdated`, `spaceDeleted`
- `goalCreated`, `goalUpdated`, `goalDeleted`
- `keyResultCreated`, `keyResultUpdated`, `keyResultDeleted`

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'endpoint': 'https://example.com/webhook', 'events': ['taskCreated', 'taskUpdated']}).encode()
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/team/1234567/webhook', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "id": "webhook123",
  "webhook": {
    "id": "webhook123",
    "userid": 123,
    "team_id": "1234567",
    "endpoint": "https://example.com/webhook",
    "client_id": "...",
    "events": ["taskCreated", "taskUpdated"],
    "health": {"status": "active", "fail_count": 0},
    "secret": "..."
  }
}
```

#### Update a Webhook

```bash
PUT /clickup/api/v2/webhook/{webhook_id}
```

#### Delete a Webhook

```bash
DELETE /clickup/api/v2/webhook/{webhook_id}
```

## Pagination

ClickUp uses page-based pagination. Use the `page` parameter (0-indexed):

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickup/api/v2/list/901234/task?page=0')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

Responses are limited to 100 tasks per page. The response includes a `last_page` boolean field. Continue incrementing the page number until `last_page` is `true`.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/clickup/api/v2/list/901234/task',
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
    'https://gateway.maton.ai/clickup/api/v2/list/901234/task',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- Task IDs are strings
- Timestamps are Unix milliseconds
- Priority values: 1=urgent, 2=high, 3=normal, 4=low, null=none
- Workspaces are called "teams" in the API
- Status values must match the exact status names configured in the list
- Responses are limited to 100 items per page
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets (`statuses[]`, `assignees[]`, `list_ids[]`) to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments. You may get "Invalid API key" errors when piping.

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or missing ClickUp connection |
| 401 | Invalid or missing Maton API key |
| 403 | Forbidden - insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from ClickUp API |

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

1. Ensure your URL path starts with `clickup`. For example:

- Correct: `https://gateway.maton.ai/clickup/api/v2/team`
- Incorrect: `https://gateway.maton.ai/api/v2/team`

## Resources

- [ClickUp API Overview](https://developer.clickup.com/docs/Getting%20Started.md)
- [Get Tasks](https://developer.clickup.com/reference/gettasks.md)
- [Create Task](https://developer.clickup.com/reference/createtask.md)
- [Update Task](https://developer.clickup.com/reference/updatetask.md)
- [Delete Task](https://developer.clickup.com/reference/deletetask.md)
- [Get Spaces](https://developer.clickup.com/reference/getspaces.md)
- [Get Lists](https://developer.clickup.com/reference/getlists.md)
- [Create Webhook](https://developer.clickup.com/reference/createwebhook.md)
- [Custom Fields](https://developer.clickup.com/docs/customfields.md)
- [Rate Limits](https://developer.clickup.com/docs/rate-limits.md)
- [LLM Reference](https://developer.clickup.com/llms.txt)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
