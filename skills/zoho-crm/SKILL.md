---
name: zoho-crm
description: |
  Zoho CRM API integration with managed OAuth. Manage leads, contacts, accounts, deals, and other CRM records.
  Use this skill when users want to read, create, update, or delete CRM records, search contacts, manage sales pipelines, access organization settings, manage users, or retrieve module metadata in Zoho CRM.
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

# Zoho CRM

Access the Zoho CRM API with managed OAuth authentication. Manage leads, contacts, accounts, deals, and other CRM modules with full CRUD operations including search and bulk operations. Also supports organization details, user management, and module metadata retrieval.

## Quick Start

```bash
# List leads
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Leads?fields=First_Name,Last_Name,Email')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-crm/crm/v8/{endpoint}
```

The gateway proxies requests to `www.zohoapis.com/crm/v8` and automatically injects your OAuth token.

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

Manage your Zoho CRM OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-crm&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-crm'}).encode()
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
    "connection_id": "e55c5bac-241a-4cc8-9db5-50d2cad09136",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "zoho-crm",
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

If you have multiple Zoho CRM connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Leads?fields=First_Name,Last_Name,Email')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'e55c5bac-241a-4cc8-9db5-50d2cad09136')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Modules

Zoho CRM organizes data into modules. Core modules include:

| Module | API Name | Description |
|--------|----------|-------------|
| Leads | `Leads` | Potential customers |
| Contacts | `Contacts` | Individual people |
| Accounts | `Accounts` | Organizations/companies |
| Deals | `Deals` | Sales opportunities |
| Campaigns | `Campaigns` | Marketing campaigns |
| Tasks | `Tasks` | To-do items |
| Calls | `Calls` | Phone call logs |
| Events | `Events` | Calendar appointments |
| Products | `Products` | Items you sell |

### List Records

```bash
GET /zoho-crm/crm/v8/{module_api_name}?fields={field1},{field2}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `fields` | string | **Required.** Comma-separated field API names (max 50) |
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Records per page (default/max: 200) |
| `sort_by` | string | Sort by: `id`, `Created_Time`, or `Modified_Time` |
| `sort_order` | string | `asc` or `desc` (default) |
| `cvid` | long | Custom view ID |
| `page_token` | string | For >2000 records pagination |

**Example - List Leads:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Leads?fields=First_Name,Last_Name,Email,Phone,Company')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "First_Name": "Christopher",
      "Email": "christopher-maclead@noemail.invalid",
      "Last_Name": "Maclead (Sample)",
      "Phone": "555-555-5555",
      "Company": "Rangoni Of Florence",
      "id": "7243485000000597000"
    }
  ],
  "info": {
    "per_page": 200,
    "count": 1,
    "page": 1,
    "sort_by": "id",
    "sort_order": "desc",
    "more_records": false,
    "next_page_token": null
  }
}
```

**Example - List Contacts:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Contacts?fields=First_Name,Last_Name,Email,Phone')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Example - List Accounts:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Accounts?fields=Account_Name,Website,Phone')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Example - List Deals:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Deals?fields=Deal_Name,Stage,Amount')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Record

```bash
GET /zoho-crm/crm/v8/{module_api_name}/{record_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Leads/7243485000000597000')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Records

```bash
POST /zoho-crm/crm/v8/{module_api_name}
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
| Leads | `Last_Name` |
| Contacts | `Last_Name` |
| Accounts | `Account_Name` |
| Deals | `Deal_Name`, `Stage` |
| Tasks | `Subject` |
| Calls | `Subject`, `Call_Type`, `Call_Start_Time`, `Call_Duration` |
| Events | `Event_Title`, `Start_DateTime`, `End_DateTime` |

**Example - Create Lead:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "data": [{
        "Last_Name": "Smith",
        "First_Name": "John",
        "Email": "john.smith@example.com",
        "Company": "Acme Corp",
        "Phone": "+1-555-0123"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Leads', data=data, method='POST')
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
        "Modified_Time": "2026-02-06T01:10:56-08:00",
        "Modified_By": {
          "name": "User Name",
          "id": "7243485000000590001"
        },
        "Created_Time": "2026-02-06T01:10:56-08:00",
        "id": "7243485000000619001",
        "Created_By": {
          "name": "User Name",
          "id": "7243485000000590001"
        }
      },
      "message": "record added",
      "status": "success"
    }
  ]
}
```

**Example - Create Contact:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "data": [{
        "Last_Name": "Doe",
        "First_Name": "Jane",
        "Email": "jane.doe@example.com",
        "Phone": "+1-555-9876"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Contacts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Example - Create Account:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "data": [{
        "Account_Name": "Acme Corporation",
        "Website": "https://acme.com",
        "Phone": "+1-555-1234"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Accounts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Update Records

```bash
PUT /zoho-crm/crm/v8/{module_api_name}
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
        "id": "7243485000000619001",
        "Phone": "+1-555-9999",
        "Company": "Updated Company Name"
    }]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Leads', data=data, method='PUT')
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
        "Modified_Time": "2026-02-06T01:11:01-08:00",
        "Modified_By": {
          "name": "User Name",
          "id": "7243485000000590001"
        },
        "Created_Time": "2026-02-06T01:10:56-08:00",
        "id": "7243485000000619001",
        "Created_By": {
          "name": "User Name",
          "id": "7243485000000590001"
        }
      },
      "message": "record updated",
      "status": "success"
    }
  ]
}
```

### Delete Records

```bash
DELETE /zoho-crm/crm/v8/{module_api_name}?ids={record_id1},{record_id2}
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
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Leads?ids=7243485000000619001', method='DELETE')
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
        "id": "7243485000000619001"
      },
      "message": "record deleted",
      "status": "success"
    }
  ]
}
```

### Search Records

```bash
GET /zoho-crm/crm/v8/{module_api_name}/search
```

**Query Parameters (one required):**

| Parameter | Type | Description |
|-----------|------|-------------|
| `criteria` | string | Search criteria (e.g., `(Last_Name:equals:Smith)`) |
| `email` | string | Search by email address |
| `phone` | string | Search by phone number |
| `word` | string | Global text search |
| `page` | integer | Page number |
| `per_page` | integer | Records per page (max 200) |

**Criteria Format:** `((field_api_name:operator:value) and/or (...))`

**Operators:**
- Text fields: `equals`, `not_equal`, `starts_with`, `in`
- Date/Number fields: `equals`, `not_equal`, `greater_than`, `less_than`, `between`, `in`
- Boolean fields: `equals`, `not_equal`

**Example - Search by email:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/Leads/search?email=christopher-maclead@noemail.invalid')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Example - Search by criteria:**

```bash
python <<'EOF'
import urllib.request, os, json
import urllib.parse
criteria = urllib.parse.quote('(Last_Name:starts_with:Smith)')
req = urllib.request.Request(f'https://gateway.maton.ai/zoho-crm/crm/v8/Leads/search?criteria={criteria}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "First_Name": "Christopher",
      "Email": "christopher-maclead@noemail.invalid",
      "Last_Name": "Maclead (Sample)",
      "id": "7243485000000597000"
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

### Organization Details

Retrieve your Zoho CRM organization details.

```bash
GET /zoho-crm/crm/v8/org
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/org')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "org": [
    {
      "id": "7243485000000020005",
      "company_name": "Acme Corp",
      "domain_name": "org123456789",
      "primary_email": "admin@example.com",
      "phone": "555-555-5555",
      "currency": "US Dollar - USD",
      "currency_symbol": "$",
      "iso_code": "USD",
      "time_zone": "PST",
      "country_code": "US",
      "zgid": "123456789",
      "type": "production",
      "mc_status": false,
      "license_details": {
        "paid": true,
        "paid_type": "enterprise",
        "users_license_purchased": 10,
        "trial_expiry": null
      }
    }
  ]
}
```

### Users

Retrieve users in your Zoho CRM organization.

```bash
GET /zoho-crm/crm/v8/users
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter by user type: `AllUsers`, `ActiveUsers`, `DeactiveUsers`, `ConfirmedUsers`, `NotConfirmedUsers`, `DeletedUsers`, `ActiveConfirmedUsers`, `AdminUsers`, `ActiveConfirmedAdmins`, `CurrentUser` |
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Records per page (default/max: 200) |
| `ids` | string | Comma-separated user IDs (max 100) |

**Example - List all users:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/users?type=AllUsers')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "users": [
    {
      "id": "7243485000000590001",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "status": "active",
      "confirm": true,
      "role": {
        "name": "CEO",
        "id": "7243485000000026005"
      },
      "profile": {
        "name": "Administrator",
        "id": "7243485000000026011"
      },
      "time_zone": "PST",
      "country": "US",
      "locale": "en_US"
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

**Example - Get specific user:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/users/7243485000000590001')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Modules Metadata

Retrieve metadata about all available CRM modules.

```bash
GET /zoho-crm/crm/v8/settings/modules
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `user_hidden`, `system_hidden`, `scheduled_for_deletion`, `visible` |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/settings/modules')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "modules": [
    {
      "api_name": "Leads",
      "module_name": "Leads",
      "singular_label": "Lead",
      "plural_label": "Leads",
      "api_supported": true,
      "creatable": true,
      "editable": true,
      "deletable": true,
      "viewable": true,
      "status": "visible",
      "generated_type": "default",
      "id": "7243485000000002175",
      "profiles": [
        {"name": "Administrator", "id": "7243485000000026011"}
      ]
    }
  ]
}
```

### Fields Metadata

Retrieve field metadata for a specific module.

```bash
GET /zoho-crm/crm/v8/settings/fields?module={module_api_name}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `module` | string | **Required.** API name of the module (e.g., `Leads`, `Contacts`) |
| `type` | string | `all` for all fields, `unused` for unused fields only |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/settings/fields?module=Leads')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "fields": [
    {
      "api_name": "Last_Name",
      "field_label": "Last Name",
      "data_type": "text",
      "system_mandatory": true,
      "custom_field": false,
      "visible": true,
      "searchable": true,
      "sortable": true,
      "id": "7243485000000002613"
    }
  ]
}
```

### Layouts Metadata

Retrieve layout metadata for a specific module.

```bash
GET /zoho-crm/crm/v8/settings/layouts?module={module_api_name}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `module` | string | **Required.** API name of the module (e.g., `Leads`, `Contacts`) |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/settings/layouts?module=Leads')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "layouts": [
    {
      "id": "7243485000000091055",
      "name": "Standard",
      "api_name": "Standard",
      "status": "active",
      "visible": true,
      "profiles": [
        {"name": "Administrator", "id": "7243485000000026011"}
      ],
      "sections": [
        {
          "display_label": "Lead Information",
          "api_name": "Lead_Information",
          "sequence_number": 1,
          "fields": [...]
        }
      ]
    }
  ]
}
```

### Roles

Retrieve roles in your Zoho CRM organization.

```bash
GET /zoho-crm/crm/v8/settings/roles
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/settings/roles')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "roles": [
    {
      "id": "7243485000000026005",
      "name": "CEO",
      "display_label": "CEO",
      "share_with_peers": true,
      "description": null,
      "reporting_to": null
    },
    {
      "id": "7243485000000026008",
      "name": "Manager",
      "display_label": "Manager",
      "share_with_peers": false,
      "reporting_to": {
        "name": "CEO",
        "id": "7243485000000026005"
      }
    }
  ]
}
```

**Example - Get specific role:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/settings/roles/7243485000000026005')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Profiles

Retrieve profiles (permission sets) in your Zoho CRM organization.

```bash
GET /zoho-crm/crm/v8/settings/profiles
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/settings/profiles')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "profiles": [
    {
      "id": "7243485000000026011",
      "name": "Administrator",
      "display_label": "Administrator",
      "type": "normal_profile",
      "custom": false,
      "description": null
    },
    {
      "id": "7243485000000026014",
      "name": "Standard",
      "display_label": "Standard",
      "type": "normal_profile",
      "custom": false,
      "description": null
    }
  ]
}
```

**Example - Get specific profile:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-crm/crm/v8/settings/profiles/7243485000000026011')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Pagination

Zoho CRM uses page-based pagination with optional page tokens for large datasets:

```bash
GET /zoho-crm/crm/v8/{module_api_name}?fields=First_Name,Last_Name&page=1&per_page=50
```

Response includes pagination info:

```json
{
  "data": [...],
  "info": {
    "per_page": 50,
    "count": 50,
    "page": 1,
    "sort_by": "id",
    "sort_order": "desc",
    "more_records": true,
    "next_page_token": "token_value",
    "page_token_expiry": "2026-02-07T01:10:56-08:00"
  }
}
```

- For up to 2,000 records: Use `page` parameter (increment each request)
- For 2,000+ records: Use `page_token` from previous response
- Page tokens expire after 24 hours

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/zoho-crm/crm/v8/Leads?fields=First_Name,Last_Name,Email',
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
    'https://gateway.maton.ai/zoho-crm/crm/v8/Leads',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'fields': 'First_Name,Last_Name,Email'}
)
data = response.json()
```

## Notes

- The `fields` parameter is **required** for list operations (max 50 fields)
- Module API names are case-sensitive (e.g., `Leads`, not `leads`)
- Maximum 100 records per create/update request
- Maximum 100 records per delete request
- Maximum 200 records returned per GET request
- Maximum 2,000 records without page_token; up to 100,000 with page_token
- Use field API names (not display names) in requests
- If you receive a scope error, contact Maton support at support@maton.ai with the specific operations/APIs you need and your use-case
- Empty datasets return HTTP 204 (No Content) with empty body
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho CRM connection, missing required parameter, or invalid request |
| 401 | Invalid or missing Maton API key, or OAuth scope mismatch |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho CRM API |

### Common Error Codes

| Code | Description |
|------|-------------|
| `OAUTH_SCOPE_MISMATCH` | OAuth token lacks required permissions for the endpoint |
| `MANDATORY_NOT_FOUND` | Required field is missing |
| `INVALID_DATA` | Data type mismatch or format error |
| `DUPLICATE_DATA` | Record violates unique field constraint |
| `RECORD_NOT_FOUND` | The specified record ID does not exist |

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

1. Ensure your URL path starts with `zoho-crm`. For example:

- Correct: `https://gateway.maton.ai/zoho-crm/crm/v8/Leads`
- Incorrect: `https://gateway.maton.ai/crm/v8/Leads`

## Resources

- [Zoho CRM API v8 Documentation](https://www.zoho.com/crm/developer/docs/api/v8/)
- [Get Records API](https://www.zoho.com/crm/developer/docs/api/v8/get-records.html)
- [Insert Records API](https://www.zoho.com/crm/developer/docs/api/v8/insert-records.html)
- [Update Records API](https://www.zoho.com/crm/developer/docs/api/v8/update-records.html)
- [Delete Records API](https://www.zoho.com/crm/developer/docs/api/v8/delete-records.html)
- [Search Records API](https://www.zoho.com/crm/developer/docs/api/v8/search-records.html)
- [Organization API](https://www.zoho.com/crm/developer/docs/api/v8/get-org-data.html)
- [Users API](https://www.zoho.com/crm/developer/docs/api/v8/get-users.html)
- [Modules API](https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html)
- [Fields API](https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html)
- [Layouts API](https://www.zoho.com/crm/developer/docs/api/v8/layouts-meta.html)
- [Roles API](https://www.zoho.com/crm/developer/docs/api/v8/get-roles.html)
- [Profiles API](https://www.zoho.com/crm/developer/docs/api/v8/get-profiles.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
