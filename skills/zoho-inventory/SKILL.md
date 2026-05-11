---
name: zoho-inventory
description: |
  Zoho Inventory API integration with managed OAuth. Manage items, sales orders, invoices, purchase orders, bills, contacts, and shipments.
  Use this skill when users want to read, create, update, or delete inventory items, sales orders, invoices, purchase orders, bills, or other inventory records in Zoho Inventory.
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

# Zoho Inventory

Access the Zoho Inventory API with managed OAuth authentication. Manage items, sales orders, invoices, purchase orders, bills, contacts, shipment orders, and item groups with full CRUD operations.

## Quick Start

```bash
# List items
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/items')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-inventory/inventory/v1/{endpoint}
```

The gateway proxies requests to `www.zohoapis.com/inventory/v1` and automatically injects your OAuth token.

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

Manage your Zoho Inventory OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-inventory&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-inventory'}).encode()
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
    "app": "zoho-inventory",
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

If you have multiple Zoho Inventory connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/items')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Available Modules

| Module | Endpoint | Description |
|--------|----------|-------------|
| Items | `/items` | Products and services |
| Item Groups | `/itemgroups` | Grouped product variants |
| Contacts | `/contacts` | Customers and vendors |
| Sales Orders | `/salesorders` | Sales orders |
| Invoices | `/invoices` | Sales invoices |
| Purchase Orders | `/purchaseorders` | Purchase orders |
| Bills | `/bills` | Vendor bills |
| Shipment Orders | `/shipmentorders` | Shipment tracking |

### Items

#### List Items

```bash
GET /zoho-inventory/inventory/v1/items
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/items')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "items": [
    {
      "item_id": "1234567890000",
      "name": "Widget",
      "status": "active",
      "sku": "WDG-001",
      "rate": 25.00,
      "purchase_rate": 10.00,
      "is_taxable": true
    }
  ],
  "page_context": {
    "page": 1,
    "per_page": 200,
    "has_more_page": false
  }
}
```

#### Get Item

```bash
GET /zoho-inventory/inventory/v1/items/{item_id}
```

#### Create Item

```bash
POST /zoho-inventory/inventory/v1/items
Content-Type: application/json

{
  "name": "Widget",
  "rate": 25.00,
  "purchase_rate": 10.00,
  "sku": "WDG-001",
  "item_type": "inventory",
  "product_type": "goods",
  "unit": "pcs",
  "is_taxable": true
}
```

**Required Fields:**
- `name` - Item name

**Optional Fields:**
- `rate` - Sales price
- `purchase_rate` - Purchase cost
- `sku` - Stock keeping unit (unique)
- `item_type` - `inventory`, `sales`, `purchases`, or `sales_and_purchases`
- `product_type` - `goods` or `service`
- `unit` - Unit of measurement
- `is_taxable` - Tax applicability
- `tax_id` - Tax identifier
- `description` - Item description
- `reorder_level` - Reorder point
- `vendor_id` - Preferred vendor

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "name": "Widget",
    "rate": 25.00,
    "purchase_rate": 10.00,
    "sku": "WDG-001",
    "item_type": "inventory",
    "product_type": "goods",
    "unit": "pcs"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/items', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "code": 0,
  "message": "The item has been added.",
  "item": {
    "item_id": "1234567890000",
    "name": "Widget",
    "status": "active",
    "rate": 25.00,
    "purchase_rate": 10.00,
    "sku": "WDG-001"
  }
}
```

#### Update Item

```bash
PUT /zoho-inventory/inventory/v1/items/{item_id}
Content-Type: application/json

{
  "name": "Updated Widget",
  "rate": 30.00
}
```

#### Delete Item

```bash
DELETE /zoho-inventory/inventory/v1/items/{item_id}
```

#### Item Status Actions

```bash
# Mark as active
POST /zoho-inventory/inventory/v1/items/{item_id}/active

# Mark as inactive
POST /zoho-inventory/inventory/v1/items/{item_id}/inactive
```

### Contacts

#### List Contacts

```bash
GET /zoho-inventory/inventory/v1/contacts
```

**Query Parameters:**
- `filter_by` - `Status.All`, `Status.Active`, `Status.Inactive`, `Status.Duplicate`, `Status.Crm`
- `search_text` - Search across contact fields
- `sort_column` - `contact_name`, `first_name`, `last_name`, `email`, `created_time`, `last_modified_time`
- `contact_name`, `company_name`, `email`, `phone` - Field-specific filters

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/contacts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Contact

```bash
GET /zoho-inventory/inventory/v1/contacts/{contact_id}
```

#### Create Contact

```bash
POST /zoho-inventory/inventory/v1/contacts
Content-Type: application/json

{
  "contact_name": "Acme Corporation",
  "contact_type": "customer",
  "company_name": "Acme Corp",
  "email": "billing@acme.com",
  "phone": "+1-555-1234"
}
```

**Required Fields:**
- `contact_name` - Display name

**Optional Fields:**
- `contact_type` - `customer` or `vendor`
- `company_name` - Legal entity name
- `email` - Email address
- `phone` - Phone number
- `billing_address` - Address object
- `shipping_address` - Address object
- `payment_terms` - Days for payment
- `currency_id` - Currency identifier
- `website` - Website URL

#### Update Contact

```bash
PUT /zoho-inventory/inventory/v1/contacts/{contact_id}
```

#### Delete Contact

```bash
DELETE /zoho-inventory/inventory/v1/contacts/{contact_id}
```

#### Contact Status Actions

```bash
# Mark as active
POST /zoho-inventory/inventory/v1/contacts/{contact_id}/active

# Mark as inactive
POST /zoho-inventory/inventory/v1/contacts/{contact_id}/inactive
```

### Sales Orders

#### List Sales Orders

```bash
GET /zoho-inventory/inventory/v1/salesorders
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/salesorders')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Sales Order

```bash
GET /zoho-inventory/inventory/v1/salesorders/{salesorder_id}
```

#### Create Sales Order

```bash
POST /zoho-inventory/inventory/v1/salesorders
Content-Type: application/json

{
  "customer_id": "1234567890000",
  "date": "2026-02-06",
  "line_items": [
    {
      "item_id": "1234567890001",
      "quantity": 5,
      "rate": 25.00
    }
  ]
}
```

**Required Fields:**
- `customer_id` - Customer identifier
- `line_items` - Array of items with `item_id`, `quantity`, `rate`

**Optional Fields:**
- `salesorder_number` - Auto-generated if not specified (do not specify if auto-generation is enabled)
- `date` - Order date (yyyy-mm-dd)
- `shipment_date` - Expected shipment date
- `reference_number` - External reference
- `notes` - Internal notes
- `terms` - Terms and conditions
- `discount` - Discount percentage or amount
- `shipping_charge` - Shipping cost
- `adjustment` - Price adjustment

#### Update Sales Order

```bash
PUT /zoho-inventory/inventory/v1/salesorders/{salesorder_id}
```

#### Delete Sales Order

```bash
DELETE /zoho-inventory/inventory/v1/salesorders/{salesorder_id}
```

#### Sales Order Status Actions

```bash
# Mark as confirmed
POST /zoho-inventory/inventory/v1/salesorders/{salesorder_id}/status/confirmed

# Mark as void
POST /zoho-inventory/inventory/v1/salesorders/{salesorder_id}/status/void
```

### Invoices

#### List Invoices

```bash
GET /zoho-inventory/inventory/v1/invoices
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/invoices')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Invoice

```bash
GET /zoho-inventory/inventory/v1/invoices/{invoice_id}
```

#### Create Invoice

```bash
POST /zoho-inventory/inventory/v1/invoices
Content-Type: application/json

{
  "customer_id": "1234567890000",
  "line_items": [
    {
      "item_id": "1234567890001",
      "quantity": 5,
      "rate": 25.00
    }
  ]
}
```

**Required Fields:**
- `customer_id` - Customer identifier
- `line_items` - Array of items

**Optional Fields:**
- `invoice_number` - Auto-generated if not specified
- `date` - Invoice date (yyyy-mm-dd)
- `due_date` - Payment due date
- `payment_terms` - Days until due
- `discount` - Discount percentage or amount
- `shipping_charge` - Shipping cost
- `notes` - Internal notes
- `terms` - Terms and conditions

#### Update Invoice

```bash
PUT /zoho-inventory/inventory/v1/invoices/{invoice_id}
```

#### Delete Invoice

```bash
DELETE /zoho-inventory/inventory/v1/invoices/{invoice_id}
```

#### Invoice Status Actions

```bash
# Mark as sent
POST /zoho-inventory/inventory/v1/invoices/{invoice_id}/status/sent

# Mark as draft
POST /zoho-inventory/inventory/v1/invoices/{invoice_id}/status/draft

# Void invoice
POST /zoho-inventory/inventory/v1/invoices/{invoice_id}/status/void
```

#### Invoice Email

```bash
# Email invoice to customer
POST /zoho-inventory/inventory/v1/invoices/{invoice_id}/email

# Get email content template
GET /zoho-inventory/inventory/v1/invoices/{invoice_id}/email
```

#### Invoice Payments

```bash
# List payments applied
GET /zoho-inventory/inventory/v1/invoices/{invoice_id}/payments

# Delete a payment
DELETE /zoho-inventory/inventory/v1/invoices/{invoice_id}/payments/{invoice_payment_id}
```

#### Invoice Credits

```bash
# List credits applied
GET /zoho-inventory/inventory/v1/invoices/{invoice_id}/creditsapplied

# Apply credits
POST /zoho-inventory/inventory/v1/invoices/{invoice_id}/credits

# Delete applied credit
DELETE /zoho-inventory/inventory/v1/invoices/{invoice_id}/creditsapplied/{creditnotes_invoice_id}
```

#### Invoice Comments

```bash
# List comments
GET /zoho-inventory/inventory/v1/invoices/{invoice_id}/comments

# Add comment
POST /zoho-inventory/inventory/v1/invoices/{invoice_id}/comments

# Update comment
PUT /zoho-inventory/inventory/v1/invoices/{invoice_id}/comments/{comment_id}

# Delete comment
DELETE /zoho-inventory/inventory/v1/invoices/{invoice_id}/comments/{comment_id}
```

### Purchase Orders

#### List Purchase Orders

```bash
GET /zoho-inventory/inventory/v1/purchaseorders
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/purchaseorders')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Purchase Order

```bash
GET /zoho-inventory/inventory/v1/purchaseorders/{purchaseorder_id}
```

#### Create Purchase Order

```bash
POST /zoho-inventory/inventory/v1/purchaseorders
Content-Type: application/json

{
  "vendor_id": "1234567890000",
  "line_items": [
    {
      "item_id": "1234567890001",
      "quantity": 100,
      "rate": 10.00
    }
  ]
}
```

**Required Fields:**
- `vendor_id` - Vendor identifier
- `line_items` - Array of items

**Optional Fields:**
- `purchaseorder_number` - Auto-generated if not specified (do not specify if auto-generation is enabled)
- `date` - Order date (yyyy-mm-dd)
- `delivery_date` - Expected delivery date
- `reference_number` - External reference
- `ship_via` - Shipping method
- `notes` - Internal notes
- `terms` - Terms and conditions

#### Update Purchase Order

```bash
PUT /zoho-inventory/inventory/v1/purchaseorders/{purchaseorder_id}
```

#### Delete Purchase Order

```bash
DELETE /zoho-inventory/inventory/v1/purchaseorders/{purchaseorder_id}
```

#### Purchase Order Status Actions

```bash
# Mark as issued
POST /zoho-inventory/inventory/v1/purchaseorders/{purchaseorder_id}/status/issued

# Mark as cancelled
POST /zoho-inventory/inventory/v1/purchaseorders/{purchaseorder_id}/status/cancelled
```

### Bills

#### List Bills

```bash
GET /zoho-inventory/inventory/v1/bills
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-inventory/inventory/v1/bills')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Bill

```bash
GET /zoho-inventory/inventory/v1/bills/{bill_id}
```

#### Create Bill

```bash
POST /zoho-inventory/inventory/v1/bills
Content-Type: application/json

{
  "vendor_id": "1234567890000",
  "bill_number": "BILL-001",
  "date": "2026-02-06",
  "due_date": "2026-03-06",
  "line_items": [
    {
      "item_id": "1234567890001",
      "quantity": 100,
      "rate": 10.00
    }
  ]
}
```

**Required Fields:**
- `vendor_id` - Vendor identifier
- `bill_number` - Unique bill number (required, not auto-generated)
- `date` - Bill date (yyyy-mm-dd)
- `due_date` - Payment due date
- `line_items` - Array of items

**Optional Fields:**
- `reference_number` - External reference
- `notes` - Internal notes
- `terms` - Terms and conditions
- `currency_id` - Currency identifier
- `exchange_rate` - Exchange rate for foreign currency

#### Update Bill

```bash
PUT /zoho-inventory/inventory/v1/bills/{bill_id}
```

#### Delete Bill

```bash
DELETE /zoho-inventory/inventory/v1/bills/{bill_id}
```

#### Bill Status Actions

```bash
# Mark as open
POST /zoho-inventory/inventory/v1/bills/{bill_id}/status/open

# Mark as void
POST /zoho-inventory/inventory/v1/bills/{bill_id}/status/void
```

### Shipment Orders

#### Create Shipment Order

```bash
POST /zoho-inventory/inventory/v1/shipmentorders
Content-Type: application/json

{
  "shipment_number": "SHP-001",
  "date": "2026-02-06",
  "delivery_method": "FedEx",
  "tracking_number": "1234567890"
}
```

**Required Fields:**
- `shipment_number` - Unique shipment number
- `date` - Shipment date
- `delivery_method` - Carrier/delivery method

**Optional Fields:**
- `tracking_number` - Carrier tracking number
- `shipping_charge` - Shipping cost
- `notes` - Internal notes
- `reference_number` - External reference

#### Get Shipment Order

```bash
GET /zoho-inventory/inventory/v1/shipmentorders/{shipmentorder_id}
```

#### Update Shipment Order

```bash
PUT /zoho-inventory/inventory/v1/shipmentorders/{shipmentorder_id}
```

#### Delete Shipment Order

```bash
DELETE /zoho-inventory/inventory/v1/shipmentorders/{shipmentorder_id}
```

#### Mark as Delivered

```bash
POST /zoho-inventory/inventory/v1/shipmentorders/{shipmentorder_id}/status/delivered
```

### Item Groups

#### List Item Groups

```bash
GET /zoho-inventory/inventory/v1/itemgroups
```

#### Get Item Group

```bash
GET /zoho-inventory/inventory/v1/itemgroups/{itemgroup_id}
```

#### Create Item Group

```bash
POST /zoho-inventory/inventory/v1/itemgroups
Content-Type: application/json

{
  "group_name": "T-Shirts",
  "unit": "pcs",
  "items": [
    {
      "name": "T-Shirt - Small",
      "rate": 20.00,
      "purchase_rate": 8.00,
      "sku": "TS-S"
    },
    {
      "name": "T-Shirt - Medium",
      "rate": 20.00,
      "purchase_rate": 8.00,
      "sku": "TS-M"
    }
  ]
}
```

**Required Fields:**
- `group_name` - Group name
- `unit` - Unit of measurement

#### Update Item Group

```bash
PUT /zoho-inventory/inventory/v1/itemgroups/{itemgroup_id}
```

#### Delete Item Group

```bash
DELETE /zoho-inventory/inventory/v1/itemgroups/{itemgroup_id}
```

#### Item Group Status Actions

```bash
# Mark as active
POST /zoho-inventory/inventory/v1/itemgroups/{itemgroup_id}/active

# Mark as inactive
POST /zoho-inventory/inventory/v1/itemgroups/{itemgroup_id}/inactive
```

## Pagination

Zoho Inventory uses page-based pagination:

```bash
GET /zoho-inventory/inventory/v1/items?page=1&per_page=50
```

Response includes pagination info in `page_context`:

```json
{
  "code": 0,
  "message": "success",
  "items": [...],
  "page_context": {
    "page": 1,
    "per_page": 50,
    "has_more_page": true,
    "sort_column": "name",
    "sort_order": "A"
  }
}
```

Continue fetching while `has_more_page` is `true`, incrementing `page` each time.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/zoho-inventory/inventory/v1/items',
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
    'https://gateway.maton.ai/zoho-inventory/inventory/v1/items',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- All successful responses have `code: 0` and a `message` field
- Dates should be in `yyyy-mm-dd` format
- Contact types are `customer` or `vendor`
- Item types: `inventory`, `sales`, `purchases`, `sales_and_purchases`
- Product types: `goods` or `service`
- The `organization_id` parameter is automatically handled by the gateway - you do not need to specify it
- Sales order and purchase order numbers are auto-generated by default - do not specify `salesorder_number` or `purchaseorder_number` unless auto-generation is disabled in settings
- Status action endpoints use POST method (e.g., `/status/confirmed`, `/status/void`)
- Rate limits: 100 requests/minute per organization
- Daily limits vary by plan: Free (1,000), Standard (2,500), Professional (5,000), Premium (7,500), Enterprise (10,000)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho Inventory connection or invalid request |
| 401 | Invalid or missing Maton API key, or OAuth scope mismatch |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho Inventory API |

### Common Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
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

1. Ensure your URL path starts with `zoho-inventory`. For example:

- Correct: `https://gateway.maton.ai/zoho-inventory/inventory/v1/items`
- Incorrect: `https://gateway.maton.ai/inventory/v1/items`

## Resources

- [Zoho Inventory API v1 Introduction](https://www.zoho.com/inventory/api/v1/introduction/)
- [Zoho Inventory Items API](https://www.zoho.com/inventory/api/v1/items/)
- [Zoho Inventory Contacts API](https://www.zoho.com/inventory/api/v1/contacts/)
- [Zoho Inventory Sales Orders API](https://www.zoho.com/inventory/api/v1/salesorders/)
- [Zoho Inventory Invoices API](https://www.zoho.com/inventory/api/v1/invoices/)
- [Zoho Inventory Purchase Orders API](https://www.zoho.com/inventory/api/v1/purchaseorders/)
- [Zoho Inventory Bills API](https://www.zoho.com/inventory/api/v1/bills/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
