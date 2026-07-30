---
name: deepread
description: AI-native OCR platform that turns documents into high-accuracy data in minutes. Using multi-model consensus, DeepRead achieves 95%+ accuracy and flags only uncertain fields for review—reducing manual work from 100% to 5-10%. Zero prompt engineering required.
metadata:
  {
    "openclaw": {
      "requires": {
        "env": ["DEEPREAD_API_KEY"]
      },
      "primaryEnv": "DEEPREAD_API_KEY",
      "homepage": "https://www.deepread.tech"
    }
  }
---

# DeepRead - Production OCR API

DeepRead is an AI-native OCR platform that turns documents into high-accuracy data in minutes. Using multi-model consensus, DeepRead achieves 95%+ accuracy and flags only uncertain fields for review—reducing manual work from 100% to 5-10%. Zero prompt engineering required.

## What This Skill Does

DeepRead is a production-grade document processing API that gives you high-accuracy structured data output in minutes with human review flagging so manual review is limited to the flagged exceptions

**Core Features:**
- **Text Extraction**: Convert PDFs and images to clean markdown
- **Structured Data**: Extract JSON fields with confidence scores
- **Quality Flags**: Human Review tagging for uncertain fields (`hil_flag`)
- **Multi-Pass Processing**: Multiple validation passes for maximum accuracy
- **Multi-Model Consensus**: Cross-validation between models for reliability
- **Free Tier**: 2,000 pages/month (no credit card required)

## Setup

### 1. Get Your API Key

Sign up and create an API key:
```bash
# Visit the dashboard
https://www.deepread.tech/dashboard

# Or use this direct link
https://www.deepread.tech/dashboard/?utm_source=clawdhub
```

Save your API key:
```bash
export DEEPREAD_API_KEY="sk_live_your_key_here"
```

### 2. Clawdbot Configuration (Optional)

Add to your `clawdbot.config.json5`:
```json5
{
  skills: {
    entries: {
      "deepread": {
        enabled: true,
        apiKey: "sk_live_your_key_here"
      }
    }
  }
}
```

### 3. Process Your First Document

**Option A: With Webhook (Recommended)**
```bash
# Upload PDF with webhook notification
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@document.pdf" \
  -F "webhook_url=https://your-app.com/webhooks/deepread"

# Returns immediately
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}

# Your webhook receives results when processing completes (2-5 minutes)
```

**Option B: Poll for Results**
```bash
# Upload PDF without webhook
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@document.pdf"

# Returns immediately
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}

# Poll until completed
curl https://api.deepread.tech/v1/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "X-API-Key: $DEEPREAD_API_KEY"
```

## Usage Examples

### Basic OCR (Text Only)

Extract text as clean markdown:

```bash
# With webhook (recommended)
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@invoice.pdf" \
  -F "webhook_url=https://your-app.com/webhook"

# OR poll for completion
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@invoice.pdf"

# Then poll
curl https://api.deepread.tech/v1/jobs/JOB_ID \
  -H "X-API-Key: $DEEPREAD_API_KEY"
```

**Response when completed:**
```json
{
  "id": "550e8400-...",
  "status": "completed",
  "result": {
    "text": "# INVOICE\n\n**Vendor:** Acme Corp\n**Total:** $1,250.00..."
  }
}
```

### Structured Data Extraction

Extract specific fields with confidence scoring:

```bash
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@invoice.pdf" \
  -F 'schema={
    "type": "object",
    "properties": {
      "vendor": {
        "type": "string",
        "description": "Vendor company name"
      },
      "total": {
        "type": "number",
        "description": "Total invoice amount"
      },
      "invoice_date": {
        "type": "string",
        "description": "Invoice date in MM/DD/YYYY format"
      }
    }
  }'
```

**Response includes confidence flags:**
```json
{
  "status": "completed",
  "result": {
    "text": "# INVOICE\n\n**Vendor:** Acme Corp...",
    "data": {
      "vendor": {
        "value": "Acme Corp",
        "hil_flag": false,
        "found_on_page": 1
      },
      "total": {
        "value": 1250.00,
        "hil_flag": false,
        "found_on_page": 1
      },
      "invoice_date": {
        "value": "2024-10-??",
        "hil_flag": true,
        "reason": "Date partially obscured",
        "found_on_page": 1
      }
    },
    "metadata": {
      "fields_requiring_review": 1,
      "total_fields": 3,
      "review_percentage": 33.3
    }
  }
}
```

### Complex Schemas (Nested Data)

Extract arrays and nested objects:

```bash
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@invoice.pdf" \
  -F 'schema={
    "type": "object",
    "properties": {
      "vendor": {"type": "string"},
      "total": {"type": "number"},
      "line_items": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "description": {"type": "string"},
            "quantity": {"type": "number"},
            "price": {"type": "number"}
          }
        }
      }
    }
  }'
```

### Page-by-Page Breakdown

Get per-page OCR results with quality flags:

```bash
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@contract.pdf" \
  -F "include_pages=true"
```

**Response:**
```json
{
  "result": {
    "text": "Combined text from all pages...",
    "pages": [
      {
        "page_number": 1,
        "text": "# Contract Agreement\n\n...",
        "hil_flag": false
      },
      {
        "page_number": 2,
        "text": "Terms and C??diti??s...",
        "hil_flag": true,
        "reason": "Multiple unrecognized characters"
      }
    ],
    "metadata": {
      "pages_requiring_review": 1,
      "total_pages": 2
      }
  }
}
```

## When to Use This Skill

### ✅ Use DeepRead For:

- **Invoice Processing**: Extract vendor, totals, line items
- **Receipt OCR**: Parse merchant, items, totals
- **Contract Analysis**: Extract parties, dates, terms
- **Form Digitization**: Convert paper forms to structured data
- **Document Workflows**: Any process requiring OCR + data extraction
- **Quality-Critical Apps**: When you need to know which extractions are uncertain

### ❌ Don't Use For:

- **Real-time Processing**: Processing takes 2-5 minutes (async workflow)
- **Batch >2,000 pages/month**: Upgrade to PRO or SCALE tier

## How It Works

### Multi-Pass Pipeline

```
PDF → Convert → Rotate Correction → OCR → Multi-Model Validation → Extract → Done
```

The pipeline automatically handles:
- Document rotation and orientation correction
- Multi-pass validation for accuracy
- Cross-model consensus for reliability
- Field-level confidence scoring

### Quality Review (hil_flag)

AI compares extracted text to the original image and sets `hil_flag`:

- **`hil_flag: false`** = Clear, confident extraction → Auto-process
- **`hil_flag: true`** = Uncertain extraction → Human review required

**AI flags extractions when:**
- Text is handwritten, blurry, or low quality
- Multiple possible interpretations exist
- Characters are partially visible or unclear
- Field not found in document

**This is multimodal AI determination, not rule-based.**

## Advanced Features

### 1. Blueprints (Optimized Schemas)

Create reusable, optimized schemas for specific document types:

```bash
# List your blueprints
curl https://api.deepread.tech/v1/blueprints \
  -H "X-API-Key: $DEEPREAD_API_KEY"

# Use blueprint instead of inline schema
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@invoice.pdf" \
  -F "blueprint_id=660e8400-e29b-41d4-a716-446655440001"
```

**Benefits:**
- 20-30% accuracy improvement over baseline schemas
- Reusable across similar documents
- Versioned with rollback support

**How to create blueprints:**

```bash
# Create a blueprint from training data
curl -X POST https://api.deepread.tech/v1/optimize \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "utility_invoice",
    "description": "Optimized for utility invoices",
    "document_type": "invoice",
    "initial_schema": {
      "type": "object",
      "properties": {
        "vendor": {"type": "string", "description": "Vendor name"},
        "total": {"type": "number", "description": "Total amount"}
      }
    },
    "training_documents": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    "ground_truth_data": [
      {"vendor": "Acme Power", "total": 125.50},
      {"vendor": "City Electric", "total": 89.25}
    ],
    "target_accuracy": 95.0,
    "max_iterations": 5
  }'

# Returns: {"job_id": "...", "blueprint_id": "...", "status": "pending"}

# Check optimization status
curl https://api.deepread.tech/v1/blueprints/jobs/JOB_ID \
  -H "X-API-Key: $DEEPREAD_API_KEY"

# Use blueprint (once completed)
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@invoice.pdf" \
  -F "blueprint_id=BLUEPRINT_ID"
```

### 2. Webhooks (Recommended for Production)

Get notified when processing completes instead of polling:

```bash
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@invoice.pdf" \
  -F "webhook_url=https://your-app.com/webhooks/deepread"
```

**Your webhook receives this payload when processing completes:**
```json
{
  "job_id": "550e8400-...",
  "status": "completed",
  "created_at": "2025-01-27T10:00:00Z",
  "completed_at": "2025-01-27T10:02:30Z",
  "result": {
    "text": "...",
    "data": {...}
  },
  "preview_url": "https://preview.deepread.tech/abc1234"
}
```

**Benefits:**
- No polling required
- Instant notification when done
- Lower latency
- Better for production workflows

### 3. Public Preview URLs

Share OCR results without authentication:

```bash
# Request preview URL
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@document.pdf" \
  -F "include_images=true"

# Get preview URL in response
{
  "result": {
    "text": "...",
    "data": {...}
  },
  "preview_url": "https://preview.deepread.tech/Xy9aB12"
}
```

**Public Preview Endpoint:**
```bash
# No authentication required
curl https://api.deepread.tech/v1/preview/Xy9aB12
```

## Rate Limits & Pricing

### Free Tier (No Credit Card)
- **2,000 pages/month**
- **10 requests/minute**
- Full feature access (OCR + structured extraction + blueprints)

### Paid Plans
- **PRO**: 50,000 pages/month, 100 requests/minute @ $99/mo
- **SCALE**: Custom volume pricing (contact sales)

**Upgrade:** https://www.deepread.tech/dashboard/billing?utm_source=clawdhub

### Rate Limit Headers

Every response includes quota information:
```
X-RateLimit-Limit: 2000
X-RateLimit-Remaining: 1847
X-RateLimit-Used: 153
X-RateLimit-Reset: 1730419200
```

## Best Practices

### 1. Use Webhooks for Production

**✅ Recommended: Webhook notifications**
```bash
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@document.pdf" \
  -F "webhook_url=https://your-app.com/webhook"
```

**Only use polling if:**
- Testing/development
- Cannot expose a webhook endpoint
- Need synchronous response

### 2. Schema Design

**✅ Good: Descriptive field descriptions**
```json
{
  "vendor": {
    "type": "string",
    "description": "Vendor company name. Usually in header or top-left of invoice."
  }
}
```

**❌ Bad: No description**
```json
{
  "vendor": {"type": "string"}
}
```

### 3. Polling Strategy (If Needed)

Only if you can't use webhooks, poll every 5-10 seconds:

```python
import time
import requests

def wait_for_result(job_id, api_key):
    while True:
        response = requests.get(
            f"https://api.deepread.tech/v1/jobs/{job_id}",
            headers={"X-API-Key": api_key}
        )
        result = response.json()

        if result["status"] == "completed":
            return result["result"]
        elif result["status"] == "failed":
            raise Exception(f"Job failed: {result.get('error')}")

        time.sleep(5)
```

### 4. Handling Quality Flags

Separate confident fields from uncertain ones:

```python
def process_extraction(data):
    confident = {}
    needs_review = []

    for field, field_data in data.items():
        if field_data["hil_flag"]:
            needs_review.append({
                "field": field,
                "value": field_data["value"],
                "reason": field_data.get("reason")
            })
        else:
            confident[field] = field_data["value"]

    # Auto-process confident fields
    save_to_database(confident)

    # Send uncertain fields to review queue
    if needs_review:
        send_to_review_queue(needs_review)
```

## Troubleshooting

### Error: `quota_exceeded`
```json
{"detail": "Monthly page quota exceeded"}
```
**Solution:** Upgrade to PRO or wait until next billing cycle.

### Error: `invalid_schema`
```json
{"detail": "Schema must be valid JSON Schema"}
```
**Solution:** Ensure schema is valid JSON and includes `type` and `properties`.

### Error: `file_too_large`
```json
{"detail": "File size exceeds 50MB limit"}
```
**Solution:** Compress PDF or split into smaller files.

### Job Status: `failed`
```json
{"status": "failed", "error": "PDF could not be processed"}
```
**Common causes:**
- Corrupted PDF file
- Password-protected PDF
- Unsupported PDF version
- Image quality too low for OCR

## Example Schema Templates

### Invoice Schema
```json
{
  "type": "object",
  "properties": {
    "invoice_number": {
      "type": "string",
      "description": "Unique invoice ID"
    },
    "invoice_date": {
      "type": "string",
      "description": "Invoice date in MM/DD/YYYY format"
    },
    "vendor": {
      "type": "string",
      "description": "Vendor company name"
    },
    "total": {
      "type": "number",
      "description": "Total amount due including tax"
    },
    "line_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "description": {"type": "string"},
          "quantity": {"type": "number"},
          "price": {"type": "number"}
        }
      }
    }
  }
}
```

### Receipt Schema
```json
{
  "type": "object",
  "properties": {
    "merchant": {
      "type": "string",
      "description": "Store or merchant name"
    },
    "date": {
      "type": "string",
      "description": "Transaction date"
    },
    "total": {
      "type": "number",
      "description": "Total amount paid"
    },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "price": {"type": "number"}
        }
      }
    }
  }
}
```

### Contract Schema
```json
{
  "type": "object",
  "properties": {
    "parties": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Names of all parties in the contract"
    },
    "effective_date": {
      "type": "string",
      "description": "Contract start date"
    },
    "term_length": {
      "type": "string",
      "description": "Duration of contract"
    },
    "termination_clause": {
      "type": "string",
      "description": "Conditions for termination"
    }
  }
}
```

## Support & Resources

- **GitHub**: https://github.com/deepread-tech
- **Issues**: https://github.com/deepread-tech/deep-read-service/issues
- **Email**:  hello@deepread.tech

### Important Notes
- **Processing Time**: 2-5 minutes (async, not real-time)
- **Async Workflow**: Use webhooks (recommended) or polling
- **Rate Limits**: 10 req/min on free tier
- **File Size Limit**: 50MB per file
- **Supported Formats**: PDF, JPG, JPEG, PNG

---

**Ready to start?** Get your free API key at https://www.deepread.tech/dashboard/?utm_source=clawdhub
