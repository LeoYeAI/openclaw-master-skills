# Veryfi Documents AI - OpenClaw Skill

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.com)
[![Veryfi](https://img.shields.io/badge/Powered%20by-Veryfi-green)](https://www.veryfi.com)

Real-time OCR and data extraction API for AI agents. Extract structured data from receipts, invoices, bank statements, checks, W-9s, passports, and 30+ other document types — with document classification and fraud detection built in.

## Features

- **Receipt & Invoice Extraction** — vendor, line items, totals, tax, payment method, and more
- **Bank Statement Parsing** — account details, balances, and full transaction history
- **Check Processing** — payer/receiver info, MICR data, endorsement detection
- **Document Classification** — identify document type before extraction (15 built-in types + custom)
- **Fraud Detection** — fraud scoring on receipts, invoices, checks, and bank statements
- **30+ Document Blueprints** — passports, driver's licenses, insurance cards, bills of lading, and more via the Any Document endpoint
- **Bounding Boxes & Confidence Scores** — per-field coordinates and accuracy scores

## Prerequisites

Sign up and grab your API credentials at **https://app.veryfi.com/api/settings/keys/**

You'll need three values:

| Variable | Description |
|----------|-------------|
| `VERYFI_CLIENT_ID` | Your application's client ID |
| `VERYFI_USERNAME` | Your Veryfi account username |
| `VERYFI_API_KEY` | Your API key |

## Installation

### npm (recommended)

```bash
npm install veryfi-documents-ai
```

### Manual

Clone this repository and place the `SKILL.md` file in your OpenClaw skills directory.

## Configuration

### Environment Variables (recommended)

```bash
export VERYFI_CLIENT_ID="your_client_id_here"
export VERYFI_USERNAME="your_username_here"
export VERYFI_API_KEY="your_api_key_here"
```

### OpenClaw Config

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

Or store keys directly in the config (use with caution):

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

> If storing keys in `~/.openclaw/openclaw.json`, set file permissions with `chmod 600 ~/.openclaw/openclaw.json` and never commit it to version control.

## Quick Start

**Extract data from a receipt or invoice:**

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/documents/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@invoice.pdf"
```

**Parse a bank statement:**

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/bank-statements/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@bank-statement.pdf"
```

**Classify a document:**

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/classify/" \
  -H "Content-Type: multipart/form-data" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@document.pdf"
```

## Supported Endpoints

| Document Type | Endpoint |
|---------------|----------|
| Receipts & Invoices | `/api/v8/partner/documents/` |
| Bank Statements | `/api/v8/partner/bank-statements/` |
| Checks | `/api/v8/partner/checks/` |
| W-9s | `/api/v8/partner/w9s/` |
| Any Document | `/api/v8/partner/any-documents/` |
| Classify | `/api/v8/partner/classify/` |

## Available Blueprints (Any Document Endpoint)

The Any Document endpoint supports 30+ document types via blueprints. Pass `blueprint_name` in the request:

```bash
curl -X POST "https://api.veryfi.com/api/v8/partner/any-documents/" \
  -H "Client-Id: $VERYFI_CLIENT_ID" \
  -H "Authorization: apikey $VERYFI_USERNAME:$VERYFI_API_KEY" \
  -F "file=@passport.jpg" \
  -F "blueprint_name=passport"
```

<details>
<summary>Full list of blueprints</summary>

| Blueprint | Document Type |
|-----------|---------------|
| `passport` | Passport (US or International) |
| `us_driver_license` | US Driver's License |
| `uk_drivers_license` | UK Driver's Licence |
| `us_health_insurance_card` | US Health Insurance Card |
| `auto_insurance_card` | Auto Insurance Card |
| `incorporation_document` | Certificate of Company Incorporation |
| `certificate_of_good_standing` | Certificate of Good Standing |
| `prescription_medication_label` | Prescription Medication Label |
| `medication_instructions` | Medication Instructions |
| `vision_prescription` | Vision Prescription |
| `medical_prescription_list` | Medical Prescription List |
| `lab_test_request_form` | Lab Test Request Form |
| `restaurant_menu` | Restaurant Menu |
| `drinks_menu` | Drinks Menu |
| `product_nutrition_facts` | Product Nutrition Facts Label |
| `goods_received_note` | Goods Received Note |
| `vendor_statement` | Vendor Statement |
| `price_sheet` | Price Sheet |
| `flight_itinerary` | Flight Itinerary |
| `bill_of_lading` | Bill of Lading |
| `air_waybill` | Air Waybill |
| `freight_invoice` | Freight Invoice |
| `shipping_label` | Shipping Label |
| `vehicle_registration` | Vehicle Registration |
| `v5c` | UK Vehicle Registration Certificate (V5C) |
| `work_order` | Work Order |
| `construction_estimate` | Construction Estimate |
| `construction_snapshot` | Construction Snapshot |
| `settlement_letter` | Settlement Letter |
| `diploma` | Diploma or Degree Certificate |
| `mortgage_application_form` | Mortgage Application Form |
| `annual_mortgage_statement` | Annual Mortgage Statement |
| `investment_account_statement` | Investment Account Statement |
| `bank_account_verification_letter` | Bank Account Verification Letter |

Missing a document type? [Create a custom blueprint](https://app.veryfi.com/inboxes/anydocs?tab=blueprints).

</details>

## Supported Input Methods

| Parameter | Description |
|-----------|-------------|
| `file` | Multipart file upload |
| `file_url` | Publicly accessible URL |
| `file_data` | Base64-encoded content |

**Limits:** 20 MB max file size. Up to 15 pages for receipts/invoices, 50 pages for bank statements (contact support to increase).

## Security

- Store API keys in environment variables or a secure secret store
- Never commit credentials to version control
- Set `chmod 600` on local config files containing keys
- Rotate keys regularly and monitor usage via the [Veryfi dashboard](https://app.veryfi.com)
- Test with non-sensitive sample documents before processing production data
- Review [Veryfi's privacy policy](https://www.veryfi.com/terms/) for data handling and retention details

## Links

- [API Documentation](https://docs.veryfi.com/)
- [Veryfi SDKs](https://github.com/veryfi)
- [Get API Keys](https://app.veryfi.com/api/settings/keys/)
- [Privacy Policy](https://www.veryfi.com/terms/)
- [Support](mailto:support@veryfi.com)

## License

See [LICENSE](LICENSE) for details.
