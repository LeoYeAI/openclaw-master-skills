---
name: zoho-books
description: |
  Zoho Books API integration with managed OAuth. Manage invoices, contacts, bills, expenses, and other accounting data.
  Use this skill when users want to read, create, update, or delete invoices, contacts, bills, expenses, or other financial records in Zoho Books.
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

# Zoho Books

Access the Zoho Books API with managed OAuth authentication. Manage invoices, contacts, bills, expenses, sales orders, purchase orders, and other accounting data with full CRUD operations.

## Quick Start

```bash
# List contacts
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/contacts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-books/books/v3/{endpoint}
```

The gateway proxies requests to `www.zohoapis.com/books/v3` and automatically injects your OAuth token.

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

Manage your Zoho Books OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-books&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-books'}).encode()
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
    "app": "zoho-books",
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

If you have multiple Zoho Books connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/contacts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Available Modules

Zoho Books organizes data into modules. Key modules include:

| Module | Endpoint | Description |
|--------|----------|-------------|
| Contacts | `/contacts` | Customers and vendors |
| Invoices | `/invoices` | Sales invoices |
| Bills | `/bills` | Vendor bills |
| Expenses | `/expenses` | Business expenses |
| Sales Orders | `/salesorders` | Sales orders |
| Purchase Orders | `/purchaseorders` | Purchase orders |
| Credit Notes | `/creditnotes` | Customer credit notes |
| Recurring Invoices | `/recurringinvoices` | Automated recurring invoices |
| Recurring Bills | `/recurringbills` | Automated recurring bills |

### Contacts

#### List Contacts

```bash
GET /zoho-books/books/v3/contacts
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/contacts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "contacts": [...],
  "page_context": {
    "page": 1,
    "per_page": 200,
    "has_more_page": false,
    "sort_column": "contact_name",
    "sort_order": "A"
  }
}
```

#### Get Contact

```bash
GET /zoho-books/books/v3/contacts/{contact_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/contacts/8527119000000099001')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Contact

```bash
POST /zoho-books/books/v3/contacts
Content-Type: application/json

{
  "contact_name": "Customer Name",
  "contact_type": "customer"
}
```

**Required Fields:**
- `contact_name` - Display name for the contact
- `contact_type` - Either `customer` or `vendor`

**Optional Fields:**
- `company_name` - Legal entity name
- `email` - Email address
- `phone` - Phone number
- `billing_address` - Address object
- `payment_terms` - Days for payment

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "contact_name": "Acme Corporation",
    "contact_type": "customer",
    "company_name": "Acme Corp",
    "email": "billing@acme.com",
    "phone": "+1-555-1234"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/contacts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "code": 0,
  "message": "The contact has been added.",
  "contact": {
    "contact_id": "8527119000000099001",
    "contact_name": "Acme Corporation",
    "company_name": "Acme Corp",
    "contact_type": "customer",
    ...
  }
}
```

#### Update Contact

```bash
PUT /zoho-books/books/v3/contacts/{contact_id}
Content-Type: application/json

{
  "contact_name": "Updated Name",
  "phone": "+1-555-9999"
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "contact_name": "Acme Corporation Updated",
    "phone": "+1-555-9999"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/contacts/8527119000000099001', data=data, method='PUT')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Delete Contact

```bash
DELETE /zoho-books/books/v3/contacts/{contact_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/contacts/8527119000000099001', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "code": 0,
  "message": "The customer has been deleted."
}
```

### Invoices

#### List Invoices

```bash
GET /zoho-books/books/v3/invoices
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/invoices')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Invoice

```bash
GET /zoho-books/books/v3/invoices/{invoice_id}
```

#### Create Invoice

```bash
POST /zoho-books/books/v3/invoices
Content-Type: application/json

{
  "customer_id": "8527119000000099001",
  "line_items": [
    {
      "item_id": "8527119000000100001",
      "quantity": 1,
      "rate": 100.00
    }
  ]
}
```

**Required Fields:**
- `customer_id` - Customer identifier
- `line_items` - Array of items with `item_id` or manual entry

**Optional Fields:**
- `invoice_number` - Auto-generated if not specified
- `date` - Invoice date (yyyy-mm-dd format)
- `due_date` - Payment due date
- `discount` - Percentage or fixed amount
- `payment_terms` - Days until due

#### Update Invoice

```bash
PUT /zoho-books/books/v3/invoices/{invoice_id}
```

#### Delete Invoice

```bash
DELETE /zoho-books/books/v3/invoices/{invoice_id}
```

#### Invoice Actions

```bash
# Mark as sent
POST /zoho-books/books/v3/invoices/{invoice_id}/status/sent

# Void invoice
POST /zoho-books/books/v3/invoices/{invoice_id}/status/void

# Email invoice
POST /zoho-books/books/v3/invoices/{invoice_id}/email
```

### Bills

#### List Bills

```bash
GET /zoho-books/books/v3/bills
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/bills')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Bill

```bash
POST /zoho-books/books/v3/bills
Content-Type: application/json

{
  "vendor_id": "8527119000000099002",
  "bill_number": "BILL-001",
  "date": "2026-02-06",
  "line_items": [
    {
      "account_id": "8527119000000100002",
      "description": "Office Supplies",
      "amount": 150.00
    }
  ]
}
```

**Required Fields:**
- `vendor_id` - Vendor identifier
- `bill_number` - Unique bill number
- `date` - Bill date (yyyy-mm-dd)

#### Update Bill

```bash
PUT /zoho-books/books/v3/bills/{bill_id}
```

#### Delete Bill

```bash
DELETE /zoho-books/books/v3/bills/{bill_id}
```

### Expenses

#### List Expenses

```bash
GET /zoho-books/books/v3/expenses
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-books/books/v3/expenses')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Expense

```bash
POST /zoho-books/books/v3/expenses
Content-Type: application/json

{
  "account_id": "8527119000000100003",
  "date": "2026-02-06",
  "amount": 75.50,
  "paid_through_account_id": "8527119000000100004",
  "description": "Business lunch"
}
```

**Required Fields:**
- `account_id` - Expense account ID
- `date` - Expense date (yyyy-mm-dd)
- `amount` - Expense amount
- `paid_through_account_id` - Payment account ID

**Optional Fields:**
- `description` - Expense details
- `customer_id` - Billable customer ID
- `is_billable` - Boolean for billable expenses
- `project_id` - Associated project

#### Update Expense

```bash
PUT /zoho-books/books/v3/expenses/{expense_id}
```

#### Delete Expense

```bash
DELETE /zoho-books/books/v3/expenses/{expense_id}
```

### Sales Orders

#### List Sales Orders

```bash
GET /zoho-books/books/v3/salesorders
```

#### Create Sales Order

```bash
POST /zoho-books/books/v3/salesorders
```

### Purchase Orders

#### List Purchase Orders

```bash
GET /zoho-books/books/v3/purchaseorders
```

#### Create Purchase Order

```bash
POST /zoho-books/books/v3/purchaseorders
```

### Credit Notes

#### List Credit Notes

```bash
GET /zoho-books/books/v3/creditnotes
```

### Recurring Invoices

#### List Recurring Invoices

```bash
GET /zoho-books/books/v3/recurringinvoices
```

### Recurring Bills

#### List Recurring Bills

```bash
GET /zoho-books/books/v3/recurringbills
```

## Pagination

Zoho Books uses page-based pagination:

```bash
GET /zoho-books/books/v3/contacts?page=1&per_page=50
```

Response includes pagination info in `page_context`:

```json
{
  "code": 0,
  "message": "success",
  "contacts": [...],
  "page_context": {
    "page": 1,
    "per_page": 50,
    "has_more_page": true,
    "sort_column": "contact_name",
    "sort_order": "A"
  }
}
```

Continue fetching while `has_more_page` is `true`, incrementing `page` each time.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/zoho-books/books/v3/contacts',
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
    'https://gateway.maton.ai/zoho-books/books/v3/contacts',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- All successful responses have `code: 0` and a `message` field
- Dates should be in `yyyy-mm-dd` format
- Contact types are `customer` or `vendor`
- Some modules (items, chart of accounts, bank accounts, projects) may require additional OAuth scopes. If you receive a scope error, contact Maton support at support@maton.ai with the specific operations/APIs you need and your use-case
- Rate limits: 100 requests/minute per organization
- Daily limits vary by plan: Free (1,000), Standard (2,000), Professional (5,000), Paid (10,000)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho Books connection or invalid request |
| 401 | Invalid or missing Maton API key, or OAuth scope mismatch |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho Books API |

### Common Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 57 | Not authorized (OAuth scope mismatch) |
| 1 | Invalid value |
| 2 | Mandatory field missing |
| 3 | Resource does not exist |
| 5 | Invalid URL |

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

1. Ensure your URL path starts with `zoho-books`. For example:

- Correct: `https://gateway.maton.ai/zoho-books/books/v3/contacts`
- Incorrect: `https://gateway.maton.ai/books/v3/contacts`

## Resources

- [Zoho Books API v3 Introduction](https://www.zoho.com/books/api/v3/introduction/)
- [Zoho Books Invoices API](https://www.zoho.com/books/api/v3/invoices/)
- [Zoho Books Contacts API](https://www.zoho.com/books/api/v3/contacts/)
- [Zoho Books Bills API](https://www.zoho.com/books/api/v3/bills/)
- [Zoho Books Expenses API](https://www.zoho.com/books/api/v3/expenses/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
