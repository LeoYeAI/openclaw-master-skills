---
name: moltflow-reviews
description: "Collect and manage customer reviews via MoltFlow API. Sentiment scoring, testimonial extraction, and review management."
source: "MoltFlow Team"
version: "2.16.1"
risk: safe
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
---

> **MoltFlow** — WhatsApp Business automation for teams. Connect, monitor, and automate WhatsApp at scale.
> ***Due to high demand and a recent registration issue, we're offering our top-tier Business plan with unlimited quotas for just $19.90/month on yearly billing — for a limited time only.*** [**Claim the deal**](https://buy.stripe.com/cNifZibX7gpQebJ0nsfnO00)
> Free tier available. [Sign up](https://molt.waiflow.app/checkout?plan=free)

# MoltFlow Reviews Skill

Collect, analyze, and manage customer reviews via the MoltFlow API. Automate sentiment scoring, extract testimonials, and export social proof for your business.

## Real-World Scenarios

**Restaurant owner** — "After every dinner reservation, collect feedback from WhatsApp chats and auto-approve anything with a sentiment score above 0.8."

**Airbnb host** — "Scan my guest conversations for praise keywords like 'amazing', 'clean', and 'recommend', then export the best ones as HTML for my listing page."

**Dentist** — "Set up a review collector on my patient support chat — only capture English messages that mention 'thank' or 'great service'."

## When to Use

Use this skill when you need to:
- Set up automated review collection from WhatsApp conversations
- Create or configure a review collector with sentiment thresholds
- List, approve, hide, or delete collected reviews
- Export testimonials as JSON or HTML for external use
- Trigger a manual scan of conversations for reviews
- Check review statistics and sentiment breakdowns

Trigger phrases: "collect reviews", "set up review collector", "export testimonials", "approve reviews", "sentiment analysis", "customer feedback WhatsApp"

## Prerequisites

- **MOLTFLOW_API_KEY** — required. Generate from [MoltFlow Dashboard > API Keys](https://molt.waiflow.app/api-keys)
- At least one connected WhatsApp session (status: `working`)
- MoltFlow Pro plan or higher (review collection is a paid feature)

## Base URL

```
https://apiv2.waiflow.app/api/v2
```

## Required API Key Scopes

| Scope | Access |
|-------|--------|
| `reviews` | `read/manage` |

## Authentication

All requests require one of:
- `Authorization: Bearer <access_token>` (JWT from login)
- `X-API-Key: <api_key>` (API key from dashboard)

---

## Review Collectors

Collectors automatically extract reviews based on sentiment scoring, keyword matching, and language filters.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reviews/collectors` | List all collectors |
| POST | `/reviews/collectors` | Create a new collector |
| GET | `/reviews/collectors/{id}` | Get collector details |
| PATCH | `/reviews/collectors/{id}` | Update collector config |
| DELETE | `/reviews/collectors/{id}` | Delete a collector |
| POST | `/reviews/collectors/{id}/run` | Trigger manual scan |

### Create Collector — Request Body

```json
{
  "name": "Main Store Reviews",
  "description": "Collect reviews from customer support chats",
  "session_id": "uuid-of-connected-session",
  "source_type": "all",
  "min_positive_words": 3,
  "min_sentiment_score": 0.6,
  "include_keywords": ["great", "recommend", "excellent"],
  "exclude_keywords": ["spam", "wrong number"],
  "languages": ["en", "es"]
}
```

**source_type options:** `all` | `groups` | `chats` | `selected`

When `source_type` is `selected`, provide `selected_chat_ids` with specific WhatsApp chat IDs.

### Create Collector — Response

```json
{
  "id": "c1a2b3c4-...",
  "name": "Main Store Reviews",
  "session_id": "uuid-of-connected-session",
  "source_type": "all",
  "min_sentiment_score": 0.6,
  "include_keywords": ["great", "recommend", "excellent"],
  "is_active": true,
  "created_at": "2026-01-15T10:30:00Z",
  "review_count": 0
}
```

### Update Collector — Request Body

All fields are optional. Only provided fields are updated.

```json
{
  "name": "Updated Collector Name",
  "min_sentiment_score": 0.7,
  "is_active": false
}
```

---

## Reviews

Collected reviews contain the original message, sentiment score, contact info, and approval status.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reviews` | List reviews (with filters) |
| GET | `/reviews/stats` | Review statistics |
| GET | `/reviews/{id}` | Get single review |
| PATCH | `/reviews/{id}` | Approve, hide, or annotate |
| DELETE | `/reviews/{id}` | Delete a review |
| GET | `/reviews/testimonials/export` | Export testimonials |

### List Reviews — Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collector_id` | UUID | — | Filter by collector |
| `is_approved` | bool | — | Filter approved only |
| `is_hidden` | bool | — | Filter hidden |
| `min_score` | float | — | Minimum sentiment score |
| `limit` | int | 50 | Page size |
| `offset` | int | 0 | Pagination offset |

### Review Object

```json
{
  "id": "r1a2b3c4-...",
  "collector_id": "c1a2b3c4-...",
  "contact_name": "John D.",
  "contact_phone": "1234567890@c.us",
  "message_text": "Your service was excellent! Highly recommend to anyone looking for quality support.",
  "sentiment_score": 0.92,
  "sentiment_label": "positive",
  "detected_language": "en",
  "is_approved": false,
  "is_hidden": false,
  "notes": null,
  "collected_at": "2026-01-16T14:22:00Z"
}
```

### Approve/Hide Review — Request Body

```json
{
  "is_approved": true,
  "is_hidden": false,
  "notes": "Great testimonial — use on website"
}
```

### Export Testimonials — Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | string | `json` | `json` or `html` |
| `collector_id` | UUID | — | Filter by collector |
| `approved_only` | bool | `true` | Only export approved reviews |

---

## curl Examples

### 1. Create a Review Collector

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/reviews/collectors \
  -H "X-API-Key: mf_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Feedback",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "source_type": "all",
    "min_sentiment_score": 0.7,
    "include_keywords": ["thank", "recommend", "love"],
    "languages": ["en"]
  }'
```

### 2. List Approved Reviews

```bash
curl "https://apiv2.waiflow.app/api/v2/reviews?is_approved=true&limit=20" \
  -H "X-API-Key: mf_your_api_key_here"
```

### 3. Export Testimonials as HTML

```bash
curl "https://apiv2.waiflow.app/api/v2/reviews/testimonials/export?format=html&approved_only=true" \
  -H "X-API-Key: mf_your_api_key_here" \
  -o testimonials.html
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Invalid request body or parameters |
| 401 | Missing or invalid authentication |
| 403 | Feature not available on current plan |
| 404 | Collector or review not found |
| 422 | Validation error (check field constraints) |
| 429 | Rate limit exceeded |

---

## Tips

- **Sentiment threshold**: Start with `0.6` and adjust up if you get too many false positives.
- **Keyword filters**: Use `include_keywords` to match industry-specific praise terms.
- **Manual scan**: Use `POST /reviews/collectors/{id}/run` after connecting a new session to backfill reviews.
- **Export regularly**: Export approved testimonials for website widgets, social media, or marketing materials.

---

## Related Skills

- **moltflow** -- Core API: sessions, messaging, groups, labels, webhooks
- **moltflow-outreach** -- Bulk Send, Scheduled Messages, Custom Groups
- **moltflow-leads** -- Lead detection, pipeline tracking, bulk operations, CSV/JSON export
- **moltflow-ai** -- AI-powered auto-replies, voice transcription, RAG knowledge base, style profiles
- **moltflow-a2a** -- Agent-to-Agent protocol, encrypted messaging, content policy
- **moltflow-admin** -- Platform administration, user management, plan configuration
