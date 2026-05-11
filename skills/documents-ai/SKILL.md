---
name: veryfi-documents-ai
description: Real-time OCR and data extraction API by Veryfi (https://veryfi.com). Extract structured data from receipts, invoices, bank statements, W-9s, purchase orders, bills of lading, and any other document. Use when you need to OCR documents, extract fields, parse receipts/invoices, bank statements, classify documents, detect fraud, or get raw OCR text from any document.
metadata:
  openclaw:
    requires:
      env:
        - VERYFI_CLIENT_ID
        - VERYFI_USERNAME
        - VERYFI_API_KEY
    primaryEnv: VERYFI_CLIENT_ID
---

# Documents AI by Veryfi

Real-time OCR and data extraction API — extract structured data from receipts, invoices, bank statements, W-9s, purchase orders, and more, with document classification, fraud detection, and raw OCR text output.

> **Get your API key:** https://app.veryfi.com/api/settings/keys/
> **Learn more:** https://veryfi.com

## Quick Start

For Receipts and Invoices:
```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/documents/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@invoice.pdf"
```

Response:
```json
{
  "id": 62047612,
  "created_date": "2026-02-19",
  "currency_code": "USD",
  "date": "2026-02-18 14:22:00",
  "document_type": "receipt",
  "category": "Meals & Entertainment",
  "is_duplicate": false,
  "vendor": {
    "name": "Starbucks",
    "address": "123 Main St, San Francisco, CA 94105"
  },
  "line_items": [
    {
      "id": 1,
      "order": 0,
      "description": "Caffe Latte Grande",
      "quantity": 1,
      "price": 5.95,
      "total": 5.95,
      "type": "food"
    }
  ],
  "subtotal": 5.95,
  "tax": 0.52,
  "total": 6.47,
  "payment": {
    "type": "visa",
    "card_number": "1234"
  },
  "ocr_text": "STARBUCKS\n123 Main St...",
  "img_url": "https://scdn.veryfi.com/documents/...",
  "pdf_url": "https://scdn.veryfi.com/documents/..."
}
```

For Bank Statements:
```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/bank-statements/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@bank-statement.pdf"
```

Response:
```json
{
  "id": 4820193,
  "created_date": "2026-02-19T12:45:00.000000Z",
  "bank_name": "Chase",
  "bank_address": "270 Park Avenue, New York, NY 10017",
  "account_holder_name": "Jane Doe",
  "account_holder_address": "456 Oak Ave, San Francisco, CA 94110",
  "account_number": "****7890",
  "account_type": "Checking",
  "routing_number": "021000021",
  "currency_code": "USD",
  "statement_date": "2026-01-31",
  "period_start_date": "2026-01-01",
  "period_end_date": "2026-01-31",
  "beginning_balance": 12500.00,
  "ending_balance": 11835.47,
  "accounts": [
    {
      "number": "****7890",
      "beginning_balance": 12500.00,
      "ending_balance": 11835.47,
      "summaries": [
        { "name": "Total Deposits", "total": 3200.00 },
        { "name": "Total Withdrawals", "total": 3864.53 }
      ],
      "transactions": [
        {
          "order": 0,
          "date": "2026-01-05",
          "description": "Direct Deposit - ACME Corp Payroll",
          "credit_amount": 3200.00,
          "debit_amount": null,
          "balance": 15700.00,
          "category": "Income"
        },
        {
          "order": 1,
          "date": "2026-01-12",
          "description": "Rent Payment - 456 Oak Ave",
          "credit_amount": null,
          "debit_amount": 2800.00,
          "balance": 12900.00,
          "category": "Housing"
        },
        {
          "order": 2,
          "date": "2026-01-20",
          "description": "PG&E Utility Bill",
          "credit_amount": null,
          "debit_amount": 1064.53,
          "balance": 11835.47,
          "category": "Utilities"
        }
      ]
    }
  ],
  "pdf_url": "https://scdn.veryfi.com/bank-statements/...",
  "img_url": "https://scdn.veryfi.com/bank-statements/..."
}
```

## Setup

### 1. Get Your API Key

```bash
# Visit API Auth Credentials page
https://app.veryfi.com/api/settings/keys/
```

Save your API keys:
```bash
export VERYFI_CLIENT_ID="your_client_id_here"
export VERYFI_USERNAME="your_username_here"
export VERYFI_API_KEY="your_api_key_here"
```

### 2. OpenClaw Configuration (Optional)

**Recommended: Use environment variables** (most secure):
```json5
{
  skills: {
    entries: {
      "veryfi-documents-ai": {
        enabled: true,
        // Keys loaded from environment variables:
        // VERYFI_CLIENT_ID, VERYFI_USERNAME, VERYFI_API_KEY
      },
    },
  },
}
```

**Alternative: Store in config file** (use with caution):
```json5
{
  skills: {
    entries: {
      "veryfi-documents-ai": {
        enabled: true,
        env: {
          VERYFI_CLIENT_ID: "your_client_id_here",
          VERYFI_USERNAME: "your_username_here",
          VERYFI_API_KEY: "your_api_key_here",
        },
      },
    },
  },
}
```

**Security Note:** If storing API keys in `~/.openclaw/openclaw.json`:
- Set file permissions: `chmod 600 ~/.openclaw/openclaw.json`
- Never commit this file to version control
- Prefer environment variables or your agent's secret store when possible
- Rotate keys regularly and limit API key permissions if supported

## Common Tasks

### Extract data from a Receipt or Invoice (file upload)

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/documents/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@invoice.pdf"
```

### Extract data from a Receipt or Invoice (base64)

When your agent already has the document as base64-encoded content (e.g., received via API, email attachment, or tool output), use `file_data` instead of uploading a file:

```bash
# Encode the file first
BASE64_DATA=$(base64 -i invoice.pdf)

curl -X POST "https://api.veryfi.com/api/v8/partner/documents/" \
  -H "Content-Type: application/json" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -d "{
    \"file_name\": \"invoice.pdf\",
    \"file_data\": \"$BASE64_DATA\"
  }"
```

### Extract data from a URL

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/documents/" \
  -H "Content-Type: application/json" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -d '{
    "file_url": "https://example.com/invoice.pdf"
  }'
```

### Extract data from a Passport

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/any-documents/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@passport.jpg" \
  -F "blueprint_name=passport"
```

### Extract data from Checks

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/checks/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@check.jpg"
```

### Extract data from W-9s

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/w9s/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@w9.pdf"
```

### Extract data from W-2s and W-8s

W-2 and W-8 forms do not have dedicated endpoints. Use the `any-documents` endpoint with the appropriate blueprint:

```bash
# W-2
curl -X POST "https://api.veryfi.com/api/v8/partner/any-documents/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@w2.pdf" \
  -F "blueprint_name=w2"

# W-8
curl -X POST "https://api.veryfi.com/api/v8/partner/any-documents/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@w8.pdf" \
  -F "blueprint_name=w8"
```

> **Note:** W-2 and W-8 appear as classification types (via `/classify/`) but their extraction is handled through the Any Document endpoint. Do **not** POST to `/api/v8/partner/w2s/` or `/api/v8/partner/w8s/` — those endpoints do not exist.

### Get Raw OCR Text from a Document

All extraction endpoints return an `ocr_text` field in the response containing the raw text content of the document as a plain string. This is useful when you want to process the text yourself or pass it to an LLM.

```bash
# Extract and pull ocr_text with jq
curl -X POST "https://api.veryfi.com/api/v8/partner/documents/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@document.pdf" \
  | jq '.ocr_text'
```

> **Note:** `ocr_text` is plain text, not markdown. If you need markdown-formatted output, pass `ocr_text` to an LLM for reformatting after extraction.

### Classify a Document

Identify the document type without full data extraction. Useful for routing documents to the correct processing endpoint, pre-filtering uploads, or bulk sorting.

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/classify/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@document.pdf"
```

> **Note:** By default, the API classifies against 15 built-in types. You can also pass a `document_types` array with custom classes (see example below).

Response:
```json
{
  "id": 81023456,
  "document_type": {
    "score": 0.97,
    "value": "invoice"
  }
}
```

Default document types: `receipt`, `invoice`, `purchase_order`, `bank_statement`, `check`, `w2`, `w8`, `w9`, `statement`, `contract`, `credit_note`, `remittance_advice`, `business_card`, `packing_slip`, `other`.

To classify against custom types, pass a `document_types` array:
```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/classify/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@document.pdf" \
  -F 'document_types=["lease_agreement", "utility_bill", "pay_stub"]'
```

## Advanced Features

### Bounding Boxes for Receipts, Invoices, Checks and Bank Statements APIs
Get element coordinates for layout analysis:
```bash
-F "bounding_boxes=true" 
-F "confidence_details=true"
```


## When to Use

### Use Veryfi Documents AI For:
- Invoice and receipt data extraction
- Processing Bank Statements
- Extracting data from Checks
- Document classification and routing
- Extracting data from any other document
- Getting raw OCR text from a document

### Don't Use For:
- Video or audio transcription
- Web search or real-time data lookup
- Image generation or editing
- Non-document binary files (spreadsheets, code, executables)
- Documents you haven't confirmed are cleared for third-party processing (see Security section)

## Best Practices

| Document Type | Endpoint | Notes |
|---------------|----------|------------|
| Receipts & Invoices | `/api/v8/partner/documents/` | use for receipts/invoices/purchase orders |
| Bank Statements | `/api/v8/partner/bank-statements/` | use for Bank statements |
| Checks | `/api/v8/partner/checks/` | use for bank checks (cheques in Canada) |
| W-9s | `/api/v8/partner/w9s/` | W9 forms |
| W-2s / W-8s | `/api/v8/partner/any-documents/` | Use blueprint_name=w2 or blueprint_name=w8 |
| Any Document | `/api/v8/partner/any-documents/` | Use to extract data from any document; list of blueprints provided below |
| Classify | `/api/v8/partner/classify/` | Identify document type without full extraction |



List of available blueprints:
| blueprint_name | Document Type |
|---------------|----------|
| passport | Passport US or International |
| incorporation_document | Certificate of Company Incorporation |
| us_driver_license | US Driver's License |
| uk_drivers_license | UK Driver's Licence |
| us_health_insurance_card | US Health Insurance Card |
| prescription_medication_label | Prescription Medication Label |
| medication_instructions | Medication Instructions |
| vision_prescription | Vision Prescription |
| auto_insurance_card | Auto Insurance Card |
| restaurant_menu | Restaurant Menu |
| drinks_menu | Drinks Menu |
| product_nutrition_facts | Product Nutrition Facts Label |
| goods_received_note | Goods Received Note |
| vendor_statement | Vendor Statement |
| flight_itinerary | Flight Itinerary |
| bill_of_lading | Bill of Lading |
| air_waybill | Air Waybill |
| freight_invoice | Freight Invoice |
| shipping_label | Shipping Label |
| vehicle_registration | Vehicle Registration |
| work_order | Work Order |
| settlement_letter | Settlement Letter |
| construction_estimate | Construction Estimate |
| diploma | Diploma or Degree Certificate |
| price_sheet | Price Sheet |
| mortgage_application_form | Mortgage Application Form |
| lab_test_request_form | Lab Test Request Form |
| construction_snapshot | Construction Snapshot |
| medical_prescription_list | Medical Prescription List |
| v5c | UK Vehicle Registration Certificate (V5C) |
| bank_account_verification_letter | Bank Account Verification Letter |
| annual_mortgage_statement | Annual Mortgage Statement |
| investment_account_statement | Investment Account Statement |
| certificate_of_good_standing | Certificate of Good Standing |
| w2 | IRS W-2 Wage and Tax Statement |
| w8 | IRS W-8 Certificate of Foreign Status |

**Missing document type?**
If document type (blueprint) you need to extract data from is missing, create one here: 
`https://app.veryfi.com/inboxes/anydocs?tab=blueprints`

**Bounding Boxes & Confidence:**
- Add `-F "bounding_boxes=true"` for element coordinates
- Add `-F "confidence_details=true"` for per-field confidence scores

**Supported Inputs:**
- `file` — multipart file upload
- `file_url` — publicly accessible URL
- `file_data` — base64-encoded content (send as JSON body with `file_name` + `file_data` fields)

## Response Schemas

### Receipt / Invoice (`/api/v8/partner/documents/`)

```json
{
  "id": 62047612,
  "created_date": "2026-02-19T00:00:00.000000Z",
  "updated_date": "2026-02-19T00:00:05.000000Z",
  "currency_code": "USD",
  "date": "2026-02-18 14:22:00",
  "due_date": "2026-03-18",
  "document_type": "receipt",
  "category": "Meals & Entertainment",
  "is_duplicate": false,
  "is_document": true,
  "invoice_number": "INV-2026-001",
  "account_number": "ACCT-12345",
  "order_date": "2026-02-18",
  "delivery_date": null,
  "vendor": {
    "name": "Starbucks",
    "address": "123 Main St, San Francisco, CA 94105",
    "phone_number": "+1 415-555-0100",
    "email": null,
    "vat_number": null,
    "reg_number": null
  },
  "bill_to": {
    "name": "Jane Doe",
    "address": "456 Oak Ave, San Francisco, CA 94110"
  },
  "ship_to": {
    "name": null,
    "address": null
  },
  "line_items": [
    {
      "id": 1,
      "order": 0,
      "description": "Caffe Latte Grande",
      "quantity": 1,
      "price": 5.95,
      "total": 5.95,
      "tax": 0.52,
      "tax_rate": 8.75,
      "discount": null,
      "type": "food",
      "sku": null,
      "upc": null,
      "category": "Meals & Entertainment",
      "section": null,
      "date": null,
      "start_date": null,
      "end_date": null
    }
  ],
  "tax_lines": [
    {
      "order": 0,
      "name": "Sales Tax",
      "rate": 8.75,
      "total": 0.52,
      "base": 5.95
    }
  ],
  "subtotal": 5.95,
  "tax": 0.52,
  "tip": 0.00,
  "discount": 0.00,
  "total": 6.47,
  "payment": {
    "type": "visa",
    "card_number": "1234"
  },
  "reference_number": null,
  "notes": null,
  "img_url": "https://scdn.veryfi.com/documents/...",
  "pdf_url": "https://scdn.veryfi.com/documents/...",
  "ocr_text": "STARBUCKS\n123 Main St...",
  "meta": {
    "total_pages": 1,
    "processed_pages": 1,
    "fraud": {
      "score": 0.01,
      "color": "green",
      "decision": "Not Fraud",
      "types": []
    }
  }
}
```

### Check (`/api/v8/partner/checks/`)

```json
{
  "id": 9301847,
  "created_date": "2026-02-19T00:00:00.000000Z",
  "updated_date": "2026-02-19T00:00:03.000000Z",
  "amount": 1500.00,
  "amount_text": "One Thousand Five Hundred and 00/100",
  "check_number": "4021",
  "date": "2026-02-15",
  "currency_code": "USD",
  "check_type": "personal_check",
  "payer_name": "John Smith",
  "payer_address": "789 Elm St, Austin, TX 78701",
  "receiver_name": "Acme Plumbing LLC",
  "receiver_address": null,
  "bank_name": "Wells Fargo",
  "bank_address": "420 Montgomery St, San Francisco, CA 94104",
  "memo": "Invoice #2026-038",
  "is_signed": true,
  "micr": {
    "routing_number": "121000248",
    "account_number": "****5678",
    "serial_number": "4021",
    "raw": "⑆121000248⑆ ****5678⑈ 4021",
    "branch": null,
    "institution": null
  },
  "fractional_routing_number": "12-1/1200",
  "routing_from_fractional": "121000248",
  "endorsement": {
    "is_endorsed": true,
    "is_signed": true,
    "mobile_or_remote_deposit": {
      "checkbox": false,
      "instructions": false
    }
  },
  "handwritten_fields": ["amount", "amount_text", "date", "receiver_name", "memo"],
  "fraud": {
    "score": 0.02,
    "color": "green",
    "types": [],
    "pages": [
      {
        "is_lcd": { "score": 0.98, "value": false },
        "ai_generated": { "score": 0.99, "value": false },
        "four_corners_detected": true
      }
    ]
  },
  "img_thumbnail_url": "https://scdn.veryfi.com/checks/...",
  "pdf_url": "https://scdn.veryfi.com/checks/..."
}
```

### Bank Statement (`/api/v8/partner/bank-statements/`)

```json
{
  "id": 4820193,
  "created_date": "2026-02-19T12:45:00.000000Z",
  "updated_date": "2026-02-19T12:45:10.000000Z",
  "bank_name": "Chase",
  "bank_address": "270 Park Avenue, New York, NY 10017",
  "account_holder_name": "Jane Doe",
  "account_holder_address": "456 Oak Ave, San Francisco, CA 94110",
  "account_number": "****7890",
  "account_type": "Checking",
  "routing_number": "021000021",
  "currency_code": "USD",
  "statement_date": "2026-01-31",
  "period_start_date": "2026-01-01",
  "period_end_date": "2026-01-31",
  "beginning_balance": 12500.00,
  "ending_balance": 11835.47,
  "minimum_due": null,
  "due_date": null,
  "accounts": [
    {
      "number": "****7890",
      "beginning_balance": 12500.00,
      "ending_balance": 11835.47,
      "summaries": [
        { "name": "Total Deposits", "total": 3200.00 },
        { "name": "Total Withdrawals", "total": 3864.53 }
      ],
      "transactions": [
        {
          "order": 0,
          "date": "2026-01-05",
          "posted_date": "2026-01-05",
          "description": "Direct Deposit - ACME Corp Payroll",
          "credit_amount": 3200.00,
          "debit_amount": null,
          "balance": 15700.00,
          "category": "Income",
          "vendor": "ACME Corp"
        },
        {
          "order": 1,
          "date": "2026-01-12",
          "posted_date": "2026-01-12",
          "description": "Rent Payment - 456 Oak Ave",
          "credit_amount": null,
          "debit_amount": 2800.00,
          "balance": 12900.00,
          "category": "Housing",
          "vendor": null
        }
      ]
    }
  ],
  "fraud": {
    "score": 0.01,
    "color": "green",
    "types": []
  },
  "pdf_url": "https://scdn.veryfi.com/bank-statements/...",
  "img_thumbnail_url": "https://scdn.veryfi.com/bank-statements/..."
}
```

## Security & Privacy

### Data Handling

**Important:** Documents uploaded to Veryfi are transmitted to `https://api.veryfi.com` and processed on AWS servers.

**Before uploading sensitive documents:**
- Review Veryfi's privacy policy and data retention policies: https://www.veryfi.com/terms/
- Confirm data deletion/retention timelines
- Test with non-sensitive sample documents first
- If you have questions reach out to support@veryfi.com

**Best practices:**
- Do not upload highly sensitive PII (SSNs, medical records, financial account numbers) until you've confirmed the service's security and compliance posture
- Use API keys with limited permissions/scopes if available
- Monitor API usage logs for unauthorized access
- Never log or commit API keys to repositories or examples

### File Size Limits

- **Max file size:** 20 MB per document
- **Number of pages:** default is <=15 pages for receipts/invoices, <=50 pages for bank statements. Contact support to increase limits.


### Operational Safeguards

- Always use environment variables or secure secret stores for API keys
- Never include real API keys in code examples or documentation
- Use placeholder values like `"your_api_key_here"` in examples
- Set appropriate file permissions on configuration files (600 for JSON configs)
- Enable API key rotation and monitor usage through the dashboard

## Rate Limits

Veryfi enforces per-account rate limits. Exact limits depend on your plan tier.

**General guidance:**
- **Free/Starter plans:** lower concurrency limits; avoid parallel bursts
- **Business/Enterprise plans:** higher throughput; contact support for specifics
- If you hit a rate limit, the API returns **HTTP 429 Too Many Requests**
- Implement exponential backoff: wait 1s → 2s → 4s → 8s before retrying
- For high-volume workloads, contact support@veryfi.com or visit https://veryfi.com to discuss an enterprise plan

## Troubleshooting

**400 Bad Request:**
- Provide exactly one input: `file`, `file_url`, or `file_data` (for base64)
- When using `file_data`, send as a JSON body (not multipart) with `file_name` and `file_data` fields
- Verify Username, API Key and Client ID are valid
- Check the `message` field in the JSON response for the specific error detail

**401 Unauthorized:**
- Your `Client-Id`, `VERYFI_USERNAME`, or `VERYFI_API_KEY` is incorrect or expired
- Verify credentials at https://app.veryfi.com/api/settings/keys/
- Check that the `Authorization` header format is exactly `apikey USERNAME:API_KEY` (no extra spaces)
- Rotate your key if you suspect it was compromised

**413 Payload Too Large:**
- File exceeds the 20 MB limit
- Compress the file or reduce image resolution before uploading
- Split multi-page PDFs if the page count exceeds the plan limit (15 pages for invoices, 50 for bank statements)

**429 Too Many Requests:**
- You've exceeded your plan's rate limit
- Implement exponential backoff and retry
- For sustained high volume, contact support@veryfi.com to upgrade your plan

**500 / 5xx Server Error:**
- Transient server-side issue — retry after a short delay
- If the error persists, check the Veryfi status page or contact support@veryfi.com

**Missing Confidence Scores:**
- Add `confidence_details=true` to the request to include `score` and `ocr_score` fields in the response
- Add `bounding_boxes=true` to also get `bounding_box` and `bounding_region` coordinates

**W-2 / W-8 endpoint 404:**
- There are no `/w2s/` or `/w8s/` endpoints — use `/any-documents/` with `blueprint_name=w2` or `blueprint_name=w8`

## Tips

- Store `VERYFI_CLIENT_ID`, `VERYFI_USERNAME`, and `VERYFI_API_KEY` in environment variables rather than hardcoding them
- Use `confidence_details=true` and `bounding_boxes=true` when you need per-field accuracy scores or element coordinates
- For large volumes, classify documents first with `/classify/` and route to the appropriate extraction endpoint
- Keep file sizes under 20 MB and stay within page limits (15 for invoices, 50 for bank statements)
- Test with sample documents before processing sensitive data in production
- If a blueprint you need is missing, create a custom one at `https://app.veryfi.com/inboxes/anydocs?tab=blueprints`
- `ocr_text` in the response gives you raw extracted text — pass it to an LLM if you need markdown or further processing
- For base64 input, always include `file_name` so Veryfi can infer the file type correctly

## References

- **API Docs:** https://docs.veryfi.com/
- **Veryfi:** https://veryfi.com
- **Veryfi SDKs:** https://github.com/veryfi
- **Get API Key:** https://app.veryfi.com/api/settings/keys/
- **Privacy Policy:** https://www.veryfi.com/terms/
- **Support:** support@veryfi.com
