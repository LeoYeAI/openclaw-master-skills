# API Reference — Apple Search Ads

Complete endpoint reference for Campaign Management API v5.

## Authentication

### Generate Client Secret (JWT)

```javascript
// Node.js example
const jwt = require('jsonwebtoken');
const fs = require('fs');

function generateClientSecret() {
  const privateKey = fs.readFileSync('AuthKey.p8');
  const now = Math.floor(Date.now() / 1000);
  
  const payload = {
    sub: process.env.ASA_CLIENT_ID,
    aud: 'https://appleid.apple.com',
    iat: now,
    exp: now + (180 * 24 * 60 * 60), // 180 days
    iss: process.env.ASA_TEAM_ID
  };
  
  return jwt.sign(payload, privateKey, {
    algorithm: 'ES256',
    header: {
      alg: 'ES256',
      kid: process.env.ASA_KEY_ID
    }
  });
}
```

### Token Exchange

```bash
curl -X POST "https://appleid.apple.com/auth/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=${ASA_CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "scope=searchadsorg"
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## Apps

### Search Apps

Find apps to promote by name or Adam ID.

```bash
POST /search/apps
```

Request:
```json
{
  "query": "meditation",
  "returnOwnedApps": false,
  "pagination": {
    "offset": 0,
    "limit": 20
  }
}
```

### Get App Eligibility

Check if an app can be promoted.

```bash
GET /apps/{adamId}/eligibilities?countriesOrRegions=US,UK
```

Response:
```json
{
  "data": [
    {
      "countryOrRegion": "US",
      "eligibilityStatus": "ELIGIBLE",
      "supplySource": "APPSTORE_SEARCH_RESULTS"
    }
  ]
}
```

### Get App Details

```bash
GET /apps/{adamId}?include=assets
```

## Campaigns

### List Campaigns

```bash
GET /campaigns?limit=100&offset=0
```

With filters:
```bash
POST /campaigns/find
```

Request:
```json
{
  "conditions": [
    {"field": "status", "operator": "IN", "values": ["ENABLED", "PAUSED"]}
  ],
  "orderBy": [{"field": "name", "sortOrder": "ASCENDING"}],
  "pagination": {"offset": 0, "limit": 100}
}
```

### Create Campaign

```bash
POST /campaigns
```

Request:
```json
{
  "name": "MyApp - US - Brand",
  "adamId": 123456789,
  "countriesOrRegions": ["US"],
  "budgetAmount": {
    "amount": "1000",
    "currency": "USD"
  },
  "dailyBudgetAmount": {
    "amount": "50",
    "currency": "USD"
  },
  "supplySources": ["APPSTORE_SEARCH_RESULTS"],
  "billingEvent": "TAPS",
  "status": "ENABLED",
  "startTime": "2026-01-01T00:00:00.000",
  "endTime": null,
  "locInvoiceDetails": {
    "billingContactEmail": "billing@example.com"
  }
}
```

### Update Campaign

```bash
PUT /campaigns/{campaignId}
```

Request (partial update):
```json
{
  "dailyBudgetAmount": {
    "amount": "75",
    "currency": "USD"
  },
  "status": "PAUSED"
}
```

### Delete Campaign

```bash
DELETE /campaigns/{campaignId}
```

## Ad Groups

### List Ad Groups

```bash
GET /campaigns/{campaignId}/adgroups
```

### Create Ad Group

```bash
POST /campaigns/{campaignId}/adgroups
```

Request:
```json
{
  "name": "Brand Keywords - Exact",
  "defaultBidAmount": {
    "amount": "2.00",
    "currency": "USD"
  },
  "cpaGoal": {
    "amount": "5.00",
    "currency": "USD"
  },
  "automatedKeywordsOptIn": false,
  "startTime": "2026-01-01T00:00:00.000",
  "targetingDimensions": {
    "age": {
      "included": [{"minAge": 18}]
    },
    "gender": {
      "included": ["M", "F"]
    },
    "deviceClass": {
      "included": ["IPHONE", "IPAD"]
    },
    "appDownloaders": {
      "included": [],
      "excluded": [123456789]
    }
  },
  "status": "ENABLED"
}
```

### Targeting Dimensions

| Dimension | Values |
|-----------|--------|
| `age` | `minAge`, `maxAge` (18-65+) |
| `gender` | `M`, `F` |
| `deviceClass` | `IPHONE`, `IPAD` |
| `daypart` | Hours 0-23, local time |
| `adminArea` | State/province codes |
| `locality` | City codes |
| `appDownloaders` | Adam IDs to include/exclude |

## Keywords

### Add Keywords (Bulk)

```bash
POST /campaigns/{campaignId}/adgroups/{adGroupId}/targetingkeywords/bulk
```

Request:
```json
[
  {
    "text": "meditation app",
    "matchType": "EXACT",
    "bidAmount": {"amount": "2.50", "currency": "USD"},
    "status": "ACTIVE"
  },
  {
    "text": "mindfulness",
    "matchType": "BROAD",
    "bidAmount": {"amount": "1.00", "currency": "USD"},
    "status": "ACTIVE"
  }
]
```

### Update Keyword

```bash
PUT /campaigns/{campaignId}/adgroups/{adGroupId}/targetingkeywords/{keywordId}
```

### Add Negative Keywords

```bash
POST /campaigns/{campaignId}/adgroups/{adGroupId}/negativekeywords/bulk
```

Request:
```json
[
  {"text": "free meditation", "matchType": "EXACT"},
  {"text": "meditation music", "matchType": "BROAD"}
]
```

### Campaign-Level Negatives

```bash
POST /campaigns/{campaignId}/negativekeywords/bulk
```

## Creatives & Ads

### List Creatives

```bash
GET /creatives?adamId={adamId}
```

### Create Ad

```bash
POST /campaigns/{campaignId}/adgroups/{adGroupId}/ads
```

Request (default creative):
```json
{
  "name": "Default Ad",
  "creativeType": "DEFAULT_PRODUCT_PAGE",
  "status": "ENABLED"
}
```

Request (Custom Product Page):
```json
{
  "name": "Summer Promo Ad",
  "creativeType": "CUSTOM_PRODUCT_PAGE",
  "productPageId": "cpp-uuid-from-app-store-connect",
  "status": "ENABLED"
}
```

### List Custom Product Pages

```bash
GET /apps/{adamId}/customproductpages
```

## Reports

### Campaign Report

```bash
POST /reports/campaigns
```

Request:
```json
{
  "startTime": "2026-01-01",
  "endTime": "2026-01-31",
  "timeZone": "UTC",
  "granularity": "DAILY",
  "selector": {
    "conditions": [
      {"field": "campaignStatus", "operator": "IN", "values": ["ENABLED"]}
    ],
    "orderBy": [{"field": "localSpend", "sortOrder": "DESCENDING"}],
    "pagination": {"offset": 0, "limit": 100}
  },
  "groupBy": ["countryOrRegion"],
  "returnRowTotals": true,
  "returnGrandTotals": true
}
```

### Available Metrics

| Metric | Description |
|--------|-------------|
| `impressions` | Ad impressions |
| `taps` | Taps on ad |
| `installs` | App installs |
| `newDownloads` | First-time downloads |
| `redownloads` | Re-downloads |
| `latOnInstalls` | LAT-on installs |
| `latOffInstalls` | LAT-off installs |
| `ttr` | Tap-through rate |
| `localSpend` | Spend in local currency |
| `avgCPA` | Average cost per acquisition |
| `avgCPT` | Average cost per tap |
| `conversionRate` | Installs / Taps |

### Search Term Report

```bash
POST /reports/campaigns/{campaignId}/searchterms
```

Request:
```json
{
  "startTime": "2026-01-01",
  "endTime": "2026-01-31",
  "selector": {
    "conditions": [
      {"field": "impressions", "operator": "GREATER_THAN", "values": ["10"]}
    ],
    "orderBy": [{"field": "installs", "sortOrder": "DESCENDING"}],
    "pagination": {"offset": 0, "limit": 1000}
  },
  "returnRowTotals": true
}
```

### Impression Share Report

```bash
POST /reports/campaigns/{campaignId}/impressionshare
```

Request:
```json
{
  "startTime": "2026-01-01",
  "endTime": "2026-01-31",
  "granularity": "DAILY",
  "selector": {
    "pagination": {"offset": 0, "limit": 100}
  }
}
```

## Geolocations

### Search Geolocations

```bash
GET /search/geo?query=california&countryOrRegion=US&entity=AdminArea
```

Entities: `Country`, `AdminArea` (state), `Locality` (city), `DMA` (metro)

## Error Handling

### Error Response Format

```json
{
  "error": {
    "errors": [
      {
        "messageCode": "INVALID_FIELD",
        "message": "Invalid field: budgetAmount",
        "field": "budgetAmount"
      }
    ]
  }
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| `UNAUTHORIZED` | Invalid or expired token |
| `FORBIDDEN` | No access to resource |
| `NOT_FOUND` | Resource doesn't exist |
| `INVALID_FIELD` | Field validation failed |
| `LIMIT_EXCEEDED` | Rate limit hit |

### Rate Limits

- 1000 requests per minute per org
- Batch endpoints count as 1 request
- Use pagination for large datasets
