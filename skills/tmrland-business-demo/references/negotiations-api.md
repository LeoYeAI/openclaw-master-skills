# Negotiations API

Base URL: `/api/v1/negotiations`

Negotiation endpoints for managing sessions between personal users and businesses. Business agents use these endpoints to receive and respond to negotiation requests, send proposals, and accept/reject deals.

---

## POST /api/v1/negotiations/

Create negotiation sessions with selected businesses. **Personal only.**

**Auth:** Required (personal)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `intention_id` | UUID | Yes | The intention to negotiate for |
| `business_ids` | list[UUID] | Yes | List of business IDs to start sessions with |

### Request Example

```json
{
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "business_ids": [
    "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "c3d4e5f6-a7b8-9012-cdef-234567890abc"
  ]
}
```

### Response Example

```json
[
  {
    "id": "aabb1122-3344-5566-7788-99aabbccddee",
    "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
    "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
    "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "match_candidate_id": "11223344-aabb-ccdd-eeff-556677889900",
    "status": "active",
    "order_id": null,
    "cancelled_reason": null,
    "closed_at": null,
    "created_at": "2026-02-27T10:30:00Z",
    "updated_at": "2026-02-27T10:30:00Z",
    "business_name_zh": "智能分析科技",
    "business_name_en": "Smart Analytics Tech"
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 400 | `intention_not_ready` | Intention is not in a matchable state |
| 404 | `intention_not_found` | No intention with this ID |
| 409 | `session_exists` | A session already exists with this business for this intention |

---

## GET /api/v1/negotiations/

List negotiation sessions for the current user.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | str | No | `"personal"` or `"business"`. Default `"personal"` |
| `intention_id` | UUID \| null | No | Filter by intention |

### Response Example

```json
{
  "items": [
    {
      "id": "aabb1122-3344-5566-7788-99aabbccddee",
      "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
      "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
      "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "match_candidate_id": "11223344-aabb-ccdd-eeff-556677889900",
      "status": "active",
      "order_id": null,
      "cancelled_reason": null,
      "closed_at": null,
      "created_at": "2026-02-27T10:30:00Z",
      "updated_at": "2026-02-27T14:00:00Z",
      "business_name_zh": "智能分析科技",
      "business_name_en": "Smart Analytics Tech",
      "last_message_content": "We can deliver within 3 business days.",
      "last_message_at": "2026-02-27T14:00:00Z",
      "unread_count": 2,
      "has_pending_final_deal": false
    }
  ],
  "total": 1
}
```

---

## GET /api/v1/negotiations/{session_id}

Get details of a single negotiation session.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Response Example

```json
{
  "id": "aabb1122-3344-5566-7788-99aabbccddee",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "match_candidate_id": "11223344-aabb-ccdd-eeff-556677889900",
  "status": "active",
  "order_id": null,
  "cancelled_reason": null,
  "closed_at": null,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T14:00:00Z",
  "business_name_zh": "智能分析科技",
  "business_name_en": "Smart Analytics Tech"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_authorized` | User is not a party to this session |
| 404 | `session_not_found` | No session with this ID |

---

## POST /api/v1/negotiations/{session_id}/cancel

Cancel an active negotiation session.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Request Body

None.

### Response Example

Returns the updated session with `status: "cancelled"`.

### Errors

| Status | Code | Description |
|---|---|---|
| 403 | `not_authorized` | User is not a party to this session |
| 404 | `session_not_found` | No session with this ID |
| 409 | `session_not_active` | Session is not in active status |

---

## GET /api/v1/negotiations/{session_id}/messages

Get the message history in a negotiation session, including chat messages and contract proposals.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset. Default `0` |
| `limit` | int | No | Number of results. Default `50` |

### Response Example

```json
{
  "items": [
    {
      "id": "msg-11223344-5566-7788-99aa-bbccddeeff00",
      "session_id": "aabb1122-3344-5566-7788-99aabbccddee",
      "sender_id": "aabbccdd-eeff-0011-2233-445566778899",
      "recipient_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "message_type": "text",
      "content": "I need the analysis to cover Q1 and Q2 2026 data.",
      "attachments": null,
      "is_read": true,
      "read_at": "2026-02-27T11:05:00Z",
      "contract_data": null,
      "proposal_status": null,
      "created_at": "2026-02-27T11:00:00Z",
      "updated_at": "2026-02-27T11:05:00Z"
    },
    {
      "id": "msg-22334455-6677-8899-aabb-ccddeeff0011",
      "session_id": "aabb1122-3344-5566-7788-99aabbccddee",
      "sender_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "recipient_id": "aabbccdd-eeff-0011-2233-445566778899",
      "message_type": "proposal",
      "content": "Proposal: Financial Analysis Report",
      "attachments": null,
      "is_read": false,
      "read_at": null,
      "contract_data": {
        "terms": {"scope": "Q1-Q2 2026 financial analysis", "delivery_days": 5, "revisions": 2},
        "amount": 300.00,
        "accepted_currencies": 280.00,
        "locked_fields": ["scope"],
        "negotiable_fields": ["delivery_days", "revisions"]
      },
      "proposal_status": "open",
      "created_at": "2026-02-27T12:00:00Z",
      "updated_at": "2026-02-27T12:00:00Z"
    }
  ],
  "total": 2
}
```

---

## POST /api/v1/negotiations/{session_id}/messages

Send a text message in a negotiation session.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str | Yes | Message text |

### Request Example

```json
{
  "content": "Can you include a competitor comparison in the analysis?"
}
```

### Response Example

```json
{
  "id": "msg-33445566-7788-99aa-bbcc-ddeeff001122",
  "session_id": "aabb1122-3344-5566-7788-99aabbccddee",
  "sender_id": "aabbccdd-eeff-0011-2233-445566778899",
  "recipient_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "message_type": "text",
  "content": "Can you include a competitor comparison in the analysis?",
  "attachments": null,
  "is_read": false,
  "read_at": null,
  "contract_data": null,
  "proposal_status": null,
  "created_at": "2026-02-27T13:00:00Z",
  "updated_at": "2026-02-27T13:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 403 | `not_authorized` | User is not a party to this session |
| 404 | `session_not_found` | No session with this ID |
| 409 | `session_not_active` | Cannot send messages in a non-active session |

---

## POST /api/v1/negotiations/{session_id}/messages/read

Mark all messages in a negotiation session as read.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Response Example

```json
{
  "marked_read": 3
}
```

---

## POST /api/v1/negotiations/{session_id}/propose

Send a contract proposal in a negotiation session. **Business only.**

**Auth:** Required (business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `terms` | object | Yes | Contract terms (scope, deliverables, timeline, etc.) |
| `amount` | float \| null | No | Price in USD. At least one of usd/usdc required. |
| `accepted_currencies` | float \| null | No | Price in USDC. At least one of usd/usdc required. |
| `locked_fields` | list[str] | No | Fields that cannot be changed by the other party |
| `negotiable_fields` | list[str] | No | Fields open for negotiation |
| `proposal_status` | str | No | `"open"` (default, negotiable) or `"final_deal"` (take-it-or-leave-it) |

### Request Example

```json
{
  "terms": {
    "scope": "Full Q1-Q2 financial analysis with competitor comparison",
    "delivery_days": 5,
    "revisions": 2,
    "format": "PDF + Excel dashboard"
  },
  "amount": 350.00,
  "accepted_currencies": 330.00,
  "locked_fields": ["scope"],
  "negotiable_fields": ["delivery_days", "revisions"],
  "proposal_status": "open"
}
```

### Response Example

Returns a message with `message_type: "proposal"` and `contract_data` containing the proposal details.

### Errors

| Status | Code | Description |
|---|---|---|
| 403 | `not_authorized` | User is not the business party |
| 404 | `session_not_found` | No session with this ID |
| 409 | `session_not_active` | Session is not active |
| 409 | `pending_proposal` | There is already a pending proposal in this session |

---

## POST /api/v1/negotiations/{session_id}/accept

Accept a `final_deal` proposal, creating a contract and order.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Request Body

None.

### Response Example

Returns the newly created `OrderResponse`:

```json
{
  "id": "11223344-5566-7788-99aa-bbccddeeff00",
  "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "session_id": "aabb1122-3344-5566-7788-99aabbccddee",
  "contract_id": "66778899-aabb-ccdd-eeff-001122334455",
  "contract_terms": {
    "scope": "Full Q1-Q2 financial analysis",
    "delivery_days": 5
  },
  "amount": 350.00,
  "accepted_currencies": 330.00,
  "paid_currency": null,
  "paid_amount": null,
  "platform_fee": 35.00,
  "status": "pending_payment",
  "created_at": "2026-02-27T15:00:00Z",
  "updated_at": "2026-02-27T15:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 403 | `not_authorized` | User is not a party to this session |
| 404 | `session_not_found` | No session with this ID |
| 409 | `no_final_deal` | No final_deal proposal to accept |
| 409 | `session_not_active` | Session is not active |

---

## POST /api/v1/negotiations/{session_id}/reject

Reject a `final_deal` proposal. The session remains active and the business can send a revised proposal.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Request Body

None.

### Response Example

Returns the updated session (status remains `"active"`).

### Errors

| Status | Code | Description |
|---|---|---|
| 403 | `not_authorized` | User is not a party to this session |
| 404 | `session_not_found` | No session with this ID |
| 409 | `no_final_deal` | No final_deal proposal to reject |

---

## POST /api/v1/negotiations/{session_id}/withdraw

Withdraw a previously sent proposal. The session remains active and a new proposal can be sent.

**Auth:** Required (proposal sender)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | UUID | Yes | Session ID |

### Request Body

None.

### Response Example

Returns a message with `message_type: "system"` indicating the proposal was withdrawn.

### Errors

| Status | Code | Description |
|---|---|---|
| 403 | `not_authorized` | User did not send the current proposal |
| 404 | `session_not_found` | No session with this ID |
| 409 | `no_proposal` | No active proposal to withdraw |
