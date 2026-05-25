#!/bin/bash
# List all trips for the authenticated user
# Ordered by start_date descending (soonest upcoming first)

API_KEY="ubt_k1_your_key_here"

curl -s \
  -H "Authorization: Bearer $API_KEY" \
  https://ubtrippin.xyz/api/v1/trips \
  | python3 -m json.tool

# Example response:
# {
#   "data": [
#     {
#       "id": "550e8400-e29b-41d4-a716-446655440000",
#       "title": "Tokyo Spring 2026",
#       "start_date": "2026-04-01",
#       "end_date": "2026-04-14",
#       "primary_location": "Tokyo, Japan",
#       "travelers": ["Ian Rogers"],
#       "notes": null,
#       "cover_image_url": "https://images.unsplash.com/...",
#       "share_enabled": false,
#       "created_at": "2026-02-15T10:00:00Z",
#       "updated_at": "2026-02-15T10:00:00Z"
#     }
#   ],
#   "meta": { "count": 1 }
# }
