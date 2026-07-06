# Messages API

Base URL: `/api/v1/messages`

Order-scoped messaging between personal and business parties. Messages are organized by order and support attachments.

---

## GET /api/v1/messages/conversations

List all message conversations for the authenticated user. Returns a summary of each order-based conversation.

**Auth:** Required

### Request Body

None.

### Request Example

```
GET /api/v1/messages/conversations
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
[
  {
    "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "other_party_id": "aabbccdd-eeff-0011-2233-445566778899",
    "other_party_name": "李伟",
    "last_message": "Thank you for the revised report, it looks great. I will confirm the order now.",
    "last_message_at": "2026-03-06T16:00:00Z",
    "unread_count": 0,
    "total_messages": 12
  },
  {
    "order_id": "22334455-6677-8899-aabb-ccddeeff0011",
    "other_party_id": "bbccddee-ff00-1122-3344-556677889900",
    "other_party_name": "王芳",
    "last_message": "Could you include a breakdown by geographic region as well?",
    "last_message_at": "2026-03-04T11:30:00Z",
    "unread_count": 2,
    "total_messages": 5
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |

---

## GET /api/v1/messages/orders/{order_id}

Retrieve all messages for a specific order.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Example

```
GET /api/v1/messages/orders/11223344-5566-7788-99aa-bbccddeeff00
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
[
  {
    "id": "msg11111-2222-3333-4444-555566667777",
    "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "sender_id": "aabbccdd-eeff-0011-2233-445566778899",
    "content": "Hi, I need a detailed financial analysis of the Q4 2025 tech sector. Can you include year-over-year comparisons?",
    "attachments": [],
    "is_read": true,
    "created_at": "2026-02-27T11:30:00Z"
  },
  {
    "id": "msg22222-3333-4444-5555-666677778888",
    "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "sender_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "content": "Absolutely. I will include YoY comparisons for all major tech sub-sectors. I will also add our proprietary sentiment index for each. Expected delivery by Feb 28.",
    "attachments": [],
    "is_read": true,
    "created_at": "2026-02-27T12:00:00Z"
  },
  {
    "id": "msg33333-4444-5555-6666-777788889999",
    "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "sender_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "content": "Report is ready. Please find the deliverable attached.",
    "attachments": [
      {
        "url": "https://cdn.tmrland.com/deliverables/11223344/report-v1.pdf",
        "filename": "Q4-2025-Tech-Sector-Analysis.pdf",
        "size_bytes": 2456789
      }
    ],
    "is_read": true,
    "created_at": "2026-02-28T09:15:00Z"
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not the personal user or business on this order |
| 404 | `order_not_found` | No order with this ID |

---

## POST /api/v1/messages/orders/{order_id}

Send a message in an order conversation.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str | Yes | Message text |
| `attachments` | list[dict] \| null | No | List of attachment objects with `url` and `filename` |

### Request Example

```json
{
  "content": "I have prepared a supplementary data appendix with the raw datasets used in the analysis. Please find it attached.",
  "attachments": [
    {
      "url": "https://cdn.tmrland.com/attachments/11223344/data-appendix.xlsx",
      "filename": "Q4-2025-Raw-Data-Appendix.xlsx"
    }
  ]
}
```

### Response Example

```json
{
  "id": "msg44444-5555-6666-7777-888899990000",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "sender_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "content": "I have prepared a supplementary data appendix with the raw datasets used in the analysis. Please find it attached.",
  "attachments": [
    {
      "url": "https://cdn.tmrland.com/attachments/11223344/data-appendix.xlsx",
      "filename": "Q4-2025-Raw-Data-Appendix.xlsx",
      "size_bytes": 1234567
    }
  ],
  "is_read": false,
  "created_at": "2026-03-01T10:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not the personal user or business on this order |
| 404 | `order_not_found` | No order with this ID |
| 422 | `validation_error` | Message content cannot be empty |

---

## POST /api/v1/messages/orders/{order_id}/read

Mark all messages in an order conversation as read for the authenticated user.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

None.

### Request Example

```
POST /api/v1/messages/orders/11223344-5566-7788-99aa-bbccddeeff00/read
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "message": "All messages marked as read",
  "marked_count": 3
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not the personal user or business on this order |
| 404 | `order_not_found` | No order with this ID |
