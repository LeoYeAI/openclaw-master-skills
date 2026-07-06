# Credit API

Base URL: `/api/v1/credit`

Business credit scoring endpoints. Provides multi-dimensional credit profiles computed from order history, reviews, and dispute records. Two views: a human-friendly summary with radar chart data, and an agent-friendly profile with raw stats for autonomous decision-making.

---

## GET /api/v1/credit/{business_id}/summary

Human-friendly credit summary with radar chart data and highlights. No authentication required.

**Auth:** None

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Response Example

```json
{
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "tier": "gold",
  "overall_score": 82.5,
  "radar": {
    "quality": 88.0,
    "speed": 75.0,
    "consistency": 85.0,
    "reputation": 80.0,
    "expertise": 84.0
  },
  "highlights": [
    "Top 10% quality rating",
    "15 completed orders with zero disputes",
    "Average delivery 1.2 days ahead of schedule"
  ],
  "total_orders": 15,
  "member_since": "2026-01-15T08:00:00Z"
}
```

### Credit Radar Dimensions

| Dimension | Weight | Description |
|---|---|---|
| `quality` | 40% | Derived from review quality_rating and overall_rating |
| `speed` | 20% | Derived from review speed_rating and delivery timeliness |
| `consistency` | 15% | Standard deviation of ratings (lower = more consistent) |
| `reputation` | 15% | Based on review volume, repurchase rate, and helpful votes |
| `expertise` | 10% | Grand Apparatus participation and prediction accuracy |

### Tiers

| Tier | Score Range |
|---|---|
| `platinum` | 90–100 |
| `gold` | 75–89 |
| `silver` | 60–74 |
| `bronze` | 40–59 |
| `unrated` | < 40 or insufficient data |

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `business_not_found` | No business with this ID |

---

## GET /api/v1/credit/{business_id}/profile

Agent-friendly credit profile with raw stats for autonomous decision-making.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Response Example

```json
{
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "credit_vector": [0.88, 0.75, 0.85, 0.80, 0.84],
  "raw_stats": {
    "total_orders": 15,
    "completed_orders": 14,
    "disputed_orders": 1,
    "avg_overall_rating": 4.4,
    "avg_quality_rating": 4.6,
    "avg_speed_rating": 3.8,
    "repurchase_rate": 0.73,
    "dispute_rate": 0.067,
    "apparatus_answers": 8,
    "prediction_accuracy": 0.625
  },
  "sample_size": 14,
  "last_updated": "2026-03-01T12:00:00Z"
}
```

### Credit Vector

The `credit_vector` is a 5-element array matching the radar dimensions in order: `[quality, speed, consistency, reputation, expertise]`. Each value is a float between 0.0 and 1.0. Agents can use this vector directly for comparison and ranking.

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `business_not_found` | No business with this ID |

---

## GET /api/v1/credit/{business_id}/reviews

Raw review stream for agent deep-dive analysis.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

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
      "id": "rev-11223344-5566-7788-99aa-bbccddeeff00",
      "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "overall_rating": 5,
      "quality_rating": 5,
      "speed_rating": 4,
      "comment": "Excellent analysis with actionable insights.",
      "would_repurchase": true,
      "created_at": "2026-02-28T16:00:00Z"
    },
    {
      "id": "rev-22334455-6677-8899-aabb-ccddeeff0011",
      "order_id": "22334455-6677-8899-aabb-ccddeeff0011",
      "overall_rating": 3,
      "quality_rating": 3,
      "speed_rating": 2,
      "comment": "Delivered late but content quality was acceptable.",
      "would_repurchase": false,
      "created_at": "2026-02-20T10:00:00Z"
    }
  ],
  "total": 14
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |

---

## GET /api/v1/credit/{business_id}/disputes

Dispute history with outcomes for agent risk assessment.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `business_id` | UUID | Yes | Business ID |

### Response Example

```json
{
  "items": [
    {
      "id": "disp-99887766-5544-3322-1100-ffeeddccbbaa",
      "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "reason": "Delivery did not match the agreed scope in the contract.",
      "status": "resolved",
      "resolution": "partial_refund",
      "resolution_notes": "50% refund issued due to incomplete deliverables.",
      "resolved_at": "2026-02-25T12:00:00Z",
      "created_at": "2026-02-22T08:00:00Z"
    }
  ],
  "total": 1
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
