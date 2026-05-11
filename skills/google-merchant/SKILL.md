---
name: google-merchant
description: |
  Google Merchant Center API integration with managed OAuth. Manage products, inventories, data sources, promotions, and reports for Google Shopping.
  Use this skill when users want to manage their Merchant Center product catalog, check product status, configure data sources, or analyze shopping performance.
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

# Google Merchant Center

Access the Google Merchant Center API with managed OAuth authentication. Manage products, inventories, promotions, data sources, and reports for Google Shopping.

## Quick Start

```bash
# List products in your Merchant Center account
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-merchant/products/v1/accounts/{accountId}/products')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/google-merchant/{sub-api}/{version}/accounts/{accountId}/{resource}
```

The Merchant API uses a modular sub-API structure. Replace:
- `{sub-api}` with the service: `products`, `accounts`, `datasources`, `reports`, `promotions`, `inventories`, `notifications`, `conversions`
- `{version}` with `v1`
- `{accountId}` with your Merchant Center account ID

The gateway proxies requests to `merchantapi.googleapis.com` and automatically injects your OAuth token.

**Important:** The v1 API requires one-time developer registration. See [Developer Registration](#developer-registration) section.

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

### Finding Your Merchant Center Account ID

Your Merchant Center account ID is a numeric identifier. To find it:

1. Log in to [Google Merchant Center](https://merchants.google.com/)
2. Look at the URL - it contains your account ID: `https://merchants.google.com/mc/overview?a=ACCOUNT_ID`

## Developer Registration

**Important:** Before using the v1 API, you must complete a one-time developer registration to associate your account with the API.

### Step 1: Get Your Account ID

**Option A: Try fetching via API first**

Try listing accounts using the v1beta endpoint. If this works, you can get your account ID automatically:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-merchant/accounts/v1beta/accounts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
try:
    result = json.load(urllib.request.urlopen(req))
    for account in result.get('accounts', []):
        print(f"Account ID: {account['accountId']}, Name: {account['accountName']}")
except Exception as e:
    print(f"v1beta not available - use Option B to get your account ID manually")
EOF
```

**Option B: From Merchant Center UI (if Option A fails)**

If the v1beta endpoint is unavailable or returns an error:

1. Log in to [Google Merchant Center](https://merchants.google.com/)
2. Your account ID is in the URL: `https://merchants.google.com/mc/overview?a=YOUR_ACCOUNT_ID`

For example, if your URL is `https://merchants.google.com/mc/overview?a=123456789`, your account ID is `123456789`.

### Step 2: Register for API Access

Call the `registerGcp` endpoint with your account ID and email:

```bash
python <<'EOF'
import urllib.request, os, json

account_id = 'YOUR_ACCOUNT_ID'  # From Step 1
developer_email = 'your-email@example.com'  # Your Google account email

data = json.dumps({'developerEmail': developer_email}).encode()
req = urllib.request.Request(
    f'https://gateway.maton.ai/google-merchant/accounts/v1/accounts/{account_id}/developerRegistration:registerGcp',
    data=data,
    method='POST'
)
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')

result = json.load(urllib.request.urlopen(req))
print(json.dumps(result, indent=2))
EOF
```

**Response:**
```json
{
  "name": "accounts/123456789/developerRegistration",
  "gcpIds": ["216141799266"]
}
```

### Step 3: Verify Registration

After registration, v1 endpoints will work:

```bash
python <<'EOF'
import urllib.request, os, json
account_id = 'YOUR_ACCOUNT_ID'
req = urllib.request.Request(f'https://gateway.maton.ai/google-merchant/accounts/v1/accounts/{account_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Note:** Registration only needs to be done once per Merchant Center account. After registration, all v1 endpoints will work for that account.

## Connection Management

Manage your Google Merchant OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=google-merchant&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'google-merchant'}).encode()
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
    "connection_id": "00726960-095e-47e2-92e6-6e9cdf3e40a1",
    "status": "ACTIVE",
    "creation_time": "2026-02-07T06:41:22.751289Z",
    "last_updated_time": "2026-02-07T06:42:29.411979Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "google-merchant",
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

If you have multiple Google Merchant connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-merchant/products/v1/accounts/123456/products')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '00726960-095e-47e2-92e6-6e9cdf3e40a1')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Sub-API Structure

The Merchant API is organized into sub-APIs:

| Sub-API | Purpose | Version |
|---------|---------|---------|
| `products` | Product catalog management | v1 |
| `accounts` | Account settings and users | v1 |
| `datasources` | Data source configuration | v1 |
| `reports` | Analytics and reporting | v1 |
| `promotions` | Promotional offers (requires enrollment) | v1 |
| `inventories` | Local and regional inventory | v1 |
| `notifications` | Webhook subscriptions | v1 |
| `conversions` | Conversion tracking | v1 |

### Accounts

#### List Accounts

```bash
GET /google-merchant/accounts/v1/accounts
```

Returns all Merchant Center accounts accessible with your OAuth credentials. Use this to find your account ID.

#### Get Account

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}
```

#### List Sub-accounts

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}:listSubaccounts
```

**Note:** This endpoint only works for multi-client accounts (MCAs). Standard merchant accounts will receive a 403 error.

#### Get Business Info

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/businessInfo
```

#### Update Business Info

```bash
PATCH /google-merchant/accounts/v1/accounts/{accountId}/businessInfo?updateMask=customerService
Content-Type: application/json

{
  "customerService": {
    "email": "support@example.com"
  }
}
```

#### Get Homepage

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/homepage
```

#### Get Shipping Settings

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/shippingSettings
```

#### Insert Shipping Settings

```bash
POST /google-merchant/accounts/v1/accounts/{accountId}/shippingSettings:insert
Content-Type: application/json

{
  "services": [
    {
      "serviceName": "Standard Shipping",
      "deliveryCountries": ["US"],
      "currencyCode": "USD",
      "deliveryTime": {
        "minTransitDays": 3,
        "maxTransitDays": 7,
        "minHandlingDays": 0,
        "maxHandlingDays": 1
      },
      "rateGroups": [
        {
          "singleValue": {
            "flatRate": {
              "amountMicros": "0",
              "currencyCode": "USD"
            }
          }
        }
      ],
      "active": true
    }
  ]
}
```

#### List Users

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/users
```

#### Get User

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/users/{email}
```

#### List Programs

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/programs
```

#### List Regions

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/regions
```

#### List Account Issues

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/issues
```

#### List Online Return Policies

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/onlineReturnPolicies
```

### Products

#### List Products

```bash
GET /google-merchant/products/v1/accounts/{accountId}/products
```

Query parameters:
- `pageSize` (integer): Maximum results per page
- `pageToken` (string): Pagination token

#### Get Product

```bash
GET /google-merchant/products/v1/accounts/{accountId}/products/{productId}
```

Product ID format: `contentLanguage~feedLabel~offerId` (e.g., `en~US~sku123`)

#### Insert Product Input

```bash
POST /google-merchant/products/v1/accounts/{accountId}/productInputs:insert?dataSource=accounts/{accountId}/dataSources/{dataSourceId}
Content-Type: application/json

{
  "offerId": "sku123",
  "contentLanguage": "en",
  "feedLabel": "US",
  "productAttributes": {
    "title": "Product Title",
    "description": "Product description",
    "link": "https://example.com/product",
    "imageLink": "https://example.com/image.jpg",
    "availability": "in_stock",
    "price": {
      "amountMicros": "19990000",
      "currencyCode": "USD"
    },
    "condition": "new"
  }
}
```

**Note:** Products can only be inserted into data sources with `input: "API"` type. Create an API data source first if needed.

#### Delete Product Input

```bash
DELETE /google-merchant/products/v1/accounts/{accountId}/productInputs/{productId}?dataSource=accounts/{accountId}/dataSources/{dataSourceId}
```

### Inventories

#### List Local Inventories

```bash
GET /google-merchant/inventories/v1/accounts/{accountId}/products/{productId}/localInventories
```

**Note:** Local inventories are only available for products with `LOCAL` channel. Use a product ID like `local~en~US~sku123`.

#### Insert Local Inventory

```bash
POST /google-merchant/inventories/v1/accounts/{accountId}/products/{productId}/localInventories:insert
Content-Type: application/json

{
  "storeCode": "store123"
}
```

**Note:** The `storeCode` must be a valid store code configured in your Merchant Center account. Additional inventory attributes may be available - refer to the [Google Merchant API Reference](https://developers.google.com/merchant/api/reference/rest) for the complete field list.

#### List Regional Inventories

```bash
GET /google-merchant/inventories/v1/accounts/{accountId}/products/{productId}/regionalInventories
```

### Data Sources

#### List Data Sources

```bash
GET /google-merchant/datasources/v1/accounts/{accountId}/dataSources
```

#### Get Data Source

```bash
GET /google-merchant/datasources/v1/accounts/{accountId}/dataSources/{dataSourceId}
```

#### Create Data Source

```bash
POST /google-merchant/datasources/v1/accounts/{accountId}/dataSources
Content-Type: application/json

{
  "displayName": "API Data Source",
  "primaryProductDataSource": {
    "feedLabel": "US",
    "contentLanguage": "en"
  }
}
```

**Response:**
```json
{
  "name": "accounts/123456/dataSources/789",
  "dataSourceId": "789",
  "displayName": "API Data Source",
  "primaryProductDataSource": {
    "feedLabel": "US",
    "contentLanguage": "en"
  },
  "input": "API"
}
```

#### Update Data Source

```bash
PATCH /google-merchant/datasources/v1/accounts/{accountId}/dataSources/{dataSourceId}?updateMask=displayName
Content-Type: application/json

{
  "displayName": "Updated Name"
}
```

#### Delete Data Source

```bash
DELETE /google-merchant/datasources/v1/accounts/{accountId}/dataSources/{dataSourceId}
```

#### Fetch Data Source (trigger immediate refresh)

```bash
POST /google-merchant/datasources/v1/accounts/{accountId}/dataSources/{dataSourceId}:fetch
```

**Note:** Fetch only works for data sources with `FILE` input type. API and UI data sources cannot be fetched.

### Reports

#### Search Reports

```bash
POST /google-merchant/reports/v1/accounts/{accountId}/reports:search
Content-Type: application/json

{
  "query": "SELECT offer_id, title, clicks, impressions FROM product_performance_view WHERE date BETWEEN '2026-01-01' AND '2026-01-31'"
}
```

**Example: Query product_view (requires `id` field):**
```json
{
  "query": "SELECT id, offer_id, title, item_issues FROM product_view LIMIT 10"
}
```

**Note:** The `product_view` table requires the `id` field in the SELECT clause.

Available report tables:
- `product_performance_view` - Clicks, impressions, CTR by product
- `product_view` - Current inventory with attributes and issues (requires `id` in SELECT)
- `price_competitiveness_product_view` - Pricing vs competitors (requires Market Insights)
- `price_insights_product_view` - Suggested pricing
- `best_sellers_product_cluster_view` - Best sellers by category (requires Market Insights)
- `competitive_visibility_competitor_view` - Competitor visibility

### Promotions

**Note:** Promotions require your Merchant Center account to be enrolled in the Promotions program. You'll receive a 403 error if not enrolled.

#### List Promotions

```bash
GET /google-merchant/promotions/v1/accounts/{accountId}/promotions
```

#### Get Promotion

```bash
GET /google-merchant/promotions/v1/accounts/{accountId}/promotions/{promotionId}
```

#### Insert Promotion

```bash
POST /google-merchant/promotions/v1/accounts/{accountId}/promotions:insert
Content-Type: application/json

{
  "promotionId": "promo123",
  "contentLanguage": "en",
  "targetCountry": "US",
  "redemptionChannel": ["ONLINE"],
  "attributes": {
    "longTitle": "20% off all products",
    "promotionEffectiveDates": "2026-02-01T00:00:00Z/2026-02-28T23:59:59Z"
  }
}
```

### Notifications

#### List Notification Subscriptions

```bash
GET /google-merchant/notifications/v1/accounts/{accountId}/notificationsubscriptions
```

#### Create Notification Subscription

```bash
POST /google-merchant/notifications/v1/accounts/{accountId}/notificationsubscriptions
Content-Type: application/json

{
  "registeredEvent": "PRODUCT_STATUS_CHANGE",
  "callBackUri": "https://example.com/webhook",
  "allManagedAccounts": true
}
```

**Note:** You must specify either `allManagedAccounts: true` OR `targetAccount: "accounts/{accountId}"` to indicate which accounts the subscription applies to.

**Alternative with targetAccount:**
```json
{
  "registeredEvent": "PRODUCT_STATUS_CHANGE",
  "callBackUri": "https://example.com/webhook",
  "targetAccount": "accounts/123456789"
}
```

#### Delete Notification Subscription

```bash
DELETE /google-merchant/notifications/v1/accounts/{accountId}/notificationsubscriptions/{subscriptionId}
```

### Conversion Sources

#### List Conversion Sources

```bash
GET /google-merchant/conversions/v1/accounts/{accountId}/conversionSources
```

#### Create Conversion Source

```bash
POST /google-merchant/conversions/v1/accounts/{accountId}/conversionSources
Content-Type: application/json

{
  "merchantCenterDestination": {
    "displayName": "My Conversion Source",
    "destination": "SHOPPING_ADS",
    "currencyCode": "USD",
    "attributionSettings": {
      "attributionLookbackWindowDays": 30,
      "attributionModel": "CROSS_CHANNEL_LAST_CLICK"
    }
  }
}
```

#### Delete Conversion Source

```bash
DELETE /google-merchant/conversions/v1/accounts/{accountId}/conversionSources/{conversionSourceId}
```

## Pagination

The API uses token-based pagination:

```bash
GET /google-merchant/products/v1/accounts/{accountId}/products?pageSize=50
```

Response includes `nextPageToken` when more results exist:

```json
{
  "products": [...],
  "nextPageToken": "CAE..."
}
```

Use the token for the next page:

```bash
GET /google-merchant/products/v1/accounts/{accountId}/products?pageSize=50&pageToken=CAE...
```

## Code Examples

### JavaScript

```javascript
const accountId = '123456789';
const response = await fetch(
  `https://gateway.maton.ai/google-merchant/products/v1/accounts/${accountId}/products`,
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

account_id = '123456789'
response = requests.get(
    f'https://gateway.maton.ai/google-merchant/products/v1/accounts/{account_id}/products',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- **Developer registration required** - You must complete [Developer Registration](#developer-registration) once per Merchant Center account before using v1 endpoints
- Product IDs use the format `contentLanguage~feedLabel~offerId` (e.g., `en~US~sku123`)
- Products can only be inserted/updated/deleted in data sources with `input: "API"` type
- After inserting/updating a product, it may take several minutes before the processed product appears
- Monetary values use micros (divide by 1,000,000 for actual value)
- Local inventories only work for products with `LOCAL` channel (not `ONLINE`)
- The Promotions API requires your account to be enrolled in the Promotions program
- List Sub-accounts only works for multi-client accounts (MCAs)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Invalid request or missing Google Merchant connection |
| 401 | Invalid/missing Maton API key, or GCP project not registered (see [Developer Registration](#developer-registration)) |
| 403 | Permission denied - account not enrolled in required program or feature not available |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Google Merchant API |

### Common Errors

**"GCP project is not registered"**: You need to complete developer registration. See [Developer Registration](#developer-registration) section.

**"The caller does not have access to the accounts"**: The specified account ID is not accessible with your OAuth credentials. Verify you have access to the Merchant Center account.

**"Promotion program not enabled"**: Your Merchant Center account is not enrolled in the Promotions program. Enable it in Merchant Center settings.

**"This method can only be accessed by multi-client accounts"**: You're calling an endpoint (like listSubaccounts) that only works for multi-client accounts (MCAs).

**"Mismatched channel"**: You're trying to access local inventories for an ONLINE product. Local inventories only work with LOCAL channel products.

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

Ensure your URL path starts with `google-merchant`. For example:

- Correct: `https://gateway.maton.ai/google-merchant/products/v1/accounts/{accountId}/products`
- Incorrect: `https://gateway.maton.ai/products/v1/accounts/{accountId}/products`

### Troubleshooting: 401 GCP Project Not Registered

If you see an error like "GCP project is not registered with the merchant account":

1. **Complete developer registration** - See [Developer Registration](#developer-registration) section
2. Get your account ID from Merchant Center UI (in the URL after `?a=`)
3. Call the `registerGcp` endpoint with your account ID and email
4. After successful registration, retry your original request

## Resources

- [Merchant API Overview](https://developers.google.com/merchant/api/overview)
- [Merchant API Reference](https://developers.google.com/merchant/api/reference/rest)
- [Products Guide](https://developers.google.com/merchant/api/guides/products/overview)
- [Data Sources Guide](https://developers.google.com/merchant/api/guides/datasources)
- [Reports Guide](https://developers.google.com/merchant/api/guides/reports)
- [Product Data Specification](https://support.google.com/merchants/answer/7052112)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
