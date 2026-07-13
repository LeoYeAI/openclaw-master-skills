---
name: clickfunnels
description: |
  ClickFunnels API integration with managed OAuth. Manage contacts, products, orders, courses, forms, and webhooks.
  Use this skill when users want to create sales funnels, manage contacts, process orders, or build marketing automation.
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

# ClickFunnels

Access the ClickFunnels 2.0 API with managed OAuth authentication. Manage contacts, products, orders, courses, forms, webhooks, and more.

## Quick Start

```bash
# List teams
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickfunnels/api/v2/teams')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('User-Agent', 'Maton/1.0')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/clickfunnels/{native-api-path}
```

Replace `{native-api-path}` with the actual ClickFunnels API endpoint path. The gateway proxies requests to `{subdomain}.myclickfunnels.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header and a User-Agent header:

```
Authorization: Bearer $MATON_API_KEY
User-Agent: Maton/1.0
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

Manage your ClickFunnels OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=clickfunnels&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'clickfunnels'}).encode()
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
    "app": "clickfunnels",
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

If you have multiple ClickFunnels connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clickfunnels/api/v2/teams')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('User-Agent', 'Maton/1.0')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Teams

#### List Teams

```bash
GET /clickfunnels/api/v2/teams
```

**Response:**
```json
[
  {
    "id": 412840,
    "public_id": "vPNqAp",
    "name": "My Team",
    "time_zone": "Pacific Time (US & Canada)",
    "locale": "en",
    "created_at": "2026-02-07T09:28:29.709Z",
    "updated_at": "2026-02-07T11:14:32.118Z"
  }
]
```

#### Get Team

```bash
GET /clickfunnels/api/v2/teams/{team_id}
```

### Workspaces

#### List Workspaces

```bash
GET /clickfunnels/api/v2/teams/{team_id}/workspaces
```

**Response:**
```json
[
  {
    "id": 435231,
    "public_id": "JZqWGb",
    "team_id": 412840,
    "name": "My Workspace",
    "subdomain": "myworkspace",
    "created_at": "2026-02-07T09:28:31.268Z",
    "updated_at": "2026-02-07T09:28:34.498Z"
  }
]
```

#### Get Workspace

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}
```

### Contacts

#### List Contacts

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/contacts
```

With filtering:

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/contacts?filter[email_address]=user@example.com
```

**Response:**
```json
[
  {
    "id": 1087091674,
    "public_id": "PWzmxEx",
    "workspace_id": 435231,
    "email_address": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": null,
    "time_zone": null,
    "uuid": "eb7a970c-727d-4c82-9209-bd8f7457a801",
    "tags": [],
    "custom_attributes": {},
    "created_at": "2026-02-07T09:28:52.713Z",
    "updated_at": "2026-02-07T09:28:52.777Z"
  }
]
```

#### Get Contact

```bash
GET /clickfunnels/api/v2/contacts/{contact_id}
```

#### Create Contact

```bash
POST /clickfunnels/api/v2/workspaces/{workspace_id}/contacts
Content-Type: application/json

{
  "contact": {
    "email_address": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+1234567890"
  }
}
```

#### Update Contact

```bash
PUT /clickfunnels/api/v2/contacts/{contact_id}
Content-Type: application/json

{
  "contact": {
    "first_name": "Updated Name",
    "phone_number": "+1987654321"
  }
}
```

#### Delete Contact

```bash
DELETE /clickfunnels/api/v2/contacts/{contact_id}
```

Returns HTTP 204 on success.

#### Upsert Contact

Create or update a contact based on matching email:

```bash
POST /clickfunnels/api/v2/workspaces/{workspace_id}/contacts/upsert
Content-Type: application/json

{
  "contact": {
    "email_address": "user@example.com",
    "first_name": "Updated"
  }
}
```

#### GDPR Redact Contact

```bash
DELETE /clickfunnels/api/v2/workspaces/{workspace_id}/contacts/{contact_id}/gdpr_destroy
```

### Products

#### List Products

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/products
```

**Response:**
```json
[
  {
    "id": 962732,
    "public_id": "jAvBEA",
    "workspace_id": 435231,
    "name": "My Product",
    "current_path": "/my-product",
    "archived": false,
    "visible_in_store": true,
    "visible_in_customer_center": true,
    "default_variant_id": 5361073,
    "variant_ids": [5361073],
    "price_ids": [],
    "tag_ids": [],
    "created_at": "2026-02-09T07:23:02.158Z",
    "updated_at": "2026-02-09T07:23:02.163Z"
  }
]
```

#### Get Product

```bash
GET /clickfunnels/api/v2/products/{product_id}
```

#### Create Product

```bash
POST /clickfunnels/api/v2/workspaces/{workspace_id}/products
Content-Type: application/json

{
  "product": {
    "name": "New Product",
    "visible_in_store": true,
    "visible_in_customer_center": true
  }
}
```

#### Update Product

```bash
PUT /clickfunnels/api/v2/products/{product_id}
Content-Type: application/json

{
  "product": {
    "name": "Updated Product Name"
  }
}
```

#### Archive Product

```bash
POST /clickfunnels/api/v2/products/{product_id}/archive
```

#### Unarchive Product

```bash
POST /clickfunnels/api/v2/products/{product_id}/unarchive
```

### Orders

#### List Orders

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/orders
```

#### Get Order

```bash
GET /clickfunnels/api/v2/orders/{order_id}
```

#### Update Order

```bash
PUT /clickfunnels/api/v2/orders/{order_id}
Content-Type: application/json

{
  "order": {
    "notes": "Updated order notes"
  }
}
```

### Fulfillments

#### List Fulfillments

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/fulfillments
```

#### Get Fulfillment

```bash
GET /clickfunnels/api/v2/fulfillments/{fulfillment_id}
```

#### Create Fulfillment

```bash
POST /clickfunnels/api/v2/workspaces/{workspace_id}/fulfillments
Content-Type: application/json

{
  "fulfillment": {
    "contact_id": 1087091674,
    "location_id": 12345,
    "tracking_url": "https://tracking.example.com/123",
    "shipping_provider": "ups",
    "tracking_code": "1Z999AA10123456784",
    "notify_customer": true
  }
}
```

#### Cancel Fulfillment

```bash
POST /clickfunnels/api/v2/fulfillments/{fulfillment_id}/cancel
```

### Courses

#### List Courses

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/courses
```

#### Get Course

```bash
GET /clickfunnels/api/v2/courses/{course_id}
```

### Enrollments

#### List Enrollments

```bash
GET /clickfunnels/api/v2/courses/{course_id}/enrollments
```

#### Create Enrollment

```bash
POST /clickfunnels/api/v2/courses/{course_id}/enrollments
Content-Type: application/json

{
  "courses_enrollment": {
    "contact_id": 1087091674
  }
}
```

#### Update Enrollment

```bash
PUT /clickfunnels/api/v2/courses/{course_id}/enrollments/{enrollment_id}
Content-Type: application/json

{
  "courses_enrollment": {
    "suspended": true,
    "suspension_reason": "Payment failed"
  }
}
```

### Forms

#### List Forms

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/forms
```

**Response:**
```json
[
  {
    "id": 442896,
    "public_id": "NdOxzL",
    "workspace_id": 435231,
    "name": "Contact Form",
    "created_at": "2026-02-07T09:28:33.316Z",
    "updated_at": "2026-02-07T09:28:33.316Z"
  }
]
```

#### Get Form

```bash
GET /clickfunnels/api/v2/forms/{form_id}
```

#### List Form Submissions

```bash
GET /clickfunnels/api/v2/forms/{form_id}/submissions
```

### Images

#### List Images

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/images
```

**Response:**
```json
[
  {
    "id": 20670308,
    "public_id": "mvvWWM",
    "url": "https://statics.myclickfunnels.com/workspace/JZqWGb/image/20670308/file/image.png",
    "workspace_id": 435231,
    "alt_text": null,
    "name": null,
    "created_at": "2026-02-07T09:28:40.102Z",
    "updated_at": "2026-02-07T09:29:01.697Z"
  }
]
```

#### Create Image (via URL)

```bash
POST /clickfunnels/api/v2/workspaces/{workspace_id}/images
Content-Type: application/json

{
  "image": {
    "upload_source_url": "https://example.com/image.png"
  }
}
```

### Webhooks

#### List Webhook Endpoints

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/webhooks/outgoing/endpoints
```

**Response:**
```json
[
  {
    "id": 96677,
    "public_id": "vBZlEl",
    "workspace_id": 435231,
    "url": "https://example.com/webhook",
    "name": "My Webhook",
    "event_type_ids": ["contact.created"],
    "api_version": 2,
    "webhook_secret": "e779d4b2faa7d986...",
    "created_at": "2026-02-09T07:23:22.295Z",
    "updated_at": "2026-02-09T07:23:22.295Z"
  }
]
```

#### Create Webhook Endpoint

```bash
POST /clickfunnels/api/v2/workspaces/{workspace_id}/webhooks/outgoing/endpoints
Content-Type: application/json

{
  "webhooks_outgoing_endpoint": {
    "url": "https://example.com/webhook",
    "name": "New Webhook",
    "event_type_ids": ["contact.created", "order.created"]
  }
}
```

#### Get Webhook Endpoint

```bash
GET /clickfunnels/api/v2/webhooks/outgoing/endpoints/{endpoint_id}
```

#### Update Webhook Endpoint

```bash
PUT /clickfunnels/api/v2/webhooks/outgoing/endpoints/{endpoint_id}
Content-Type: application/json

{
  "webhooks_outgoing_endpoint": {
    "name": "Updated Webhook",
    "event_type_ids": ["contact.created", "contact.updated"]
  }
}
```

#### Delete Webhook Endpoint

```bash
DELETE /clickfunnels/api/v2/webhooks/outgoing/endpoints/{endpoint_id}
```

Returns HTTP 204 on success.

## Pagination

ClickFunnels uses cursor-based pagination. Each list endpoint returns a maximum of 20 items.

Use the `after` parameter with the ID of the last item to get the next page:

```bash
GET /clickfunnels/api/v2/workspaces/{workspace_id}/contacts?after=1087091674
```

**Response Headers:**

- `Pagination-Next`: ID of the last item (use for next page)
- `Link`: Full URL for the next page

Example pagination flow:

```bash
# First page
GET /clickfunnels/api/v2/workspaces/{workspace_id}/images

# Response header: Pagination-Next: 20670327

# Next page
GET /clickfunnels/api/v2/workspaces/{workspace_id}/images?after=20670327
```

## Filtering

Use the `filter` query parameter to filter list results:

```bash
# Filter by email
GET /clickfunnels/api/v2/workspaces/{workspace_id}/contacts?filter[email_address]=user@example.com

# Filter by multiple emails (OR)
GET /clickfunnels/api/v2/workspaces/{workspace_id}/contacts?filter[email_address]=user1@example.com,user2@example.com

# Multiple filters (AND)
GET /clickfunnels/api/v2/workspaces/{workspace_id}/contacts?filter[email_address]=user@example.com&filter[id]=1087091674
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/clickfunnels/api/v2/teams',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'User-Agent': 'Maton/1.0'
    }
  }
);
const teams = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/clickfunnels/api/v2/teams',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'User-Agent': 'Maton/1.0'
    }
)
teams = response.json()
```

### Create Contact Example

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/clickfunnels/api/v2/workspaces/435231/contacts',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json',
        'User-Agent': 'Maton/1.0'
    },
    json={
        'contact': {
            'email_address': 'newuser@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
    }
)
contact = response.json()
```

## Notes

- Team IDs, workspace IDs, and resource IDs are integers
- Each resource also has a `public_id` (string) for public-facing URLs
- List endpoints return max 20 items per page by default
- Use `after` parameter for pagination
- Delete operations return HTTP 204 with empty response
- Request bodies use nested resource keys (e.g., `{"contact": {...}}`)
- Images max size: 10MB, max dimensions: 10,000 x 10,000 pixels
- Supported image formats: JPEG, PNG, WebP, GIF, SVG
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing ClickFunnels connection |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 422 | Validation error (check response body) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from ClickFunnels API |

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

1. Ensure your URL path starts with `clickfunnels`. For example:

- Correct: `https://gateway.maton.ai/clickfunnels/api/v2/teams`
- Incorrect: `https://gateway.maton.ai/api/v2/teams`

## Resources

- [ClickFunnels API Introduction](https://developers.myclickfunnels.com/docs/intro)
- [ClickFunnels API Reference](https://developers.myclickfunnels.com/reference)
- [Pagination Guide](https://developers.myclickfunnels.com/docs/pagination)
- [Filtering Guide](https://developers.myclickfunnels.com/docs/filtering)
- [Webhooks Overview](https://developers.myclickfunnels.com/docs/webhooks-overview)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
