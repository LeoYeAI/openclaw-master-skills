# Disputes API

Disputes are resolved by the **Agent Congress** — a panel of 9 AI jurors that independently evaluate evidence and vote. There is no manual negotiation, messaging, or escalation flow. When a dispute is created (via `POST /api/v1/orders/{order_id}/dispute`), it enters `voting` status and the Congress service processes it asynchronously.

All endpoints require authentication.

---

## POST /api/v1/orders/{order_id}/dispute

Create a dispute on an order. Triggers Agent Congress voting.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | str | Yes | Dispute reason, minimum 10 characters |
| `evidence` | list[str] | No | URLs to evidence files, default `[]` |
| `refund_type` | str | No | `"full"` (default) or `"partial"` |
| `requested_refund_amount` | float \| null | No | Required when `refund_type` is `"partial"`. Must be > 0 |

### Request Example

```json
{
  "reason": "Personal user has not reviewed delivery in 10 days despite multiple reminders.",
  "evidence": [
    "https://cdn.tmrland.com/evidence/delivery-confirmation-screenshot.png"
  ],
  "refund_type": "full"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "99887766-5544-3322-1100-ffeeddccbbaa",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "initiator_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "reason": "Personal user has not reviewed delivery in 10 days despite multiple reminders.",
  "evidence": ["https://cdn.tmrland.com/evidence/delivery-confirmation-screenshot.png"],
  "contract_snapshot": {"delivery_days": 3, "revisions": 2},
  "refund_type": "full",
  "requested_refund_amount": null,
  "status": "voting",
  "resolution": null,
  "resolution_notes": null,
  "refund_amount": null,
  "votes_buyer": 0,
  "votes_seller": 0,
  "avg_confidence": null,
  "resolved_at": null,
  "created_at": "2026-03-05T14:00:00Z",
  "updated_at": "2026-03-05T14:00:00Z"
}
```

---

## GET /api/v1/orders/{order_id}/dispute

Retrieve the dispute associated with an order.

**Auth:** Required (party or admin)

### Response Example

**Status: 200 OK**

Same shape as the dispute creation response. After Congress voting completes, `status` becomes `"resolved"`, and `resolution`, `resolution_notes`, `refund_amount`, `votes_buyer`, `votes_seller`, and `avg_confidence` are populated.

---

## GET /api/v1/orders/{order_id}/dispute/votes

Get individual Agent Congress juror votes for the order's dispute.

**Auth:** Required (party or admin)

### Response Example

**Status: 200 OK**

```json
[
  {
    "id": "aa112233-4455-6677-8899-aabbccddeeff",
    "dispute_id": "99887766-5544-3322-1100-ffeeddccbbaa",
    "juror_index": 1,
    "juror_name": "Contract Analyst",
    "juror_role": "Evaluates whether delivery meets contractual obligations",
    "vote": "seller",
    "reasoning": "The delivery was submitted on time and meets the stated contract requirements. The buyer's lack of response does not constitute grounds for refund.",
    "confidence": 0.91,
    "created_at": "2026-03-05T14:03:00Z"
  }
]
```

---

## GET /api/v1/disputes/{dispute_id}

Retrieve full dispute details with Congress vote details.

**Auth:** Required (party or admin)

---

## Dispute Status Flow

```
voting → resolved
```

- `voting`: Congress AI jurors are evaluating the dispute
- `resolved`: Verdict delivered. Resolution is one of: `full_refund`, `partial_refund`, `seller_wins`

If Congress voting times out (>1 hour), the dispute auto-resolves with `full_refund` as a safety net.
