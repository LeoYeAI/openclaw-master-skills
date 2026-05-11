---
name: fundraiseup
description: Interact with FundraiseUp REST API to manage donations, recurring plans, supporters, campaigns, and donor portal access. Process online and offline donations, retrieve fundraising analytics, and integrate with nonprofit CRM systems.
compatibility: 
  - bash_tool
  - web_search
  - web_fetch
metadata:
  author: Amish
  version: 1.0.0
  api_version: v1
  tags:
    - fundraising
    - donations
    - nonprofit
    - payments
    - crm-integration
    - stripe
---

# FundraiseUp API Skill

## Overview
This skill enables Claude to interact with the FundraiseUp REST API for processing donations, managing recurring plans, retrieving supporter data, and accessing fundraising analytics. FundraiseUp is a digital fundraising platform that allows nonprofits to process donations from various channels.

## Configuration
Required environment variables:


```FUNDRAISEUP_API_KEY ```- API Key (e.g., ```ABEDDDD_XSSSHwzZc98KR53CWQeWeclA```)

## Base URL
```
https://api.fundraiseup.com/v1
```

## Authentication

### API Key Generation
1. Go to Dashboard > Settings > API keys
2. Click "Create API key"
3. Enter a descriptive name
4. Select data mode:
   - **Live data**: For production use
   - **Test data**: For testing (keys have `test_` prefix)
5. Select permissions:
   - Retrieve donation data
   - Create new donations
   - Generate Donor Portal access links
6. Save the API key securely (shown only once)

### Authentication Header
All API requests must include the `Authorization` header with Bearer token:

```bash
Authorization: Bearer YOUR_API_KEY
```

### Important Notes
- API keys are scoped to specific accounts/subaccounts
- Parent account API keys cannot create donations for subaccounts
- Only Organization Administrators can create API keys
- Never expose API keys publicly

## Rate Limits
- **8 requests per second**
- **128 requests per minute**
- Implement retry logic with exponential backoff for rate limit handling

## Required Headers
```bash
Content-Type: application/json
Accept: application/json
Authorization: Bearer YOUR_API_KEY
```

---

## API Endpoints

### 1. Donations

#### List Donations
**Endpoint:** `GET /donations`

**Description:** Retrieve all donations with cursor-based pagination.

**Query Parameters:**
- `limit` (optional): Number of records per page (1-100, default: 10)
- `starting_after` (optional): Cursor for pagination (donation ID)
- `ending_before` (optional): Cursor for backward pagination (donation ID)
- Note: `starting_after` and `ending_before` are mutually exclusive

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/donations?limit=50' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

**Response Fields:**
- `id`: Donation identifier
- `created_at`: ISO 8601 timestamp
- `livemode`: Boolean (true for live, false for test)
- `amount`: Donation amount in selected currency
- `amount_in_default_currency`: Amount in organization's default currency
- `currency`: Three-letter ISO code (lowercase)
- `status`: Donation status (e.g., succeeded, pending, failed)
- `campaign`: Campaign details (id, code, name)
- `supporter`: Supporter information
- `recurring_plan`: Recurring plan details (if applicable)
- `designation`: Fund/program designation
- `tribute`: Tribute information (if provided)
- `custom_fields`: Array of custom field values
- `processing_fee`: Processing fee details
- `platform_fee`: Platform fee details
- `fees_covered`: Amount of fees covered by donor

---

#### Get Single Donation
**Endpoint:** `GET /donations/{id}`

**Description:** Retrieve details of a specific donation.

**Path Parameters:**
- `id` (required): Donation ID

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/donations/DFQLCFEP' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

---

#### Create Donation
**Endpoint:** `POST /donations`

**Description:** Create a one-time or recurring donation. API-created donations will have "API" as the donation source.

**Prerequisites:**
- Stripe account connected to FundraiseUp and activated
- Active campaign with money-based payment method
- API key with "create new donations" permission
- Stripe Payment Method ID (created via Stripe API)
- PCI compliance requirements met

**Request Body:**
```json
{
  "campaign_id": "FUNCPJTZZQR",
  "amount": "25.00",
  "currency": "usd",
  "payment_method_id": "pm_1234567890abcdef",
  "supporter": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "mailing_address": {
      "line1": "123 Main St",
      "line2": "Apt 4B",
      "city": "New York",
      "region": "NY",
      "postal_code": "10001",
      "country": "us"
    }
  },
  "recurring_plan": {
    "frequency": "monthly"
  },
  "designation": [
    {
      "id": "EHHJ9R36"
    }
  ],
  "tribute": {
    "type": "in_honor_of",
    "honoree": "Jane Smith"
  },
  "comment": "Monthly donation for general fund",
  "anonymous": false,
  "custom_fields": [
    {
      "name": "referral_source",
      "value": "Email Campaign"
    }
  ]
}
```

**Required Fields:**
- `campaign_id`: Must belong to the account and be active
- `amount`: Decimal string (e.g., "9.99" for USD, "200" for JPY), minimum $1 or equivalent
- `currency`: Three-letter ISO code (lowercase)
- `payment_method_id`: Stripe Payment Method ID
- `supporter.first_name`: Up to 256 characters
- `supporter.last_name`: Up to 256 characters
- `supporter.email`: Valid email address (not verified by API)
- `supporter.phone`: Up to 20 characters (required if campaign requires it)
- `supporter.mailing_address`: Required if campaign requires it

**Optional Fields:**
- `recurring_plan.frequency`: Creates recurring plan ("monthly", "weekly", "quarterly", "yearly", "daily")
- `designation`: Array of designation IDs
- `tribute.type`: "in_honor_of" or "in_memory_of"
- `tribute.honoree`: Name of person being honored
- `comment`: Donation comment
- `anonymous`: Boolean (default: false)
- `custom_fields`: Array of custom field objects

**Example Request:**
```bash
curl --request POST \
  --url 'https://api.fundraiseup.com/v1/donations' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}' \
  --header 'Content-Type: application/json' \
  --data '{
    "campaign_id": "FUNCPJTZZQR",
    "amount": "50.00",
    "currency": "usd",
    "payment_method_id": "pm_1234567890",
    "supporter": {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@example.com"
    }
  }'
```

**Important Notes:**
- All string parameters are trimmed; empty strings converted to null
- Addresses and emails are not formatted or verified
- Only credit card payments are currently supported
- Fees may show as 0 initially until Stripe finalizes (use Events endpoint for finalized fees)

---

#### Update Donation
**Endpoint:** `PATCH /donations/{id}`

**Description:** Update a donation. Updates only allowed within 24 hours of creation and only for API-created donations.

**Path Parameters:**
- `id` (required): Donation ID

**Limitations:**
- Only API-created donations can be updated
- Updates must occur within 24 hours of creation
- No bulk updates supported

---

### 2. Recurring Plans

#### List Recurring Plans
**Endpoint:** `GET /recurring_plans`

**Description:** Retrieve all recurring donation plans.

**Query Parameters:**
- `limit` (optional): Number of records per page (1-100)
- `starting_after` (optional): Cursor for pagination
- `ending_before` (optional): Cursor for backward pagination

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/recurring_plans?limit=50' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

**Response Fields:**
- `id`: Recurring plan identifier
- `created_at`: ISO 8601 timestamp
- `frequency`: "monthly", "weekly", "quarterly", "yearly", or "daily"
- `amount`: Recurring donation amount
- `currency`: Three-letter ISO code
- `status`: Plan status (active, paused, canceled)
- `next_installment_at`: Next scheduled donation date
- `ended_at`: End date (if set)
- `campaign`: Associated campaign details
- `supporter`: Supporter information

---

#### Get Single Recurring Plan
**Endpoint:** `GET /recurring_plans/{id}`

**Description:** Retrieve details of a specific recurring plan.

**Path Parameters:**
- `id` (required): Recurring plan ID

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/recurring_plans/RVSHJNPJ' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

---

#### Update Recurring Plan
**Endpoint:** `PATCH /recurring_plans/{id}`

**Description:** Update a recurring plan. Updates only allowed within 24 hours of creation and only for API-created plans.

---

### 3. Supporters

#### List Supporters
**Endpoint:** `GET /supporters`

**Description:** Retrieve all supporters/donors.

**Query Parameters:**
- `limit` (optional): Number of records per page (1-100)
- `starting_after` (optional): Cursor for pagination
- `ending_before` (optional): Cursor for backward pagination

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/supporters?limit=50' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

**Response Fields:**
- `id`: Supporter identifier
- `created_at`: ISO 8601 timestamp
- `email`: Email address
- `first_name`: First name
- `last_name`: Last name
- `phone`: Phone number
- `mailing_address`: Address details
- `mailing_list_subscribed`: Boolean
- `anonymous`: Boolean
- `employer`: Employer name (if provided)

---

#### Get Single Supporter
**Endpoint:** `GET /supporters/{id}`

**Description:** Retrieve details of a specific supporter.

**Path Parameters:**
- `id` (required): Supporter ID

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/supporters/SXXXXXXX' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

---

### 4. Events

#### List Events
**Endpoint:** `GET /events`

**Description:** Retrieve audit log events for donations, recurring plans, and supporters.

**Query Parameters:**
- `limit` (optional): Number of records per page (1-100)
- `starting_after` (optional): Cursor for pagination
- `ending_before` (optional): Cursor for backward pagination

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/events?limit=50' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

**Use Cases:**
- Track when fees are finalized (look for `donation.success` event)
- Monitor status changes
- Audit trail for compliance
- Integration debugging

---

### 5. Campaigns

#### List Campaigns
**Endpoint:** `GET /campaigns`

**Description:** Retrieve all campaigns.

**Query Parameters:**
- `limit` (optional): Number of records per page (1-100)
- `starting_after` (optional): Cursor for pagination
- `ending_before` (optional): Cursor for backward pagination

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/campaigns' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

**Response Fields:**
- `id`: Campaign identifier
- `code`: Campaign code
- `name`: Campaign name
- `status`: Campaign status

---

#### Get Single Campaign
**Endpoint:** `GET /campaigns/{id}`

**Path Parameters:**
- `id` (required): Campaign ID

---

### 6. Designations

#### List Designations
**Endpoint:** `GET /designations`

**Description:** Retrieve all fund/program designations.

**Example Request:**
```bash
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/designations' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

---

### 7. Donor Portal Access

#### Generate Supporter Portal Link
**Endpoint:** `POST /donor_portal/access_links/supporters/{id}`

**Description:** Generate a secure link for a supporter to access their Donor Portal without logging in.

**Path Parameters:**
- `id` (required): Supporter ID

**Prerequisites:**
- API key with "Generate Donor Portal access links" permission enabled

**Example Request:**
```bash
curl --request POST \
  --url 'https://api.fundraiseup.com/v1/donor_portal/access_links/supporters/64b0ba9d9a19ea001fa3516a' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

**Response:**
```json
{
  "url": "https://yourorg.org/login/?auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Important Security Notes:**
- Links are valid for **1 minute only**
- Should only be used within Donor Portal context
- **Never** share via email, SMS, or public channels
- Provides access to sensitive data (payment methods, donation history, receipts)
- Validate supporter ownership before generating links
- Implement automatic redirect (do not require manual action)

---

#### Generate Recurring Plan Portal Link
**Endpoint:** `POST /donor_portal/access_links/recurring_plans/{id}`

**Description:** Generate a link for a supporter to access a specific recurring plan in the Donor Portal.

**Path Parameters:**
- `id` (required): Recurring plan ID

**Optional Query Parameters:**
- `return_url` (optional): URL to return to after managing the recurring plan

**Example Request:**
```bash
curl --request POST \
  --url 'https://api.fundraiseup.com/v1/donor_portal/access_links/recurring_plans/RVSHJNPJ' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {{FUNDRAISEUP_API_KEY}}'
```

**Response:**
```json
{
  "url": "https://yourorg.org/login/?auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Pagination Best Practices

All list endpoints use cursor-based pagination:

1. **Initial Request:** Set `limit` parameter (1-100)
2. **Next Page:** Use the last item's `id` in `starting_after`
3. **Previous Page:** Use the first item's `id` in `ending_before`
4. **Sorting:** Records sorted by creation date (newest first), then by ID (Z to A)

**Example Pagination Flow:**
```bash
# Page 1
GET /donations?limit=50

# Page 2 (use last donation ID from page 1)
GET /donations?limit=50&starting_after=LAST_DONATION_ID

# Previous page
GET /donations?limit=50&ending_before=FIRST_DONATION_ID
```

---

## Error Handling

### Standard HTTP Response Codes
- `200 OK`: Successful GET request
- `201 Created`: Successful POST request
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Best Practices
1. Implement exponential backoff for rate limits
2. Log all API errors with request details
3. Validate data before sending to API
4. Handle null values gracefully
5. Check for finalized fees using Events endpoint

---

## Code Examples

### Python Example
```python
import requests
import os

API_KEY = os.environ.get('FUNDRAISEUP_API_KEY')
BASE_URL = 'https://api.fundraiseup.com/v1'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# List donations
def get_donations(limit=50):
    url = f'{BASE_URL}/donations'
    params = {'limit': limit}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Create donation
def create_donation(campaign_id, amount, currency, payment_method_id, supporter):
    url = f'{BASE_URL}/donations'
    data = {
        'campaign_id': campaign_id,
        'amount': str(amount),
        'currency': currency,
        'payment_method_id': payment_method_id,
        'supporter': supporter
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Get single donation
def get_donation(donation_id):
    url = f'{BASE_URL}/donations/{donation_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
```

### Node.js Example
```javascript
const axios = require('axios');

const API_KEY = process.env.FUNDRAISEUP_API_KEY;
const BASE_URL = 'https://api.fundraiseup.com/v1';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Accept': 'application/json',
  'Content-Type': 'application/json'
};

// List donations
async function getDonations(limit = 50) {
  const response = await axios.get(`${BASE_URL}/donations`, {
    headers,
    params: { limit }
  });
  return response.data;
}

// Create donation
async function createDonation(campaignId, amount, currency, paymentMethodId, supporter) {
  const response = await axios.post(`${BASE_URL}/donations`, {
    campaign_id: campaignId,
    amount: amount.toString(),
    currency,
    payment_method_id: paymentMethodId,
    supporter
  }, { headers });
  return response.data;
}

// Get single donation
async function getDonation(donationId) {
  const response = await axios.get(`${BASE_URL}/donations/${donationId}`, { headers });
  return response.data;
}
```

### cURL Example with Environment Variable
```bash
# Set your API key as environment variable
export FUNDRAISEUP_API_KEY="your_api_key_here"

# List donations
curl --request GET \
  --url 'https://api.fundraiseup.com/v1/donations?limit=50' \
  --header "Accept: application/json" \
  --header "Authorization: Bearer $FUNDRAISEUP_API_KEY"

# Create donation
curl --request POST \
  --url 'https://api.fundraiseup.com/v1/donations' \
  --header "Accept: application/json" \
  --header "Authorization: Bearer $FUNDRAISEUP_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "campaign_id": "FUNCPJTZZQR",
    "amount": "25.00",
    "currency": "usd",
    "payment_method_id": "pm_1234567890",
    "supporter": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com"
    }
  }'

# Get single donation
curl --request GET \
  --url "https://api.fundraiseup.com/v1/donations/DFQLCFEP" \
  --header "Accept: application/json" \
  --header "Authorization: Bearer $FUNDRAISEUP_API_KEY"
```

---

## Testing

### Test Mode
- Generate API keys with "Test data" mode
- Test keys have `test_` prefix
- Test mode data doesn't affect live data or banking networks
- Use test Stripe Payment Methods for creating test donations

### URL Parameter for Testing
Add `fundraiseupLivemode=no` to any URL for testing without processing real donations

---

## Integration Patterns

### Historical Data Sync
1. Use `limit` parameter to fetch batches (recommended: 50-100)
2. Use `starting_after` with last record ID for next batch
3. Process batches sequentially
4. Implement error handling and retry logic

### Real-time Polling
1. Poll API at regular intervals (respect rate limits)
2. Use Events endpoint to track changes
3. Store last processed record ID
4. Use `starting_after` to get only new records

### Event-Based Integration
- Use Zapier for event triggers (FundraiseUp doesn't support direct webhooks)
- Configure Zapier to trigger on FundraiseUp events
- Trigger sync jobs in your system based on events

---

## Common Use Cases

1. **Processing Offline Donations**
   - Face-to-face fundraising
   - Direct mail donations
   - Telethon pledges
   - Event registrations

2. **CRM Integration**
   - Sync donation data to CRM (Salesforce, HubSpot, etc.)
   - Update supporter records
   - Track recurring plans
   - Generate reports

3. **Analytics and Reporting**
   - Export donation data for BI tools
   - Track campaign performance
   - Analyze donor behavior
   - Calculate lifetime value

4. **Donor Portal Integration**
   - Seamless authentication from custom portals
   - Direct access to recurring plan management
   - Single sign-on experience

---

## Security Best Practices

1. **API Key Management**
   - Store API keys in environment variables (never hardcode)
   - Use separate keys for different integrations
   - Rotate keys periodically
   - Revoke compromised keys immediately

2. **HTTPS Only**
   - All requests must use HTTPS
   - HTTP requests are rejected

3. **Data Validation**
   - Validate all input before sending to API
   - Sanitize user-provided data
   - Check response data before processing

4. **PCI Compliance**
   - Never handle raw card data in your application
   - Use Stripe Payment Methods API for card processing
   - Meet PCI DSS requirements (SAQ D for direct API integration)
   - Consider using Stripe Elements to reduce PCI scope

5. **Donor Portal Security**
   - Validate supporter ownership before generating access links
   - Use automatic redirects (never manual links)
   - Never share access links via email or public channels
   - Access links expire in 1 minute

---

## Limitations and Considerations

1. **Payment Methods:** Currently only credit cards are supported
2. **Updates:** Only allowed within 24 hours of creation, only for API-created records
3. **Bulk Operations:** No bulk update support
4. **Webhooks:** Direct webhooks not supported (use Zapier for events)
5. **Subaccounts:** Parent API keys cannot create donations for subaccounts
6. **Fee Calculations:** Fees may be 0 initially; use Events endpoint for finalized fees
7. **Address Validation:** API does not format or verify addresses
8. **Email Validation:** API does not verify email addresses
9. **Migration:** REST API is not a migration mechanism (use Migration service)

---

## Additional Resources

- Official Documentation: https://fundraiseup.com/docs/rest-api/
- API Resources: https://fundraiseup.com/docs/rest-api-resources/
- Donor Portal Integration: https://fundraiseup.com/docs/seamless-donor-portal/
- Support: https://fundraiseup.com/support/

---

## Troubleshooting

### Common Issues

**401 Unauthorized**
- Check API key is correct and active
- Verify Authorization header format
- Ensure API key has required permissions

**429 Rate Limit Exceeded**
- Implement exponential backoff
- Reduce request frequency
- Batch operations where possible

**400 Bad Request**
- Validate all required fields are present
- Check data types and formats
- Ensure currency codes are lowercase
- Verify amount format (decimal string)

**Fees Showing as 0**
- Fees are finalized asynchronously
- Use Events endpoint to get finalized fees
- Look for `donation.success` event

**Cannot Update Donation**
- Verify donation was created via API
- Ensure update is within 24 hours
- Check API key permissions

---

## Version Information
- API Version: v1
- Last Updated: February 2026
- Supported Payment Methods: Credit Card only