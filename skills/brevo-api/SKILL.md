---
name: brevo
description: |
  Brevo API integration with managed OAuth. Email marketing, transactional emails, SMS, contacts, and CRM.
  Use this skill when users want to send emails, manage contacts, create campaigns, or work with Brevo lists and templates.
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

# Brevo

Access the Brevo API with managed OAuth authentication. Send transactional emails, manage contacts and lists, create email campaigns, and work with templates.

## Quick Start

```bash
# Get account info
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brevo/v3/account')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/brevo/v3/{resource}
```

The gateway proxies requests to `api.brevo.com` and automatically injects your OAuth token.

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

Manage your Brevo OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=brevo&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'brevo'}).encode()
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
    "connection_id": "b04dd695-d056-433b-baf9-0fb4eb3bde9e",
    "status": "ACTIVE",
    "creation_time": "2026-02-09T19:51:00.932629Z",
    "last_updated_time": "2026-02-09T19:51:30.123456Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "brevo",
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

If you have multiple Brevo connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brevo/v3/account')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'b04dd695-d056-433b-baf9-0fb4eb3bde9e')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Account

#### Get Account Info

```bash
GET /brevo/v3/account
```

**Response:**
```json
{
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "companyName": "Acme Inc",
  "relay": {
    "enabled": true,
    "data": {
      "userName": "user@smtp-brevo.com",
      "relay": "smtp-relay.brevo.com",
      "port": 587
    }
  }
}
```

### Contacts

#### List Contacts

```bash
GET /brevo/v3/contacts
```

**Query Parameters:**
- `limit` - Number of results per page (default: 50, max: 500)
- `offset` - Index of first result (0-based)
- `modifiedSince` - Filter by modification date (ISO 8601)

**Response:**
```json
{
  "contacts": [
    {
      "id": 1,
      "email": "contact@example.com",
      "emailBlacklisted": false,
      "smsBlacklisted": false,
      "createdAt": "2026-02-09T20:33:59.705+01:00",
      "modifiedAt": "2026-02-09T20:35:19.529+01:00",
      "listIds": [2],
      "attributes": {
        "FIRSTNAME": "John",
        "LASTNAME": "Doe"
      }
    }
  ],
  "count": 1
}
```

#### Get Contact

```bash
GET /brevo/v3/contacts/{identifier}
```

The identifier can be email address, phone number, or contact ID.

**Query Parameters:**
- `identifierType` - Type of identifier: `email_id`, `phone_id`, `contact_id`, `ext_id`

#### Create Contact

```bash
POST /brevo/v3/contacts
Content-Type: application/json

{
  "email": "newcontact@example.com",
  "attributes": {
    "FIRSTNAME": "Jane",
    "LASTNAME": "Smith"
  },
  "listIds": [2],
  "updateEnabled": false
}
```

**Response:**
```json
{
  "id": 2
}
```

Set `updateEnabled: true` to update the contact if it already exists.

#### Update Contact

```bash
PUT /brevo/v3/contacts/{identifier}
Content-Type: application/json

{
  "attributes": {
    "FIRSTNAME": "Updated",
    "LASTNAME": "Name"
  }
}
```

Returns 204 No Content on success.

#### Delete Contact

```bash
DELETE /brevo/v3/contacts/{identifier}
```

Returns 204 No Content on success.

#### Get Contact Campaign Stats

```bash
GET /brevo/v3/contacts/{identifier}/campaignStats
```

### Lists

#### List All Lists

```bash
GET /brevo/v3/contacts/lists
```

**Response:**
```json
{
  "lists": [
    {
      "id": 2,
      "name": "Newsletter Subscribers",
      "folderId": 1,
      "uniqueSubscribers": 150,
      "totalBlacklisted": 2,
      "totalSubscribers": 148
    }
  ],
  "count": 1
}
```

#### Get List

```bash
GET /brevo/v3/contacts/lists/{listId}
```

#### Create List

```bash
POST /brevo/v3/contacts/lists
Content-Type: application/json

{
  "name": "New List",
  "folderId": 1
}
```

**Response:**
```json
{
  "id": 3
}
```

#### Update List

```bash
PUT /brevo/v3/contacts/lists/{listId}
Content-Type: application/json

{
  "name": "Updated List Name"
}
```

Returns 204 No Content on success.

#### Delete List

```bash
DELETE /brevo/v3/contacts/lists/{listId}
```

Returns 204 No Content on success.

#### Get Contacts in List

```bash
GET /brevo/v3/contacts/lists/{listId}/contacts
```

#### Add Contacts to List

```bash
POST /brevo/v3/contacts/lists/{listId}/contacts/add
Content-Type: application/json

{
  "emails": ["contact1@example.com", "contact2@example.com"]
}
```

#### Remove Contacts from List

```bash
POST /brevo/v3/contacts/lists/{listId}/contacts/remove
Content-Type: application/json

{
  "emails": ["contact1@example.com"]
}
```

### Folders

#### List Folders

```bash
GET /brevo/v3/contacts/folders
```

**Response:**
```json
{
  "folders": [
    {
      "id": 1,
      "name": "Marketing",
      "uniqueSubscribers": 500,
      "totalSubscribers": 480,
      "totalBlacklisted": 20
    }
  ],
  "count": 1
}
```

#### Get Folder

```bash
GET /brevo/v3/contacts/folders/{folderId}
```

#### Create Folder

```bash
POST /brevo/v3/contacts/folders
Content-Type: application/json

{
  "name": "New Folder"
}
```

**Response:**
```json
{
  "id": 4
}
```

#### Update Folder

```bash
PUT /brevo/v3/contacts/folders/{folderId}
Content-Type: application/json

{
  "name": "Renamed Folder"
}
```

Returns 204 No Content on success.

#### Delete Folder

```bash
DELETE /brevo/v3/contacts/folders/{folderId}
```

Deletes folder and all lists within it. Returns 204 No Content on success.

#### Get Lists in Folder

```bash
GET /brevo/v3/contacts/folders/{folderId}/lists
```

### Attributes

#### List Attributes

```bash
GET /brevo/v3/contacts/attributes
```

**Response:**
```json
{
  "attributes": [
    {
      "name": "FIRSTNAME",
      "category": "normal",
      "type": "text"
    },
    {
      "name": "LASTNAME",
      "category": "normal",
      "type": "text"
    }
  ]
}
```

#### Create Attribute

```bash
POST /brevo/v3/contacts/attributes/{category}/{attributeName}
Content-Type: application/json

{
  "type": "text"
}
```

Categories: `normal`, `transactional`, `category`, `calculated`, `global`

#### Update Attribute

```bash
PUT /brevo/v3/contacts/attributes/{category}/{attributeName}
Content-Type: application/json

{
  "value": "new value"
}
```

#### Delete Attribute

```bash
DELETE /brevo/v3/contacts/attributes/{category}/{attributeName}
```

### Transactional Emails

#### Send Email

```bash
POST /brevo/v3/smtp/email
Content-Type: application/json

{
  "sender": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "to": [
    {
      "email": "recipient@example.com",
      "name": "Jane Smith"
    }
  ],
  "subject": "Welcome!",
  "htmlContent": "<html><body><h1>Hello!</h1><p>Welcome to our service.</p></body></html>"
}
```

**Response:**
```json
{
  "messageId": "<202602092329.12910305853@smtp-relay.mailin.fr>"
}
```

**Optional Parameters:**
- `cc` - Carbon copy recipients
- `bcc` - Blind carbon copy recipients
- `replyTo` - Reply-to address
- `textContent` - Plain text version
- `templateId` - Use a template instead of htmlContent
- `params` - Template parameters
- `attachment` - File attachments
- `headers` - Custom headers
- `tags` - Email tags for tracking
- `scheduledAt` - Schedule for later (ISO 8601)

#### Get Transactional Emails

```bash
GET /brevo/v3/smtp/emails
```

**Query Parameters:**
- `email` - Filter by recipient email
- `templateId` - Filter by template
- `messageId` - Filter by message ID
- `startDate` - Start date (YYYY-MM-DD)
- `endDate` - End date (YYYY-MM-DD)
- `limit` - Results per page
- `offset` - Starting index

#### Delete Scheduled Email

```bash
DELETE /brevo/v3/smtp/email/{identifier}
```

The identifier can be a messageId or batchId.

#### Get Email Statistics

```bash
GET /brevo/v3/smtp/statistics/events
```

**Query Parameters:**
- `limit` - Results per page
- `offset` - Starting index
- `startDate` - Start date
- `endDate` - End date
- `email` - Filter by recipient
- `event` - Filter by event type: `delivered`, `opened`, `clicked`, `bounced`, etc.

### Email Templates

#### List Templates

```bash
GET /brevo/v3/smtp/templates
```

**Response:**
```json
{
  "count": 1,
  "templates": [
    {
      "id": 1,
      "name": "Welcome Email",
      "subject": "Welcome {{params.name}}!",
      "isActive": true,
      "sender": {
        "name": "Company",
        "email": "noreply@company.com"
      },
      "htmlContent": "<html>...</html>",
      "createdAt": "2026-02-09 23:29:38",
      "modifiedAt": "2026-02-09 23:29:38"
    }
  ]
}
```

#### Get Template

```bash
GET /brevo/v3/smtp/templates/{templateId}
```

#### Create Template

```bash
POST /brevo/v3/smtp/templates
Content-Type: application/json

{
  "sender": {
    "name": "Company",
    "email": "noreply@company.com"
  },
  "templateName": "Welcome Email",
  "subject": "Welcome {{params.name}}!",
  "htmlContent": "<html><body><h1>Hello {{params.name}}!</h1></body></html>"
}
```

**Response:**
```json
{
  "id": 1
}
```

#### Update Template

```bash
PUT /brevo/v3/smtp/templates/{templateId}
Content-Type: application/json

{
  "templateName": "Updated Template Name",
  "subject": "New Subject"
}
```

Returns 204 No Content on success.

#### Delete Template

```bash
DELETE /brevo/v3/smtp/templates/{templateId}
```

Returns 204 No Content on success.

#### Send Test Email

```bash
POST /brevo/v3/smtp/templates/{templateId}/sendTest
Content-Type: application/json

{
  "emailTo": ["test@example.com"]
}
```

### Email Campaigns

#### List Campaigns

```bash
GET /brevo/v3/emailCampaigns
```

**Query Parameters:**
- `type` - Filter by type: `classic`, `trigger`
- `status` - Filter by status: `draft`, `sent`, `archive`, `queued`, `suspended`, `in_process`
- `limit` - Results per page
- `offset` - Starting index

**Response:**
```json
{
  "count": 1,
  "campaigns": [
    {
      "id": 2,
      "name": "Monthly Newsletter",
      "subject": "Our March Update",
      "type": "classic",
      "status": "draft",
      "sender": {
        "name": "Company",
        "email": "news@company.com"
      },
      "createdAt": "2026-02-09T23:29:39.000Z"
    }
  ]
}
```

#### Get Campaign

```bash
GET /brevo/v3/emailCampaigns/{campaignId}
```

#### Create Campaign

```bash
POST /brevo/v3/emailCampaigns
Content-Type: application/json

{
  "name": "March Newsletter",
  "subject": "Our March Update",
  "sender": {
    "name": "Company",
    "email": "news@company.com"
  },
  "htmlContent": "<html><body><h1>March News</h1></body></html>",
  "recipients": {
    "listIds": [2]
  }
}
```

**Response:**
```json
{
  "id": 2
}
```

#### Update Campaign

```bash
PUT /brevo/v3/emailCampaigns/{campaignId}
Content-Type: application/json

{
  "name": "Updated Campaign Name",
  "subject": "Updated Subject"
}
```

Returns 204 No Content on success.

#### Delete Campaign

```bash
DELETE /brevo/v3/emailCampaigns/{campaignId}
```

Returns 204 No Content on success.

#### Send Campaign Now

```bash
POST /brevo/v3/emailCampaigns/{campaignId}/sendNow
```

#### Send Test Email

```bash
POST /brevo/v3/emailCampaigns/{campaignId}/sendTest
Content-Type: application/json

{
  "emailTo": ["test@example.com"]
}
```

#### Update Campaign Status

```bash
PUT /brevo/v3/emailCampaigns/{campaignId}/status
Content-Type: application/json

{
  "status": "suspended"
}
```

### Senders

#### List Senders

```bash
GET /brevo/v3/senders
```

**Response:**
```json
{
  "senders": [
    {
      "id": 1,
      "name": "Company",
      "email": "noreply@company.com",
      "active": true,
      "ips": []
    }
  ]
}
```

#### Get Sender

```bash
GET /brevo/v3/senders/{senderId}
```

#### Create Sender

```bash
POST /brevo/v3/senders
Content-Type: application/json

{
  "name": "Marketing",
  "email": "marketing@company.com"
}
```

#### Update Sender

```bash
PUT /brevo/v3/senders/{senderId}
Content-Type: application/json

{
  "name": "Updated Name"
}
```

#### Delete Sender

```bash
DELETE /brevo/v3/senders/{senderId}
```

### Blocked Contacts

#### List Blocked Contacts

```bash
GET /brevo/v3/smtp/blockedContacts
```

#### Unblock Contact

```bash
DELETE /brevo/v3/smtp/blockedContacts/{email}
```

### Blocked Domains

#### List Blocked Domains

```bash
GET /brevo/v3/smtp/blockedDomains
```

#### Add Blocked Domain

```bash
POST /brevo/v3/smtp/blockedDomains
Content-Type: application/json

{
  "domain": "spam-domain.com"
}
```

#### Remove Blocked Domain

```bash
DELETE /brevo/v3/smtp/blockedDomains/{domain}
```

## Pagination

Brevo uses offset-based pagination:

```bash
GET /brevo/v3/contacts?limit=50&offset=0
```

**Parameters:**
- `limit` - Number of results per page (varies by endpoint, typically max 500)
- `offset` - Starting index (0-based)

**Response includes count:**
```json
{
  "contacts": [...],
  "count": 150
}
```

To get the next page, increment offset by limit:
- Page 1: `offset=0&limit=50`
- Page 2: `offset=50&limit=50`
- Page 3: `offset=100&limit=50`

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/brevo/v3/contacts',
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
    'https://gateway.maton.ai/brevo/v3/contacts',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
print(data['contacts'])
```

### Python (Send Email)

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/brevo/v3/smtp/email',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'sender': {'name': 'John', 'email': 'john@example.com'},
        'to': [{'email': 'recipient@example.com', 'name': 'Jane'}],
        'subject': 'Hello!',
        'htmlContent': '<html><body><h1>Hi Jane!</h1></body></html>'
    }
)
result = response.json()
print(f"Sent! Message ID: {result['messageId']}")
```

### Python (Create Contact and Add to List)

```python
import os
import requests

headers = {
    'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
    'Content-Type': 'application/json'
}

# Create contact
response = requests.post(
    'https://gateway.maton.ai/brevo/v3/contacts',
    headers=headers,
    json={
        'email': 'newuser@example.com',
        'attributes': {'FIRSTNAME': 'New', 'LASTNAME': 'User'},
        'listIds': [2]
    }
)
contact = response.json()
print(f"Created contact ID: {contact['id']}")
```

## Notes

- All endpoints require the `/v3/` prefix in the path
- Attribute names must be in UPPERCASE
- Contact identifiers can be email, phone, or ID
- Sender email addresses must be verified in Brevo
- Template parameters use `{{params.name}}` syntax
- PUT and DELETE operations return 204 No Content on success
- Rate limits: 300 calls/minute on free plans, higher on paid plans
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Brevo connection or bad request |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Brevo API |

Rate limit headers in response:
- `x-sib-ratelimit-limit` - Request limit
- `x-sib-ratelimit-remaining` - Remaining requests
- `x-sib-ratelimit-reset` - Reset time

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

- [Brevo API Overview](https://developers.brevo.com/)
- [Brevo API Key Concepts](https://developers.brevo.com/docs/how-it-works)
- [Brevo OAuth 2.0](https://developers.brevo.com/docs/integrating-oauth-20-to-your-solution)
- [Manage Contacts](https://developers.brevo.com/docs/synchronise-contact-lists)
- [Send Transactional Email](https://developers.brevo.com/docs/send-a-transactional-email)
