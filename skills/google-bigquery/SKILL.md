---
name: google-bigquery
description: |
  Google BigQuery API integration with managed OAuth. Run SQL queries, manage datasets and tables, and analyze data at scale.
  Use this skill when users want to query BigQuery data, create or manage datasets/tables, run analytics jobs, or work with BigQuery resources.
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

# Google BigQuery

Access the Google BigQuery API with managed OAuth authentication. Run SQL queries, manage datasets and tables, and analyze data at scale.

## Quick Start

```bash
# Run a simple query
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'query': 'SELECT 1 as test_value', 'useLegacySql': False}).encode()
req = urllib.request.Request('https://gateway.maton.ai/google-bigquery/bigquery/v2/projects/{projectId}/queries', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/google-bigquery/bigquery/v2/{resource-path}
```

Replace `{resource-path}` with the actual BigQuery API endpoint path. The gateway proxies requests to `bigquery.googleapis.com` and automatically injects your OAuth token.

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

Manage your Google BigQuery OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=google-bigquery&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'google-bigquery'}).encode()
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
    "connection_id": "c8463a31-e5b4-4e52-9a32-e78dcd7ba7b1",
    "status": "ACTIVE",
    "creation_time": "2026-02-14T09:02:02.780520Z",
    "last_updated_time": "2026-02-14T09:02:19.977436Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "google-bigquery",
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

If you have multiple Google BigQuery connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-bigquery/bigquery/v2/projects')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'c8463a31-e5b4-4e52-9a32-e78dcd7ba7b1')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Projects

#### List Projects

List all projects accessible to the authenticated user.

```bash
GET /google-bigquery/bigquery/v2/projects
```

**Response:**
```json
{
  "kind": "bigquery#projectList",
  "projects": [
    {
      "id": "my-project-123",
      "numericId": "822245862053",
      "projectReference": {
        "projectId": "my-project-123"
      },
      "friendlyName": "My Project"
    }
  ],
  "totalItems": 1
}
```

### Datasets

#### List Datasets

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/datasets
```

**Query Parameters:**
- `maxResults` - Maximum number of results to return
- `pageToken` - Token for pagination
- `all` - Include hidden datasets if true

#### Get Dataset

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}
```

#### Create Dataset

```bash
POST /google-bigquery/bigquery/v2/projects/{projectId}/datasets
Content-Type: application/json

{
  "datasetReference": {
    "datasetId": "my_dataset",
    "projectId": "{projectId}"
  },
  "description": "My dataset description",
  "location": "US"
}
```

**Response:**
```json
{
  "kind": "bigquery#dataset",
  "id": "my-project:my_dataset",
  "datasetReference": {
    "datasetId": "my_dataset",
    "projectId": "my-project"
  },
  "location": "US",
  "creationTime": "1771059780773"
}
```

#### Update Dataset (PATCH)

```bash
PATCH /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}
Content-Type: application/json

{
  "description": "Updated description"
}
```

#### Delete Dataset

```bash
DELETE /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}
```

**Query Parameters:**
- `deleteContents` - If true, delete all tables in the dataset (default: false)

### Tables

#### List Tables

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}/tables
```

**Query Parameters:**
- `maxResults` - Maximum number of results to return
- `pageToken` - Token for pagination

#### Get Table

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}/tables/{tableId}
```

#### Create Table

```bash
POST /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}/tables
Content-Type: application/json

{
  "tableReference": {
    "projectId": "{projectId}",
    "datasetId": "{datasetId}",
    "tableId": "my_table"
  },
  "schema": {
    "fields": [
      {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
      {"name": "name", "type": "STRING", "mode": "NULLABLE"},
      {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
    ]
  }
}
```

**Response:**
```json
{
  "kind": "bigquery#table",
  "id": "my-project:my_dataset.my_table",
  "tableReference": {
    "projectId": "my-project",
    "datasetId": "my_dataset",
    "tableId": "my_table"
  },
  "schema": {
    "fields": [
      {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
      {"name": "name", "type": "STRING", "mode": "NULLABLE"},
      {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
    ]
  },
  "numRows": "0",
  "type": "TABLE"
}
```

#### Update Table (PATCH)

```bash
PATCH /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}/tables/{tableId}
Content-Type: application/json

{
  "description": "Updated table description"
}
```

#### Delete Table

```bash
DELETE /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}/tables/{tableId}
```

### Table Data

#### List Table Data

Retrieve rows from a table.

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}/tables/{tableId}/data
```

**Query Parameters:**
- `maxResults` - Maximum number of results to return
- `pageToken` - Token for pagination
- `startIndex` - Zero-based index of the starting row

**Response:**
```json
{
  "kind": "bigquery#tableDataList",
  "totalRows": "100",
  "rows": [
    {
      "f": [
        {"v": "1"},
        {"v": "Alice"},
        {"v": "1.7710597807E9"}
      ]
    }
  ],
  "pageToken": "..."
}
```

#### Insert Table Data (Streaming)

Insert rows into a table using streaming insert. Note: Requires BigQuery paid tier.

```bash
POST /google-bigquery/bigquery/v2/projects/{projectId}/datasets/{datasetId}/tables/{tableId}/insertAll
Content-Type: application/json

{
  "rows": [
    {"json": {"id": 1, "name": "Alice"}},
    {"json": {"id": 2, "name": "Bob"}}
  ]
}
```

### Jobs and Queries

#### Run Query (Synchronous)

Execute a SQL query and return results directly.

```bash
POST /google-bigquery/bigquery/v2/projects/{projectId}/queries
Content-Type: application/json

{
  "query": "SELECT * FROM `my_dataset.my_table` LIMIT 10",
  "useLegacySql": false,
  "maxResults": 100
}
```

**Response:**
```json
{
  "kind": "bigquery#queryResponse",
  "schema": {
    "fields": [
      {"name": "id", "type": "INTEGER"},
      {"name": "name", "type": "STRING"}
    ]
  },
  "jobReference": {
    "projectId": "my-project",
    "jobId": "job_abc123",
    "location": "US"
  },
  "totalRows": "2",
  "rows": [
    {"f": [{"v": "1"}, {"v": "Alice"}]},
    {"f": [{"v": "2"}, {"v": "Bob"}]}
  ],
  "jobComplete": true,
  "totalBytesProcessed": "1024"
}
```

**Query Parameters:**
- `useLegacySql` - Use legacy SQL syntax (default: false for GoogleSQL)
- `maxResults` - Maximum results per page
- `timeoutMs` - Query timeout in milliseconds

#### Create Job (Asynchronous)

Submit a job for asynchronous execution.

```bash
POST /google-bigquery/bigquery/v2/projects/{projectId}/jobs
Content-Type: application/json

{
  "configuration": {
    "query": {
      "query": "SELECT * FROM `my_dataset.my_table`",
      "useLegacySql": false,
      "destinationTable": {
        "projectId": "{projectId}",
        "datasetId": "{datasetId}",
        "tableId": "results_table"
      },
      "writeDisposition": "WRITE_TRUNCATE"
    }
  }
}
```

#### List Jobs

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/jobs
```

**Query Parameters:**
- `maxResults` - Maximum number of results to return
- `pageToken` - Token for pagination
- `stateFilter` - Filter by job state: `done`, `pending`, `running`
- `projection` - `full` or `minimal`

**Response:**
```json
{
  "kind": "bigquery#jobList",
  "jobs": [
    {
      "id": "my-project:US.job_abc123",
      "jobReference": {
        "projectId": "my-project",
        "jobId": "job_abc123",
        "location": "US"
      },
      "state": "DONE",
      "statistics": {
        "creationTime": "1771059781456",
        "startTime": "1771059782203",
        "endTime": "1771059782324"
      }
    }
  ]
}
```

#### Get Job

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/jobs/{jobId}
```

**Query Parameters:**
- `location` - Job location (e.g., "US", "EU")

#### Get Query Results

Retrieve results from a completed query job.

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/queries/{jobId}
```

**Query Parameters:**
- `location` - Job location
- `maxResults` - Maximum results per page
- `pageToken` - Token for pagination
- `startIndex` - Zero-based starting row

#### Cancel Job

```bash
POST /google-bigquery/bigquery/v2/projects/{projectId}/jobs/{jobId}/cancel
```

**Query Parameters:**
- `location` - Job location

## Pagination

BigQuery uses token-based pagination. List responses include a `pageToken` when more results exist:

```bash
GET /google-bigquery/bigquery/v2/projects/{projectId}/datasets?maxResults=10&pageToken={token}
```

**Response:**
```json
{
  "datasets": [...],
  "nextPageToken": "eyJvZmZzZXQiOjEwfQ=="
}
```

Use the `nextPageToken` value as `pageToken` in subsequent requests.

## Code Examples

### JavaScript

```javascript
// Run a query
const response = await fetch(
  'https://gateway.maton.ai/google-bigquery/bigquery/v2/projects/my-project/queries',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: 'SELECT * FROM `my_dataset.my_table` LIMIT 10',
      useLegacySql: false
    })
  }
);
const data = await response.json();
console.log(data.rows);
```

### Python

```python
import os
import requests

# Run a query
response = requests.post(
    'https://gateway.maton.ai/google-bigquery/bigquery/v2/projects/my-project/queries',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={
        'query': 'SELECT * FROM `my_dataset.my_table` LIMIT 10',
        'useLegacySql': False
    }
)
data = response.json()
for row in data.get('rows', []):
    print([field['v'] for field in row['f']])
```

## Schema Field Types

Common BigQuery data types for table schemas:

| Type | Description |
|------|-------------|
| `STRING` | Variable-length character data |
| `INTEGER` | 64-bit signed integer |
| `FLOAT` | 64-bit IEEE floating point |
| `BOOLEAN` | True or false |
| `TIMESTAMP` | Absolute point in time |
| `DATE` | Calendar date |
| `TIME` | Time of day |
| `DATETIME` | Date and time |
| `BYTES` | Variable-length binary data |
| `NUMERIC` | Exact numeric value with 38 digits of precision |
| `BIGNUMERIC` | Exact numeric value with 76+ digits of precision |
| `GEOGRAPHY` | Geographic data |
| `JSON` | JSON data |
| `RECORD` | Nested fields (also called STRUCT) |

**Field Modes:**
- `NULLABLE` - Field can be null (default)
- `REQUIRED` - Field cannot be null
- `REPEATED` - Field is an array

## Notes

- Project IDs are typically in the format `project-name` or `project-name-12345`
- Dataset IDs follow naming rules: letters, numbers, underscores (max 1024 characters)
- Table IDs follow same naming rules as datasets
- Job IDs are generated by BigQuery and include location prefix
- Query results use `f` (fields) and `v` (value) structure
- Streaming inserts require BigQuery paid tier (not available in free tier)
- Use `useLegacySql: false` for GoogleSQL (standard SQL) syntax
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Google BigQuery connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 403 | Access denied (insufficient permissions or quota exceeded) |
| 404 | Resource not found (project, dataset, table, or job) |
| 409 | Resource already exists |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from BigQuery API |

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

1. Ensure your URL path starts with `google-bigquery`. For example:

- Correct: `https://gateway.maton.ai/google-bigquery/bigquery/v2/projects`
- Incorrect: `https://gateway.maton.ai/bigquery/v2/projects`

## Resources

- [BigQuery API Overview](https://cloud.google.com/bigquery/docs/reference/rest)
- [Datasets](https://cloud.google.com/bigquery/docs/reference/rest/v2/datasets)
- [Tables](https://cloud.google.com/bigquery/docs/reference/rest/v2/tables)
- [Jobs](https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs)
- [Tabledata](https://cloud.google.com/bigquery/docs/reference/rest/v2/tabledata)
- [Standard SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
