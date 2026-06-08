---
name: one-note
description: |
  OneNote API integration with managed OAuth via Microsoft Graph. Access notebooks, sections, section groups, and pages.
  Use this skill when users want to create or manage OneNote notebooks, organize notes, or work with page content.
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

# OneNote

Access the OneNote API via Microsoft Graph with managed OAuth authentication. Create and manage notebooks, sections, section groups, and pages for note-taking and organization.

## Quick Start

```bash
# List notebooks
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/one-note/v1.0/me/onenote/{resource}
```

The gateway proxies requests to Microsoft Graph (`graph.microsoft.com`) and automatically injects your OAuth token.

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

Manage your OneNote OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=one-note&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'one-note'}).encode()
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
    "connection_id": "1447c2f4-3e5f-4ece-93df-67bc7e7a2857",
    "status": "ACTIVE",
    "creation_time": "2026-03-12T10:24:32.321168Z",
    "last_updated_time": "2026-03-12T10:24:49.890969Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "one-note",
    "metadata": {},
    "method": "OAUTH2"
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization with Microsoft.

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

If you have multiple OneNote connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '1447c2f4-3e5f-4ece-93df-67bc7e7a2857')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Notebooks

Manage OneNote notebooks.

#### List Notebooks

```bash
GET /one-note/v1.0/me/onenote/notebooks
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "value": [
    {
      "id": "1-30487038-8c2e-440a-860d-e82c6dc74f10",
      "displayName": "My Notebook",
      "createdDateTime": "2026-03-12T10:25:00Z",
      "lastModifiedDateTime": "2026-03-12T10:30:00Z",
      "isDefault": true,
      "isShared": false,
      "sectionsUrl": "https://graph.microsoft.com/v1.0/me/onenote/notebooks/.../sections",
      "sectionGroupsUrl": "https://graph.microsoft.com/v1.0/me/onenote/notebooks/.../sectionGroups"
    }
  ]
}
```

#### List Notebooks with Sections

Use `$expand` to include sections and section groups:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks?$expand=sections,sectionGroups')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get a Notebook

```bash
GET /one-note/v1.0/me/onenote/notebooks/{notebook_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks/{notebook_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create a Notebook

```bash
POST /one-note/v1.0/me/onenote/notebooks
Content-Type: application/json

{
  "displayName": "New Notebook"
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'displayName': 'My New Notebook'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Copy a Notebook

```bash
POST /one-note/v1.0/me/onenote/notebooks/{notebook_id}/copyNotebook
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'renameAs': 'Copied Notebook'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks/{notebook_id}/copyNotebook', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

> **Note:** Copy operations are asynchronous. The response includes a status URL to check progress.

#### Get Recent Notebooks

```bash
GET /one-note/v1.0/me/onenote/notebooks/getRecentNotebooks(includePersonalNotebooks=true)
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks/getRecentNotebooks(includePersonalNotebooks=true)')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Sections

Manage sections within notebooks.

#### List All Sections

```bash
GET /one-note/v1.0/me/onenote/sections
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/sections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "value": [
    {
      "id": "1-c9d63289-4f64-4579-9043-155543978c78",
      "displayName": "My Section",
      "createdDateTime": "2026-03-12T10:26:00Z",
      "lastModifiedDateTime": "2026-03-12T10:28:00Z",
      "isDefault": false,
      "pagesUrl": "https://graph.microsoft.com/v1.0/me/onenote/sections/.../pages"
    }
  ]
}
```

#### List Sections in a Notebook

```bash
GET /one-note/v1.0/me/onenote/notebooks/{notebook_id}/sections
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks/{notebook_id}/sections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get a Section

```bash
GET /one-note/v1.0/me/onenote/sections/{section_id}
```

#### Create a Section

```bash
POST /one-note/v1.0/me/onenote/notebooks/{notebook_id}/sections
Content-Type: application/json

{
  "displayName": "New Section"
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'displayName': 'Meeting Notes'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks/{notebook_id}/sections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Section Groups

Organize sections into groups.

#### List All Section Groups

```bash
GET /one-note/v1.0/me/onenote/sectionGroups
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/sectionGroups')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### List Section Groups in a Notebook

```bash
GET /one-note/v1.0/me/onenote/notebooks/{notebook_id}/sectionGroups
```

#### Get a Section Group

```bash
GET /one-note/v1.0/me/onenote/sectionGroups/{section_group_id}
```

#### Create a Section Group

```bash
POST /one-note/v1.0/me/onenote/notebooks/{notebook_id}/sectionGroups
Content-Type: application/json

{
  "displayName": "New Section Group"
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'displayName': 'Project Notes'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks/{notebook_id}/sectionGroups', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Pages

Create and manage pages with rich content.

#### List All Pages

```bash
GET /one-note/v1.0/me/onenote/pages
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/pages')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "value": [
    {
      "id": "1-42a904024c734393b561d0a85428965d!251-c9d63289-4f64-4579-9043-155543978c78",
      "title": "My Page",
      "createdDateTime": "2026-03-12T10:29:42Z",
      "lastModifiedDateTime": "2026-03-12T10:30:00Z",
      "contentUrl": "https://graph.microsoft.com/v1.0/me/onenote/pages/.../content"
    }
  ]
}
```

#### List Pages in a Section

```bash
GET /one-note/v1.0/me/onenote/sections/{section_id}/pages
```

#### Get a Page

```bash
GET /one-note/v1.0/me/onenote/pages/{page_id}
```

#### Get Page Content

Returns the HTML content of a page:

```bash
GET /one-note/v1.0/me/onenote/pages/{page_id}/content
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/pages/{page_id}/content')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
resp = urllib.request.urlopen(req)
print(resp.read().decode())
EOF
```

#### Create a Page

Pages are created with HTML content:

```bash
POST /one-note/v1.0/me/onenote/sections/{section_id}/pages
Content-Type: text/html

<!DOCTYPE html>
<html>
  <head>
    <title>Page Title</title>
  </head>
  <body>
    <p>Page content here</p>
  </body>
</html>
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
html = """<!DOCTYPE html>
<html>
  <head>
    <title>Meeting Notes - March 12</title>
  </head>
  <body>
    <h1>Meeting Notes</h1>
    <p>Attendees: Alice, Bob, Charlie</p>
    <ul>
      <li>Discussed Q1 goals</li>
      <li>Reviewed project timeline</li>
    </ul>
  </body>
</html>""".encode()
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/sections/{section_id}/pages', data=html, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'text/html')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update Page Content

Use PATCH to append, insert, or replace content:

```bash
PATCH /one-note/v1.0/me/onenote/pages/{page_id}/content
Content-Type: application/json

[
  {
    "target": "body",
    "action": "append",
    "content": "<p>New paragraph added!</p>"
  }
]
```

**Actions:**
- `append` - Add content at the end of target
- `prepend` - Add content at the beginning of target
- `replace` - Replace target content
- `insert` - Insert after target

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps([
    {
        "target": "body",
        "action": "append",
        "content": "<p>Updated at 2026-03-12</p>"
    }
]).encode()
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/pages/{page_id}/content', data=data, method='PATCH')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
resp = urllib.request.urlopen(req)
print(f"Updated: {resp.status}")
EOF
```

## OData Query Parameters

The OneNote API supports OData query parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `$select` | Select specific properties | `$select=id,displayName` |
| `$expand` | Include related resources | `$expand=sections,sectionGroups` |
| `$filter` | Filter results | `$filter=isDefault eq true` |
| `$orderby` | Sort results | `$orderby=displayName` |
| `$top` | Limit results | `$top=10` |
| `$skip` | Skip results | `$skip=20` |

**Example with $select:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks?$select=id,displayName')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Page HTML Format

OneNote pages use a specific HTML format:

### Basic Structure

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Page Title</title>
    <meta name="created" content="2026-03-12T10:00:00Z" />
  </head>
  <body>
    <p>Content here</p>
  </body>
</html>
```

### Supported Elements

- Headings: `<h1>` through `<h6>`
- Paragraphs: `<p>`
- Lists: `<ul>`, `<ol>`, `<li>`
- Tables: `<table>`, `<tr>`, `<td>`
- Images: `<img src="..." />`
- Links: `<a href="...">`
- Formatting: `<b>`, `<i>`, `<u>`, `<strike>`

### Adding Images

```html
<img src="https://example.com/image.jpg" alt="Description" />
```

Or embed base64 images:

```html
<img src="data:image/png;base64,..." alt="Embedded image" />
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.value);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
notebooks = response.json()
print(notebooks['value'])
```

### Create Page with Python

```python
import os
import requests

html_content = """<!DOCTYPE html>
<html>
  <head><title>New Page</title></head>
  <body><p>Hello from Python!</p></body>
</html>"""

response = requests.post(
    f'https://gateway.maton.ai/one-note/v1.0/me/onenote/sections/{section_id}/pages',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'text/html'
    },
    data=html_content
)
page = response.json()
print(f"Created page: {page['title']}")
```

## Notes

- OneNote uses Microsoft Graph API v1.0
- Pages are created with HTML content (Content-Type: text/html)
- Page updates use PATCH with JSON array of operations
- Copy operations are asynchronous - check the returned status URL
- Use `$expand=sections,sectionGroups` to get notebook contents in one call
- Notebook and section names must be unique within their container
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or missing OneNote connection |
| 401 | Invalid or missing Maton API key |
| 403 | Forbidden - insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict - duplicate name |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Microsoft Graph |

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

1. Ensure your URL path starts with `one-note`. For example:

- Correct: `https://gateway.maton.ai/one-note/v1.0/me/onenote/notebooks`
- Incorrect: `https://gateway.maton.ai/v1.0/me/onenote/notebooks`

## Resources

- [OneNote API Overview](https://learn.microsoft.com/en-us/graph/integrate-with-onenote)
- [OneNote REST API Reference](https://learn.microsoft.com/en-us/graph/api/resources/onenote-api-overview)
- [Page HTML Reference](https://learn.microsoft.com/en-us/graph/onenote-input-output-html)
- [Microsoft Graph Explorer](https://developer.microsoft.com/graph/graph-explorer)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
