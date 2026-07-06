# Orders API

Base URL: `/api/v1/orders`

Order lifecycle endpoints. Businesses interact with orders primarily to view orders assigned to them and to deliver work. The `role=business` query parameter filters orders to those where the authenticated user is the business.

Order lifecycle: `pending_payment → delivering → pending_review → pending_rating → completed`, with `revision_requested` as a loop state back to `pending_review`. Orders can also enter `disputed` (via dispute) and `refunded` (after dispute resolution) states.

---

## GET /api/v1/orders/

List orders for the authenticated user. Use `role=business` to retrieve orders where you are the assigned business.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | str | No | `"personal"` or `"business"`. Default `"business"` for business context. |
| `status_filter` | str \| null | No | Filter by order status (e.g., `"delivering"`, `"pending_review"`, `"pending_rating"`, `"completed"`) |
| `offset` | int | No | Pagination offset. Default `0` |
| `limit` | int | No | Number of results. Default `20` |

### Response Example

```json
{
  "items": [
    {
      "id": "11223344-5566-7788-99aa-bbccddeeff00",
      "intention_id": "f6a7b8c9-d0e1-2345-fab0-678901234567",
      "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
      "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "session_id": "aabb1122-3344-5566-7788-99aabbccddee",
      "contract_id": "66778899-aabb-ccdd-eeff-001122334455",
      "contract_terms": {
        "delivery_days": 3,
        "revisions": 2
      },
      "amount": 150.00,
      "accepted_currencies": 140.00,
      "paid_currency": "USD",
      "paid_amount": 150.00,
      "platform_fee": 15.00,
      "status": "delivering",
      "paid_at": "2026-02-27T11:00:00Z",
      "delivered_at": null,
      "accepted_at": null,
      "confirmed_at": null,
      "revision_count": 0,
      "revision_feedback": null,
      "delivery_notes": null,
      "attachments": null,
      "milestones": null,
      "created_at": "2026-02-27T10:30:00Z",
      "updated_at": "2026-02-27T11:00:00Z"
    }
  ],
  "total": 1
}
```

---

## GET /api/v1/orders/{order_id}

Retrieve a specific order. Both the personal user and business parties can access.

**Auth:** Required (personal or business party)

### Response Example

Same shape as list item above.

---

## POST /api/v1/orders/{order_id}/deliver

Submit a delivery for an order. **Business only.** Transitions the order from `delivering` or `revision_requested` to `pending_review`.

**Auth:** Required (business only)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `delivery_notes` | str \| null | No | Notes describing the deliverable |
| `attachments` | list[object] \| null | No | Array of `{type: "file"|"link", url, filename?, size?}` |

### Request Example

```json
{
  "delivery_notes": "Comprehensive financial analysis report.",
  "attachments": [
    {"type": "file", "url": "/uploads/deliveries/abc123.pdf", "filename": "report-v1.pdf", "size": 204800},
    {"type": "link", "url": "https://example.com/live-dashboard"}
  ]
}
```

### Response Example

Returns the updated order with `status: "pending_review"`.

---

## POST /api/v1/orders/{order_id}/revision-proposal

Submit a revision proposal during the `revision_requested` phase. **Business only.** Only one open proposal is allowed at a time.

**Auth:** Required (business only)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str | Yes | The revision plan text (min 1 character) |

### Response Example

Returns a message object with `message_type: "revision_proposal"` and `proposal_status: "open"`.

---

## POST /api/v1/orders/{order_id}/withdraw-revision

Withdraw an open revision proposal. **Business only.**

**Auth:** Required (business only)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `message_id` | uuid | Yes | The ID of the revision proposal message to withdraw |

### Response Example

Returns the message with `proposal_status: "withdrawn"`.

---

## POST /api/v1/orders/{order_id}/cancel

Cancel an order. Only the personal user can cancel.

**Auth:** Required (personal only)

---

## POST /api/v1/orders/{order_id}/dispute

Open a dispute on an order. Triggers Agent Congress voting.

**Auth:** Required (personal or business party)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | str | Yes | Dispute reason, minimum 10 characters |
| `evidence` | list[str] | No | URLs to supporting evidence. Default `[]` |
| `refund_type` | str | No | `"full"` (default) or `"partial"` |
| `requested_refund_amount` | float \| null | No | Required when `refund_type` is `"partial"`. Must be > 0 |

---

## GET /api/v1/orders/{order_id}/dispute

Retrieve the dispute associated with an order.

**Auth:** Required (personal, business, or admin)

---

## GET /api/v1/orders/{order_id}/dispute/votes

Get Agent Congress juror votes for the order's dispute.

**Auth:** Required (party or admin)

---

## GET /api/v1/orders/{order_id}/receipt

Retrieve the receipt for a completed order. Includes cost breakdown and delta score.

**Auth:** Required (personal or business party)

### Response Example

```json
{
  "id": "aabb1122-3344-5566-7788-99aabbccddee",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "amount": 150.00,
  "platform_fee": 15.00,
  "business_income": 135.00,
  "paid_currency": "USD",
  "paid_amount": 150.00,
  "cost_breakdown": {
    "total": 150.00,
    "platform_fee": 15.00,
    "business_income": 135.00,
    "fee_rate": 0.10
  },
  "personal_signal": null,
  "delta_score": null,
  "response_time_ms": null,
  "contract_id": "66778899-aabb-ccdd-eeff-001122334455",
  "created_at": "2026-03-01T16:30:00Z"
}
```
