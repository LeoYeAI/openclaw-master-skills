#!/bin/bash
# Get a single trip with all its items (flights, hotels, trains, etc.)

API_KEY="ubt_k1_your_key_here"
TRIP_ID="550e8400-e29b-41d4-a716-446655440000"

curl -s \
  -H "Authorization: Bearer $API_KEY" \
  https://ubtrippin.xyz/api/v1/trips/$TRIP_ID \
  | python3 -m json.tool

# Example response:
# {
#   "data": {
#     "id": "550e8400-e29b-41d4-a716-446655440000",
#     "title": "Tokyo Spring 2026",
#     "start_date": "2026-04-01",
#     "end_date": "2026-04-14",
#     "primary_location": "Tokyo, Japan",
#     "travelers": ["Ian Rogers"],
#     "items": [
#       {
#         "id": "660e8400-e29b-41d4-a716-446655440001",
#         "trip_id": "550e8400-e29b-41d4-a716-446655440000",
#         "kind": "flight",
#         "provider": "Air France",
#         "traveler_names": ["Ian Rogers"],
#         "start_ts": "2026-04-01T08:30:00Z",
#         "end_ts": "2026-04-01T18:45:00Z",
#         "start_date": "2026-04-01",
#         "end_date": "2026-04-01",
#         "start_location": "Paris CDG",
#         "end_location": "Tokyo NRT",
#         "summary": "Flight AF276 CDG → NRT",
#         "details_json": {
#           "flight_number": "AF276",
#           "seat": "12A",
#           "confirmation": "XYZ123",
#           "terminal": "2E"
#         },
#         "status": "confirmed",
#         "confidence": 0.98,
#         "needs_review": false,
#         "created_at": "2026-02-15T10:00:00Z",
#         "updated_at": "2026-02-15T10:00:00Z"
#       },
#       {
#         "id": "770e8400-e29b-41d4-a716-446655440002",
#         "trip_id": "550e8400-e29b-41d4-a716-446655440000",
#         "kind": "hotel",
#         "provider": "Park Hyatt Tokyo",
#         "traveler_names": ["Ian Rogers"],
#         "start_ts": null,
#         "end_ts": null,
#         "start_date": "2026-04-01",
#         "end_date": "2026-04-07",
#         "start_location": "Tokyo, Japan",
#         "end_location": null,
#         "summary": "Park Hyatt Tokyo — 6 nights",
#         "details_json": {
#           "confirmation": "HYA987654",
#           "room_type": "Deluxe King",
#           "check_in": "2026-04-01",
#           "check_out": "2026-04-07"
#         },
#         "status": "confirmed",
#         "confidence": 0.97,
#         "needs_review": false,
#         "created_at": "2026-02-15T10:30:00Z",
#         "updated_at": "2026-02-15T10:30:00Z"
#       }
#     ]
#   },
#   "meta": { "item_count": 2 }
# }
