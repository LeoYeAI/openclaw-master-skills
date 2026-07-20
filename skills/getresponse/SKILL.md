---
name: getresponse
description: |
  GetResponse API integration with managed OAuth. Manage email marketing campaigns, contacts, newsletters, autoresponders, and segments.
  Use this skill when users want to manage email lists, send newsletters, create campaigns, or work with contacts in GetResponse.
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

# GetResponse

Access the GetResponse API with managed OAuth authentication. Manage email marketing campaigns, contacts, newsletters, autoresponders, segments, and forms.

## Quick Start

```bash
# List campaigns
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/getresponse/v3/campaigns')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/getresponse/{native-api-path}
```

Replace `{native-api-path}` with the actual GetResponse API endpoint path. The gateway proxies requests to `api.getresponse.com` and automatically injects your OAuth token.

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

Manage your GetResponse OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=getresponse&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'getresponse'}).encode()
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
    "app": "getresponse",
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

If you have multiple GetResponse connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/getresponse/v3/campaigns')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Account Operations

#### Get Account Details

```bash
GET /getresponse/v3/accounts
```

#### Get Billing Info

```bash
GET /getresponse/v3/accounts/billing
```

### Campaign Operations

Campaigns in GetResponse are equivalent to email lists/audiences.

#### List Campaigns

```bash
GET /getresponse/v3/campaigns
```

With pagination:

```bash
GET /getresponse/v3/campaigns?page=1&perPage=100
```

#### Get Campaign

```bash
GET /getresponse/v3/campaigns/{campaignId}
```

#### Create Campaign

```bash
POST /getresponse/v3/campaigns
Content-Type: application/json

{
  "name": "My Campaign"
}
```

### Contact Operations

#### List Contacts

```bash
GET /getresponse/v3/contacts
```

With campaign filter:

```bash
GET /getresponse/v3/contacts?query[campaignId]={campaignId}
```

With pagination:

```bash
GET /getresponse/v3/contacts?page=1&perPage=100
```

With sorting:

```bash
GET /getresponse/v3/contacts?sort[createdOn]=desc
```

#### Get Contact

```bash
GET /getresponse/v3/contacts/{contactId}
```

#### Create Contact

```bash
POST /getresponse/v3/contacts
Content-Type: application/json

{
  "email": "john@example.com",
  "name": "John Doe",
  "campaign": {
    "campaignId": "abc123"
  },
  "customFieldValues": [
    {
      "customFieldId": "xyz789",
      "value": ["Custom Value"]
    }
  ]
}
```

#### Update Contact

```bash
POST /getresponse/v3/contacts/{contactId}
Content-Type: application/json

{
  "name": "John Smith",
  "customFieldValues": [
    {
      "customFieldId": "xyz789",
      "value": ["Updated Value"]
    }
  ]
}
```

#### Delete Contact

```bash
DELETE /getresponse/v3/contacts/{contactId}
```

#### Get Contact Activities

```bash
GET /getresponse/v3/contacts/{contactId}/activities
```

### Custom Fields

#### List Custom Fields

```bash
GET /getresponse/v3/custom-fields
```

#### Get Custom Field

```bash
GET /getresponse/v3/custom-fields/{customFieldId}
```

#### Create Custom Field

```bash
POST /getresponse/v3/custom-fields
Content-Type: application/json

{
  "name": "company",
  "type": "text",
  "hidden": false,
  "values": []
}
```

### Newsletter Operations

#### List Newsletters

```bash
GET /getresponse/v3/newsletters
```

#### Send Newsletter

```bash
POST /getresponse/v3/newsletters
Content-Type: application/json

{
  "subject": "Newsletter Subject",
  "name": "Internal Newsletter Name",
  "campaign": {
    "campaignId": "abc123"
  },
  "content": {
    "html": "<html><body>Newsletter content</body></html>",
    "plain": "Newsletter content"
  },
  "sendOn": "2026-02-15T10:00:00Z"
}
```

#### Send Draft Newsletter

```bash
POST /getresponse/v3/newsletters/send-draft
Content-Type: application/json

{
  "messageId": "newsletter123",
  "sendOn": "2026-02-15T10:00:00Z"
}
```

#### List RSS Newsletters

```bash
GET /getresponse/v3/rss-newsletters
```

### Tags

#### List Tags

```bash
GET /getresponse/v3/tags
```

#### Get Tag

```bash
GET /getresponse/v3/tags/{tagId}
```

#### Create Tag

```bash
POST /getresponse/v3/tags
Content-Type: application/json

{
  "name": "VIP Customer"
}
```

#### Update Tag

```bash
POST /getresponse/v3/tags/{tagId}
Content-Type: application/json

{
  "name": "Premium Customer"
}
```

#### Delete Tag

```bash
DELETE /getresponse/v3/tags/{tagId}
```

#### Assign Tags to Contact

```bash
POST /getresponse/v3/contacts/{contactId}/tags
Content-Type: application/json

{
  "tags": [
    {"tagId": "abc123"},
    {"tagId": "xyz789"}
  ]
}
```

### Autoresponders

#### List Autoresponders

```bash
GET /getresponse/v3/autoresponders
```

#### Get Autoresponder

```bash
GET /getresponse/v3/autoresponders/{autoresponderId}
```

#### Create Autoresponder

```bash
POST /getresponse/v3/autoresponders
Content-Type: application/json

{
  "name": "Welcome Email",
  "subject": "Welcome to our list!",
  "campaign": {
    "campaignId": "abc123"
  },
  "triggerSettings": {
    "dayOfCycle": 0
  },
  "content": {
    "html": "<html><body>Welcome!</body></html>",
    "plain": "Welcome!"
  }
}
```

#### Update Autoresponder

```bash
POST /getresponse/v3/autoresponders/{autoresponderId}
Content-Type: application/json

{
  "subject": "Updated Welcome Email"
}
```

#### Delete Autoresponder

```bash
DELETE /getresponse/v3/autoresponders/{autoresponderId}
```

#### Get Autoresponder Statistics

```bash
GET /getresponse/v3/autoresponders/{autoresponderId}/statistics
```

#### Get All Autoresponder Statistics

```bash
GET /getresponse/v3/autoresponders/statistics
```

### From Fields

#### List From Fields

```bash
GET /getresponse/v3/from-fields
```

#### Get From Field

```bash
GET /getresponse/v3/from-fields/{fromFieldId}
```

### Transactional Emails

**Note:** Transactional email endpoints may require additional OAuth scopes that are not included in the default authorization.

#### List Transactional Emails

```bash
GET /getresponse/v3/transactional-emails
```

#### Send Transactional Email

```bash
POST /getresponse/v3/transactional-emails
Content-Type: application/json

{
  "fromField": {
    "fromFieldId": "abc123"
  },
  "subject": "Your Order Confirmation",
  "recipients": {
    "to": "customer@example.com"
  },
  "content": {
    "html": "<html><body>Order confirmed!</body></html>",
    "plain": "Order confirmed!"
  }
}
```

#### Get Transactional Email

```bash
GET /getresponse/v3/transactional-emails/{transactionalEmailId}
```

#### Get Transactional Email Statistics

```bash
GET /getresponse/v3/transactional-emails/statistics
```

### Imports

#### List Imports

```bash
GET /getresponse/v3/imports
```

#### Create Import

```bash
POST /getresponse/v3/imports
Content-Type: application/json

{
  "campaign": {
    "campaignId": "abc123"
  },
  "contacts": [
    {
      "email": "user1@example.com",
      "name": "User One"
    },
    {
      "email": "user2@example.com",
      "name": "User Two"
    }
  ]
}
```

#### Get Import

```bash
GET /getresponse/v3/imports/{importId}
```

### Workflows (Automations)

#### List Workflows

```bash
GET /getresponse/v3/workflow
```

#### Get Workflow

```bash
GET /getresponse/v3/workflow/{workflowId}
```

#### Update Workflow

```bash
POST /getresponse/v3/workflow/{workflowId}
Content-Type: application/json

{
  "status": "enabled"
}
```

### Segments (Search Contacts)

#### List Segments

```bash
GET /getresponse/v3/search-contacts
```

#### Create Segment

```bash
POST /getresponse/v3/search-contacts
Content-Type: application/json

{
  "name": "Active Subscribers",
  "subscribersType": ["subscribed"],
  "sectionLogicOperator": "or",
  "section": []
}
```

#### Get Segment

```bash
GET /getresponse/v3/search-contacts/{searchContactId}
```

#### Update Segment

```bash
POST /getresponse/v3/search-contacts/{searchContactId}
Content-Type: application/json

{
  "name": "Updated Segment Name"
}
```

#### Delete Segment

```bash
DELETE /getresponse/v3/search-contacts/{searchContactId}
```

#### Get Contacts from Segment

```bash
GET /getresponse/v3/search-contacts/{searchContactId}/contacts
```

#### Search Contacts Without Saving

```bash
POST /getresponse/v3/search-contacts/contacts
Content-Type: application/json

{
  "subscribersType": ["subscribed"],
  "sectionLogicOperator": "or",
  "section": []
}
```

### Forms

**Note:** Forms endpoints may require additional OAuth scopes (form_view, form_design, form_select) that are not included in the default authorization.

#### List Forms

```bash
GET /getresponse/v3/forms
```

#### Get Form

```bash
GET /getresponse/v3/forms/{formId}
```

### Webforms

#### List Webforms

```bash
GET /getresponse/v3/webforms
```

#### Get Webform

```bash
GET /getresponse/v3/webforms/{webformId}
```

### SMS Messages

#### List SMS Messages

```bash
GET /getresponse/v3/sms
```

#### Send SMS

```bash
POST /getresponse/v3/sms
Content-Type: application/json

{
  "recipients": {
    "campaignId": "abc123"
  },
  "content": {
    "message": "Your SMS message content"
  },
  "sendOn": "2026-02-15T10:00:00Z"
}
```

#### Get SMS Message

```bash
GET /getresponse/v3/sms/{smsId}
```

#### Get SMS Statistics

```bash
GET /getresponse/v3/statistics/sms/{smsId}
```

### Shops (Ecommerce)

#### List Shops

```bash
GET /getresponse/v3/shops
```

#### Create Shop

```bash
POST /getresponse/v3/shops
Content-Type: application/json

{
  "name": "My Store",
  "locale": "en_US",
  "currency": "USD"
}
```

#### Get Shop

```bash
GET /getresponse/v3/shops/{shopId}
```

#### List Products

```bash
GET /getresponse/v3/shops/{shopId}/products
```

#### Create Product

```bash
POST /getresponse/v3/shops/{shopId}/products
Content-Type: application/json

{
  "name": "Product Name",
  "url": "https://example.com/product",
  "variants": [
    {
      "name": "Default",
      "price": 29.99,
      "priceTax": 32.99
    }
  ]
}
```

#### List Orders

```bash
GET /getresponse/v3/shops/{shopId}/orders
```

#### Create Order

```bash
POST /getresponse/v3/shops/{shopId}/orders
Content-Type: application/json

{
  "contactId": "abc123",
  "totalPrice": 99.99,
  "currency": "USD",
  "status": "completed"
}
```

### Webinars

#### List Webinars

```bash
GET /getresponse/v3/webinars
```

#### Get Webinar

```bash
GET /getresponse/v3/webinars/{webinarId}
```

### Landing Pages

#### List Landing Pages

```bash
GET /getresponse/v3/lps
```

#### Get Landing Page

```bash
GET /getresponse/v3/lps/{lpsId}
```

#### Get Landing Page Statistics

```bash
GET /getresponse/v3/statistics/lps/{lpsId}/performance
```

## Pagination

Use `page` and `perPage` query parameters for pagination:

```bash
GET /getresponse/v3/contacts?page=1&perPage=100
```

- `page` - Page number (starts at 1)
- `perPage` - Number of records per page (max 1000)

Response headers include pagination info:
- `TotalCount` - Total number of records
- `TotalPages` - Total number of pages
- `CurrentPage` - Current page number

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/getresponse/v3/contacts?perPage=10',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const contacts = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/getresponse/v3/contacts',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'perPage': 10}
)
contacts = response.json()
```

## Notes

- Campaign IDs and Contact IDs are alphanumeric strings
- All timestamps use ISO 8601 format (e.g., `2026-02-15T10:00:00Z`)
- Field names use camelCase
- Rate limits: 30,000 requests per 10 minutes, 80 requests per second
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing GetResponse connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 409 | Conflict (e.g., contact already exists) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from GetResponse API |

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

1. Ensure your URL path starts with `getresponse`. For example:

- Correct: `https://gateway.maton.ai/getresponse/v3/contacts`
- Incorrect: `https://gateway.maton.ai/v3/contacts`

## Resources

- [GetResponse API Documentation](https://apidocs.getresponse.com/v3)
- [GetResponse OpenAPI Spec](https://apireference.getresponse.com/open-api.json)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
