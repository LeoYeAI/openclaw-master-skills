---
name: wrike
description: |
  Wrike API integration with managed OAuth. Manage tasks, folders, projects, spaces, and team collaboration. Use this skill when users want to manage project work, track tasks, handle time logs, or access team resources in Wrike. For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Wrike

Access the Wrike API v4 with managed OAuth authentication. Manage tasks, folders, projects, spaces, groups, comments, attachments, timelogs, workflows, and more.

## Quick Start

```bash
# List all tasks
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/wrike/api/v4/tasks')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/wrike/api/v4/{endpoint-path}
```

Replace `{endpoint-path}` with the actual Wrike API endpoint path. The gateway proxies requests to `www.wrike.com/api/v4` and automatically injects your OAuth token.

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

Manage your Wrike OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=wrike&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'wrike'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection_id": "32c76f2f-54a0-47ca-b4d2-8e99ad852210",
  "status": "PENDING",
  "url": "https://connect.maton.ai/?session_token=...",
  "app": "wrike"
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
urllib.request.urlopen(req)
print("Deleted")
EOF
```

### Specifying Connection

If you have multiple Wrike connections, specify which one to use with the `Maton-Connection` header:

```python
req.add_header('Maton-Connection', '{connection_id}')
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Spaces

#### List Spaces

```bash
GET /wrike/api/v4/spaces
```

**Response:**
```json
{
  "kind": "spaces",
  "data": [
    {
      "id": "MQAAAAEFzzdO",
      "title": "First space",
      "avatarUrl": "https://www.wrike.com/static/spaceicons2/v3/6/6-planet.png",
      "accessType": "Public",
      "archived": false,
      "defaultProjectWorkflowId": "IEAGXR2EK77ZIOF4",
      "defaultTaskWorkflowId": "IEAGXR2EK4G2YNU4"
    }
  ]
}
```

#### Get Space

```bash
GET /wrike/api/v4/spaces/{spaceId}
```

#### Create Space

```bash
POST /wrike/api/v4/spaces
Content-Type: application/json

{
  "title": "New Space"
}
```

#### Update Space

```bash
PUT /wrike/api/v4/spaces/{spaceId}
Content-Type: application/json

{
  "title": "Updated Space Name"
}
```

#### Delete Space

```bash
DELETE /wrike/api/v4/spaces/{spaceId}
```

### Folders & Projects

Folders and projects are the main ways to organize work in Wrike. Projects are folders with additional properties (owners, dates, status).

#### Get Folder Tree

```bash
GET /wrike/api/v4/folders
```

**Response:**
```json
{
  "kind": "folderTree",
  "data": [
    {
      "id": "IEAGXR2EI7777777",
      "title": "Root",
      "childIds": ["MQAAAAEFzzdO", "MQAAAAEFzzRZ"],
      "scope": "WsRoot"
    },
    {
      "id": "MQAAAAEFzzdV",
      "title": "My Project",
      "childIds": [],
      "scope": "WsFolder",
      "project": {
        "authorId": "KUAXHKXS",
        "ownerIds": ["KUAXHKXS"],
        "customStatusId": "IEAGXR2EJMG2YNA4",
        "createdDate": "2026-03-09T08:15:07Z"
      }
    }
  ]
}
```

#### Get Folders in Space

```bash
GET /wrike/api/v4/spaces/{spaceId}/folders
```

#### Get Folder

```bash
GET /wrike/api/v4/folders/{folderId}
GET /wrike/api/v4/folders/{folderId},{folderId},... (up to 100 IDs)
```

#### Get Subfolders

```bash
GET /wrike/api/v4/folders/{folderId}/folders
```

#### Create Folder

```bash
POST /wrike/api/v4/folders/{parentFolderId}/folders
Content-Type: application/json

{
  "title": "New Folder"
}
```

#### Update Folder

```bash
PUT /wrike/api/v4/folders/{folderId}
Content-Type: application/json

{
  "title": "Updated Folder Name"
}
```

#### Delete Folder

```bash
DELETE /wrike/api/v4/folders/{folderId}
```

#### Copy Folder

```bash
POST /wrike/api/v4/copy_folder/{folderId}
Content-Type: application/json

{
  "parent": "{destinationFolderId}",
  "title": "Copy of Folder"
}
```

### Tasks

#### List Tasks

```bash
GET /wrike/api/v4/tasks
```

**Response:**
```json
{
  "kind": "tasks",
  "data": [
    {
      "id": "MAAAAAEFzzde",
      "accountId": "IEAGXR2E",
      "title": "First task",
      "status": "Active",
      "importance": "Normal",
      "createdDate": "2026-03-09T08:15:07Z",
      "updatedDate": "2026-03-10T07:07:57Z",
      "dates": {
        "type": "Planned",
        "duration": 2400,
        "start": "2026-03-05T09:00:00",
        "due": "2026-03-11T17:00:00"
      },
      "scope": "WsTask",
      "customStatusId": "IEAGXR2EJMG2YNV2",
      "permalink": "https://www.wrike.com/open.htm?id=4392433502"
    }
  ]
}
```

#### List Tasks in Folder

```bash
GET /wrike/api/v4/folders/{folderId}/tasks
```

#### List Tasks in Space

```bash
GET /wrike/api/v4/spaces/{spaceId}/tasks
```

#### Get Task

```bash
GET /wrike/api/v4/tasks/{taskId}
GET /wrike/api/v4/tasks/{taskId},{taskId},... (up to 100 IDs)
```

#### Create Task

```bash
POST /wrike/api/v4/folders/{folderId}/tasks
Content-Type: application/json

{
  "title": "New Task",
  "description": "Task description",
  "importance": "Normal",
  "dates": {
    "start": "2026-03-15",
    "due": "2026-03-20"
  }
}
```

**Response:**
```json
{
  "kind": "tasks",
  "data": [
    {
      "id": "MAAAAAEF7ufN",
      "accountId": "IEAGXR2E",
      "title": "New Task",
      "description": "Task description",
      "status": "Active",
      "importance": "Normal",
      "createdDate": "2026-03-10T07:16:07Z",
      "scope": "WsTask",
      "customStatusId": "IEAGXR2EJMG2YNU4",
      "permalink": "https://www.wrike.com/open.htm?id=4394510285"
    }
  ]
}
```

#### Update Task

```bash
PUT /wrike/api/v4/tasks/{taskId}
Content-Type: application/json

{
  "title": "Updated Task Title",
  "importance": "High"
}
```

#### Update Multiple Tasks

```bash
PUT /wrike/api/v4/tasks/{taskId},{taskId},... (up to 100 IDs)
Content-Type: application/json

{
  "status": "Completed"
}
```

#### Delete Task

```bash
DELETE /wrike/api/v4/tasks/{taskId}
```

### Comments

#### List Comments

```bash
GET /wrike/api/v4/comments
GET /wrike/api/v4/tasks/{taskId}/comments
GET /wrike/api/v4/folders/{folderId}/comments
GET /wrike/api/v4/comments/{commentId},{commentId},... (up to 100 IDs)
```

**Response:**
```json
{
  "kind": "comments",
  "data": [
    {
      "id": "IEAGXR2EIMBGYQMR",
      "authorId": "KUAXI4LC",
      "text": "This is a comment",
      "updatedDate": "2026-03-10T07:07:57Z",
      "createdDate": "2026-03-10T07:07:57Z",
      "taskId": "MAAAAAEFzzde"
    }
  ]
}
```

#### Create Comment

```bash
POST /wrike/api/v4/tasks/{taskId}/comments
Content-Type: application/json

{
  "text": "New comment text"
}
```

#### Update Comment

```bash
PUT /wrike/api/v4/comments/{commentId}
Content-Type: application/json

{
  "text": "Updated comment text"
}
```

#### Delete Comment

```bash
DELETE /wrike/api/v4/comments/{commentId}
```

### Attachments

#### List Attachments

```bash
GET /wrike/api/v4/attachments
GET /wrike/api/v4/tasks/{taskId}/attachments
GET /wrike/api/v4/folders/{folderId}/attachments
GET /wrike/api/v4/attachments/{attachmentId},{attachmentId},... (up to 100 IDs)
```

**Response:**
```json
{
  "kind": "attachments",
  "data": [
    {
      "id": "IEAGXR2EIYUN54ZV",
      "authorId": "KUAXHKXS",
      "name": "document.pdf",
      "createdDate": "2026-03-09T08:15:08Z",
      "version": 1,
      "type": "Wrike",
      "contentType": "application/pdf",
      "size": 117940,
      "taskId": "MAAAAAEFzzde"
    }
  ]
}
```

#### Download Attachment

```bash
GET /wrike/api/v4/attachments/{attachmentId}/download
```

#### Get Attachment Preview

```bash
GET /wrike/api/v4/attachments/{attachmentId}/preview
```

#### Get Attachment Access URL

```bash
GET /wrike/api/v4/attachments/{attachmentId}/url
```

#### Update Attachment

```bash
PUT /wrike/api/v4/attachments/{attachmentId}
```

#### Delete Attachment

```bash
DELETE /wrike/api/v4/attachments/{attachmentId}
```

### Contacts

Contacts represent users and groups in Wrike.

#### List Contacts

```bash
GET /wrike/api/v4/contacts
GET /wrike/api/v4/contacts/{contactId},{contactId},... (up to 100 IDs)
```

**Response:**
```json
{
  "kind": "contacts",
  "data": [
    {
      "id": "KUAXHKXS",
      "firstName": "Chris",
      "lastName": "",
      "type": "Person",
      "profiles": [
        {
          "accountId": "IEAGXR2E",
          "email": "user@example.com",
          "role": "User",
          "external": false,
          "admin": false,
          "owner": true,
          "active": true
        }
      ],
      "timezone": "US/Pacific",
      "locale": "en",
      "deleted": false,
      "me": true
    }
  ]
}
```

#### Update Contact

```bash
PUT /wrike/api/v4/contacts/{contactId}
Content-Type: application/json

{
  "metadata": [{"key": "customKey", "value": "customValue"}]
}
```

### Groups

#### List Groups

```bash
GET /wrike/api/v4/groups
GET /wrike/api/v4/groups/{groupId}
```

**Response:**
```json
{
  "kind": "groups",
  "data": [
    {
      "id": "KX7XIKVN",
      "accountId": "IEAGXR2E",
      "title": "My Team",
      "memberIds": ["KUAXHKXS"],
      "childIds": [],
      "parentIds": [],
      "myTeam": true
    }
  ]
}
```

#### Create Group

```bash
POST /wrike/api/v4/groups
Content-Type: application/json

{
  "title": "New Group",
  "members": ["KUAXHKXS"]
}
```

#### Update Group

```bash
PUT /wrike/api/v4/groups/{groupId}
Content-Type: application/json

{
  "title": "Updated Group Name"
}
```

#### Delete Group

```bash
DELETE /wrike/api/v4/groups/{groupId}
```

### Workflows

#### List Workflows

```bash
GET /wrike/api/v4/workflows
GET /wrike/api/v4/spaces/{spaceId}/workflows
```

**Response:**
```json
{
  "kind": "workflows",
  "data": [
    {
      "id": "IEAGXR2EK77ZIOF4",
      "name": "Default Workflow",
      "standard": true,
      "hidden": false,
      "customStatuses": [
        {
          "id": "IEAGXR2EJMAAAAAA",
          "name": "New",
          "color": "Blue",
          "group": "Active",
          "hidden": false
        },
        {
          "id": "IEAGXR2EJMG2YNA4",
          "name": "In Progress",
          "color": "Turquoise",
          "group": "Active",
          "hidden": false
        },
        {
          "id": "IEAGXR2EJMAAAAAB",
          "name": "Completed",
          "color": "Green",
          "group": "Completed",
          "hidden": false
        }
      ]
    }
  ]
}
```

#### Create Workflow

```bash
POST /wrike/api/v4/workflows
Content-Type: application/json

{
  "name": "Custom Workflow"
}
```

#### Update Workflow

```bash
PUT /wrike/api/v4/workflows/{workflowId}
Content-Type: application/json

{
  "name": "Updated Workflow Name"
}
```

### Custom Fields

#### List Custom Fields

```bash
GET /wrike/api/v4/customfields
GET /wrike/api/v4/spaces/{spaceId}/customfields
GET /wrike/api/v4/customfields/{customfieldId},{customfieldId},... (up to 100 IDs)
```

**Response:**
```json
{
  "kind": "customfields",
  "data": [
    {
      "id": "IEAGXR2EJUALBS23",
      "accountId": "IEAGXR2E",
      "title": "Impact",
      "type": "DropDown",
      "spaceId": "MQAAAAEFzzdO",
      "settings": {
        "values": ["Low", "Medium", "High"],
        "options": [
          {"value": "Low", "color": "Green"},
          {"value": "Medium", "color": "Yellow"},
          {"value": "High", "color": "Red"}
        ]
      }
    }
  ]
}
```

#### Create Custom Field

```bash
POST /wrike/api/v4/customfields
Content-Type: application/json

{
  "title": "Priority",
  "type": "DropDown",
  "settings": {
    "values": ["Low", "Medium", "High"]
  }
}
```

#### Update Custom Field

```bash
PUT /wrike/api/v4/customfields/{customfieldId}
Content-Type: application/json

{
  "title": "Updated Field Name"
}
```

### Timelogs

#### List Timelogs

```bash
GET /wrike/api/v4/timelogs
GET /wrike/api/v4/tasks/{taskId}/timelogs
GET /wrike/api/v4/folders/{folderId}/timelogs
GET /wrike/api/v4/contacts/{contactId}/timelogs
GET /wrike/api/v4/timelogs/{timelogId},{timelogId},... (up to 100 IDs)
```

#### Create Timelog

```bash
POST /wrike/api/v4/tasks/{taskId}/timelogs
Content-Type: application/json

{
  "hours": 2,
  "trackedDate": "2026-03-10",
  "comment": "Worked on implementation"
}
```

#### Update Timelog

```bash
PUT /wrike/api/v4/timelogs/{timelogId}
Content-Type: application/json

{
  "hours": 3,
  "comment": "Updated time entry"
}
```

#### Delete Timelog

```bash
DELETE /wrike/api/v4/timelogs/{timelogId}
```

### Timelog Categories

```bash
GET /wrike/api/v4/timelog_categories
```

### Dependencies

#### List Dependencies

```bash
GET /wrike/api/v4/tasks/{taskId}/dependencies
GET /wrike/api/v4/dependencies/{dependencyId},{dependencyId},... (up to 100 IDs)
```

**Response:**
```json
{
  "kind": "dependencies",
  "data": [
    {
      "id": "MgAAAAEFzzdeMwAAAAEFzzdb",
      "predecessorId": "MAAAAAEFzzde",
      "successorId": "MAAAAAEFzzdb",
      "relationType": "FinishToStart",
      "lagTime": 0
    }
  ]
}
```

#### Create Dependency

```bash
POST /wrike/api/v4/tasks/{taskId}/dependencies
Content-Type: application/json

{
  "predecessorId": "{taskId}",
  "relationType": "FinishToStart"
}
```

#### Update Dependency

```bash
PUT /wrike/api/v4/dependencies/{dependencyId}
Content-Type: application/json

{
  "relationType": "StartToStart"
}
```

#### Delete Dependency

```bash
DELETE /wrike/api/v4/dependencies/{dependencyId}
```

### Approvals

#### List Approvals

```bash
GET /wrike/api/v4/approvals
GET /wrike/api/v4/tasks/{taskId}/approvals
GET /wrike/api/v4/folders/{folderId}/approvals
GET /wrike/api/v4/approvals/{approvalId},{approvalId},... (up to 100 IDs)
```

**Response:**
```json
{
  "kind": "approvals",
  "data": [
    {
      "id": "IEAGXR2EMEB33OQA",
      "taskId": "MAAAAAEFzzde",
      "authorId": "KUAXHKXS",
      "dueDate": "2026-03-12",
      "decisions": [
        {
          "approverId": "KUAXHKXS",
          "status": "Pending",
          "updatedDate": "2026-03-09T08:15:08Z"
        }
      ],
      "status": "Pending",
      "finished": false
    }
  ]
}
```

#### Create Approval

```bash
POST /wrike/api/v4/tasks/{taskId}/approvals
Content-Type: application/json

{
  "approvers": ["KUAXHKXS"],
  "dueDate": "2026-03-15"
}
```

#### Update Approval

```bash
PUT /wrike/api/v4/approvals/{approvalId}
```

#### Cancel Approval

```bash
DELETE /wrike/api/v4/approvals/{approvalId}
```

### Invitations

#### List Invitations

```bash
GET /wrike/api/v4/invitations
```

**Response:**
```json
{
  "kind": "invitations",
  "data": [
    {
      "id": "IEAGXR2EJEAVFLCG",
      "accountId": "IEAGXR2E",
      "firstName": "John",
      "email": "john@example.com",
      "status": "Accepted",
      "inviterUserId": "KUAXHKXS",
      "invitationDate": "2026-03-09T08:14:04Z",
      "role": "User",
      "external": false
    }
  ]
}
```

#### Create Invitation

```bash
POST /wrike/api/v4/invitations
Content-Type: application/json

{
  "email": "newuser@example.com",
  "firstName": "New",
  "lastName": "User",
  "role": "User"
}
```

#### Update Invitation

```bash
PUT /wrike/api/v4/invitations/{invitationId}
```

#### Delete Invitation

```bash
DELETE /wrike/api/v4/invitations/{invitationId}
```

### Work Schedules

#### List Work Schedules

```bash
GET /wrike/api/v4/workschedules
GET /wrike/api/v4/workschedules/{workscheduleId}
```

**Response:**
```json
{
  "kind": "workschedules",
  "data": [
    {
      "id": "IEAGXR2EML7ZIOF4",
      "scheduleType": "Default",
      "title": "Default Schedule",
      "workweek": [
        {
          "workDays": ["Mon", "Tue", "Wed", "Thu", "Fri"],
          "capacityMinutes": 480
        }
      ]
    }
  ]
}
```

#### Create Work Schedule

```bash
POST /wrike/api/v4/workschedules
Content-Type: application/json

{
  "title": "Custom Schedule"
}
```

#### Update Work Schedule

```bash
PUT /wrike/api/v4/workschedules/{workscheduleId}
```

#### Delete Work Schedule

```bash
DELETE /wrike/api/v4/workschedules/{workscheduleId}
```

### Users (Admin)

#### Get User

```bash
GET /wrike/api/v4/users/{userId}
```

**Response:**
```json
{
  "kind": "users",
  "data": [
    {
      "id": "KUAXHKXS",
      "firstName": "Chris",
      "lastName": "",
      "type": "Person",
      "profiles": [
        {
          "accountId": "IEAGXR2E",
          "email": "user@example.com",
          "role": "User",
          "external": false,
          "admin": false,
          "owner": true,
          "active": true
        }
      ],
      "timezone": "US/Pacific",
      "locale": "en",
      "deleted": false,
      "me": true,
      "title": "Engineer",
      "companyName": "Company",
      "primaryEmail": "user@example.com",
      "userTypeId": "IEAGXR2ENH777777"
    }
  ]
}
```

#### Update User

```bash
PUT /wrike/api/v4/users/{userId}
PUT /wrike/api/v4/users/{userId},{userId},... (up to 100 IDs)
```

### Access Roles (Admin)

#### List Access Roles

```bash
GET /wrike/api/v4/access_roles
```

**Response:**
```json
{
  "kind": "accessRoles",
  "data": [
    {
      "id": "IEAGXR2END777777",
      "title": "Full",
      "description": "Can edit"
    },
    {
      "id": "IEAGXR2END777776",
      "title": "Editor",
      "description": "Can edit, but can't share or delete"
    },
    {
      "id": "IEAGXR2END777775",
      "title": "Limited",
      "description": "Can comment, change statuses, attach files, and start approvals"
    },
    {
      "id": "IEAGXR2END777774",
      "title": "Read Only",
      "description": "Can view"
    }
  ]
}
```

### Audit Log (Admin)

#### Get Audit Log

```bash
GET /wrike/api/v4/audit_log
```

**Response:**
```json
{
  "kind": "auditLog",
  "data": [
    {
      "id": "IEAGXR2ENQAAAAABMUI3U3A",
      "operation": "UserLoggedIn",
      "userId": "KUAXHKXS",
      "userEmail": "user@example.com",
      "eventDate": "2026-03-10T07:24:24Z",
      "ipAddress": "35.84.133.252",
      "objectType": "User",
      "objectName": "user@example.com",
      "objectId": "KUAXHKXS",
      "details": {
        "Login Type": "Oauth2",
        "User Agent": "Nango"
      }
    }
  ]
}
```

**Common Operations:**
- `UserLoggedIn` - User login events
- `Oauth2AccessGranted` - OAuth authorization events
- `TaskCreated`, `TaskDeleted`, `TaskModified` - Task operations
- `FolderCreated`, `FolderDeleted` - Folder operations
- `CommentAdded` - Comment events

### Data Export (Admin)

#### Get Data Export

```bash
GET /wrike/api/v4/data_export
GET /wrike/api/v4/data_export/{data_exportId}
```

Returns 202 on first request (export generation starts automatically). Subsequent calls return available daily-updated exports.

#### Refresh Data Export

```bash
POST /wrike/api/v4/data_export
```

Triggers a new data export refresh.

#### Get Data Export Schema

```bash
GET /wrike/api/v4/data_export_schema
```

Retrieves the schema documentation for export tables.

## Response Format

All Wrike API responses follow a standardized JSON structure:

```json
{
  "kind": "[resource_type]",
  "data": [...]
}
```

## Pagination

Some endpoints support pagination with `nextPageToken`:

```json
{
  "kind": "timelogs",
  "nextPageToken": "AFZ2V4QAAAAA6AAAAAAAAAAAAAAAAAAA22NEEX6HNLKBU",
  "responseSize": 100,
  "data": [...]
}
```

Use `pageToken` parameter for subsequent requests:

```bash
GET /wrike/api/v4/timelogs?pageToken={nextPageToken}
```

## Code Examples

### JavaScript

```javascript
async function listTasks() {
  const response = await fetch(
    'https://gateway.maton.ai/wrike/api/v4/tasks',
    {
      headers: {
        'Authorization': `Bearer ${process.env.MATON_API_KEY}`
      }
    }
  );
  return await response.json();
}

async function createTask(folderId, title) {
  const response = await fetch(
    `https://gateway.maton.ai/wrike/api/v4/folders/${folderId}/tasks`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title })
    }
  );
  return await response.json();
}
```

### Python

```python
import os
import json
import urllib.request

def list_tasks():
    url = 'https://gateway.maton.ai/wrike/api/v4/tasks'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    return json.load(urllib.request.urlopen(req))

def create_task(folder_id, title):
    url = f'https://gateway.maton.ai/wrike/api/v4/folders/{folder_id}/tasks'
    data = json.dumps({'title': title}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    req.add_header('Content-Type', 'application/json')
    return json.load(urllib.request.urlopen(req))
```

## Notes

- **Batch Operations**: Many endpoints support up to 100 IDs in a single request (comma-separated)
- **Custom Status IDs**: Tasks use `customStatusId` to reference workflow statuses
- **Projects vs Folders**: Projects are folders with additional properties (owners, dates, status)
- IMPORTANT: When using curl commands with URLs containing brackets, use `curl -g` to disable glob parsing
- IMPORTANT: When piping curl output to `jq`, environment variables may not expand correctly in some shells

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or invalid parameters |
| 401 | Invalid or missing API key |
| 403 | Insufficient permissions/scopes |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Wrike API |

## Resources

- [Wrike API Documentation](https://developers.wrike.com/)
- [Wrike API Overview](https://developers.wrike.com/overview/)
- [OAuth 2.0 Authorization](https://developers.wrike.com/oauth-20-authorization/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
