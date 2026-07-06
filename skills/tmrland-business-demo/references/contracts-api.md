# Contracts API

Base URL: `/api/v1/contract-templates` and `/api/v1/contracts`

Businesses create contract templates that define default terms, pricing, locked fields, and negotiable fields. Templates are auto-sent as the first proposal when a negotiation session starts. Contract proposals are exchanged within negotiation sessions via `POST /negotiations/{session_id}/propose`. The backend enforces `locked_fields` — any proposal that modifies a locked field returns `400 locked_field_change`.

---

## POST /api/v1/contract-templates/

Create a new contract template. Businesses define reusable templates for their services.

**Auth:** Required (business)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | str | Yes | Template name, 1-200 characters |
| `default_terms` | dict | No | Default contract terms. Default `{}` |
| `locked_fields` | list[str] | No | Fields that cannot be changed in proposals. Default `[]` |
| `negotiable_fields` | list[str] | No | Fields open for negotiation. Default `[]` |
| `amount` | float \| null | No | Default USD price |
| `accepted_currencies` | float \| null | No | Default USDC price |

### Request Example

```json
{
  "name": "Standard Financial Analysis Package",
  "default_terms": {
    "delivery_days": 5,
    "revisions": 2,
    "scope": "Market analysis report with data visualizations",
    "base_price": 200.00,
    "currency": "USD",
    "includes_raw_data": true
  },
  "locked_fields": ["currency", "includes_raw_data"],
  "negotiable_fields": ["delivery_days", "revisions", "scope", "base_price"]
}
```

### Response Example

```json
{
  "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "name": "Standard Financial Analysis Package",
  "default_terms": {
    "delivery_days": 5,
    "revisions": 2,
    "scope": "Market analysis report with data visualizations",
    "base_price": 200.00,
    "currency": "USD",
    "includes_raw_data": true
  },
  "locked_fields": ["currency", "includes_raw_data"],
  "negotiable_fields": ["delivery_days", "revisions", "scope", "base_price"],
  "status": "draft",
  "is_system_template": false,
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_business` | User does not have business role |
| 422 | `validation_error` | Name missing or exceeds 200 characters |

---

## GET /api/v1/contract-templates/

List contract templates. Businesses see their own templates.

**Auth:** Required (business)

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID \| null | No | Filter by business ID |

### Request Example

```
GET /api/v1/contract-templates/?business_id=b2c3d4e5-f6a7-8901-bcde-f12345678901
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
[
  {
    "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
    "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "name": "Standard Financial Analysis Package",
    "default_terms": {
      "delivery_days": 5,
      "revisions": 2,
      "scope": "Market analysis report with data visualizations",
      "base_price": 200.00,
      "currency": "USD",
      "includes_raw_data": true
    },
    "locked_fields": ["currency", "includes_raw_data"],
    "negotiable_fields": ["delivery_days", "revisions", "scope", "base_price"],
    "status": "published",
    "is_system_template": false,
    "created_at": "2026-02-27T10:30:00Z"
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |

---

## GET /api/v1/contract-templates/{template_id}

Retrieve a specific contract template by ID.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `template_id` | UUID | Yes | Template ID |

### Request Example

```
GET /api/v1/contract-templates/d4e5f6a7-b8c9-0123-defa-234567890123
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "name": "Standard Financial Analysis Package",
  "default_terms": {
    "delivery_days": 5,
    "revisions": 2,
    "scope": "Market analysis report with data visualizations",
    "base_price": 200.00,
    "currency": "USD",
    "includes_raw_data": true
  },
  "locked_fields": ["currency", "includes_raw_data"],
  "negotiable_fields": ["delivery_days", "revisions", "scope", "base_price"],
  "status": "published",
  "is_system_template": false,
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `template_not_found` | No template with this ID |

---

## PATCH /api/v1/contract-templates/{template_id}

Update an existing contract template. Only the template owner can update.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `template_id` | UUID | Yes | Template ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | str \| null | No | Template name, 1-200 characters |
| `default_terms` | dict \| null | No | Updated default terms |
| `locked_fields` | list[str] \| null | No | Updated locked fields |
| `negotiable_fields` | list[str] \| null | No | Updated negotiable fields |
| `status` | str \| null | No | `"draft"`, `"published"`, or `"archived"` |
| `amount` | float \| null | No | USD price |
| `accepted_currencies` | float \| null | No | USDC price |

### Request Example

```json
{
  "default_terms": {
    "delivery_days": 3,
    "revisions": 3,
    "scope": "Market analysis report with data visualizations and executive summary",
    "base_price": 250.00,
    "currency": "USD",
    "includes_raw_data": true
  },
  "status": "published"
}
```

### Response Example

```json
{
  "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "name": "Standard Financial Analysis Package",
  "default_terms": {
    "delivery_days": 3,
    "revisions": 3,
    "scope": "Market analysis report with data visualizations and executive summary",
    "base_price": 250.00,
    "currency": "USD",
    "includes_raw_data": true
  },
  "locked_fields": ["currency", "includes_raw_data"],
  "negotiable_fields": ["delivery_days", "revisions", "scope", "base_price"],
  "status": "published",
  "is_system_template": false,
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_owner` | Authenticated user is not the template owner |
| 404 | `template_not_found` | No template with this ID |

---

## DELETE /api/v1/contract-templates/{template_id}

Delete a contract template. Only the template owner can delete.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `template_id` | UUID | Yes | Template ID |

### Request Example

```
DELETE /api/v1/contract-templates/d4e5f6a7-b8c9-0123-defa-234567890123
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "ok": true
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_owner` | Authenticated user is not the template owner |
| 404 | `template_not_found` | No template with this ID |

---

## GET /api/v1/contracts/

List contracts for the authenticated user. Use `role=business` to see contracts where you are the business party.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | str | No | `"business"` or `"personal"`. Filters by the user's role in the contract |
| `offset` | int | No | Pagination offset. Default `0` |
| `limit` | int | No | Number of results. Default `20` |

### Request Example

```
GET /api/v1/contracts/?role=business&offset=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "items": [
    {
      "id": "ff001122-3344-5566-7788-99aabbccddee",
      "template_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
      "terms": {
        "delivery_days": 3,
        "revisions": 3,
        "scope": "Customized financial analysis with sector drill-down",
        "base_price": 220.00,
        "currency": "USD",
        "includes_raw_data": true
      },
      "amount": 220.00,
      "accepted_currencies": null,
      "confirmed_at": "2026-02-27T15:00:00Z",
      "created_at": "2026-02-27T10:30:00Z",
      "updated_at": "2026-02-27T12:30:00Z"
    }
  ],
  "total": 1
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |

---

## GET /api/v1/contracts/{contract_id}

Retrieve a specific contract.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `contract_id` | UUID | Yes | Contract ID |

### Request Example

```
GET /api/v1/contracts/ff001122-3344-5566-7788-99aabbccddee
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "ff001122-3344-5566-7788-99aabbccddee",
  "template_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "terms": {
    "delivery_days": 3,
    "revisions": 3,
    "scope": "Customized financial analysis with sector drill-down",
    "base_price": 220.00,
    "currency": "USD",
    "includes_raw_data": true
  },
  "amount": 220.00,
  "accepted_currencies": null,
  "confirmed_at": "2026-02-27T15:00:00Z",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T12:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not a party to this contract |
| 404 | `contract_not_found` | No contract with this ID |
