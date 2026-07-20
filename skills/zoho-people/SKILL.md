---
name: zoho-people
description: |
  Zoho People API integration with managed OAuth. Manage employees, departments, designations, attendance, and leave.
  Use this skill when users want to read, create, update, or query HR data like employees, departments, designations, and forms in Zoho People.
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

# Zoho People

Access the Zoho People API with managed OAuth authentication. Manage employees, departments, designations, attendance, leave, and custom HR forms with full CRUD operations.

## Quick Start

```bash
# List all employees
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms/employee/getRecords?sIndex=1&limit=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-people/{native-api-path}
```

Replace `{native-api-path}` with the actual Zoho People API endpoint path. The gateway proxies requests to `people.zoho.com` and automatically injects your OAuth token.

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

Manage your Zoho People OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-people&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-people'}).encode()
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
    "connection_id": "7d11ea2e-c580-43fe-bc56-d9d4765b9bc6",
    "status": "ACTIVE",
    "creation_time": "2026-02-06T07:42:07.681370Z",
    "last_updated_time": "2026-02-06T07:46:12.648445Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "zoho-people",
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

If you have multiple Zoho People connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '7d11ea2e-c580-43fe-bc56-d9d4765b9bc6')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Forms Operations

#### List All Forms

Get a list of all available forms in your Zoho People account.

```bash
GET /zoho-people/people/api/forms
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "result": [
      {
        "componentId": 943596000000035679,
        "iscustom": false,
        "displayName": "Employee",
        "formLinkName": "employee",
        "PermissionDetails": {
          "Add": 3,
          "Edit": 3,
          "View": 3
        },
        "isVisible": true,
        "viewDetails": {
          "view_Id": 943596000000035705,
          "view_Name": "P_EmployeeView"
        }
      }
    ],
    "message": "Data fetched successfully",
    "status": 0
  }
}
```

### Employee Operations

#### List Employees (Bulk Records)

```bash
GET /zoho-people/people/api/forms/employee/getRecords?sIndex={startIndex}&limit={limit}
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sIndex` | integer | 1 | Starting index (1-based) |
| `limit` | integer | 200 | Number of records (max 200) |
| `SearchColumn` | string | - | `EMPLOYEEID` or `EMPLOYEEMAILALIAS` |
| `SearchValue` | string | - | Value to search for |
| `modifiedtime` | long | - | Timestamp in milliseconds for modified records |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms/employee/getRecords?sIndex=1&limit=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "result": [
      {
        "943596000000294355": [
          {
            "FirstName": "Christopher",
            "LastName": "Brown",
            "EmailID": "christopherbrown@zylker.com",
            "EmployeeID": "S20",
            "Department": "Management",
            "Designation": "Administration",
            "Employeestatus": "Active",
            "Gender": "Male",
            "Date_of_birth": "02-Feb-1987",
            "Zoho_ID": 943596000000294355
          }
        ]
      }
    ],
    "message": "Data fetched successfully",
    "status": 0
  }
}
```

#### List Employees (View-based)

```bash
GET /zoho-people/api/forms/{viewName}/records?rec_limit={limit}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-people/api/forms/P_EmployeeView/records?rec_limit=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Search Employee by ID

```bash
GET /zoho-people/people/api/forms/employee/getRecords?SearchColumn=EMPLOYEEID&SearchValue={employeeId}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms/employee/getRecords?SearchColumn=EMPLOYEEID&SearchValue=S20')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Search Employee by Email

```bash
GET /zoho-people/people/api/forms/employee/getRecords?SearchColumn=EMPLOYEEMAILALIAS&SearchValue={email}
```

### Department Operations

#### List Departments

```bash
GET /zoho-people/people/api/forms/department/getRecords?sIndex={startIndex}&limit={limit}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms/department/getRecords?sIndex=1&limit=50')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "result": [
      {
        "943596000000294315": [
          {
            "Department": "IT",
            "Department_Lead": "",
            "Parent_Department": "",
            "Zoho_ID": 943596000000294315
          }
        ]
      }
    ],
    "message": "Data fetched successfully",
    "status": 0
  }
}
```

### Designation Operations

#### List Designations

```bash
GET /zoho-people/people/api/forms/designation/getRecords?sIndex={startIndex}&limit={limit}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms/designation/getRecords?sIndex=1&limit=50')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "result": [
      {
        "943596000000294399": [
          {
            "Designation": "Team Member",
            "EEO_Category": "Professionals",
            "Zoho_ID": 943596000000294399
          }
        ]
      }
    ],
    "message": "Data fetched successfully",
    "status": 0
  }
}
```

### Insert Record

Add a new record to any form.

```bash
POST /zoho-people/people/api/forms/json/{formLinkName}/insertRecord
Content-Type: application/x-www-form-urlencoded

inputData={field1:'value1',field2:'value2'}
```

**Example - Create Department:**

```bash
python <<'EOF'
import urllib.request, os, json
from urllib.parse import urlencode

inputData = json.dumps({"Department": "Engineering"})
data = urlencode({"inputData": inputData}).encode()

req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms/json/department/insertRecord', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "result": {
      "pkId": "943596000000300001",
      "message": "Successfully Added"
    },
    "message": "Data added successfully",
    "status": 0
  }
}
```

### Update Record

Modify an existing record.

```bash
POST /zoho-people/people/api/forms/json/{formLinkName}/updateRecord
Content-Type: application/x-www-form-urlencoded

inputData={field1:'newValue'}&recordId={recordId}
```

**Example - Update Employee:**

```bash
python <<'EOF'
import urllib.request, os, json
from urllib.parse import urlencode

inputData = json.dumps({"Department": "Engineering"})
data = urlencode({
    "inputData": inputData,
    "recordId": "943596000000294355"
}).encode()

req = urllib.request.Request('https://gateway.maton.ai/zoho-people/people/api/forms/json/employee/updateRecord', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Leave Operations

#### List Leave Records

```bash
GET /zoho-people/people/api/forms/leave/getRecords?sIndex={startIndex}&limit={limit}
```

#### Add Leave

```bash
POST /zoho-people/people/api/forms/json/leave/insertRecord
Content-Type: application/x-www-form-urlencoded

inputData={Employee_ID:'EMP001',Leavetype:'123456',From:'01-Feb-2026',To:'02-Feb-2026'}
```

### Attendance Operations

Note: Attendance endpoints require additional OAuth scopes.

#### Get Attendance Entries

```bash
GET /zoho-people/people/api/attendance/getAttendanceEntries?date={date}&dateFormat={format}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `date` | string | Date in organization format |
| `dateFormat` | string | Date format (e.g., `dd-MMM-yyyy`) |
| `empId` | string | Employee ID (optional) |
| `emailId` | string | Employee email (optional) |

#### Check-In/Check-Out

```bash
POST /zoho-people/people/api/attendance
Content-Type: application/x-www-form-urlencoded

dateFormat=dd/MM/yyyy HH:mm:ss&checkIn={datetime}&checkOut={datetime}&empId={empId}
```

## Common Form Link Names

| Form | formLinkName | Description |
|------|--------------|-------------|
| Employee | `employee` | Employee records |
| Department | `department` | Departments |
| Designation | `designation` | Job titles |
| Leave | `leave` | Leave requests |
| Clients | `P_ClientDetails` | Client information |

## Pagination

Zoho People uses index-based pagination:

```bash
GET /zoho-people/people/api/forms/{formLinkName}/getRecords?sIndex=1&limit=200
```

- `sIndex`: Starting index (1-based)
- `limit`: Number of records per request (max 200)

For subsequent pages:
- Page 1: `sIndex=1&limit=200`
- Page 2: `sIndex=201&limit=200`
- Page 3: `sIndex=401&limit=200`

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/zoho-people/people/api/forms/employee/getRecords?sIndex=1&limit=10',
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
    'https://gateway.maton.ai/zoho-people/people/api/forms/employee/getRecords',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'sIndex': 1, 'limit': 10}
)
data = response.json()
```

## Notes

- Record IDs are numeric strings (e.g., `943596000000294355`)
- The `Zoho_ID` field in responses contains the record ID
- Maximum 200 records per GET request
- Insert/Update operations use form-urlencoded data with `inputData` JSON
- Date format varies by field and organization settings
- Some endpoints (attendance, leave) require additional OAuth scopes. If you receive an `INVALID_OAUTHSCOPE` error, contact Maton support at support@maton.ai with the specific operations/APIs you need and your use-case
- Response structure wraps data in `response.result[]` array
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain special characters
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho People connection or invalid request |
| 401 | Invalid or missing Maton API key, or invalid OAuth scope |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho People API |

### Common Error Codes

| Code | Description |
|------|-------------|
| 7011 | Invalid form name |
| 7012 | Invalid view name |
| 7021 | Maximum record limit exceeded (200) |
| 7024 | No records found |
| 7042 | Invalid search value |
| 7218 | Invalid OAuth scope |

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

1. Ensure your URL path starts with `zoho-people`. For example:

- Correct: `https://gateway.maton.ai/zoho-people/people/api/forms`
- Incorrect: `https://gateway.maton.ai/people/api/forms`

## Resources

- [Zoho People API Overview](https://www.zoho.com/people/api/overview.html)
- [Get Bulk Records API](https://www.zoho.com/people/api/bulk-records.html)
- [Fetch Forms API](https://www.zoho.com/people/api/forms-api/fetch-forms.html)
- [Insert Record API](https://www.zoho.com/people/api/insert-records.html)
- [Update Record API](https://www.zoho.com/people/api/update-records.html)
- [Attendance API](https://www.zoho.com/people/api/attendance-entries.html)
- [Leave API](https://www.zoho.com/people/api/add-leave.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
