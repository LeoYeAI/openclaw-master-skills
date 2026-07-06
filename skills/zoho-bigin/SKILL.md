---
name: zoho-bigin
description: |
  Zoho Bigin API integration with managed OAuth. Manage contacts, companies, pipelines, and products in Bigin CRM.
  Use this skill when users want to read, create, update, or delete CRM records, search contacts, or manage sales pipelines.
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

# Zoho Bigin

Access the Zoho Bigin API with managed OAuth authentication. Manage contacts, companies, pipelines, and products with full CRUD operations.

## Quick Start

```bash
# List contacts
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts?fields=First_Name,Last_Name,Email')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-bigin/bigin/v2/{endpoint}
```

The gateway proxies requests to `www.zohoapis.com/bigin/v2` and automatically injects your OAuth token.

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

Manage your Zoho Bigin OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-bigin&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-bigin'}).encode()
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
    "app": "zoho-bigin",
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

If you have multiple Zoho Bigin connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts?fields=First_Name,Last_Name,Email')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Modules

Zoho Bigin organizes data into modules. Available modules include:

| Module | API Name | Description |
|--------|----------|-------------|
| Contacts | `Contacts` | Individual people |
| Companies | `Accounts` | Organizations/businesses |
| Pipelines | `Pipelines` | Sales opportunities/deals |
| Products | `Products` | Items you sell |
| Tasks | `Tasks` | To-do items (requires additional OAuth scope) |
| Events | `Events` | Calendar appointments (requires additional OAuth scope) |
| Calls | `Calls` | Phone call logs (requires additional OAuth scope) |
| Notes | `Notes` | Notes attached to records (requires additional OAuth scope) |

### List Records

```bash
GET /zoho-bigin/bigin/v2/{module_api_name}?fields={field1},{field2}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `fields` | string | **Required.** Comma-separated field API names to retrieve |
| `sort_order` | string | `asc` or `desc` |
| `sort_by` | string | Field API name to sort by |
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Records per page (default: 200, max: 200) |
| `cvid` | string | Custom view ID for filtered results |

**Example - List Contacts:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts?fields=First_Name,Last_Name,Email,Phone')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "First_Name": "Ted",
      "Email": "support@bigin.com",
      "Last_Name": "Watson",
      "id": "7255024000000596045"
    }
  ],
  "info": {
    "per_page": 200,
    "count": 1,
    "page": 1,
    "more_records": false
  }
}
```

**Example - List Companies (Accounts):**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Accounts?fields=Account_Name,Website')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Record

```bash
GET /zoho-bigin/bigin/v2/{module_api_name}/{record_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts/7255024000000596045')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Records

```bash
POST /zoho-bigin/bigin/v2/{module_api_name}
Content-Type: application/json

{
  "data": [
    {
      "field_api_name": "value"
    }
  ]
}
```

**Mandatory Fields by Module:**

| Module | Required Fields |
|--------|-----------------|
| Contacts | `Last_Name` |
| Accounts | `Account_Name` |
| Pipelines | `Pipeline_Name`, `Stage` |
| Products | `Product_Name` |

**Example - Create Contact:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "data": [{
        "Last_Name": "Smith",
        "First_Name": "John",
        "Email": "john.smith@example.com",
        "Phone": "+1-555-0123"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "code": "SUCCESS",
      "details": {
        "Modified_Time": "2026-02-06T00:28:53-08:00",
        "Modified_By": {
          "name": "User Name",
          "id": "7255024000000590001"
        },
        "Created_Time": "2026-02-06T00:28:53-08:00",
        "id": "7255024000000605002",
        "Created_By": {
          "name": "User Name",
          "id": "7255024000000590001"
        }
      },
      "message": "record added",
      "status": "success"
    }
  ]
}
```

**Example - Create Company (Account):**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "data": [{
        "Account_Name": "Acme Corporation",
        "Website": "https://acme.com"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Accounts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Update Records

```bash
PUT /zoho-bigin/bigin/v2/{module_api_name}
Content-Type: application/json

{
  "data": [
    {
      "id": "record_id",
      "field_api_name": "updated_value"
    }
  ]
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "data": [{
        "id": "7255024000000605002",
        "Phone": "+1-555-9999"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts', data=data, method='PUT')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "code": "SUCCESS",
      "details": {
        "Modified_Time": "2026-02-06T00:29:07-08:00",
        "id": "7255024000000605002"
      },
      "message": "record updated",
      "status": "success"
    }
  ]
}
```

### Delete Records

```bash
DELETE /zoho-bigin/bigin/v2/{module_api_name}?ids={record_id1},{record_id2}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ids` | string | Comma-separated record IDs (required, max 100) |
| `wf_trigger` | boolean | Execute workflows (default: true) |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts?ids=7255024000000605002', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "code": "SUCCESS",
      "details": {
        "id": "7255024000000605002"
      },
      "message": "record deleted",
      "status": "success"
    }
  ]
}
```

### Search Records

```bash
GET /zoho-bigin/bigin/v2/{module_api_name}/search
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `criteria` | string | Search criteria (e.g., `(Last_Name:equals:Smith)`) |
| `email` | string | Search by email address |
| `phone` | string | Search by phone number |
| `word` | string | Global text search |
| `page` | integer | Page number |
| `per_page` | integer | Records per page (max 200) |

**Criteria Format:** `((field_api_name:operator:value)and/or(...))`

**Operators:** `equals`, `starts_with`

**Example - Search by email:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts/search?email=support@bigin.com')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Example - Search by criteria:**

```bash
python <<'EOF'
import urllib.request, os, json
import urllib.parse
criteria = urllib.parse.quote('(Last_Name:equals:Watson)')
req = urllib.request.Request(f'https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts/search?criteria={criteria}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Metadata APIs

#### Get Modules

```bash
GET /zoho-bigin/bigin/v2/settings/modules
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/settings/modules')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Users

```bash
GET /zoho-bigin/bigin/v2/users
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | `AllUsers`, `ActiveUsers`, `AdminUsers`, `CurrentUser` |
| `page` | integer | Page number |
| `per_page` | integer | Users per page (max 200) |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bigin/bigin/v2/users?type=ActiveUsers')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Pagination

Zoho Bigin uses page-based pagination with `page` and `per_page` parameters:

```bash
GET /zoho-bigin/bigin/v2/{module_api_name}?fields=First_Name,Last_Name&page=1&per_page=50
```

Response includes pagination info:

```json
{
  "data": [...],
  "info": {
    "per_page": 50,
    "count": 50,
    "page": 1,
    "more_records": true
  }
}
```

Continue fetching while `more_records` is `true`, incrementing `page` each time.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts?fields=First_Name,Last_Name,Email',
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
    'https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'fields': 'First_Name,Last_Name,Email'}
)
data = response.json()
```

## Notes

- The `fields` parameter is **required** for list operations
- Module API names are case-sensitive (e.g., `Contacts`, not `contacts`)
- Companies are accessed via the `Accounts` module API name
- Sales opportunities are accessed via the `Pipelines` module (not `Deals`)
- Maximum 100 records per create/update request
- Maximum 100 records per delete request
- Maximum 200 records returned per GET request
- Use field API names (not display names) in requests
- Some modules (Tasks, Events, Calls, Notes) require additional OAuth scopes. If you receive a scope error, contact Maton support at support@maton.ai with the specific operations/APIs you need and your use-case
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho Bigin connection, missing required parameter, or invalid request |
| 401 | Invalid or missing Maton API key, or OAuth scope mismatch |
| 404 | Invalid URL pattern or resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho Bigin API |

### Common Error Codes

| Code | Description |
|------|-------------|
| `REQUIRED_PARAM_MISSING` | Required parameter (like `fields`) is missing |
| `INVALID_URL_PATTERN` | Invalid API endpoint path |
| `INVALID_MODULE` | Module does not exist or is not API-supported |
| `OAUTH_SCOPE_MISMATCH` | OAuth token lacks required permissions for the endpoint |
| `NO_PERMISSION` | Insufficient privileges for the operation |
| `MANDATORY_NOT_FOUND` | Required field is missing |
| `INVALID_DATA` | Data type mismatch or format error |
| `DUPLICATE_DATA` | Record violates unique field constraint |

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

1. Ensure your URL path starts with `zoho-bigin`. For example:

- Correct: `https://gateway.maton.ai/zoho-bigin/bigin/v2/Contacts`
- Incorrect: `https://gateway.maton.ai/bigin/v2/Contacts`

## Resources

- [Bigin API Overview](https://www.bigin.com/developer/docs/apis/v2/)
- [Bigin REST API Documentation](https://www.bigin.com/developer/docs/apis/)
- [Modules API](https://www.bigin.com/developer/docs/apis/modules-api.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
