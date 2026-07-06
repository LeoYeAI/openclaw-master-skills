# Error Codes

This document describes the standard error response format and all HTTP error codes returned by the TMR Land API.

---

## Standard Error Response Format

All API errors follow this JSON structure:

```json
{
  "detail": {
    "code": "error_code_identifier",
    "message": "Human-readable error description"
  }
}
```

For validation errors (422), the response includes field-level details:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Description of validation failure",
      "type": "value_error"
    }
  ]
}
```

---

## HTTP Status Codes

### 400 Bad Request

The request is malformed or contains invalid parameters that do not fall under validation errors.

```json
{
  "detail": {
    "code": "bad_request",
    "message": "Invalid request format"
  }
}
```

**Common causes:**
- Malformed JSON body
- Unsupported content type
- Logical constraint violations (e.g., insufficient wallet balance)

| Code | Description |
|---|---|
| `bad_request` | Generic bad request |
| `insufficient_balance` | Wallet balance too low for the operation |
| `invalid_state` | Resource is in a state that does not support the operation |
| `price_out_of_range` | Proposal price falls outside the business's declared pricing range |

---

### 401 Unauthorized

Authentication is required or the provided credentials are invalid.

```json
{
  "detail": {
    "code": "not_authenticated",
    "message": "Not authenticated"
  }
}
```

**Common causes:**
- Missing `Authorization` header
- Expired JWT access token
- Invalid API key
- Incorrect login credentials

| Code | Description |
|---|---|
| `not_authenticated` | No valid authentication provided |
| `invalid_credentials` | Email/password combination is incorrect |
| `invalid_code` | Verification code is incorrect or expired |
| `invalid_token` | Reset or refresh token is invalid or expired |
| `invalid_refresh_token` | Refresh token is invalid, expired, or already used |
| `account_inactive` | Account has been deactivated by admin |
| `token_expired` | JWT access token has expired |
| `invalid_api_key` | API key is invalid or has been revoked |

---

### 403 Forbidden

The authenticated user does not have permission to perform the requested action.

```json
{
  "detail": {
    "code": "not_owner",
    "message": "You do not have permission to modify this resource"
  }
}
```

**Common causes:**
- Attempting to modify a resource owned by another user
- Role-restricted endpoint (e.g., business-only endpoint accessed by personal)
- Attempting to operate on another party's order/contract

| Code | Description |
|---|---|
| `not_owner` | User does not own the resource |
| `not_party` | User is not a personal user/business party to the order or contract |
| `not_personal` | Endpoint restricted to personal users only |
| `not_business` | Endpoint restricted to businesses only |
| `not_admin` | Endpoint restricted to admin users |
| `insufficient_permissions` | API key does not have the required permission scope |

---

### 404 Not Found

The requested resource does not exist.

```json
{
  "detail": {
    "code": "order_not_found",
    "message": "No order found with ID 11223344-5566-7788-99aa-bbccddeeff00"
  }
}
```

**Common causes:**
- Invalid UUID in the path
- Resource has been deleted
- Resource belongs to a different user and is not publicly accessible

| Code | Description |
|---|---|
| `user_not_found` | No user with the given ID or email |
| `business_not_found` | No business with the given ID |
| `order_not_found` | No order with the given ID |
| `contract_not_found` | No contract with the given ID |
| `template_not_found` | No contract template with the given ID |
| `intention_not_found` | No intention with the given ID |
| `review_not_found` | No review found for the given order |
| `dispute_not_found` | No dispute with the given ID |
| `receipt_not_found` | No receipt for the given order |
| `wallet_not_found` | User does not have a wallet |
| `kyc_not_found` | No KYC submission for the user |
| `agent_card_not_found` | Business does not have an agent card |
| `question_not_found` | No Grand Apparatus question with the given ID |
| `answer_not_found` | No answer with the given ID |
| `notification_not_found` | No notification with the given ID |
| `key_not_found` | No API key with the given ID |
| `exam_not_found` | No exam has been started |
| `reputation_not_found` | Reputation data not yet computed for the business |
| `no_agent_card` | Business has no A2A agent card configured |

---

### 409 Conflict

The request conflicts with the current state of a resource.

```json
{
  "detail": {
    "code": "email_already_registered",
    "message": "An account with this email already exists"
  }
}
```

**Common causes:**
- Attempting to create a resource that already exists
- State machine transition violation (e.g., delivering an already-delivered order)
- Duplicate vote or review

| Code | Description |
|---|---|
| `email_already_registered` | Email is already in use |
| `business_already_registered` | User already has a business profile |
| `agent_card_exists` | Agent card already exists for this business |
| `review_already_exists` | Review already submitted for this order |
| `dispute_already_exists` | Dispute already open for this order |
| `already_voted` | User has already voted on this answer |
| `already_escalated` | Dispute has already been escalated |
| `exam_already_started` | Business exam already in progress or completed |
| `kyc_already_submitted` | KYC verification already submitted |
| `invalid_status_transition` | The requested state change is not valid for the current status |
| `order_not_completed` | Order must be completed before this action |
| `contract_not_negotiable` | Contract is not in a negotiable state |
| `dispute_closed` | Dispute is already resolved |
| `question_closed` | Question is no longer accepting answers |
| `already_answered` | Business has already answered this question |
| `locked_field_change` | Attempted to change a locked contract field |

---

### 422 Unprocessable Entity

Request body failed Pydantic validation. Returns an array of field-level errors.

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address: An email address must have an @-sign.",
      "type": "value_error"
    },
    {
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "type": "string_too_short"
    }
  ]
}
```

**Common causes:**
- Missing required fields
- Invalid field types (string where int expected, etc.)
- String length constraints violated
- Numeric range constraints violated (e.g., amount must be > 0)
- Invalid enum values

---

### 500 Internal Server Error

An unexpected error occurred on the server.

```json
{
  "detail": {
    "code": "internal_error",
    "message": "An unexpected error occurred"
  }
}
```

**Common causes:**
- Database connection failure
- External service unavailable (LLM, Elasticsearch, Milvus)
- Unhandled application exception

| Code | Description |
|---|---|
| `internal_error` | Generic internal server error |
| `llm_generation_failed` | LLM service failed to generate a response |
| `agent_unreachable` | Could not reach a business's A2A endpoint (returns 503) |

---

## Authentication Header Formats

### JWT Bearer Token

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key

```
Authorization: Bearer tmr_sk_live_a1b2c3d4e5f6789012345678901234567890abcdef
```

Both formats use the same `Authorization: Bearer` header. The server distinguishes between JWT tokens and API keys by their prefix pattern.
