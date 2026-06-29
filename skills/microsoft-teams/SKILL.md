---
name: microsoft-teams
description: |
  Microsoft Teams API integration with managed OAuth. Manage teams, channels, messages, and meetings via Microsoft Graph API.
  Use this skill when users want to list teams, create channels, send messages, schedule meetings, or access meeting recordings and transcripts.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
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

# Microsoft Teams

Access the Microsoft Teams API with managed OAuth authentication via Microsoft Graph. Manage teams, channels, messages, meetings, and access recordings and transcripts.

## Quick Start

```bash
# List user's joined teams
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/microsoft-teams/v1.0/me/joinedTeams')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/microsoft-teams/{native-api-path}
```

Replace `{native-api-path}` with the actual Microsoft Graph API endpoint path. The gateway proxies requests to `graph.microsoft.com` and automatically injects your OAuth token.

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

Manage your Microsoft Teams OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=microsoft-teams&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'microsoft-teams'}).encode()
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
    "connection_id": "fb0fdc4a-0b5a-40cf-8b92-3bdae848cde3",
    "status": "ACTIVE",
    "creation_time": "2026-02-17T09:51:21.074601Z",
    "last_updated_time": "2026-02-17T09:51:34.323814Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "microsoft-teams",
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

If you have multiple Microsoft Teams connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/microsoft-teams/v1.0/me/joinedTeams')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'fb0fdc4a-0b5a-40cf-8b92-3bdae848cde3')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Teams

#### List Joined Teams

```bash
GET /microsoft-teams/v1.0/me/joinedTeams
```

**Response:**
```json
{
  "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#teams",
  "@odata.count": 1,
  "value": [
    {
      "id": "b643f103-870d-4f98-a23d-e6f164fae33e",
      "displayName": "carvedai.com",
      "description": null,
      "isArchived": false,
      "tenantId": "cb83c3f9-6d16-4cf3-bd8c-ab16b37932f9"
    }
  ]
}
```

#### Get Team

```bash
GET /microsoft-teams/v1.0/teams/{team-id}
```

### Channels

#### List Channels

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/channels
```

**Response:**
```json
{
  "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#teams('...')/channels",
  "@odata.count": 1,
  "value": [
    {
      "id": "19:9fwtZjo3IM0D8bLdQqR-_oMFw1eUDlzWjPfIhNGhVd41@thread.tacv2",
      "createdDateTime": "2026-02-16T20:09:27.254Z",
      "displayName": "General",
      "description": null,
      "email": "carvedai.com473@carvedai.com",
      "membershipType": "standard",
      "isArchived": false
    }
  ]
}
```

#### List Private Channels

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/channels?$filter=membershipType eq 'private'
```

#### Get Channel

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}
```

#### Create Channel

```bash
POST /microsoft-teams/v1.0/teams/{team-id}/channels
Content-Type: application/json

{
  "displayName": "New Channel",
  "description": "Channel description",
  "membershipType": "standard"
}
```

**Response:**
```json
{
  "id": "19:3b3361df822044558a062bb1a4ac8357@thread.tacv2",
  "createdDateTime": "2026-02-17T20:24:33.9284462Z",
  "displayName": "Maton Test Channel",
  "description": "Channel created by Maton integration test",
  "membershipType": "standard",
  "isArchived": false
}
```

#### Update Channel

```bash
PATCH /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}
Content-Type: application/json

{
  "description": "Updated description"
}
```

Returns `204 No Content` on success. Note: The default "General" channel cannot be updated.

#### Delete Channel

```bash
DELETE /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}
```

Returns `204 No Content` on success.

### Channel Members

#### List Channel Members

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}/members
```

**Response:**
```json
{
  "@odata.count": 1,
  "value": [
    {
      "@odata.type": "#microsoft.graph.aadUserConversationMember",
      "id": "MCMjMiMj...",
      "roles": ["owner"],
      "displayName": "Kevin Kim",
      "userId": "5f56d55b-2ffb-448d-982a-b52547431f71",
      "email": "richard@carvedai.com"
    }
  ]
}
```

### Messages

#### List Channel Messages

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}/messages
```

#### Send Message to Channel

```bash
POST /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}/messages
Content-Type: application/json

{
  "body": {
    "content": "Hello World"
  }
}
```

**Response:**
```json
{
  "id": "1771359569239",
  "replyToId": null,
  "messageType": "message",
  "createdDateTime": "2026-02-17T20:19:29.239Z",
  "importance": "normal",
  "locale": "en-us",
  "from": {
    "user": {
      "id": "5f56d55b-2ffb-448d-982a-b52547431f71",
      "displayName": "Kevin Kim",
      "userIdentityType": "aadUser",
      "tenantId": "cb83c3f9-6d16-4cf3-bd8c-ab16b37932f9"
    }
  },
  "body": {
    "contentType": "text",
    "content": "Hello World"
  },
  "channelIdentity": {
    "teamId": "b643f103-870d-4f98-a23d-e6f164fae33e",
    "channelId": "19:9fwtZjo3IM0D8bLdQqR-_oMFw1eUDlzWjPfIhNGhVd41@thread.tacv2"
  }
}
```

#### Send HTML Message

```bash
POST /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}/messages
Content-Type: application/json

{
  "body": {
    "contentType": "html",
    "content": "<h1>Hello</h1><p>This is <strong>formatted</strong> content.</p>"
  }
}
```

#### Reply to Message

```bash
POST /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}/messages/{message-id}/replies
Content-Type: application/json

{
  "body": {
    "content": "This is a reply"
  }
}
```

#### List Message Replies

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}/messages/{message-id}/replies
```

#### Edit Message

```bash
PATCH /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}/messages/{message-id}
Content-Type: application/json

{
  "body": {
    "content": "Updated message content"
  }
}
```

Returns `204 No Content` on success.

### Team Members

#### List Team Members

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/members
```

**Response:**
```json
{
  "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#teams('...')/members",
  "@odata.count": 1,
  "value": [
    {
      "@odata.type": "#microsoft.graph.aadUserConversationMember",
      "id": "MCMjMSMj...",
      "roles": ["owner"],
      "displayName": "Kevin Kim",
      "userId": "5f56d55b-2ffb-448d-982a-b52547431f71",
      "email": "richard@carvedai.com",
      "tenantId": "cb83c3f9-6d16-4cf3-bd8c-ab16b37932f9"
    }
  ]
}
```

### Presence

#### Get User Presence

```bash
GET /microsoft-teams/v1.0/me/presence
```

**Response:**
```json
{
  "id": "5f56d55b-2ffb-448d-982a-b52547431f71",
  "availability": "Offline",
  "activity": "Offline",
  "outOfOfficeSettings": {
    "message": null,
    "isOutOfOffice": false
  }
}
```

Availability values: `Available`, `Busy`, `DoNotDisturb`, `Away`, `Offline`

#### Get User Presence by ID

```bash
GET /microsoft-teams/v1.0/users/{user-id}/presence
```

Returns presence information for a specific user by their ID.

### Tabs

#### List Channel Tabs

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/channels/{channel-id}/tabs
```

**Response:**
```json
{
  "@odata.count": 2,
  "value": [
    {
      "id": "ee0b3e8b-dfc8-4945-a45d-28ceaf787d92",
      "displayName": "Notes",
      "webUrl": "https://teams.microsoft.com/l/entity/..."
    },
    {
      "id": "3ed5b337-c2c9-4d5d-b7b4-84ff09a8fc1c",
      "displayName": "Files",
      "webUrl": "https://teams.microsoft.com/l/entity/..."
    }
  ]
}
```

### Apps

#### List Installed Apps

```bash
GET /microsoft-teams/v1.0/teams/{team-id}/installedApps
```

### Online Meetings

#### Create Meeting

```bash
POST /microsoft-teams/v1.0/me/onlineMeetings
Content-Type: application/json

{
  "subject": "Team Sync",
  "startDateTime": "2026-02-18T10:00:00Z",
  "endDateTime": "2026-02-18T11:00:00Z"
}
```

**Response:**
```json
{
  "id": "MSo1ZjU2ZDU1Yi0yZmZi...",
  "subject": "Team Sync",
  "startDateTime": "2026-02-18T10:00:00Z",
  "endDateTime": "2026-02-18T11:00:00Z",
  "joinUrl": "https://teams.microsoft.com/l/meetup-join/...",
  "joinWebUrl": "https://teams.microsoft.com/l/meetup-join/...",
  "meetingCode": "28636743235745",
  "joinMeetingIdSettings": {
    "joinMeetingId": "28636743235745",
    "passcode": "qh37NK9V",
    "isPasscodeRequired": true
  },
  "participants": {
    "organizer": {
      "upn": "richard@carvedai.com",
      "role": "presenter"
    }
  }
}
```

The `joinUrl` can be shared with attendees to join the meeting.

#### Get Meeting

```bash
GET /microsoft-teams/v1.0/me/onlineMeetings/{meeting-id}
```

#### Find Meeting by Join URL

```bash
GET /microsoft-teams/v1.0/me/onlineMeetings?$filter=JoinWebUrl eq '{encoded-join-url}'
```

Note: Microsoft Graph requires a filter to query meetings. You cannot list all meetings without filtering by `JoinWebUrl`.

#### List Calendar Events (includes scheduled meetings)

```bash
GET /microsoft-teams/v1.0/me/calendar/events?$top=10
```

Scheduled Teams meetings appear as calendar events with `isOnlineMeeting: true`.

#### Delete Meeting

```bash
DELETE /microsoft-teams/v1.0/me/onlineMeetings/{meeting-id}
```

Returns `204 No Content` on success.

#### Create Meeting with Attendees

```bash
POST /microsoft-teams/v1.0/me/onlineMeetings
Content-Type: application/json

{
  "subject": "Project Review",
  "startDateTime": "2026-02-18T14:00:00Z",
  "endDateTime": "2026-02-18T15:00:00Z",
  "participants": {
    "attendees": [
      {
        "upn": "attendee@example.com",
        "role": "attendee"
      }
    ]
  }
}
```

#### List Meeting Recordings

```bash
GET /microsoft-teams/v1.0/me/onlineMeetings/{meeting-id}/recordings
```

Returns a list of recordings for a meeting (available after the meeting has ended and recording was enabled).

#### Get Meeting Recording

```bash
GET /microsoft-teams/v1.0/me/onlineMeetings/{meeting-id}/recordings/{recording-id}
```

#### List Meeting Transcripts

```bash
GET /microsoft-teams/v1.0/me/onlineMeetings/{meeting-id}/transcripts
```

Returns a list of transcripts for a meeting (available after the meeting has ended and transcription was enabled).

#### Get Meeting Transcript

```bash
GET /microsoft-teams/v1.0/me/onlineMeetings/{meeting-id}/transcripts/{transcript-id}
```

#### List Attendance Reports

```bash
GET /microsoft-teams/v1.0/me/onlineMeetings/{meeting-id}/attendanceReports
```

Returns attendance reports for a meeting (available after the meeting has ended).

#### Get Attendance Report

```bash
GET /microsoft-teams/v1.0/me/onlineMeetings/{meeting-id}/attendanceReports/{report-id}
```

### Chats

#### List User Chats

```bash
GET /microsoft-teams/v1.0/me/chats
```

#### Get Chat

```bash
GET /microsoft-teams/v1.0/chats/{chat-id}
```

#### List Chat Messages

```bash
GET /microsoft-teams/v1.0/chats/{chat-id}/messages
```

#### Send Chat Message

```bash
POST /microsoft-teams/v1.0/chats/{chat-id}/messages
Content-Type: application/json

{
  "body": {
    "content": "Hello in chat"
  }
}
```

## Pagination

Microsoft Graph uses OData-style pagination with `@odata.nextLink`:

```bash
GET /microsoft-teams/v1.0/me/joinedTeams?$top=10
```

Response includes pagination link when more results exist:

```json
{
  "value": [...],
  "@odata.nextLink": "https://graph.microsoft.com/v1.0/me/joinedTeams?$skiptoken=..."
}
```

Use the `$top` parameter to limit results per page.

## OData Query Parameters

- `$top=10` - Limit results
- `$skip=20` - Skip results
- `$select=id,displayName` - Select specific fields
- `$filter=membershipType eq 'private'` - Filter results
- `$orderby=displayName` - Sort results

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/microsoft-teams/v1.0/me/joinedTeams',
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
    'https://gateway.maton.ai/microsoft-teams/v1.0/me/joinedTeams',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

### Send Message Example (Python)

```python
import os
import requests

team_id = "your-team-id"
channel_id = "your-channel-id"

response = requests.post(
    f'https://gateway.maton.ai/microsoft-teams/v1.0/teams/{team_id}/channels/{channel_id}/messages',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={'body': {'content': 'Hello from Maton!'}}
)
data = response.json()
```

## Notes

- Uses Microsoft Graph API v1.0
- **Messages are sent as the authenticated user** (not as a bot) - the `from.user` field shows the actual user identity
- Team IDs are GUIDs (e.g., `b643f103-870d-4f98-a23d-e6f164fae33e`)
- Channel IDs include thread suffix (e.g., `19:9fwtZjo3IM0D8bLdQqR-_oMFw1eUDlzWjPfIhNGhVd41@thread.tacv2`)
- Message IDs are timestamps (e.g., `1771359569239`)
- Message body content types: `text` (default) or `html`
- Channel membership types: `standard`, `private`, `shared`
- The default "General" channel cannot be updated or deleted
- Only `me` endpoint is supported for listing joined teams (not arbitrary user IDs)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Microsoft Teams connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 403 | Insufficient permissions for the requested resource |
| 404 | Team, channel, or message not found |
| 429 | Rate limited (Microsoft Graph throttling) |
| 4xx/5xx | Passthrough error from Microsoft Graph API |

## Resources

- [Microsoft Teams API Overview](https://learn.microsoft.com/en-us/graph/api/resources/teams-api-overview)
- [Microsoft Graph API Reference](https://learn.microsoft.com/en-us/graph/api/overview)
- [Channel Resource](https://learn.microsoft.com/en-us/graph/api/resources/channel)
- [ChatMessage Resource](https://learn.microsoft.com/en-us/graph/api/resources/chatmessage)
- [Team Resource](https://learn.microsoft.com/en-us/graph/api/resources/team)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
