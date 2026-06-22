---
name: zoho-recruit
description: |
  Zoho Recruit API integration with managed OAuth. Manage candidates, job openings, interviews, and recruitment workflows.
  Use this skill when users want to read, create, update, or search recruitment data like candidates, job openings, interviews, and applications in Zoho Recruit.
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

# Zoho Recruit

Access the Zoho Recruit API with managed OAuth authentication. Manage candidates, job openings, interviews, applications, and recruitment workflows with full CRUD operations.

## Quick Start

```bash
# List all candidates
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates?per_page=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-recruit/{native-api-path}
```

Replace `{native-api-path}` with the actual Zoho Recruit API endpoint path. The gateway proxies requests to `recruit.zoho.com` and automatically injects your OAuth token.

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

Manage your Zoho Recruit OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-recruit&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-recruit'}).encode()
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
    "connection_id": "0c9fa9b1-80b6-4caa-afc2-8629fe4d9661",
    "status": "ACTIVE",
    "creation_time": "2026-02-06T07:48:59.474215Z",
    "last_updated_time": "2026-02-06T07:57:52.950167Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "zoho-recruit",
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

If you have multiple Zoho Recruit connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '0c9fa9b1-80b6-4caa-afc2-8629fe4d9661')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Modules

#### List All Modules

Get a list of all available modules in your Zoho Recruit account.

```bash
GET /zoho-recruit/recruit/v2/settings/modules
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/settings/modules')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Candidates

#### List Candidates

```bash
GET /zoho-recruit/recruit/v2/Candidates
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fields` | string | - | Comma-separated field API names |
| `sort_order` | string | - | `asc` or `desc` |
| `sort_by` | string | - | Field API name to sort by |
| `converted` | string | - | `true`, `false`, or `both` |
| `approved` | string | - | `true`, `false`, or `both` |
| `page` | integer | 1 | Page number |
| `per_page` | integer | 200 | Records per page (max 200) |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates?per_page=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "id": "846336000000552208",
      "First_Name": "Christina",
      "Last_Name": "Palaskas",
      "Email": "c.palaskas@example.com",
      "Candidate_Status": "Converted - Employee",
      "Current_Employer": "Chandlers",
      "Current_Job_Title": "Technical Consultant",
      "Experience_in_Years": 3,
      "Skill_Set": "Communication, Presentation, Customer service",
      "Candidate_Owner": {
        "name": "Byungkyu Park",
        "id": "846336000000549541"
      }
    }
  ],
  "info": {
    "per_page": 10,
    "count": 1,
    "page": 1,
    "more_records": false
  }
}
```

#### Get Candidate by ID

```bash
GET /zoho-recruit/recruit/v2/Candidates/{record_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates/846336000000552208')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Search Candidates

```bash
GET /zoho-recruit/recruit/v2/Candidates/search?criteria={criteria}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `criteria` | string | Search criteria (e.g., `(Last_Name:contains:Smith)`) |
| `email` | string | Search by email |
| `phone` | string | Search by phone |
| `word` | string | Global word search |
| `page` | integer | Page number |
| `per_page` | integer | Records per page |

**Search Operators:**
- Text: `equals`, `not_equal`, `starts_with`, `ends_with`, `contains`, `not_contains`, `in`
- Date/Number: `equals`, `not_equal`, `greater_than`, `less_than`, `greater_equal`, `less_equal`, `between`

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
import urllib.parse
criteria = urllib.parse.quote('(Candidate_Status:equals:Active)')
req = urllib.request.Request(f'https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates/search?criteria={criteria}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Candidate

```bash
POST /zoho-recruit/recruit/v2/Candidates
Content-Type: application/json

{
  "data": [
    {
      "First_Name": "John",
      "Last_Name": "Doe",
      "Email": "john.doe@example.com",
      "Phone": "555-123-4567",
      "Current_Job_Title": "Software Engineer"
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
        "First_Name": "John",
        "Last_Name": "Doe",
        "Email": "john.doe@example.com",
        "Phone": "555-123-4567"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates', data=data, method='POST')
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
      "status": "success",
      "message": "record added",
      "details": {
        "id": "846336000000600001",
        "Created_Time": "2026-02-06T10:00:00-08:00",
        "Created_By": {
          "name": "User Name",
          "id": "846336000000549541"
        }
      }
    }
  ]
}
```

#### Update Candidate

```bash
PUT /zoho-recruit/recruit/v2/Candidates/{record_id}
Content-Type: application/json

{
  "data": [
    {
      "Current_Job_Title": "Senior Software Engineer"
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
        "Current_Job_Title": "Senior Software Engineer"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates/846336000000552208', data=data, method='PUT')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Delete Candidates

```bash
DELETE /zoho-recruit/recruit/v2/Candidates?ids={record_id1},{record_id2}
```

### Job Openings

#### List Job Openings

```bash
GET /zoho-recruit/recruit/v2/Job_Openings
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Job_Openings?per_page=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "id": "846336000000552093",
      "Posting_Title": "Senior Accountant (Sample)",
      "Job_Opening_Status": "Waiting for approval",
      "Date_Opened": "2026-01-21",
      "Target_Date": "2026-02-20",
      "Industry": "Accounting",
      "City": "Tallahassee",
      "No_of_Candidates_Hired": 0,
      "No_of_Candidates_Associated": 0
    }
  ],
  "info": {
    "per_page": 10,
    "count": 1,
    "page": 1,
    "more_records": false
  }
}
```

#### Get Job Opening by ID

```bash
GET /zoho-recruit/recruit/v2/Job_Openings/{record_id}
```

#### Create Job Opening

```bash
POST /zoho-recruit/recruit/v2/Job_Openings
Content-Type: application/json

{
  "data": [
    {
      "Posting_Title": "Software Engineer",
      "Job_Opening_Status": "In-progress",
      "Date_Opened": "2026-02-01",
      "Target_Date": "2026-03-01"
    }
  ]
}
```

#### Update Job Opening

```bash
PUT /zoho-recruit/recruit/v2/Job_Openings/{record_id}
Content-Type: application/json
```

#### Delete Job Openings

```bash
DELETE /zoho-recruit/recruit/v2/Job_Openings?ids={record_id1},{record_id2}
```

### Interviews

#### List Interviews

```bash
GET /zoho-recruit/recruit/v2/Interviews
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Interviews?per_page=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Interview by ID

```bash
GET /zoho-recruit/recruit/v2/Interviews/{record_id}
```

#### Create Interview

```bash
POST /zoho-recruit/recruit/v2/Interviews
Content-Type: application/json

{
  "data": [
    {
      "Interview_Name": "Technical Interview",
      "Candidate_Name": {"id": "846336000000552208"},
      "Posting_Title": {"id": "846336000000552093"},
      "Start_DateTime": "2026-02-10T10:00:00-08:00",
      "End_DateTime": "2026-02-10T11:00:00-08:00"
    }
  ]
}
```

### Departments

#### List Departments

```bash
GET /zoho-recruit/recruit/v2/Departments
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-recruit/recruit/v2/Departments?per_page=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Applications

#### List Applications

```bash
GET /zoho-recruit/recruit/v2/Applications
```

### Generic Record Operations

All modules support the same CRUD operations:

```bash
# List records
GET /zoho-recruit/recruit/v2/{module_api_name}

# Get record by ID
GET /zoho-recruit/recruit/v2/{module_api_name}/{record_id}

# Create records
POST /zoho-recruit/recruit/v2/{module_api_name}

# Update records
PUT /zoho-recruit/recruit/v2/{module_api_name}/{record_id}

# Delete records
DELETE /zoho-recruit/recruit/v2/{module_api_name}?ids={id1},{id2}

# Search records
GET /zoho-recruit/recruit/v2/{module_api_name}/search?criteria={criteria}
```

## Available Modules

| Module | API Name | Description |
|--------|----------|-------------|
| Candidates | `Candidates` | Job candidates |
| Job Openings | `Job_Openings` | Open positions |
| Applications | `Applications` | Job applications |
| Interviews | `Interviews` | Scheduled interviews |
| Departments | `Departments` | Company departments |
| Clients | `Clients` | Client companies |
| Contacts | `Contacts` | Contact persons |
| Campaigns | `Campaigns` | Recruitment campaigns |
| Referrals | `Referrals` | Employee referrals |
| Tasks | `Tasks` | To-do items |
| Events | `Events` | Calendar events |
| Vendors | `Vendors` | External vendors |

## Pagination

Zoho Recruit uses page-based pagination:

```bash
GET /zoho-recruit/recruit/v2/{module_api_name}?page=1&per_page=200
```

- `page`: Page number (default: 1)
- `per_page`: Records per page (default: 200, max: 200)

Response includes pagination info:
```json
{
  "data": [...],
  "info": {
    "per_page": 200,
    "count": 50,
    "page": 1,
    "more_records": false
  }
}
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates?per_page=10',
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
    'https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'per_page': 10}
)
data = response.json()
```

## Notes

- Record IDs are numeric strings (e.g., `846336000000552208`)
- Maximum 200 records per GET request
- Maximum 100 records per POST/PUT request
- Maximum 100 records per DELETE request
- Module API names are case-sensitive (e.g., `Job_Openings`, not `job_openings`)
- `Last_Name` is mandatory for Candidates
- Date format: `yyyy-MM-dd`
- DateTime format: `yyyy-MM-ddTHH:mm:ss±HH:mm` (ISO 8601)
- Lookup fields use JSON objects with `id` and optionally `name`
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain special characters
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho Recruit connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho Recruit API |

### Common Error Codes

| Code | Description |
|------|-------------|
| INVALID_DATA | Invalid field value |
| MANDATORY_NOT_FOUND | Required field missing |
| DUPLICATE_DATA | Duplicate record detected |
| INVALID_MODULE | Invalid module API name |
| NO_PERMISSION | Insufficient permissions |

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

1. Ensure your URL path starts with `zoho-recruit`. For example:

- Correct: `https://gateway.maton.ai/zoho-recruit/recruit/v2/Candidates`
- Incorrect: `https://gateway.maton.ai/recruit/v2/Candidates`

## Resources

- [Zoho Recruit API v2 Overview](https://www.zoho.com/recruit/developer-guide/apiv2/)
- [Get Records API](https://www.zoho.com/recruit/developer-guide/apiv2/get-records.html)
- [Insert Records API](https://www.zoho.com/recruit/developer-guide/apiv2/insert-records.html)
- [Update Records API](https://www.zoho.com/recruit/developer-guide/apiv2/update-records.html)
- [Delete Records API](https://www.zoho.com/recruit/developer-guide/apiv2/delete-records.html)
- [Search Records API](https://www.zoho.com/recruit/developer-guide/apiv2/search-records.html)
- [Modules API](https://www.zoho.com/recruit/developer-guide/apiv2/modules-api.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
