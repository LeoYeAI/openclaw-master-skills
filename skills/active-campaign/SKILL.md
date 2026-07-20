---
name: active-campaign
description: |
  ActiveCampaign API integration with managed OAuth. Marketing automation, CRM, contacts, deals, and email campaigns.
  Use this skill when users want to manage contacts, deals, tags, lists, automations, or campaigns in ActiveCampaign.
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

# ActiveCampaign

Access the ActiveCampaign API with managed OAuth authentication. Manage contacts, deals, tags, lists, automations, and email campaigns.

## Quick Start

```bash
# List all contacts
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/active-campaign/api/3/contacts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/active-campaign/{native-api-path}
```

Replace `{native-api-path}` with the actual ActiveCampaign API endpoint path. The gateway proxies requests to `{account}.api-us1.com` and automatically injects your OAuth token.


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

Manage your ActiveCampaign OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=active-campaign&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'active-campaign'}).encode()
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
    "connection_id": "9e8ba2aa-25ec-4ba0-8815-3068be304dca",
    "status": "ACTIVE",
    "creation_time": "2026-02-09T20:03:16.595823Z",
    "last_updated_time": "2026-02-09T20:04:09.550767Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "active-campaign",
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

If you have multiple ActiveCampaign connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/active-campaign/api/3/contacts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '9e8ba2aa-25ec-4ba0-8815-3068be304dca')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Contacts

#### List Contacts

```bash
GET /active-campaign/api/3/contacts
```

**Query Parameters:**
- `limit` - Number of results (default: 20)
- `offset` - Starting index
- `search` - Search by email
- `filters[email]` - Filter by email
- `filters[listid]` - Filter by list ID

**Response:**
```json
{
  "contacts": [
    {
      "id": "1",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "phone": "",
      "cdate": "2026-02-09T14:03:19-06:00",
      "udate": "2026-02-09T14:03:19-06:00"
    }
  ],
  "meta": {
    "total": "1"
  }
}
```

#### Get Contact

```bash
GET /active-campaign/api/3/contacts/{contactId}
```

Returns contact with related data including lists, tags, deals, and field values.

#### Create Contact

```bash
POST /active-campaign/api/3/contacts
Content-Type: application/json

{
  "contact": {
    "email": "newcontact@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phone": "555-1234"
  }
}
```

**Response:**
```json
{
  "contact": {
    "id": "2",
    "email": "newcontact@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "cdate": "2026-02-09T17:51:39-06:00",
    "udate": "2026-02-09T17:51:39-06:00"
  }
}
```

#### Update Contact

```bash
PUT /active-campaign/api/3/contacts/{contactId}
Content-Type: application/json

{
  "contact": {
    "firstName": "Updated",
    "lastName": "Name"
  }
}
```

#### Delete Contact

```bash
DELETE /active-campaign/api/3/contacts/{contactId}
```

Returns 200 OK on success.

#### Sync Contact (Create or Update)

```bash
POST /active-campaign/api/3/contact/sync
Content-Type: application/json

{
  "contact": {
    "email": "user@example.com",
    "firstName": "Updated Name"
  }
}
```

Creates the contact if it doesn't exist, updates if it does.

### Tags

#### List Tags

```bash
GET /active-campaign/api/3/tags
```

**Response:**
```json
{
  "tags": [
    {
      "id": "1",
      "tag": "VIP Customer",
      "tagType": "contact",
      "description": "High-value customers",
      "cdate": "2026-02-09T17:51:39-06:00"
    }
  ],
  "meta": {
    "total": "1"
  }
}
```

#### Get Tag

```bash
GET /active-campaign/api/3/tags/{tagId}
```

#### Create Tag

```bash
POST /active-campaign/api/3/tags
Content-Type: application/json

{
  "tag": {
    "tag": "New Tag",
    "tagType": "contact",
    "description": "Tag description"
  }
}
```

#### Update Tag

```bash
PUT /active-campaign/api/3/tags/{tagId}
Content-Type: application/json

{
  "tag": {
    "tag": "Updated Tag Name"
  }
}
```

#### Delete Tag

```bash
DELETE /active-campaign/api/3/tags/{tagId}
```

### Contact Tags

#### Add Tag to Contact

```bash
POST /active-campaign/api/3/contactTags
Content-Type: application/json

{
  "contactTag": {
    "contact": "2",
    "tag": "1"
  }
}
```

#### Remove Tag from Contact

```bash
DELETE /active-campaign/api/3/contactTags/{contactTagId}
```

#### Get Contact's Tags

```bash
GET /active-campaign/api/3/contacts/{contactId}/contactTags
```

### Lists

#### List All Lists

```bash
GET /active-campaign/api/3/lists
```

**Response:**
```json
{
  "lists": [
    {
      "id": "1",
      "stringid": "master-contact-list",
      "name": "Master Contact List",
      "cdate": "2026-02-09T14:03:20-06:00"
    }
  ],
  "meta": {
    "total": "1"
  }
}
```

#### Get List

```bash
GET /active-campaign/api/3/lists/{listId}
```

#### Create List

```bash
POST /active-campaign/api/3/lists
Content-Type: application/json

{
  "list": {
    "name": "New List",
    "stringid": "new-list",
    "sender_url": "https://example.com",
    "sender_reminder": "You signed up on our website"
  }
}
```

#### Update List

```bash
PUT /active-campaign/api/3/lists/{listId}
Content-Type: application/json

{
  "list": {
    "name": "Updated List Name"
  }
}
```

#### Delete List

```bash
DELETE /active-campaign/api/3/lists/{listId}
```

### Contact Lists

#### Subscribe Contact to List

```bash
POST /active-campaign/api/3/contactLists
Content-Type: application/json

{
  "contactList": {
    "contact": "2",
    "list": "1",
    "status": "1"
  }
}
```

Status values: `1` = subscribed, `2` = unsubscribed

### Deals

#### List Deals

```bash
GET /active-campaign/api/3/deals
```

**Query Parameters:**
- `search` - Search by title, contact, or org
- `filters[stage]` - Filter by stage ID
- `filters[owner]` - Filter by owner ID

**Response:**
```json
{
  "deals": [
    {
      "id": "1",
      "title": "New Deal",
      "value": "10000",
      "currency": "usd",
      "stage": "1",
      "owner": "1"
    }
  ],
  "meta": {
    "total": 0,
    "currencies": []
  }
}
```

#### Get Deal

```bash
GET /active-campaign/api/3/deals/{dealId}
```

#### Create Deal

```bash
POST /active-campaign/api/3/deals
Content-Type: application/json

{
  "deal": {
    "title": "New Deal",
    "value": "10000",
    "currency": "usd",
    "contact": "2",
    "stage": "1",
    "owner": "1"
  }
}
```

#### Update Deal

```bash
PUT /active-campaign/api/3/deals/{dealId}
Content-Type: application/json

{
  "deal": {
    "title": "Updated Deal",
    "value": "15000"
  }
}
```

#### Delete Deal

```bash
DELETE /active-campaign/api/3/deals/{dealId}
```

### Deal Stages

#### List Deal Stages

```bash
GET /active-campaign/api/3/dealStages
```

#### Create Deal Stage

```bash
POST /active-campaign/api/3/dealStages
Content-Type: application/json

{
  "dealStage": {
    "title": "New Stage",
    "group": "1",
    "order": "1"
  }
}
```

### Deal Groups (Pipelines)

#### List Pipelines

```bash
GET /active-campaign/api/3/dealGroups
```

#### Create Pipeline

```bash
POST /active-campaign/api/3/dealGroups
Content-Type: application/json

{
  "dealGroup": {
    "title": "Sales Pipeline",
    "currency": "usd"
  }
}
```

### Automations

#### List Automations

```bash
GET /active-campaign/api/3/automations
```

**Response:**
```json
{
  "automations": [
    {
      "id": "1",
      "name": "Welcome Series",
      "cdate": "2026-02-09T14:00:00-06:00",
      "mdate": "2026-02-09T14:00:00-06:00",
      "status": "1"
    }
  ],
  "meta": {
    "total": "1"
  }
}
```

#### Get Automation

```bash
GET /active-campaign/api/3/automations/{automationId}
```

### Campaigns

#### List Campaigns

```bash
GET /active-campaign/api/3/campaigns
```

**Response:**
```json
{
  "campaigns": [
    {
      "id": "1",
      "name": "Newsletter",
      "type": "single",
      "status": "0"
    }
  ],
  "meta": {
    "total": "1"
  }
}
```

#### Get Campaign

```bash
GET /active-campaign/api/3/campaigns/{campaignId}
```

### Users

#### List Users

```bash
GET /active-campaign/api/3/users
```

**Response:**
```json
{
  "users": [
    {
      "id": "1",
      "username": "admin",
      "firstName": "John",
      "lastName": "Doe",
      "email": "admin@example.com"
    }
  ]
}
```

#### Get User

```bash
GET /active-campaign/api/3/users/{userId}
```

### Accounts

#### List Accounts

```bash
GET /active-campaign/api/3/accounts
```

#### Create Account

```bash
POST /active-campaign/api/3/accounts
Content-Type: application/json

{
  "account": {
    "name": "Acme Inc"
  }
}
```

### Custom Fields

#### List Fields

```bash
GET /active-campaign/api/3/fields
```

#### Create Field

```bash
POST /active-campaign/api/3/fields
Content-Type: application/json

{
  "field": {
    "type": "text",
    "title": "Custom Field",
    "descript": "A custom field"
  }
}
```

### Field Values

#### Update Contact Field Value

```bash
PUT /active-campaign/api/3/fieldValues/{fieldValueId}
Content-Type: application/json

{
  "fieldValue": {
    "value": "New Value"
  }
}
```

### Notes

#### List Notes

```bash
GET /active-campaign/api/3/notes
```

#### Create Note

```bash
POST /active-campaign/api/3/notes
Content-Type: application/json

{
  "note": {
    "note": "This is a note",
    "relid": "2",
    "reltype": "Subscriber"
  }
}
```

### Webhooks

#### List Webhooks

```bash
GET /active-campaign/api/3/webhooks
```

#### Create Webhook

```bash
POST /active-campaign/api/3/webhooks
Content-Type: application/json

{
  "webhook": {
    "name": "My Webhook",
    "url": "https://example.com/webhook",
    "events": ["subscribe", "unsubscribe"],
    "sources": ["public", "admin"]
  }
}
```

## Pagination

ActiveCampaign uses offset-based pagination:

```bash
GET /active-campaign/api/3/contacts?limit=20&offset=0
```

**Parameters:**
- `limit` - Results per page (default: 20)
- `offset` - Starting index

**Response includes meta:**
```json
{
  "contacts": [...],
  "meta": {
    "total": "150"
  }
}
```

For large datasets, use `orders[id]=ASC` and `id_greater` parameter for better performance:
```bash
GET /active-campaign/api/3/contacts?orders[id]=ASC&id_greater=100
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/active-campaign/api/3/contacts',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.contacts);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/active-campaign/api/3/contacts',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
print(data['contacts'])
```

### Python (Create Contact with Tag)

```python
import os
import requests

headers = {
    'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
    'Content-Type': 'application/json'
}

# Create contact
contact_response = requests.post(
    'https://gateway.maton.ai/active-campaign/api/3/contacts',
    headers=headers,
    json={
        'contact': {
            'email': 'newuser@example.com',
            'firstName': 'New',
            'lastName': 'User'
        }
    }
)
contact = contact_response.json()['contact']
print(f"Created contact ID: {contact['id']}")

# Add tag to contact
tag_response = requests.post(
    'https://gateway.maton.ai/active-campaign/api/3/contactTags',
    headers=headers,
    json={
        'contactTag': {
            'contact': contact['id'],
            'tag': '1'
        }
    }
)
print("Tag added to contact")
```

## Notes

- All endpoints require the `/api/3/` prefix
- Request bodies use singular resource names wrapped in an object (e.g., `{"contact": {...}}`)
- IDs are returned as strings
- Timestamps are in ISO 8601 format with timezone
- Rate limit: 5 requests per second per account
- DELETE operations return 200 OK (not 204)
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing ActiveCampaign connection or bad request |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 422 | Validation error |
| 429 | Rate limited (5 req/sec) |
| 4xx/5xx | Passthrough error from ActiveCampaign API |

Error responses include details:
```json
{
  "errors": [
    {
      "title": "The contact email is required",
      "source": {
        "pointer": "/data/attributes/email"
      }
    }
  ]
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

- [ActiveCampaign API Overview](https://developers.activecampaign.com/reference/overview)
- [ActiveCampaign Developer Portal](https://developers.activecampaign.com/)
- [API Base URL](https://developers.activecampaign.com/reference/url)
- [Contacts API](https://developers.activecampaign.com/reference/list-all-contacts)
- [Tags API](https://developers.activecampaign.com/reference/contact-tags)
- [Deals API](https://developers.activecampaign.com/reference/list-all-deals)
