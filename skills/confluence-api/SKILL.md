---
name: confluence
description: |
  Confluence API integration with managed OAuth. Manage pages, spaces, blogposts, comments, and attachments.
  Use this skill when users want to create, read, update, or delete Confluence content, manage spaces, or work with comments and attachments.
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

# Confluence

Access the Confluence Cloud API with managed OAuth authentication. Manage pages, spaces, blogposts, comments, attachments, and properties.

## Quick Start

```bash
# List pages in your Confluence site
python3 <<'EOF'
import urllib.request, os, json

# First get your Cloud ID
req = urllib.request.Request('https://gateway.maton.ai/confluence/oauth/token/accessible-resources')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
resources = json.load(urllib.request.urlopen(req))
cloud_id = resources[0]['id']

# Then list pages
req = urllib.request.Request(f'https://gateway.maton.ai/confluence/ex/confluence/{cloud_id}/wiki/api/v2/pages')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/confluence/{atlassian-api-path}
```

Confluence Cloud uses two URL patterns:

**V2 API (recommended):**
```
https://gateway.maton.ai/confluence/ex/confluence/{cloudId}/wiki/api/v2/{resource}
```

**V1 REST API (limited):**
```
https://gateway.maton.ai/confluence/ex/confluence/{cloudId}/wiki/rest/api/{resource}
```

The `{cloudId}` is required for all API calls. Obtain it via the accessible-resources endpoint (see below).

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

Manage your Confluence OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=confluence&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'confluence'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python3 <<'EOF'
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
    "connection_id": "6cb7787f-7c32-4658-a3c3-4ddf1367a4ce",
    "status": "ACTIVE",
    "creation_time": "2026-02-13T00:00:00.000000Z",
    "last_updated_time": "2026-02-13T00:00:00.000000Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "confluence",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Confluence connections, specify which one to use with the `Maton-Connection` header:

```bash
python3 <<'EOF'
import urllib.request, os, json
cloud_id = "YOUR_CLOUD_ID"
req = urllib.request.Request(f'https://gateway.maton.ai/confluence/ex/confluence/{cloud_id}/wiki/api/v2/pages')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '6cb7787f-7c32-4658-a3c3-4ddf1367a4ce')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## Getting Your Cloud ID

Before making API calls, you must obtain your Confluence Cloud ID:

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/confluence/oauth/token/accessible-resources')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
resources = json.load(urllib.request.urlopen(req))
print(json.dumps(resources, indent=2))
# Use resources[0]['id'] as your cloudId
EOF
```

**Response:**
```json
[
  {
    "id": "62909843-b784-4c35-b770-e4e2a26f024b",
    "name": "your-site-name",
    "url": "https://your-site.atlassian.net",
    "scopes": ["read:confluence-content.all", "write:confluence-content", ...],
    "avatarUrl": "https://..."
  }
]
```

## API Reference

All V2 API endpoints use the base path:
```
/confluence/ex/confluence/{cloudId}/wiki/api/v2
```

### Pages

#### List Pages

```bash
GET /pages
GET /pages?space-id={spaceId}
GET /pages?limit=25
GET /pages?status=current
GET /pages?body-format=storage
```

**Response:**
```json
{
  "results": [
    {
      "id": "98391",
      "status": "current",
      "title": "My Page",
      "spaceId": "98306",
      "parentId": "98305",
      "parentType": "page",
      "authorId": "557058:...",
      "createdAt": "2026-02-12T23:00:00.000Z",
      "version": {
        "number": 1,
        "authorId": "557058:...",
        "createdAt": "2026-02-12T23:00:00.000Z"
      },
      "_links": {
        "webui": "/spaces/SPACEKEY/pages/98391/My+Page"
      }
    }
  ],
  "_links": {
    "next": "/wiki/api/v2/pages?cursor=..."
  }
}
```

#### Get Page

```bash
GET /pages/{pageId}
GET /pages/{pageId}?body-format=storage
GET /pages/{pageId}?body-format=atlas_doc_format
GET /pages/{pageId}?body-format=view
```

**Body formats:**
- `storage` - Confluence storage format (XML-like)
- `atlas_doc_format` - Atlassian Document Format (JSON)
- `view` - Rendered HTML

#### Create Page

```bash
POST /pages
Content-Type: application/json

{
  "spaceId": "98306",
  "status": "current",
  "title": "New Page Title",
  "body": {
    "representation": "storage",
    "value": "<p>Page content in storage format</p>"
  }
}
```

To create a child page, include `parentId`:

```json
{
  "spaceId": "98306",
  "parentId": "98391",
  "status": "current",
  "title": "Child Page",
  "body": {
    "representation": "storage",
    "value": "<p>Child page content</p>"
  }
}
```

**Response:**
```json
{
  "id": "98642",
  "status": "current",
  "title": "New Page Title",
  "spaceId": "98306",
  "version": {
    "number": 1
  }
}
```

#### Update Page

```bash
PUT /pages/{pageId}
Content-Type: application/json

{
  "id": "98391",
  "status": "current",
  "title": "Updated Page Title",
  "body": {
    "representation": "storage",
    "value": "<p>Updated content</p>"
  },
  "version": {
    "number": 2,
    "message": "Updated via API"
  }
}
```

**Note:** You must increment the version number with each update.

#### Delete Page

```bash
DELETE /pages/{pageId}
```

Returns `204 No Content` on success.

#### Get Page Children

```bash
GET /pages/{pageId}/children
```

#### Get Page Versions

```bash
GET /pages/{pageId}/versions
```

#### Get Page Labels

```bash
GET /pages/{pageId}/labels
```

#### Get Page Attachments

```bash
GET /pages/{pageId}/attachments
```

#### Get Page Comments

```bash
GET /pages/{pageId}/footer-comments
```

#### Get Page Properties

```bash
GET /pages/{pageId}/properties
GET /pages/{pageId}/properties/{propertyId}
```

#### Create Page Property

```bash
POST /pages/{pageId}/properties
Content-Type: application/json

{
  "key": "my-property-key",
  "value": {"customKey": "customValue"}
}
```

#### Update Page Property

```bash
PUT /pages/{pageId}/properties/{propertyId}
Content-Type: application/json

{
  "key": "my-property-key",
  "value": {"customKey": "updatedValue"},
  "version": {"number": 2}
}
```

#### Delete Page Property

```bash
DELETE /pages/{pageId}/properties/{propertyId}
```

### Spaces

#### List Spaces

```bash
GET /spaces
GET /spaces?limit=25
GET /spaces?type=global
```

**Response:**
```json
{
  "results": [
    {
      "id": "98306",
      "key": "SPACEKEY",
      "name": "Space Name",
      "type": "global",
      "status": "current",
      "authorId": "557058:...",
      "createdAt": "2026-02-12T23:00:00.000Z",
      "homepageId": "98305",
      "_links": {
        "webui": "/spaces/SPACEKEY"
      }
    }
  ]
}
```

#### Get Space

```bash
GET /spaces/{spaceId}
```

#### Get Space Pages

```bash
GET /spaces/{spaceId}/pages
```

#### Get Space Blogposts

```bash
GET /spaces/{spaceId}/blogposts
```

#### Get Space Properties

```bash
GET /spaces/{spaceId}/properties
```

#### Create Space Property

```bash
POST /spaces/{spaceId}/properties
Content-Type: application/json

{
  "key": "space-property-key",
  "value": {"key": "value"}
}
```

#### Get Space Permissions

```bash
GET /spaces/{spaceId}/permissions
```

#### Get Space Labels

```bash
GET /spaces/{spaceId}/labels
```

### Blogposts

#### List Blogposts

```bash
GET /blogposts
GET /blogposts?space-id={spaceId}
GET /blogposts?limit=25
```

#### Get Blogpost

```bash
GET /blogposts/{blogpostId}
GET /blogposts/{blogpostId}?body-format=storage
```

#### Create Blogpost

```bash
POST /blogposts
Content-Type: application/json

{
  "spaceId": "98306",
  "title": "My Blog Post",
  "body": {
    "representation": "storage",
    "value": "<p>Blog post content</p>"
  }
}
```

#### Update Blogpost

```bash
PUT /blogposts/{blogpostId}
Content-Type: application/json

{
  "id": "458753",
  "status": "current",
  "title": "Updated Blog Post",
  "body": {
    "representation": "storage",
    "value": "<p>Updated content</p>"
  },
  "version": {
    "number": 2
  }
}
```

#### Delete Blogpost

```bash
DELETE /blogposts/{blogpostId}
```

#### Get Blogpost Labels

```bash
GET /blogposts/{blogpostId}/labels
```

#### Get Blogpost Versions

```bash
GET /blogposts/{blogpostId}/versions
```

#### Get Blogpost Comments

```bash
GET /blogposts/{blogpostId}/footer-comments
```

### Comments

#### List Footer Comments

```bash
GET /footer-comments
GET /footer-comments?body-format=storage
```

#### Get Comment

```bash
GET /footer-comments/{commentId}
```

#### Create Footer Comment

```bash
POST /footer-comments
Content-Type: application/json

{
  "pageId": "98391",
  "body": {
    "representation": "storage",
    "value": "<p>Comment text</p>"
  }
}
```

For blogpost comments:
```json
{
  "blogpostId": "458753",
  "body": {
    "representation": "storage",
    "value": "<p>Comment on blogpost</p>"
  }
}
```

#### Update Comment

```bash
PUT /footer-comments/{commentId}
Content-Type: application/json

{
  "version": {"number": 2},
  "body": {
    "representation": "storage",
    "value": "<p>Updated comment</p>"
  }
}
```

#### Delete Comment

```bash
DELETE /footer-comments/{commentId}
```

#### Get Comment Replies

```bash
GET /footer-comments/{commentId}/children
```

#### List Inline Comments

```bash
GET /inline-comments
```

### Attachments

#### List Attachments

```bash
GET /attachments
GET /attachments?limit=25
```

#### Get Attachment

```bash
GET /attachments/{attachmentId}
```

#### Get Page Attachments

```bash
GET /pages/{pageId}/attachments
```

### Tasks

#### List Tasks

```bash
GET /tasks
```

#### Get Task

```bash
GET /tasks/{taskId}
```

### Labels

#### List Labels

```bash
GET /labels
GET /labels?prefix=global
```

### Custom Content

#### List Custom Content

```bash
GET /custom-content
GET /custom-content?type={customContentType}
```

### User (V1 API)

The current user endpoint uses the V1 REST API:

```bash
GET /confluence/ex/confluence/{cloudId}/wiki/rest/api/user/current
```

**Response:**
```json
{
  "type": "known",
  "accountId": "557058:...",
  "accountType": "atlassian",
  "email": "user@example.com",
  "publicName": "User Name",
  "displayName": "User Name"
}
```

## Pagination

The V2 API uses cursor-based pagination. Responses include a `_links.next` URL when more results are available.

```bash
GET /pages?limit=25
```

**Response:**
```json
{
  "results": [...],
  "_links": {
    "next": "/wiki/api/v2/pages?cursor=eyJpZCI6Ijk4MzkyIn0"
  }
}
```

To get the next page, extract the cursor and pass it:

```bash
GET /pages?limit=25&cursor=eyJpZCI6Ijk4MzkyIn0
```

## Code Examples

### JavaScript

```javascript
// Get Cloud ID first
const resourcesRes = await fetch(
  'https://gateway.maton.ai/confluence/oauth/token/accessible-resources',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const resources = await resourcesRes.json();
const cloudId = resources[0].id;

// List pages
const response = await fetch(
  `https://gateway.maton.ai/confluence/ex/confluence/${cloudId}/wiki/api/v2/pages`,
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

# Get Cloud ID first
resources = requests.get(
    'https://gateway.maton.ai/confluence/oauth/token/accessible-resources',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
).json()
cloud_id = resources[0]['id']

# List pages
response = requests.get(
    f'https://gateway.maton.ai/confluence/ex/confluence/{cloud_id}/wiki/api/v2/pages',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- **Cloud ID Required**: You must obtain your Cloud ID via `/oauth/token/accessible-resources` before making API calls
- **V2 API Recommended**: Use the V2 API (`/wiki/api/v2/`) for most operations. The V1 API (`/wiki/rest/api/`) is limited
- **Body Formats**: Use `storage` format for creating/updating content. Use `view` for rendered HTML
- **Version Numbers**: When updating pages or blogposts, you must increment the version number
- **Storage Format**: Content uses Confluence storage format (XML-like). Example: `<p>Paragraph</p>`, `<h1>Heading</h1>`
- **Delete Returns 204**: DELETE operations return 204 No Content with no response body
- **IDs are Strings**: Page, space, and other IDs should be passed as strings
- **IMPORTANT**: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or malformed data |
| 401 | Invalid API key or insufficient OAuth scopes |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict (e.g., duplicate title) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Confluence API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

Ensure your URL path starts with `confluence`. For example:

- Correct: `https://gateway.maton.ai/confluence/ex/confluence/{cloudId}/wiki/api/v2/pages`
- Incorrect: `https://gateway.maton.ai/ex/confluence/{cloudId}/wiki/api/v2/pages`

### Troubleshooting: Scope Issues

If you receive a 401 error with "scope does not match", you may need to re-authorize with the required scopes. Delete your connection and create a new one:

```bash
# Delete existing connection
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF

# Create new connection
python3 <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'confluence'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Resources

- [Confluence REST API V2 Documentation](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/)
- [Confluence REST API V2 Reference](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/)
- [Confluence Storage Format](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
