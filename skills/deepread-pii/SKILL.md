---
name: deepread-pii
title: DeepRead PII Redaction
description: Redact PII from documents before sharing or sending to LLMs. 14 PII types (names, SSN, credit cards, medical records, etc.) detected with context-aware AI — not regex. Knows patient vs. doctor, personal vs. institutional. Black bar redaction on PDFs, scanned images, and text files. Free tier: 2,000 pages/month.
metadata:
  openclaw:
    requires:
      env:
        - DEEPREAD_API_KEY
    primaryEnv: DEEPREAD_API_KEY
    homepage: https://www.deepread.tech
---

# DeepRead PII — Document Redaction API

Your agent processes documents. Some of those documents contain names, SSNs, medical records, credit card numbers. Before that data flows to another API, a database, a teammate, or an LLM — **it needs to be clean.**

```
Input:  "Invoice to: John Smith, 123 Oak St, SSN: 456-78-9012, Card: 4532-1234-5678-9012"
Output: "Invoice to: ██████████, ██████████, SSN: ███████████, Card: ███████████████████"
```

**One API call. Document in, redacted copy + detection report back.**

DeepRead PII detects 14 types of personally identifiable information using context-aware AI — not regex. It knows "Dr. Sarah Chen" on a hospital letterhead is the physician (skip), but "Sarah Chen" on a patient intake form is the patient (redact). No regex rules to write. No word lists to maintain. No false positive floods.

> This skill instructs the agent to POST your file to `https://api.deepread.tech`, poll for results, and download the redacted copy. No system files are modified and no elevated permissions are requested.

## What This Skill Does

- **14 PII types detected**: Names, SSNs, credit cards, emails, phones, addresses, dates of birth, passport numbers, driver's licenses, bank accounts, IBANs, IPs, URLs, medical record numbers
- **Black bar redaction**: PII replaced with solid black bars — text physically removed from the PDF content stream, irreversible, not just a visual overlay
- **Any document format**: PDF (digital + scanned), PNG, JPEG, plain text
- **Context-aware**: AI distinguishes personal vs. institutional, patient vs. provider, form labels vs. actual values
- **Audit trail**: Every redaction logged with detection counts per type. See DeepRead's [privacy policy](https://www.deepread.tech/privacy) for data handling details.
- **Copy-paste proof**: Redacted text cannot be recovered via copy-paste, text selection, or PDF parsing
- **Free tier**: 2,000 pages/month (no credit card required)
- **Works with other DeepRead skills**: Extract data with `deepread-ocr`, fill forms with `deepread-form-fill`, then redact the originals

## Setup

### 1. Get Your API Key

Sign up and create an API key:
```bash
# Visit the dashboard
https://www.deepread.tech/dashboard

# Or use this direct link
https://www.deepread.tech/dashboard/?utm_source=clawhub
```

Save your API key:
```bash
export DEEPREAD_API_KEY="sk_live_your_key_here"
```

### 2. Configuration (Optional)

Add to your `clawdbot.config.json5`:
```json5
{
  skills: {
    entries: {
      "deepread-pii": {
        enabled: true
        // API key is read from DEEPREAD_API_KEY environment variable
        // Do NOT hardcode your API key here
      }
    }
  }
}
```

### 3. Redact Your First Document

**Option A: With Webhook (Recommended)**
```bash
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@document.pdf" \
  -F "webhook_url=https://your-app.com/webhooks/pii"

# Returns immediately:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}

# Your webhook receives results when processing completes
```

**Option B: Poll for Results**
```bash
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@patient_record.pdf"

# Returns immediately:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}

# Poll until completed:
curl https://api.deepread.tech/v1/pii/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: $DEEPREAD_API_KEY"
```

## Usage Examples

### Redact a PDF

Replaces all detected PII with solid black bars. Text is physically removed from the PDF content stream. Copy-paste cannot recover it.

```bash
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@contract.pdf"
```

**Response when completed:**
```json
{
  "id": "550e8400-...",
  "status": "completed",
  "progress_percent": 100,
  "redacted_file_url": "https://...(signed URL)...",
  "report": {
    "id": "550e8400-...",
    "page_count": 5,
    "processing_time_ms": 3421,
    "pii_detected": {
      "NAME": {
        "count": 3,
        "pages": [1, 2],
        "confidence_avg": 0.92
      },
      "PHONE": {
        "count": 2,
        "pages": [1],
        "confidence_avg": 0.89
      },
      "EMAIL": {
        "count": 1,
        "pages": [2],
        "confidence_avg": 0.97
      }
    },
    "total_redactions": 6,
    "redaction_policy": "black_bar",
    "confidence_threshold_used": 0.85,
    "below_threshold_count": 0
  }
}
```

### Redact an Image

Works on scanned documents, photos of IDs, screenshots — any PNG or JPEG.

```bash
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@drivers_license.png"
```

Vision AI detects PII in the image, locates exact positions, and draws black bars over the text.

### Redact Plain Text

```bash
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@notes.txt"
```

**Before:** `Patient John Smith, SSN 456-78-9012, called from (555) 867-5309`
**After:** `Patient ██████████, SSN ███████████, called from ██████████████`

### Multi-Language Support

Supports documents in English, Chinese, Spanish, Hindi, and Arabic.

```bash
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@documento.pdf" \
  -F "language=es"
```

**Supported languages:** `en` (default), `zh`, `es`, `hi`, `ar`

## When to Use This Skill

### Use DeepRead PII For:

- **Before sharing documents externally** — redact before sending to vendors, partners, opposing counsel
- **Before feeding documents to LLMs** — strip PII before sending content to any AI model
- **Compliance workflows** — GDPR right to erasure, HIPAA de-identification, CCPA requests
- **Training data preparation** — create clean datasets from real documents
- **Insurance claims** — redact claimant PII before adjuster handoff
- **Legal discovery** — privilege review with PII protection
- **Medical records** — de-identify patient data for research or sharing
- **Financial documents** — mask account numbers, SSNs on statements
- **HR documents** — clean employee files before audits

### Don't Use For:

- **Real-time processing** — async workflow, not instant (use webhooks)
- **Structured data extraction** — use `deepread-ocr` skill for that, then redact
- **Documents with no text** — blank images or decorative PDFs

## How It Works

### 3-Layer Detection Pipeline

```
Document → AI Detection → Threshold Filter → Context Validation → Redact
```

**Layer 1: AI Detection**
- Text documents: LLM scans for all 14 PII types with confidence scoring
- Images/scans: Vision model detects PII with precise bounding box coordinates
- Returns type, exact value, and confidence score (0.0–1.0) for each detection

**Layer 2: Confidence Threshold**
- Default threshold: 0.85
- Detections below threshold are recorded but NOT redacted
- Reported separately as `below_threshold_count` for manual review

**Layer 3: Context-Aware Validation**
- Second AI pass with full document context
- Filters false positives that regex-based tools can't handle:
  - `admissions@university.edu` → institutional email, SKIP
  - `john.smith@gmail.com` → personal email, REDACT
  - "Dr. Sarah Chen" on letterhead → physician, SKIP
  - "Sarah Chen" on intake form → patient, REDACT
  - "Name:" (form label) → not PII, SKIP
  - "John Smith" (form value) → PII, REDACT
  - Invoice dates → not DOB, SKIP
  - "Date of Birth: 03/15/1990" → DOB, REDACT

### What Gets Detected

| PII Type | Examples |
|----------|----------|
| `SSN` | Social Security numbers, national IDs |
| `CREDIT_CARD` | Card numbers, transaction IDs tied to a person |
| `EMAIL` | Personal email addresses (not institutional) |
| `PHONE` | Phone numbers (all country formats) |
| `NAME` | Person names (all cultures/languages) |
| `ADDRESS` | Physical addresses, postal codes |
| `IP_ADDRESS` | IPv4 and IPv6 addresses |
| `DATE_OF_BIRTH` | Birth dates (only when labeled as DOB — not random dates) |
| `PASSPORT_NUMBER` | Passport numbers |
| `DRIVER_LICENSE` | Driver's licenses, registration numbers |
| `BANK_ACCOUNT` | Account numbers, routing numbers |
| `IBAN` | International Bank Account Numbers |
| `URL` | Personal URLs and web addresses |
| `MEDICAL_RECORD` | Medical record numbers, patient IDs, hospital IDs |

### PDF Redaction is Irreversible

- Digital PDFs: Text is physically removed from the PDF content stream using redaction annotations — not just covered
- Scanned PDFs: Pages are re-rendered as images with black bars, replacing the original
- All PDFs: Metadata stripped, content streams cleaned and deflated
- Copy-paste, text selection, and PDF parsing cannot recover redacted content

## API Reference

### POST /v1/pii/redact — Submit Document for Redaction

**Auth:** `X-API-Key: YOUR_KEY`
**Content-Type:** `multipart/form-data`
**Rate Limit:** 10 requests per 60 seconds

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | Yes | — | PDF, PNG, JPEG, or TXT (max 50MB) |
| `language` | string | No | `"en"` | `"en"`, `"zh"`, `"es"`, `"hi"`, `"ar"` |
| `webhook_url` | string | No | — | HTTPS URL for completion notification |

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

**Errors:**
| Status | Code | Meaning |
|--------|------|---------|
| 400 | `INVALID_REQUEST` | Bad request parameters |
| 400 | `UNSUPPORTED_FORMAT` | File type not supported |
| 400 | `EMPTY_DOCUMENT` | File is empty |
| 400 | `DOCUMENT_CORRUPTED` | File is corrupt or unreadable |
| 400 | `PASSWORD_PROTECTED` | Document is password-protected |
| 401 | `UNAUTHORIZED` | Invalid or missing API key |
| 413 | `FILE_TOO_LARGE` | Exceeds 50MB size limit |
| 429 | `RATE_LIMITED` | Rate limit exceeded |
| 500 | `INTERNAL_ERROR` | Server error (retry or contact support) |

### GET /v1/pii/{job_id} — Get Redaction Results

**Auth:** `X-API-Key: YOUR_KEY`
**Rate Limit:** 60 requests per 60 seconds

Poll until `status` is `completed` or `failed`.

**Response (completed):**
```json
{
  "id": "550e8400-...",
  "status": "completed",
  "progress_percent": 100,
  "redacted_file_url": "https://...(signed URL)...",
  "report": {
    "id": "550e8400-...",
    "page_count": 3,
    "processing_time_ms": 4200,
    "pii_detected": {
      "NAME": {
        "count": 4,
        "pages": [1, 2, 3],
        "confidence_avg": 0.93,
        "confidence_min": 0.87,
        "below_threshold": 0,
        "allowed": 0
      },
      "SSN": {
        "count": 1,
        "pages": [1],
        "confidence_avg": 0.98,
        "confidence_min": 0.98,
        "below_threshold": 0,
        "allowed": 0
      }
    },
    "total_redactions": 5,
    "redaction_policy": "black_bar",
    "confidence_threshold_used": 0.85,
    "below_threshold_count": 0
  },
  "error": null
}
```

**Response (failed):**
```json
{
  "id": "550e8400-...",
  "status": "failed",
  "progress_percent": 0,
  "redacted_file_url": null,
  "report": null,
  "error": {
    "code": "DOCUMENT_CORRUPTED",
    "message": "Unable to process the document"
  }
}
```

**Statuses:** `queued` → `processing` → `completed` or `failed`

## Code Examples

### Python

```python
import requests
import time

API_KEY = "sk_live_YOUR_KEY"
BASE = "https://api.deepread.tech"

# Submit document for redaction
with open("patient_record.pdf", "rb") as f:
    resp = requests.post(
        f"{BASE}/v1/pii/redact",
        headers={"X-API-Key": API_KEY},
        files={"file": f},
    )
job_id = resp.json()["id"]

# Poll with backoff
delay = 3
while True:
    time.sleep(delay)
    result = requests.get(
        f"{BASE}/v1/pii/{job_id}",
        headers={"X-API-Key": API_KEY}
    ).json()

    if result["status"] == "completed":
        # Download redacted file
        redacted_url = result["redacted_file_url"]
        redacted_pdf = requests.get(redacted_url).content
        with open("patient_record_redacted.pdf", "wb") as f:
            f.write(redacted_pdf)

        # Review detection report
        report = result["report"]
        print(f"Redacted {report['total_redactions']} PII instances")
        for pii_type, summary in report["pii_detected"].items():
            print(f"  {pii_type}: {summary['count']} found on pages {summary['pages']}")
        break

    elif result["status"] == "failed":
        print(f"Failed: {result['error']['message']}")
        break

    delay = min(delay * 1.5, 15)
```

### JavaScript / Node.js

```javascript
import fs from "fs";

const API_KEY = "sk_live_YOUR_KEY";
const BASE = "https://api.deepread.tech";

// Submit document
const form = new FormData();
form.append("file", fs.createReadStream("contract.pdf"));

const { id: jobId } = await fetch(`${BASE}/v1/pii/redact`, {
  method: "POST",
  headers: { "X-API-Key": API_KEY },
  body: form,
}).then((r) => r.json());

// Poll with backoff
let delay = 3000;
let result;
do {
  await new Promise((r) => setTimeout(r, delay));
  result = await fetch(`${BASE}/v1/pii/${jobId}`, {
    headers: { "X-API-Key": API_KEY },
  }).then((r) => r.json());
  delay = Math.min(delay * 1.5, 15000);
} while (!["completed", "failed"].includes(result.status));

if (result.status === "completed") {
  console.log(`Redacted file: ${result.redacted_file_url}`);
  console.log(`Total redactions: ${result.report.total_redactions}`);
}
```

### cURL

```bash
# Redact a PDF
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@document.pdf"

# Redact a scanned image
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@id_card.png"

# Redact with language hint
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@documento.pdf" \
  -F "language=es"

# Check status
curl https://api.deepread.tech/v1/pii/JOB_ID \
  -H "X-API-Key: $DEEPREAD_API_KEY"
```

## Workflows: Combine with Other DeepRead Skills

### Extract Then Redact

Use `deepread-ocr` to extract data, then redact the original before archiving:

```bash
# Step 1: Extract structured data (keeps the data you need)
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@claim.pdf" \
  -F 'schema={"type":"object","properties":{"claim_number":{"type":"string"},"amount":{"type":"number"}}}'

# Step 2: Redact PII from original (clean copy for filing)
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@claim.pdf"
```

### Redact Before LLM Processing

Strip PII before sending document content to any AI model:

```python
# 1. Redact the document
resp = requests.post(f"{BASE}/v1/pii/redact",
    headers={"X-API-Key": API_KEY},
    files={"file": open("report.pdf", "rb")})
job_id = resp.json()["id"]

# 2. Wait for completion, download redacted version
# 3. Now safe to send to any LLM for analysis
```

### Fill Form Then Redact Copy

Use `deepread-form-fill` to complete a form, then redact a copy for records:

```bash
# Step 1: Fill the form
curl -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@w4_form.pdf" \
  -F 'form_fields={"full_name":"Jane Smith","ssn":"456-78-9012"}'

# Step 2: Redact the filled form for internal records
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@w4_filled.pdf"
```

## Best Practices

### 1. Use Webhooks for Production

```bash
curl -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@document.pdf" \
  -F "webhook_url=https://your-app.com/webhooks/pii"
```

Only use polling if you cannot expose a webhook endpoint.

### 2. Review the Detection Report

The report tells you exactly what was found and where:

```python
report = result["report"]

# Check if anything was below confidence threshold
if report["below_threshold_count"] > 0:
    print(f"Warning: {report['below_threshold_count']} detections below threshold")
    print("Consider manual review of the original document")

# See breakdown by type
for pii_type, summary in report["pii_detected"].items():
    print(f"{pii_type}: {summary['count']} on pages {summary['pages']}")
```

### 3. Set Language for Non-English Documents

Always specify the language for better detection accuracy:

```bash
-F "language=zh"   # Chinese
-F "language=es"   # Spanish
-F "language=hi"   # Hindi
-F "language=ar"   # Arabic
```

### 4. Polling Strategy

Poll every 3-5 seconds with backoff:

```python
delay = 3
while True:
    time.sleep(delay)
    result = check_status(job_id)
    if result["status"] in ("completed", "failed"):
        break
    delay = min(delay * 1.5, 15)  # cap at 15s
```

## Rate Limits & Pricing

### Free Tier (No Credit Card)
- **2,000 pages/month**
- **10 requests/minute** (redact endpoint)
- **60 requests/minute** (status endpoint)
- Full feature access

### Paid Plans
- **PRO**: 50,000 pages/month, 100 req/min @ $99/mo
- **SCALE**: Custom volume pricing

**Upgrade:** https://www.deepread.tech/dashboard/billing?utm_source=clawhub

## Troubleshooting

### Error: `UNSUPPORTED_FORMAT`
**Solution:** Only PDF, PNG, JPEG, and TXT are supported. Convert other formats first.

### Error: `EMPTY_DOCUMENT`
**Solution:** File has no content. Check the file is not corrupted or zero-bytes.

### Error: `FILE_TOO_LARGE`
**Solution:** Compress the file or split into smaller documents. Max 50MB.

### No PII detected in report
**Possible causes:**
- Document genuinely contains no PII
- PII is in a language not specified (set `language` parameter)
- Image quality too low for detection (try higher resolution scan)

### Redaction missed some PII
**Possible causes:**
- Value was below the 0.85 confidence threshold (check `below_threshold_count`)
- Unusual formatting or handwritten text
- Report the issue: https://github.com/deepread-tech/deep-read-service/issues

## Security Notes

- This skill only calls `https://api.deepread.tech` — no other endpoints are contacted
- Documents are uploaded to DeepRead servers for processing and redacted copies are returned via signed URLs
- This skill does not modify any system files, install packages, or request elevated permissions
- Keep `DEEPREAD_API_KEY` secret — rotate if compromised
- If using webhooks, ensure your receiving endpoint uses HTTPS and is authenticated
- Test with non-sensitive documents first to verify behavior
- Review DeepRead's [privacy policy](https://www.deepread.tech/privacy) for data retention and handling details

## Related DeepRead Skills

DeepRead is three tools with one API key:

| Skill | What it does | Install |
|-------|-------------|---------|
| **`deepread-ocr`** | Extract text + structured JSON from any document. 97%+ accuracy. | `clawhub install uday390/deepread-ocr` |
| **`deepread-form-fill`** | Fill any PDF form with AI vision — scanned forms, government PDFs | `clawhub install uday390/deepread-form-fill` |
| **`deepread-pii`** | Redact sensitive data. This skill. | You're here |

**Common pipeline:** Extract data (OCR) → Fill target form (Form Fill) → Redact originals for filing (PII)

## Support & Resources

- **Dashboard**: https://www.deepread.tech/dashboard
- **Issues**: https://github.com/deepread-tech/deep-read-service/issues
- **Email**: hello@deepread.tech

---

**Ready to start?** Get your free API key at https://www.deepread.tech/dashboard/?utm_source=clawhub
