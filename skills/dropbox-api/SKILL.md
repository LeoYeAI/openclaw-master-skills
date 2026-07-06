---
name: dropbox
description: |
  Dropbox API integration with managed OAuth. Files, folders, search, metadata, and cloud storage.
  Use this skill when users want to manage files and folders in Dropbox, search content, or work with file metadata.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Dropbox

Access the Dropbox API with managed OAuth authentication. Manage files and folders, search content, retrieve metadata, and work with file revisions.

## Quick Start

```bash
# List files in root folder
python <<'EOF'
import urllib.request, os, json
data = json.dumps({"path": ""}).encode()
req = urllib.request.Request('https://gateway.maton.ai/dropbox/2/files/list_folder', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/dropbox/2/{endpoint}
```

The gateway proxies requests to `api.dropboxapi.com` and automatically injects your OAuth token.

**Important:** Dropbox API v2 uses POST for all endpoints with JSON request bodies.

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

Manage your Dropbox OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=dropbox&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'dropbox'}).encode()
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
    "connection_id": "1efbb655-88e9-4a23-ad3b-f3e19cbff279",
    "status": "ACTIVE",
    "creation_time": "2026-02-09T23:34:49.818074Z",
    "last_updated_time": "2026-02-09T23:37:09.697559Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "dropbox",
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

If you have multiple Dropbox connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({"path": ""}).encode()
req = urllib.request.Request('https://gateway.maton.ai/dropbox/2/files/list_folder', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
req.add_header('Maton-Connection', '1efbb655-88e9-4a23-ad3b-f3e19cbff279')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Users

#### Get Current Account

```bash
POST /dropbox/2/users/get_current_account
Content-Type: application/json

null
```

**Response:**
```json
{
  "account_id": "dbid:AAA-AdT84WzkyLw5s590DbYF1nGomiAoO8I",
  "name": {
    "given_name": "John",
    "surname": "Doe",
    "familiar_name": "John",
    "display_name": "John Doe",
    "abbreviated_name": "JD"
  },
  "email": "john@example.com",
  "email_verified": true,
  "disabled": false,
  "country": "US",
  "locale": "en",
  "account_type": {
    ".tag": "basic"
  },
  "root_info": {
    ".tag": "user",
    "root_namespace_id": "11989877987",
    "home_namespace_id": "11989877987"
  }
}
```

#### Get Space Usage

```bash
POST /dropbox/2/users/get_space_usage
Content-Type: application/json

null
```

**Response:**
```json
{
  "used": 538371,
  "allocation": {
    ".tag": "individual",
    "allocated": 2147483648
  }
}
```

### Files and Folders

#### List Folder

```bash
POST /dropbox/2/files/list_folder
Content-Type: application/json

{
  "path": "",
  "recursive": false,
  "include_deleted": false,
  "include_has_explicit_shared_members": false
}
```

Use empty string `""` for the root folder.

**Optional Parameters:**
- `recursive` - Include contents of subdirectories (default: false)
- `include_deleted` - Include deleted files (default: false)
- `include_media_info` - Include media info for photos/videos
- `limit` - Maximum entries per response (1-2000)

**Response:**
```json
{
  "entries": [
    {
      ".tag": "file",
      "name": "document.pdf",
      "path_lower": "/document.pdf",
      "path_display": "/document.pdf",
      "id": "id:Awe3Av8A8YYAAAAAAAAABQ",
      "client_modified": "2026-02-09T19:58:12Z",
      "server_modified": "2026-02-09T19:58:13Z",
      "rev": "016311c063b4f8700000002caa704e3",
      "size": 538371,
      "is_downloadable": true,
      "content_hash": "6542845d7b65ffc5358ebaa6981d991bab9fda194afa48bd727fcbe9e4a3158b"
    },
    {
      ".tag": "folder",
      "name": "Documents",
      "path_lower": "/documents",
      "path_display": "/Documents",
      "id": "id:Awe3Av8A8YYAAAAAAAAABw"
    }
  ],
  "cursor": "AAVqv-MUYFlM98b1QpFK6YaYC8L1s39lWjqbeqgWu4un...",
  "has_more": false
}
```

#### Continue Listing Folder

```bash
POST /dropbox/2/files/list_folder/continue
Content-Type: application/json

{
  "cursor": "AAVqv-MUYFlM98b1QpFK6YaYC8L1s39lWjqbeqgWu4un..."
}
```

Use when `has_more` is true in the previous response.

#### Get Metadata

```bash
POST /dropbox/2/files/get_metadata
Content-Type: application/json

{
  "path": "/document.pdf",
  "include_media_info": false,
  "include_deleted": false,
  "include_has_explicit_shared_members": false
}
```

**Response:**
```json
{
  ".tag": "file",
  "name": "document.pdf",
  "path_lower": "/document.pdf",
  "path_display": "/document.pdf",
  "id": "id:Awe3Av8A8YYAAAAAAAAABQ",
  "client_modified": "2026-02-09T19:58:12Z",
  "server_modified": "2026-02-09T19:58:13Z",
  "rev": "016311c063b4f8700000002caa704e3",
  "size": 538371,
  "is_downloadable": true,
  "content_hash": "6542845d7b65ffc5358ebaa6981d991bab9fda194afa48bd727fcbe9e4a3158b"
}
```

#### Create Folder

```bash
POST /dropbox/2/files/create_folder_v2
Content-Type: application/json

{
  "path": "/New Folder",
  "autorename": false
}
```

**Response:**
```json
{
  "metadata": {
    "name": "New Folder",
    "path_lower": "/new folder",
    "path_display": "/New Folder",
    "id": "id:Awe3Av8A8YYAAAAAAAAABw"
  }
}
```

#### Copy File or Folder

```bash
POST /dropbox/2/files/copy_v2
Content-Type: application/json

{
  "from_path": "/source/file.pdf",
  "to_path": "/destination/file.pdf",
  "autorename": false
}
```

**Response:**
```json
{
  "metadata": {
    ".tag": "file",
    "name": "file.pdf",
    "path_lower": "/destination/file.pdf",
    "path_display": "/destination/file.pdf",
    "id": "id:Awe3Av8A8YYAAAAAAAAACA"
  }
}
```

#### Move File or Folder

```bash
POST /dropbox/2/files/move_v2
Content-Type: application/json

{
  "from_path": "/old/location/file.pdf",
  "to_path": "/new/location/file.pdf",
  "autorename": false
}
```

**Response:**
```json
{
  "metadata": {
    ".tag": "file",
    "name": "file.pdf",
    "path_lower": "/new/location/file.pdf",
    "path_display": "/new/location/file.pdf",
    "id": "id:Awe3Av8A8YYAAAAAAAAACA"
  }
}
```

#### Delete File or Folder

```bash
POST /dropbox/2/files/delete_v2
Content-Type: application/json

{
  "path": "/file-to-delete.pdf"
}
```

**Response:**
```json
{
  "metadata": {
    ".tag": "file",
    "name": "file-to-delete.pdf",
    "path_lower": "/file-to-delete.pdf",
    "path_display": "/file-to-delete.pdf",
    "id": "id:Awe3Av8A8YYAAAAAAAAABQ"
  }
}
```

#### Get Temporary Download Link

```bash
POST /dropbox/2/files/get_temporary_link
Content-Type: application/json

{
  "path": "/document.pdf"
}
```

**Response:**
```json
{
  "metadata": {
    "name": "document.pdf",
    "path_lower": "/document.pdf",
    "path_display": "/document.pdf",
    "id": "id:Awe3Av8A8YYAAAAAAAAABQ",
    "size": 538371,
    "is_downloadable": true
  },
  "link": "https://uc785ee484c03b6556c091ea4491.dl.dropboxusercontent.com/cd/0/get/..."
}
```

The link is valid for 4 hours.

### Search

#### Search Files

```bash
POST /dropbox/2/files/search_v2
Content-Type: application/json

{
  "query": "document",
  "options": {
    "path": "",
    "max_results": 100,
    "file_status": "active",
    "filename_only": false
  }
}
```

**Response:**
```json
{
  "has_more": false,
  "matches": [
    {
      "highlight_spans": [],
      "match_type": {
        ".tag": "filename"
      },
      "metadata": {
        ".tag": "metadata",
        "metadata": {
          ".tag": "file",
          "name": "document.pdf",
          "path_display": "/document.pdf",
          "path_lower": "/document.pdf",
          "id": "id:Awe3Av8A8YYAAAAAAAAABw"
        }
      }
    }
  ]
}
```

#### Continue Search

```bash
POST /dropbox/2/files/search/continue_v2
Content-Type: application/json

{
  "cursor": "..."
}
```

### File Revisions

#### List Revisions

```bash
POST /dropbox/2/files/list_revisions
Content-Type: application/json

{
  "path": "/document.pdf",
  "mode": "path",
  "limit": 10
}
```

**Response:**
```json
{
  "is_deleted": false,
  "entries": [
    {
      "name": "document.pdf",
      "path_lower": "/document.pdf",
      "path_display": "/document.pdf",
      "id": "id:Awe3Av8A8YYAAAAAAAAABQ",
      "client_modified": "2026-02-09T19:58:12Z",
      "server_modified": "2026-02-09T19:58:13Z",
      "rev": "016311c063b4f8700000002caa704e3",
      "size": 538371,
      "is_downloadable": true
    }
  ],
  "has_more": false
}
```

#### Restore File

```bash
POST /dropbox/2/files/restore
Content-Type: application/json

{
  "path": "/document.pdf",
  "rev": "016311c063b4f8700000002caa704e3"
}
```

### Tags

#### Get Tags

```bash
POST /dropbox/2/files/tags/get
Content-Type: application/json

{
  "paths": ["/document.pdf", "/folder"]
}
```

**Response:**
```json
{
  "paths_to_tags": [
    {
      "path": "/document.pdf",
      "tags": [
        {
          ".tag": "user_generated_tag",
          "tag_text": "important"
        }
      ]
    },
    {
      "path": "/folder",
      "tags": []
    }
  ]
}
```

#### Add Tag

```bash
POST /dropbox/2/files/tags/add
Content-Type: application/json

{
  "path": "/document.pdf",
  "tag_text": "important"
}
```

Returns `null` on success.

**Note:** Tag text must match pattern `[\w]+` (alphanumeric and underscores only, no hyphens or spaces).

#### Remove Tag

```bash
POST /dropbox/2/files/tags/remove
Content-Type: application/json

{
  "path": "/document.pdf",
  "tag_text": "important"
}
```

Returns `null` on success.

### Batch Operations

#### Delete Batch

```bash
POST /dropbox/2/files/delete_batch
Content-Type: application/json

{
  "entries": [
    {"path": "/file1.pdf"},
    {"path": "/file2.pdf"}
  ]
}
```

Returns async job ID. Check status with `/files/delete_batch/check`.

#### Copy Batch

```bash
POST /dropbox/2/files/copy_batch_v2
Content-Type: application/json

{
  "entries": [
    {"from_path": "/source/file1.pdf", "to_path": "/dest/file1.pdf"},
    {"from_path": "/source/file2.pdf", "to_path": "/dest/file2.pdf"}
  ],
  "autorename": false
}
```

#### Move Batch

```bash
POST /dropbox/2/files/move_batch_v2
Content-Type: application/json

{
  "entries": [
    {"from_path": "/old/file1.pdf", "to_path": "/new/file1.pdf"},
    {"from_path": "/old/file2.pdf", "to_path": "/new/file2.pdf"}
  ],
  "autorename": false
}
```

## Pagination

Dropbox uses cursor-based pagination. When `has_more` is true, use the `/continue` endpoint with the returned cursor.

```python
import os
import requests

headers = {
    'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
    'Content-Type': 'application/json'
}

# Initial request
response = requests.post(
    'https://gateway.maton.ai/dropbox/2/files/list_folder',
    headers=headers,
    json={'path': '', 'limit': 100}
)
result = response.json()
all_entries = result['entries']

# Continue while has_more is True
while result.get('has_more'):
    response = requests.post(
        'https://gateway.maton.ai/dropbox/2/files/list_folder/continue',
        headers=headers,
        json={'cursor': result['cursor']}
    )
    result = response.json()
    all_entries.extend(result['entries'])

print(f"Total entries: {len(all_entries)}")
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/dropbox/2/files/list_folder',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ path: '' })
  }
);
const data = await response.json();
console.log(data.entries);
```

### Python

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/dropbox/2/files/list_folder',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={'path': ''}
)
data = response.json()
print(data['entries'])
```

### Python (Create Folder and Search)

```python
import os
import requests

headers = {
    'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
    'Content-Type': 'application/json'
}

# Create folder
response = requests.post(
    'https://gateway.maton.ai/dropbox/2/files/create_folder_v2',
    headers=headers,
    json={'path': '/My New Folder', 'autorename': False}
)
folder = response.json()
print(f"Created folder: {folder['metadata']['path_display']}")

# Search for files
response = requests.post(
    'https://gateway.maton.ai/dropbox/2/files/search_v2',
    headers=headers,
    json={'query': 'document'}
)
results = response.json()
print(f"Found {len(results['matches'])} matches")
```

## Notes

- All Dropbox API v2 endpoints use HTTP POST method
- Request bodies are JSON (not form-urlencoded)
- Use empty string `""` for the root folder path
- Paths are case-insensitive but case-preserving
- File IDs (e.g., `id:Awe3Av8A8YYAAAAAAAAABQ`) persist even when files are moved or renamed
- Tag text must match pattern `[\w]+` (alphanumeric and underscores only)
- Temporary download links expire after 4 hours
- Rate limits are generous and per-user
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Dropbox connection or bad request |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 409 | Conflict (path doesn't exist, already exists, etc.) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Dropbox API |

Error responses include details:
```json
{
  "error_summary": "path/not_found/...",
  "error": {
    ".tag": "path",
    "path": {
      ".tag": "not_found"
    }
  }
}
```

### Troubleshooting: Invalid API Key

**When you receive an "Invalid API key" error, ALWAYS follow these steps before concluding there is an issue:**

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

## Resources

- [Dropbox HTTP API Overview](https://www.dropbox.com/developers/documentation/http/overview)
- [Dropbox Developer Portal](https://www.dropbox.com/developers)
- [Dropbox API Explorer](https://dropbox.github.io/dropbox-api-v2-explorer/)
- [DBX File Access Guide](https://developers.dropbox.com/dbx-file-access-guide)
