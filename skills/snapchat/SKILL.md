---
name: snapchat
description: |
  Snapchat Marketing API integration with managed OAuth. Manage ad accounts, campaigns, ad squads, ads, creatives, and audiences.
  Use this skill when users want to create and manage Snapchat advertising campaigns, view ad performance stats, or manage targeting.
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

# Snapchat

Access the Snapchat Marketing API with managed OAuth authentication. Manage organizations, ad accounts, campaigns, ad squads, ads, creatives, media, and audiences.

## Quick Start

```bash
# List your organizations
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/snapchat/v1/me/organizations')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/snapchat/{api-path}
```

The Snapchat Marketing API uses the path pattern:
```
https://gateway.maton.ai/snapchat/v1/{resource}
```

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

Manage your Snapchat OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=snapchat&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'snapchat'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python3 <<'EOF'
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
    "connection_id": "f5d5458b-fb65-458c-9e51-08844662dd39",
    "status": "ACTIVE",
    "creation_time": "2026-02-14T00:00:00.000000Z",
    "last_updated_time": "2026-02-14T00:00:00.000000Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "snapchat",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Snapchat connections, specify which one to use with the `Maton-Connection` header:

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/snapchat/v1/me/organizations')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'f5d5458b-fb65-458c-9e51-08844662dd39')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Current User

#### Get Current User

```bash
GET /v1/me
```

**Response:**
```json
{
  "request_status": "SUCCESS",
  "request_id": "...",
  "me": {
    "id": "...",
    "email": "user@example.com",
    "display_name": "User Name"
  }
}
```

#### List My Organizations

```bash
GET /v1/me/organizations
```

**Response:**
```json
{
  "request_status": "SUCCESS",
  "request_id": "...",
  "organizations": [
    {
      "sub_request_status": "SUCCESS",
      "organization": {
        "id": "63acee69-77ff-4378-8492-3f8d28e8f241",
        "name": "My Organization",
        "country": "US",
        "contact_name": "John Doe",
        "contact_email": "john@example.com"
      }
    }
  ]
}
```

### Organizations

#### Get Organization

```bash
GET /v1/organizations/{organizationId}
```

#### List Organization Ad Accounts

```bash
GET /v1/organizations/{organizationId}/adaccounts
```

#### List Organization Funding Sources

```bash
GET /v1/organizations/{organizationId}/fundingsources
```

#### List Organization Members

```bash
GET /v1/organizations/{organizationId}/members
```

#### List Organization Roles

```bash
GET /v1/organizations/{organizationId}/roles
```

#### List Product Catalogs

```bash
GET /v1/organizations/{organizationId}/catalogs
```

### Ad Accounts

#### Get Ad Account

```bash
GET /v1/adaccounts/{adAccountId}
```

**Response:**
```json
{
  "request_status": "SUCCESS",
  "request_id": "...",
  "adaccounts": [
    {
      "sub_request_status": "SUCCESS",
      "adaccount": {
        "id": "6e916ba9-db2f-40cd-9553-a90e32cedea3",
        "name": "My Ad Account",
        "type": "PARTNER",
        "status": "ACTIVE",
        "organization_id": "...",
        "currency": "USD",
        "timezone": "America/Los_Angeles"
      }
    }
  ]
}
```

#### List Ad Account Roles

```bash
GET /v1/adaccounts/{adAccountId}/roles
```

### Campaigns

#### List Campaigns

```bash
GET /v1/adaccounts/{adAccountId}/campaigns
GET /v1/adaccounts/{adAccountId}/campaigns?limit=50
```

**Query Parameters:**
- `limit` - Number of results (50-1000)

#### Get Campaign

```bash
GET /v1/campaigns/{campaignId}
```

#### Create Campaign

```bash
POST /v1/adaccounts/{adAccountId}/campaigns
Content-Type: application/json

{
  "campaigns": [{
    "name": "Campaign Name",
    "status": "PAUSED",
    "ad_account_id": "{adAccountId}",
    "start_time": "2026-02-15T00:00:00.000-08:00"
  }]
}
```

#### Update Campaign

```bash
PUT /v1/adaccounts/{adAccountId}/campaigns
Content-Type: application/json

{
  "campaigns": [{
    "id": "{campaignId}",
    "name": "Updated Campaign Name",
    "status": "ACTIVE"
  }]
}
```

#### Delete Campaign

```bash
DELETE /v1/campaigns/{campaignId}
```

### Ad Squads

#### List Ad Squads

```bash
GET /v1/adaccounts/{adAccountId}/adsquads
GET /v1/campaigns/{campaignId}/adsquads
```

#### Get Ad Squad

```bash
GET /v1/adsquads/{adSquadId}
```

#### Create Ad Squad

```bash
POST /v1/campaigns/{campaignId}/adsquads
Content-Type: application/json

{
  "adsquads": [{
    "name": "Ad Squad Name",
    "status": "PAUSED",
    "campaign_id": "{campaignId}",
    "type": "SNAP_ADS",
    "placement": "SNAP_ADS",
    "optimization_goal": "IMPRESSIONS",
    "bid_micro": 1000000,
    "daily_budget_micro": 50000000,
    "start_time": "2026-02-15T00:00:00.000-08:00",
    "targeting": {
      "geos": [{"country_code": "us"}]
    }
  }]
}
```

#### Update Ad Squad

```bash
PUT /v1/campaigns/{campaignId}/adsquads
Content-Type: application/json

{
  "adsquads": [{
    "id": "{adSquadId}",
    "name": "Updated Ad Squad Name"
  }]
}
```

#### Delete Ad Squad

```bash
DELETE /v1/adsquads/{adSquadId}
```

### Ads

#### List Ads

```bash
GET /v1/adaccounts/{adAccountId}/ads
GET /v1/adsquads/{adSquadId}/ads
```

#### Get Ad

```bash
GET /v1/ads/{adId}
```

#### Create Ad

```bash
POST /v1/adsquads/{adSquadId}/ads
Content-Type: application/json

{
  "ads": [{
    "name": "Ad Name",
    "status": "PAUSED",
    "ad_squad_id": "{adSquadId}",
    "creative_id": "{creativeId}",
    "type": "SNAP_AD"
  }]
}
```

#### Update Ad

```bash
PUT /v1/adsquads/{adSquadId}/ads
Content-Type: application/json

{
  "ads": [{
    "id": "{adId}",
    "name": "Updated Ad Name"
  }]
}
```

#### Delete Ad

```bash
DELETE /v1/ads/{adId}
```

### Creatives

#### List Creatives

```bash
GET /v1/adaccounts/{adAccountId}/creatives
GET /v1/adaccounts/{adAccountId}/creatives?limit=50&sort=updated_at-desc
```

#### Get Creative

```bash
GET /v1/creatives/{creativeId}
```

#### Create Creative

```bash
POST /v1/adaccounts/{adAccountId}/creatives
Content-Type: application/json

{
  "creatives": [{
    "name": "Creative Name",
    "ad_account_id": "{adAccountId}",
    "type": "SNAP_AD",
    "top_snap_media_id": "{mediaId}",
    "headline": "Headline Text",
    "brand_name": "Brand Name",
    "call_to_action": "VIEW_MORE"
  }]
}
```

#### Update Creative

```bash
PUT /v1/adaccounts/{adAccountId}/creatives
Content-Type: application/json

{
  "creatives": [{
    "id": "{creativeId}",
    "name": "Updated Creative Name"
  }]
}
```

### Media

#### List Media

```bash
GET /v1/adaccounts/{adAccountId}/media
GET /v1/adaccounts/{adAccountId}/media?limit=50&sort=created_at-desc
```

#### Get Media

```bash
GET /v1/media/{mediaId}
```

### Pixels

#### List Pixels

```bash
GET /v1/adaccounts/{adAccountId}/pixels
```

#### Get Pixel

```bash
GET /v1/pixels/{pixelId}
```

### Audience Segments

#### List Segments

```bash
GET /v1/adaccounts/{adAccountId}/segments
```

#### Get Segment

```bash
GET /v1/segments/{segmentId}
```

### Stats

#### Get Ad Account Stats

```bash
GET /v1/adaccounts/{adAccountId}/stats?granularity=DAY&start_time=2026-02-01&end_time=2026-02-14
```

**Query Parameters:**
- `granularity` - `HOUR`, `DAY`, `LIFETIME`
- `start_time` - Start date (YYYY-MM-DD)
- `end_time` - End date (YYYY-MM-DD)

#### Get Campaign Stats

```bash
GET /v1/campaigns/{campaignId}/stats?granularity=DAY&start_time=2026-02-01&end_time=2026-02-14
```

### Targeting

#### Get Countries

```bash
GET /v1/targeting/geo/country
```

#### Get Regions by Country

```bash
GET /v1/targeting/geo/{countryCode}/region
```

Example: `GET /v1/targeting/geo/us/region`

#### Get OS Types

```bash
GET /v1/targeting/device/os_type
```

#### Get Location Categories

```bash
GET /v1/targeting/location/categories_loi
```

### Ads Gallery (Public Ads Library)

The Ads Gallery API provides access to Snapchat's public advertising transparency library. This API does not require authentication but can be accessed through the gateway.

#### List Sponsored Content

```bash
GET /v1/ads_library/sponsored_content
```

**Response:**
```json
{
  "request_status": "SUCCESS",
  "request_id": "...",
  "sponsored_content": [
    {
      "sub_request_status": "SUCCESS",
      "sponsored_content": {
        "id": "...",
        "name": "Content Name",
        "status": "ACTIVE"
      }
    }
  ]
}
```

#### Search Sponsored Content

```bash
POST /v1/ads_library/sponsored_content/search
Content-Type: application/json

{
  "limit": 50
}
```

#### Search Ads

Search for ads in the public Ads Library by advertiser name and country.

```bash
POST /v1/ads_library/ads/search
Content-Type: application/json

{
  "paying_advertiser_name": "Nike",
  "countries": ["fr", "de"],
  "limit": 50
}
```

**Parameters:**
- `paying_advertiser_name` (required) - Advertiser name to search for
- `countries` (required) - Array of lowercase 2-letter ISO country codes (e.g., `["fr", "de", "gb"]`)
- `start_date` - ISO 8601 timestamp for date range start
- `end_date` - ISO 8601 timestamp for date range end
- `status` - Filter by status (e.g., `"ACTIVE"`, `"PAUSED"`)
- `limit` - Number of results to return

**Note:** Not all countries are available in the Ads Library. EU countries (fr, de, gb, etc.) are supported. US ads may not be available due to regional restrictions.

**Response:**
```json
{
  "request_status": "SUCCESS",
  "request_id": "...",
  "paging": {
    "next_link": "..."
  },
  "ad_previews": [
    {
      "sub_request_status": "SUCCESS",
      "ad_preview": {
        "id": "...",
        "name": "Ad Name",
        "ad_account_name": "Advertiser Name",
        "status": "ACTIVE",
        "creative_type": "WEB_VIEW",
        "headline": "Ad Headline",
        "call_to_action": "SHOP NOW"
      }
    }
  ]
}
```

## Pagination

The Snapchat API uses cursor-based pagination with the `limit` parameter (50-1000) and returns a `paging` object with `next_link`.

```bash
GET /v1/adaccounts/{adAccountId}/campaigns?limit=50
```

**Response:**
```json
{
  "request_status": "SUCCESS",
  "campaigns": [...],
  "paging": {
    "next_link": "https://adsapi.snapchat.com/v1/adaccounts/{id}/campaigns?cursor=..."
  }
}
```

To get the next page, use the `next_link` URL (replace host with gateway):

```bash
GET /v1/adaccounts/{adAccountId}/campaigns?cursor=...
```

## Sorting

Some endpoints support sorting with the `sort` parameter:

```bash
GET /v1/adaccounts/{adAccountId}/creatives?sort=updated_at-desc
GET /v1/adaccounts/{adAccountId}/media?sort=created_at-desc
```

Supported values: `updated_at-desc`, `created_at-desc`

## Code Examples

### JavaScript

```javascript
// List organizations
const response = await fetch(
  'https://gateway.maton.ai/snapchat/v1/me/organizations',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.organizations);
```

### Python

```python
import os
import requests

# List organizations
response = requests.get(
    'https://gateway.maton.ai/snapchat/v1/me/organizations',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
print(data['organizations'])
```

### List All Campaigns Example

```python
import os
import requests

org_id = "YOUR_ORG_ID"
headers = {'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}

# Get ad accounts
response = requests.get(
    f'https://gateway.maton.ai/snapchat/v1/organizations/{org_id}/adaccounts',
    headers=headers
)
ad_accounts = response.json()['adaccounts']

# List campaigns for each ad account
for aa in ad_accounts:
    ad_account_id = aa['adaccount']['id']
    campaigns = requests.get(
        f'https://gateway.maton.ai/snapchat/v1/adaccounts/{ad_account_id}/campaigns',
        headers=headers
    ).json()
    print(f"Ad Account: {aa['adaccount']['name']}")
    print(f"Campaigns: {campaigns}")
```

## Notes

- **Monetary Values**: All monetary values use micro-currency (1 USD = 1,000,000 micro)
- **Bulk Operations**: Create/update endpoints accept arrays for batch operations
- **Response Format**: All responses include `request_status`, `request_id`, and entity arrays with `sub_request_status`
- **Timestamps**: Use ISO 8601 format with timezone (e.g., `2026-02-15T00:00:00.000-08:00`)
- **Ads Gallery Countries**: Not all countries are available in the Ads Library. EU countries (fr, de, gb, etc.) are supported.
- **Conversions API**: The Conversions API uses a different base URL (`tr.snapchat.com`) and is not currently routed through this gateway.
- **Public Profile API**: The Public Profile API may not be available or requires separate configuration.
- **IMPORTANT**: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or invalid parameters |
| 401 | Invalid API key or expired token |
| 403 | Permission denied |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Snapchat API |

### Response Error Format

```json
{
  "request_status": "ERROR",
  "request_id": "...",
  "debug_message": "Error details",
  "display_message": "User-friendly message"
}
```

## Resources

- [Snapchat Ads API Introduction](https://developers.snap.com/api/marketing-api/Ads-API/introduction)
- [API Patterns](https://developers.snap.com/api/marketing-api/Ads-API/api-patterns)
- [Campaign Management](https://developers.snap.com/api/marketing-api/Ads-API/campaigns)
- [Creative Management](https://developers.snap.com/api/marketing-api/Ads-API/creatives)
- [Targeting](https://developers.snap.com/api/marketing-api/Ads-API/targeting)
- [Ads Gallery API](https://developers.snap.com/api/marketing-api/Ads-Gallery-Api/using-the-api)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
