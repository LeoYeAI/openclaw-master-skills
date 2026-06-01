---
name: baserow
description: |
  Baserow API integration with managed API key authentication. Manage database rows, fields, and tables.
  Use this skill when users want to read, create, update, or delete Baserow database rows, or query data with filters.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji:
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Baserow

Access the Baserow API with managed API key authentication. Manage database rows with full CRUD operations, filtering, sorting, and batch operations.

## Quick Start

```bash
# List rows from a table
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/baserow/api/database/rows/table/{table_id}/?user_field_names=true')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/baserow/{native-api-path}
```

Replace `{native-api-path}` with the actual Baserow API endpoint path. The gateway proxies requests to `api.baserow.io` and automatically injects your API token.

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

Manage your Baserow API key connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=baserow&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'baserow'}).encode()
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
    "connection_id": "90a5d047-b856-4577-ac05-faccaabf8989",
    "status": "ACTIVE",
    "creation_time": "2026-03-02T12:01:29.812801Z",
    "last_updated_time": "2026-03-02T12:02:17.932675Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "baserow",
    "metadata": {},
    "method": "API_KEY"
  }
}
```

Open the returned `url` in a browser to enter your Baserow database token.

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

If you have multiple Baserow connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/baserow/api/database/rows/table/123/')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '90a5d047-b856-4577-ac05-faccaabf8989')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Rows

#### List Rows

```bash
GET /baserow/api/database/rows/table/{table_id}/
```

Query parameters:
- `user_field_names=true` - Use human-readable field names instead of `field_123` IDs
- `size` - Number of rows per page (default: 100)
- `page` - Page number (1-indexed)
- `order_by` - Field name to sort by (prefix with `-` for descending)
- `filter__{field}__{operator}` - Filter rows (see Filtering section)
- `search` - Search query across all fields
- `include` - Comma-separated field names to include
- `exclude` - Comma-separated field names to exclude

**Response:**
```json
{
  "count": 5,
  "next": "http://api.baserow.io/api/database/rows/table/123/?page=2&size=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order": "1.00000000000000000000",
      "Assignee Name": "Alice Johnson",
      "Email": "alice.johnson@example.com",
      "Tasks": []
    }
  ]
}
```

#### Get Row

```bash
GET /baserow/api/database/rows/table/{table_id}/{row_id}/
```

**Response:**
```json
{
  "id": 1,
  "order": "1.00000000000000000000",
  "field_7456198": "Alice Johnson",
  "field_7456201": "alice.johnson@example.com",
  "field_7456215": []
}
```

#### Create Row

```bash
POST /baserow/api/database/rows/table/{table_id}/
Content-Type: application/json

{
  "field_7456198": "New User",
  "field_7456201": "newuser@example.com"
}
```

Or with user field names:

```bash
POST /baserow/api/database/rows/table/{table_id}/?user_field_names=true
Content-Type: application/json

{
  "Assignee Name": "New User",
  "Email": "newuser@example.com"
}
```

**Response:**
```json
{
  "id": 6,
  "order": "6.00000000000000000000",
  "field_7456198": "New User",
  "field_7456201": "newuser@example.com",
  "field_7456215": []
}
```

#### Update Row

```bash
PATCH /baserow/api/database/rows/table/{table_id}/{row_id}/
Content-Type: application/json

{
  "field_7456198": "Updated Name"
}
```

**Response:**
```json
{
  "id": 1,
  "order": "1.00000000000000000000",
  "field_7456198": "Updated Name",
  "field_7456201": "alice.johnson@example.com",
  "field_7456215": []
}
```

#### Delete Row

```bash
DELETE /baserow/api/database/rows/table/{table_id}/{row_id}/
```

Returns HTTP 204 No Content on success.

---

### Batch Operations

#### Batch Create Rows

```bash
POST /baserow/api/database/rows/table/{table_id}/batch/
Content-Type: application/json

{
  "items": [
    {"field_7456198": "User 1", "field_7456201": "user1@example.com"},
    {"field_7456198": "User 2", "field_7456201": "user2@example.com"}
  ]
}
```

**Response:**
```json
{
  "items": [
    {"id": 7, "order": "7.00000000000000000000", "field_7456198": "User 1", ...},
    {"id": 8, "order": "8.00000000000000000000", "field_7456198": "User 2", ...}
  ]
}
```

#### Batch Update Rows

```bash
PATCH /baserow/api/database/rows/table/{table_id}/batch/
Content-Type: application/json

{
  "items": [
    {"id": 7, "field_7456198": "Updated User 1"},
    {"id": 8, "field_7456198": "Updated User 2"}
  ]
}
```

**Response:**
```json
{
  "items": [
    {"id": 7, "order": "7.00000000000000000000", "field_7456198": "Updated User 1", ...},
    {"id": 8, "order": "8.00000000000000000000", "field_7456198": "Updated User 2", ...}
  ]
}
```

#### Batch Delete Rows

```bash
POST /baserow/api/database/rows/table/{table_id}/batch-delete/
Content-Type: application/json

{
  "items": [7, 8]
}
```

Returns HTTP 204 No Content on success.

---

### Fields

#### List Fields

```bash
GET /baserow/api/database/fields/table/{table_id}/
```

**Response:**
```json
[
  {
    "id": 7456198,
    "table_id": 863922,
    "name": "Assignee Name",
    "order": 0,
    "type": "text",
    "primary": true,
    "read_only": false,
    "description": null
  },
  {
    "id": 7456201,
    "table_id": 863922,
    "name": "Email",
    "order": 1,
    "type": "text",
    "primary": false
  }
]
```

---

### Tables

#### List All Tables

Get all tables across all databases accessible by your token.

```bash
GET /baserow/api/database/tables/all-tables/
```

**Response:**
```json
[
  {
    "id": 863922,
    "name": "Assignees",
    "order": 0,
    "database_id": 419329
  },
  {
    "id": 863923,
    "name": "Tasks",
    "order": 1,
    "database_id": 419329
  }
]
```

---

### Move Row

Reposition a row within a table.

```bash
PATCH /baserow/api/database/rows/table/{table_id}/{row_id}/move/
```

Query parameters:
- `before_id` - Row ID to move before (if omitted, moves to end)

**Example - Move row to before row 3:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request(
    'https://gateway.maton.ai/baserow/api/database/rows/table/863922/5/move/?before_id=3',
    method='PATCH'
)
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "id": 5,
  "order": "2.50000000000000000000",
  "field_7456198": "Moved User",
  "field_7456201": "moved@example.com"
}
```

---

### File Uploads

#### Upload File via URL

Upload a file from a publicly accessible URL.

```bash
POST /baserow/api/user-files/upload-via-url/
Content-Type: application/json

{
  "url": "https://example.com/image.png"
}
```

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'url': 'https://httpbin.org/image/png'}).encode()
req = urllib.request.Request(
    'https://gateway.maton.ai/baserow/api/user-files/upload-via-url/',
    data=data,
    method='POST'
)
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "url": "https://files.baserow.io/user_files/...",
  "thumbnails": {
    "tiny": {"url": "...", "width": 21, "height": 21},
    "small": {"url": "...", "width": 48, "height": 48},
    "card_cover": {"url": "...", "width": 300, "height": 160}
  },
  "visible_name": "image.png",
  "name": "abc123_image.png",
  "size": 8090,
  "mime_type": "image/png",
  "is_image": true,
  "image_width": 100,
  "image_height": 100,
  "uploaded_at": "2026-03-02T12:00:00Z"
}
```

#### Upload File (Multipart)

Upload a file directly using multipart form data.

```bash
POST /baserow/api/user-files/upload-file/
Content-Type: multipart/form-data
```

**Example:**
```bash
curl -X POST "https://gateway.maton.ai/baserow/api/user-files/upload-file/" \
  -H "Authorization: Bearer $MATON_API_KEY" \
  -F "file=@/path/to/file.pdf"
```

**Response:** Same format as upload-via-url.

#### Using Uploaded Files in Rows

After uploading, use the file object in a file field:

```bash
POST /baserow/api/database/rows/table/{table_id}/?user_field_names=true
Content-Type: application/json

{
  "Attachment": [{"name": "abc123_image.png"}]
}
```

---

## Filtering

Use filter parameters to query rows:

```
filter__{field}__{operator}={value}
```

With `user_field_names=true`:
```bash
GET /baserow/api/database/rows/table/{table_id}/?user_field_names=true&filter__Assignee+Name__contains=Alice
```

Multiple filters use AND logic by default. Use `filter_type=OR` to change to OR logic.

### Filter Operators

#### Text Filters
| Operator | Description |
|----------|-------------|
| `equal` | Exact match |
| `not_equal` | Not equal |
| `contains` | Contains substring |
| `contains_not` | Does not contain substring |
| `contains_word` | Contains whole word |
| `doesnt_contain_word` | Does not contain whole word |
| `length_is_lower_than` | Text length is less than value |

#### Numeric Filters
| Operator | Description |
|----------|-------------|
| `higher_than` | Greater than |
| `higher_than_or_equal` | Greater than or equal |
| `lower_than` | Less than |
| `lower_than_or_equal` | Less than or equal |
| `is_even_and_whole` | Value is even and whole number |

#### Date Filters
| Operator | Description |
|----------|-------------|
| `date_is` | Date equals (use with timezone) |
| `date_is_not` | Date does not equal |
| `date_is_before` | Date is before |
| `date_is_on_or_before` | Date is on or before |
| `date_is_after` | Date is after |
| `date_is_on_or_after` | Date is on or after |
| `date_is_within` | Date is within period |
| `date_equal` | Date equals (legacy) |
| `date_not_equal` | Date does not equal (legacy) |
| `date_equals_today` | Date is today |
| `date_before_today` | Date is before today |
| `date_after_today` | Date is after today |
| `date_within_days` | Date within X days |
| `date_within_weeks` | Date within X weeks |
| `date_within_months` | Date within X months |
| `date_equals_days_ago` | Date equals X days ago |
| `date_equals_weeks_ago` | Date equals X weeks ago |
| `date_equals_months_ago` | Date equals X months ago |
| `date_equals_years_ago` | Date equals X years ago |
| `date_equals_day_of_month` | Date equals specific day of month |
| `date_before_or_equal` | Date is before or equal (legacy) |
| `date_after_or_equal` | Date is after or equal (legacy) |

#### Boolean Filters
| Operator | Description |
|----------|-------------|
| `boolean` | Boolean equals (true/false) |

#### Link Row Filters
| Operator | Description |
|----------|-------------|
| `link_row_has` | Has linked row with ID |
| `link_row_has_not` | Does not have linked row with ID |
| `link_row_contains` | Linked row contains text |
| `link_row_not_contains` | Linked row does not contain text |

#### Single Select Filters
| Operator | Description |
|----------|-------------|
| `single_select_equal` | Single select equals option ID |
| `single_select_not_equal` | Single select does not equal option ID |
| `single_select_is_any_of` | Single select is any of option IDs |
| `single_select_is_none_of` | Single select is none of option IDs |

#### Multiple Select Filters
| Operator | Description |
|----------|-------------|
| `multiple_select_has` | Has option selected |
| `multiple_select_has_not` | Does not have option selected |
| `multiple_select_is_exactly` | Exactly these options selected |

#### Collaborator Filters
| Operator | Description |
|----------|-------------|
| `multiple_collaborators_has` | Has collaborator |
| `multiple_collaborators_has_not` | Does not have collaborator |

#### File Filters
| Operator | Description |
|----------|-------------|
| `filename_contains` | File name contains |
| `has_file_type` | Has file of type (image, document) |
| `files_lower_than` | Number of files less than |

#### Empty/Not Empty Filters
| Operator | Description |
|----------|-------------|
| `empty` | Field is empty (value: `true`) |
| `not_empty` | Field is not empty (value: `true`) |

#### User Filters
| Operator | Description |
|----------|-------------|
| `user_is` | User field equals user ID |
| `user_is_not` | User field does not equal user ID |

### Filter Examples

**Text contains:**
```bash
GET /baserow/api/database/rows/table/{table_id}/?user_field_names=true&filter__Name__contains=John
```

**Date within last 7 days:**
```bash
GET /baserow/api/database/rows/table/{table_id}/?user_field_names=true&filter__Created__date_within_days=7
```

**Multiple filters (AND):**
```bash
GET /baserow/api/database/rows/table/{table_id}/?user_field_names=true&filter__Status__single_select_equal=1&filter__Priority__higher_than=3
```

**Multiple filters (OR):**
```bash
GET /baserow/api/database/rows/table/{table_id}/?user_field_names=true&filter_type=OR&filter__Status__equal=Active&filter__Status__equal=Pending
```

## Sorting

Use `order_by` parameter:

```bash
# Sort ascending by field name
GET /baserow/api/database/rows/table/{table_id}/?user_field_names=true&order_by=Assignee+Name

# Sort descending (prefix with -)
GET /baserow/api/database/rows/table/{table_id}/?user_field_names=true&order_by=-Assignee+Name
```

## Pagination

Use `size` and `page` parameters:

```bash
GET /baserow/api/database/rows/table/{table_id}/?size=25&page=2
```

Response includes `next` and `previous` URLs:

```json
{
  "count": 100,
  "next": "http://api.baserow.io/api/database/rows/table/123/?page=3&size=25",
  "previous": "http://api.baserow.io/api/database/rows/table/123/?page=1&size=25",
  "results": [...]
}
```

## Code Examples

### JavaScript

```javascript
// List rows with user field names
const response = await fetch(
  'https://gateway.maton.ai/baserow/api/database/rows/table/863922/?user_field_names=true',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.results);
```

### Python

```python
import os
import requests

# Create a row
response = requests.post(
    'https://gateway.maton.ai/baserow/api/database/rows/table/863922/?user_field_names=true',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'Assignee Name': 'New User',
        'Email': 'newuser@example.com'
    }
)
row = response.json()
print(f"Created row ID: {row['id']}")
```

## Notes

- Connection uses API_KEY authentication (database token), not OAuth
- By default, fields are returned as `field_{id}` format; use `user_field_names=true` for human-readable names
- Row IDs are integers (not strings like Airtable's `recXXX` format)
- Table IDs can be found in the Baserow UI URL or API documentation
- Database tokens grant access only to database row endpoints, not admin endpoints
- Cloud version has a limit of 10 concurrent API requests

## Error Handling

| Status | Name | Description |
|--------|------|-------------|
| 200 | Ok | Request completed successfully |
| 204 | No Content | Success (for DELETE operations) |
| 400 | Bad Request | The request contains invalid values or the JSON could not be parsed |
| 401 | Unauthorized | Invalid or missing database token |
| 404 | Not Found | Row or table not found |
| 413 | Request Entity Too Large | The request exceeded the maximum allowed payload size |
| 429 | Too Many Requests | Rate limited (10 concurrent requests on cloud) |
| 500 | Internal Server Error | The server encountered an unexpected condition |
| 502 | Bad Gateway | Baserow is restarting or an unexpected outage is in progress |
| 503 | Service Unavailable | The server could not process your request in time |

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

Ensure your URL path starts with `baserow`. For example:

- Correct: `https://gateway.maton.ai/baserow/api/database/rows/table/{table_id}/`
- Incorrect: `https://gateway.maton.ai/api/database/rows/table/{table_id}/`

## Resources

- [Baserow API Documentation](https://baserow.io/api-docs)
- [Baserow Database API](https://baserow.io/user-docs/database-api)
- [Baserow API Spec (OpenAPI)](https://api.baserow.io/api/redoc/)
- [Database Tokens](https://baserow.io/user-docs/personal-api-tokens)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
