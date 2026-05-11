---
name: microsoft-excel
description: |
  Microsoft Excel API integration with managed OAuth. Read and write Excel workbooks, worksheets, ranges, tables, and charts stored in OneDrive.
  Use this skill when users want to read or modify Excel spreadsheets, manage worksheet data, work with tables, or access cell values.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
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

# Microsoft Excel

Access the Microsoft Excel API (via Microsoft Graph) with managed OAuth authentication. Read and write workbooks, worksheets, ranges, tables, and charts stored in OneDrive or SharePoint.

## Quick Start

```bash
# List worksheets in a workbook
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/microsoft-excel/{native-api-path}
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

Manage your Microsoft Excel OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=microsoft-excel&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'microsoft-excel'}).encode()
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
    "connection_id": "4751ac89-3970-47e1-872c-eacdf4291732",
    "status": "ACTIVE",
    "creation_time": "2026-02-07T00:43:18.565932Z",
    "last_updated_time": "2026-02-07T00:43:29.729782Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "microsoft-excel",
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

If you have multiple Microsoft Excel connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/microsoft-excel/v1.0/me/drive')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '4751ac89-3970-47e1-872c-eacdf4291732')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## Workbook Access Patterns

You can access workbooks using either ID-based or path-based patterns:

**By File ID:**
```
/microsoft-excel/v1.0/me/drive/items/{file-id}/workbook/...
```

**By File Path:**
```
/microsoft-excel/v1.0/me/drive/root:/{path-to-file}:/workbook/...
```

## API Reference

### Drive Operations

#### Get Drive Info

```bash
GET /microsoft-excel/v1.0/me/drive
```

#### List Root Files

```bash
GET /microsoft-excel/v1.0/me/drive/root/children
```

#### Search for Excel Files

```bash
GET /microsoft-excel/v1.0/me/drive/root/search(q='.xlsx')
```

#### Upload Excel File

```bash
PUT /microsoft-excel/v1.0/me/drive/root:/{filename}.xlsx:/content
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

{binary xlsx content}
```

### Session Management

Sessions improve performance for multiple operations. Recommended for batch operations.

#### Create Session

```bash
POST /microsoft-excel/v1.0/me/drive/root:/{path}:/workbook/createSession
Content-Type: application/json

{
  "persistChanges": true
}
```

**Response:**
```json
{
  "persistChanges": true,
  "id": "cluster=PUS7&session=..."
}
```

Use the session ID in subsequent requests:
```
workbook-session-id: {session-id}
```

#### Close Session

```bash
POST /microsoft-excel/v1.0/me/drive/root:/{path}:/workbook/closeSession
workbook-session-id: {session-id}
```

### Worksheet Operations

#### List Worksheets

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets
```

**Response:**
```json
{
  "value": [
    {
      "id": "{00000000-0001-0000-0000-000000000000}",
      "name": "Sheet1",
      "position": 0,
      "visibility": "Visible"
    }
  ]
}
```

#### Get Worksheet

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')
```

#### Create Worksheet

```bash
POST /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets
Content-Type: application/json

{
  "name": "NewSheet"
}
```

#### Update Worksheet

```bash
PATCH /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')
Content-Type: application/json

{
  "name": "RenamedSheet",
  "position": 2
}
```

#### Delete Worksheet

```bash
DELETE /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('{worksheet-id}')
```

Returns 204 No Content on success.

### Range Operations

#### Get Range

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')/range(address='A1:B2')
```

**Response:**
```json
{
  "address": "Sheet1!A1:B2",
  "values": [
    ["Hello", "World"],
    [1, 2]
  ],
  "formulas": [
    ["Hello", "World"],
    [1, 2]
  ],
  "text": [
    ["Hello", "World"],
    ["1", "2"]
  ],
  "numberFormat": [
    ["General", "General"],
    ["General", "General"]
  ],
  "rowCount": 2,
  "columnCount": 2
}
```

#### Get Used Range

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')/usedRange
```

#### Update Range

```bash
PATCH /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')/range(address='A1:B2')
Content-Type: application/json

{
  "values": [
    ["Updated", "Values"],
    [100, 200]
  ]
}
```

#### Clear Range

```bash
POST /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')/range(address='A1:B2')/clear
Content-Type: application/json

{
  "applyTo": "All"
}
```

Options: `All`, `Formats`, `Contents`

### Table Operations

#### List Tables

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')/tables
```

#### Create Table from Range

```bash
POST /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')/tables/add
Content-Type: application/json

{
  "address": "A1:C4",
  "hasHeaders": true
}
```

**Response:**
```json
{
  "id": "{6D182180-5F5F-448B-9E9C-377A5251CFC5}",
  "name": "Table1",
  "showHeaders": true,
  "showTotals": false,
  "style": "TableStyleMedium2"
}
```

#### Get Table

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/tables('Table1')
```

#### Update Table

```bash
PATCH /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/tables('Table1')
Content-Type: application/json

{
  "name": "PeopleTable",
  "showTotals": true
}
```

#### Get Table Rows

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/tables('Table1')/rows
```

**Response:**
```json
{
  "value": [
    {
      "index": 0,
      "values": [["Alice", 30, "NYC"]]
    },
    {
      "index": 1,
      "values": [["Bob", 25, "LA"]]
    }
  ]
}
```

#### Add Table Row

```bash
POST /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/tables('Table1')/rows
Content-Type: application/json

{
  "values": [["Carol", 35, "Chicago"]]
}
```

#### Delete Table Row

```bash
DELETE /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/tables('Table1')/rows/itemAt(index=0)
```

Returns 204 No Content on success.

#### Get Table Columns

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/tables('Table1')/columns
```

#### Add Table Column

```bash
POST /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/tables('Table1')/columns
Content-Type: application/json

{
  "values": [["Email"], ["alice@example.com"], ["bob@example.com"]]
}
```

### Named Items

#### List Named Items

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/names
```

### Charts

#### List Charts

```bash
GET /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')/charts
```

#### Add Chart

```bash
POST /microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets('Sheet1')/charts/add
Content-Type: application/json

{
  "type": "ColumnClustered",
  "sourceData": "A1:C4",
  "seriesBy": "Auto"
}
```

## Code Examples

### JavaScript

```javascript
// Get range values
const response = await fetch(
  "https://gateway.maton.ai/microsoft-excel/v1.0/me/drive/root:/data.xlsx:/workbook/worksheets('Sheet1')/range(address='A1:B10')",
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.values);
```

### Python

```python
import os
import requests

# Update range values
response = requests.patch(
    "https://gateway.maton.ai/microsoft-excel/v1.0/me/drive/root:/data.xlsx:/workbook/worksheets('Sheet1')/range(address='A1:B2')",
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={'values': [['Name', 'Age'], ['Alice', 30]]}
)
print(response.json())
```

## Notes

- Only `.xlsx` files are supported (not legacy `.xls`)
- Worksheet names with special characters need URL encoding
- Table and worksheet IDs containing `{` and `}` must be URL-encoded (`%7B` and `%7D`)
- Sessions expire after ~5 minutes of inactivity (persistent) or ~7 minutes (non-persistent)
- Use `null` in value arrays to skip updating specific cells
- Blank cells should use `""` (empty string)
- Range addresses use A1 notation (e.g., `A1:C10`, `Sheet1!A1:B5`)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain parentheses to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Microsoft Excel connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 404 | Item not found or session expired |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Microsoft Graph API |

### Common Error Codes

| Code | Description |
|------|-------------|
| `ItemNotFound` | File or resource doesn't exist |
| `ItemAlreadyExists` | Worksheet or table with that name already exists |
| `InvalidArgument` | Invalid parameter or missing required field |
| `SessionNotFound` | Session expired or doesn't exist |

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

1. Ensure your URL path starts with `microsoft-excel`. For example:

- Correct: `https://gateway.maton.ai/microsoft-excel/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets`
- Incorrect: `https://gateway.maton.ai/v1.0/me/drive/root:/workbook.xlsx:/workbook/worksheets`

## Resources

- [Microsoft Graph Excel API Overview](https://learn.microsoft.com/en-us/graph/api/resources/excel)
- [Working with Excel in Microsoft Graph](https://learn.microsoft.com/en-us/graph/excel-concept-overview)
- [Excel Workbook Resource](https://learn.microsoft.com/en-us/graph/api/resources/workbook)
- [Excel Worksheet Resource](https://learn.microsoft.com/en-us/graph/api/resources/worksheet)
- [Excel Range Resource](https://learn.microsoft.com/en-us/graph/api/resources/range)
- [Excel Table Resource](https://learn.microsoft.com/en-us/graph/api/resources/table)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
