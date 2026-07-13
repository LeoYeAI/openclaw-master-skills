---
name: zoho-mail
description: |
  Zoho Mail API integration with managed OAuth. Send, receive, and manage emails, folders, and labels.
  Use this skill when users want to send emails, read messages, manage folders, or work with email labels in Zoho Mail.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
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

# Zoho Mail

Access the Zoho Mail API with managed OAuth authentication. Send, receive, search, and manage emails with full folder and label management.

## Quick Start

```bash
# List all accounts
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-mail/{native-api-path}
```

Replace `{native-api-path}` with the actual Zoho Mail API endpoint path. The gateway proxies requests to `mail.zoho.com` and automatically injects your OAuth token.

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

Manage your Zoho Mail OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-mail&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-mail'}).encode()
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
    "app": "zoho-mail",
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

If you have multiple Zoho Mail connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Account Operations

#### Get All Accounts

Retrieve all mail accounts for the authenticated user.

```bash
GET /zoho-mail/api/accounts
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Account Details

```bash
GET /zoho-mail/api/accounts/{accountId}
```

### Folder Operations

#### List All Folders

```bash
GET /zoho-mail/api/accounts/{accountId}/folders
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts/{accountId}/folders')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "status": {
    "code": 200,
    "description": "success"
  },
  "data": [
    {
      "folderId": "1367000000000008014",
      "folderName": "Inbox",
      "folderType": "Inbox",
      "path": "/Inbox",
      "imapAccess": true,
      "isArchived": 0,
      "URI": "https://mail.zoho.com/api/accounts/1367000000000008002/folders/1367000000000008014"
    },
    {
      "folderId": "1367000000000008016",
      "folderName": "Drafts",
      "folderType": "Drafts",
      "path": "/Drafts",
      "imapAccess": true,
      "isArchived": 0
    }
  ]
}
```

#### Create Folder

```bash
POST /zoho-mail/api/accounts/{accountId}/folders
Content-Type: application/json

{
  "folderName": "My Custom Folder"
}
```

#### Rename Folder

```bash
PUT /zoho-mail/api/accounts/{accountId}/folders/{folderId}
Content-Type: application/json

{
  "folderName": "Renamed Folder"
}
```

#### Delete Folder

```bash
DELETE /zoho-mail/api/accounts/{accountId}/folders/{folderId}
```

### Label Operations

#### List Labels

```bash
GET /zoho-mail/api/accounts/{accountId}/labels
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts/{accountId}/labels')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Label

```bash
POST /zoho-mail/api/accounts/{accountId}/labels
Content-Type: application/json

{
  "labelName": "Important"
}
```

#### Update Label

```bash
PUT /zoho-mail/api/accounts/{accountId}/labels/{labelId}
Content-Type: application/json

{
  "labelName": "Updated Label"
}
```

#### Delete Label

```bash
DELETE /zoho-mail/api/accounts/{accountId}/labels/{labelId}
```

### Email Message Operations

#### List Emails in Folder

```bash
GET /zoho-mail/api/accounts/{accountId}/messages/view?folderId={folderId}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `folderId` | long | Folder ID to list messages from |
| `limit` | integer | Number of messages to return (default: 50) |
| `start` | integer | Offset for pagination |
| `sortBy` | string | Sort field (e.g., `date`) |
| `sortOrder` | boolean | `true` for ascending, `false` for descending |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts/{accountId}/messages/view?folderId={folderId}&limit=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Search Emails

```bash
GET /zoho-mail/api/accounts/{accountId}/messages/search?searchKey={query}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `searchKey` | string | Search query |
| `limit` | integer | Number of results to return |
| `start` | integer | Offset for pagination |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
import urllib.parse
query = urllib.parse.quote('from:sender@example.com')
req = urllib.request.Request(f'https://gateway.maton.ai/zoho-mail/api/accounts/{{accountId}}/messages/search?searchKey={query}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Email Content

```bash
GET /zoho-mail/api/accounts/{accountId}/folders/{folderId}/messages/{messageId}/content
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts/{accountId}/folders/{folderId}/messages/{messageId}/content')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Email Headers

```bash
GET /zoho-mail/api/accounts/{accountId}/folders/{folderId}/messages/{messageId}/header
```

#### Get Email Metadata

```bash
GET /zoho-mail/api/accounts/{accountId}/folders/{folderId}/messages/{messageId}/details
```

#### Get Original Message (MIME)

```bash
GET /zoho-mail/api/accounts/{accountId}/messages/{messageId}/originalmessage
```

#### Send Email

```bash
POST /zoho-mail/api/accounts/{accountId}/messages
Content-Type: application/json

{
  "fromAddress": "sender@yourdomain.com",
  "toAddress": "recipient@example.com",
  "subject": "Email Subject",
  "content": "Email body content",
  "mailFormat": "html"
}
```

**Request Body Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fromAddress` | string | Yes | Sender's email address |
| `toAddress` | string | Yes | Recipient's email address |
| `subject` | string | Yes | Email subject |
| `content` | string | Yes | Email body content |
| `ccAddress` | string | No | CC recipient |
| `bccAddress` | string | No | BCC recipient |
| `mailFormat` | string | No | `html` or `plaintext` (default: `html`) |
| `askReceipt` | string | No | `yes` or `no` for read receipt |
| `encoding` | string | No | Character encoding (default: `UTF-8`) |

**Example - Send Email:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "fromAddress": "sender@yourdomain.com",
    "toAddress": "recipient@example.com",
    "subject": "Hello from Zoho Mail API",
    "content": "<h1>Hello!</h1><p>This is a test email.</p>",
    "mailFormat": "html"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts/{accountId}/messages', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Scheduling Parameters (Optional):**

| Field | Type | Description |
|-------|------|-------------|
| `isSchedule` | boolean | Enable scheduling |
| `scheduleType` | integer | 1-5 for preset times; 6 for custom |
| `timeZone` | string | Required if scheduleType=6 (e.g., `GMT 5:30`) |
| `scheduleTime` | string | Required if scheduleType=6 (format: `MM/DD/YYYY HH:MM:SS`) |

#### Reply to Email

```bash
POST /zoho-mail/api/accounts/{accountId}/messages/{messageId}
Content-Type: application/json

{
  "fromAddress": "sender@yourdomain.com",
  "toAddress": "recipient@example.com",
  "subject": "Re: Original Subject",
  "content": "Reply content"
}
```

#### Save Draft

```bash
POST /zoho-mail/api/accounts/{accountId}/messages
Content-Type: application/json

{
  "fromAddress": "sender@yourdomain.com",
  "toAddress": "recipient@example.com",
  "subject": "Draft Subject",
  "content": "Draft content",
  "mode": "draft"
}
```

#### Update Message (Mark as Read/Unread, Move, Flag)

```bash
PUT /zoho-mail/api/accounts/{accountId}/updatemessage
Content-Type: application/json

{
  "messageId": ["messageId1", "messageId2"],
  "folderId": "folderId",
  "mode": "markAsRead"
}
```

**Mode Options:**
- `markAsRead` - Mark messages as read
- `markAsUnread` - Mark messages as unread
- `moveMessage` - Move messages (requires `destfolderId`)
- `flag` - Set flag (requires `flagid`: 1-4)
- `archive` - Archive messages
- `unArchive` - Unarchive messages
- `spam` - Mark as spam
- `notSpam` - Mark as not spam

**Example - Mark as Read:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "messageId": ["1234567890123456789"],
    "folderId": "9876543210987654321",
    "mode": "markAsRead"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-mail/api/accounts/{accountId}/updatemessage', data=data, method='PUT')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Delete Email

```bash
DELETE /zoho-mail/api/accounts/{accountId}/folders/{folderId}/messages/{messageId}
```

### Attachment Operations

#### Upload Attachment

```bash
POST /zoho-mail/api/accounts/{accountId}/messages/attachments
Content-Type: multipart/form-data
```

#### Get Attachment Info

```bash
GET /zoho-mail/api/accounts/{accountId}/folders/{folderId}/messages/{messageId}/attachmentinfo
```

#### Download Attachment

```bash
GET /zoho-mail/api/accounts/{accountId}/folders/{folderId}/messages/{messageId}/attachments/{attachmentId}
```

## Pagination

Zoho Mail uses offset-based pagination:

```bash
GET /zoho-mail/api/accounts/{accountId}/messages/view?folderId={folderId}&start=0&limit=50
```

- `start`: Offset index (default: 0)
- `limit`: Number of records to return (default: 50)

For subsequent pages, increment `start` by `limit`:
- Page 1: `start=0&limit=50`
- Page 2: `start=50&limit=50`
- Page 3: `start=100&limit=50`

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/zoho-mail/api/accounts',
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
    'https://gateway.maton.ai/zoho-mail/api/accounts',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- Account IDs are required for most operations - first call `/api/accounts` to get your account ID
- Message IDs and Folder IDs are numeric strings
- The `fromAddress` must be associated with the authenticated account
- Default folders include: Inbox, Drafts, Templates, Snoozed, Sent, Spam, Trash, Outbox
- Supported encodings: Big5, EUC-JP, EUC-KR, GB2312, ISO-2022-JP, ISO-8859-1, KOI8-R, Shift_JIS, US-ASCII, UTF-8, WINDOWS-1251
- Some operations (labels, folder management, sending) require additional OAuth scopes. If you receive an `INVALID_OAUTHSCOPE` error, contact Maton support at support@maton.ai with the specific operations/APIs you need and your use-case
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho Mail connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho Mail API |

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

1. Ensure your URL path starts with `zoho-mail`. For example:

- Correct: `https://gateway.maton.ai/zoho-mail/api/accounts`
- Incorrect: `https://gateway.maton.ai/api/accounts`

## Resources

- [Zoho Mail API Overview](https://www.zoho.com/mail/help/api/overview.html)
- [Zoho Mail API Index](https://www.zoho.com/mail/help/api/)
- [Email Messages API](https://www.zoho.com/mail/help/api/email-api.html)
- [Getting Started with Zoho Mail API](https://www.zoho.com/mail/help/api/getting-started-with-api.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
