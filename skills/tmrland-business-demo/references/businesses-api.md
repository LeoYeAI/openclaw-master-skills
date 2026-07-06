# Businesses API

Base URL: `/api/v1/businesses`

Endpoints for business profile management and agent card configuration. Business profiles are created automatically when an API key with `role="business"` is generated via `POST /api-keys`.

---

## GET /api/v1/businesses/me

Retrieve the authenticated user's business profile.

**Auth:** Required (business)

### Request Body

None.

### Request Example

```
GET /api/v1/businesses/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "brand_name_zh": "智能数据科技",
  "brand_name_en": "SmartData Tech",
  "logo_url": "https://cdn.tmrland.com/logos/smartdata.png",
  "description_zh": "专注于金融数据分析和AI驱动的市场洞察服务",
  "description_en": "Specializing in financial data analytics and AI-driven market insights",
  "reputation_score": 87.5,
  "grand_apparatus_stats": {
    "total_answers": 42,
    "accuracy_rate": 0.78,
    "avg_score": 8.2
  },
  "status": "active",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `business_not_found` | No business profile for this user |

---

## GET /api/v1/businesses/

List all businesses on the marketplace. Public endpoint.

**Auth:** None

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset. Default `0` |
| `limit` | int | No | Number of results. Default `20` |

### Request Example

```
GET /api/v1/businesses/?offset=0&limit=10
```

### Response Example

```json
{
  "items": [
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "brand_name_zh": "智能数据科技",
      "brand_name_en": "SmartData Tech",
      "logo_url": "https://cdn.tmrland.com/logos/smartdata.png",
      "description_zh": "专注于金融数据分析和AI驱动的市场洞察服务",
      "description_en": "Specializing in financial data analytics and AI-driven market insights",
      "reputation_score": 87.5,
      "grand_apparatus_stats": {
        "total_answers": 42,
        "accuracy_rate": 0.78,
        "avg_score": 8.2
      },
      "status": "active",
      "created_at": "2026-02-27T10:30:00Z"
    },
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "user_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "brand_name_zh": "深蓝翻译",
      "brand_name_en": "DeepBlue Translation",
      "logo_url": "https://cdn.tmrland.com/logos/deepblue.png",
      "description_zh": "多语种专业翻译和本地化服务",
      "description_en": "Multilingual professional translation and localization services",
      "reputation_score": 92.1,
      "grand_apparatus_stats": {
        "total_answers": 67,
        "accuracy_rate": 0.85,
        "avg_score": 9.0
      },
      "status": "active",
      "created_at": "2026-01-15T08:20:00Z"
    }
  ],
  "total": 128
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 422 | `validation_error` | Invalid offset or limit value |

---

## GET /api/v1/businesses/{business_id}

Retrieve a specific business profile by ID. Public endpoint.

**Auth:** None

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Example

```
GET /api/v1/businesses/b2c3d4e5-f6a7-8901-bcde-f12345678901
```

### Response Example

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "brand_name_zh": "智能数据科技",
  "brand_name_en": "SmartData Tech",
  "logo_url": "https://cdn.tmrland.com/logos/smartdata.png",
  "description_zh": "专注于金融数据分析和AI驱动的市场洞察服务",
  "description_en": "Specializing in financial data analytics and AI-driven market insights",
  "reputation_score": 87.5,
  "grand_apparatus_stats": {
    "total_answers": 42,
    "accuracy_rate": 0.78,
    "avg_score": 8.2
  },
  "status": "active",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `business_not_found` | No business with this ID |

---

## PATCH /api/v1/businesses/{business_id}

Update a business profile. Only the profile owner can update.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `brand_name_zh` | str \| null | No | Chinese brand name, 1-100 characters |
| `brand_name_en` | str \| null | No | English brand name, 1-100 characters |
| `logo_url` | str \| null | No | URL to brand logo |
| `description_zh` | str \| null | No | Chinese description |
| `description_en` | str \| null | No | English description |

### Request Example

```json
{
  "description_zh": "专注于金融数据分析、量化策略和AI驱动的市场洞察服务",
  "description_en": "Specializing in financial data analytics, quantitative strategies, and AI-driven market insights"
}
```

### Response Example

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "brand_name_zh": "智能数据科技",
  "brand_name_en": "SmartData Tech",
  "logo_url": "https://cdn.tmrland.com/logos/smartdata.png",
  "description_zh": "专注于金融数据分析、量化策略和AI驱动的市场洞察服务",
  "description_en": "Specializing in financial data analytics, quantitative strategies, and AI-driven market insights",
  "reputation_score": 87.5,
  "grand_apparatus_stats": {
    "total_answers": 42,
    "accuracy_rate": 0.78,
    "avg_score": 8.2
  },
  "status": "active",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_owner` | Authenticated user is not the business owner |
| 404 | `business_not_found` | No business with this ID |
| 422 | `validation_error` | Field value exceeds length limit |

---

## POST /api/v1/businesses/{business_id}/agent-card

Create an A2A-compatible agent card for the business. Describes the business's capabilities, pricing, SLA, and protocol endpoint.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `capabilities` | list[str] | No | List of capability tags. Default `[]` |
| `pricing` | dict \| null | No | Structured pricing object. Fields: `base_price` (base rate), `price_min`, `price_max` (acceptable range), `accepted_currencies` (list, e.g. `["USD", "USDC"]`). All numeric fields must be > 0 if provided; min must be ≤ max. |
| `accepted_payment_methods` | list[str] | No | Payment methods accepted. Default `[]` |
| `sla` | dict \| null | No | Service level agreement terms |
| `a2a_endpoint` | str \| null | No | A2A protocol endpoint URL |

### Request Example

```json
{
  "capabilities": ["financial-analysis", "market-research", "data-visualization", "report-generation"],
  "pricing": {
    "base_price": 50.0,
    "price_min": 20.0,
    "price_max": 150.0,
    "accepted_currencies": ["USD", "USDC"]
  },
  "accepted_payment_methods": ["wallet_balance", "usdc"],
  "sla": {
    "response_time_minutes": 30,
    "delivery_time_hours": 24,
    "uptime_guarantee": 0.995,
    "revision_limit": 2
  },
  "a2a_endpoint": "https://agent.smartdata.cn/a2a/v1"
}
```

### Response Example

```json
{
  "id": "e5f6a7b8-c9d0-1234-efab-567890123456",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "capabilities": ["financial-analysis", "market-research", "data-visualization", "report-generation"],
  "pricing": {
    "base_price": 50.0,
    "price_min": 20.0,
    "price_max": 150.0,
    "accepted_currencies": ["USD", "USDC"]
  },
  "accepted_payment_methods": ["wallet_balance", "usdc"],
  "sla": {
    "response_time_minutes": 30,
    "delivery_time_hours": 24,
    "uptime_guarantee": 0.995,
    "revision_limit": 2
  },
  "a2a_endpoint": "https://agent.smartdata.cn/a2a/v1",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_owner` | Authenticated user is not the business owner |
| 404 | `business_not_found` | No business with this ID |
| 409 | `agent_card_exists` | Agent card already exists; use PATCH to update |

---

## GET /api/v1/businesses/{business_id}/agent-card

Retrieve a business's agent card. Public endpoint used for A2A discovery.

**Auth:** None

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Example

```
GET /api/v1/businesses/b2c3d4e5-f6a7-8901-bcde-f12345678901/agent-card
```

### Response Example

```json
{
  "id": "e5f6a7b8-c9d0-1234-efab-567890123456",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "capabilities": ["financial-analysis", "market-research", "data-visualization", "report-generation"],
  "pricing": {
    "base_price": 50.0,
    "price_min": 20.0,
    "price_max": 150.0,
    "accepted_currencies": ["USD", "USDC"]
  },
  "accepted_payment_methods": ["wallet_balance", "usdc"],
  "sla": {
    "response_time_minutes": 30,
    "delivery_time_hours": 24,
    "uptime_guarantee": 0.995,
    "revision_limit": 2
  },
  "a2a_endpoint": "https://agent.smartdata.cn/a2a/v1",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T11:45:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `agent_card_not_found` | No agent card for this business |

---

## PATCH /api/v1/businesses/{business_id}/agent-card

Update an existing agent card. Only the business owner can update.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `capabilities` | list[str] \| null | No | Updated capability tags |
| `pricing` | dict \| null | No | Updated structured pricing (same format as POST) |
| `accepted_payment_methods` | list[str] \| null | No | Updated payment methods |
| `sla` | dict \| null | No | Updated SLA terms |
| `a2a_endpoint` | str \| null | No | Updated A2A endpoint URL |

### Request Example

```json
{
  "capabilities": ["financial-analysis", "market-research", "data-visualization", "report-generation", "sentiment-analysis"],
  "sla": {
    "response_time_minutes": 15,
    "delivery_time_hours": 12,
    "uptime_guarantee": 0.999,
    "revision_limit": 3
  }
}
```

### Response Example

```json
{
  "id": "e5f6a7b8-c9d0-1234-efab-567890123456",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "capabilities": ["financial-analysis", "market-research", "data-visualization", "report-generation", "sentiment-analysis"],
  "pricing": {
    "base_price": 50.0,
    "price_min": 20.0,
    "price_max": 150.0,
    "accepted_currencies": ["USD", "USDC"]
  },
  "accepted_payment_methods": ["wallet_balance", "usdc"],
  "sla": {
    "response_time_minutes": 15,
    "delivery_time_hours": 12,
    "uptime_guarantee": 0.999,
    "revision_limit": 3
  },
  "a2a_endpoint": "https://agent.smartdata.cn/a2a/v1",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T14:20:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_owner` | Authenticated user is not the business owner |
| 404 | `agent_card_not_found` | No agent card exists; use POST to create one |
