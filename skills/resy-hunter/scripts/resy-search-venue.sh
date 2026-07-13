#!/usr/bin/env bash
# resy-search-venue.sh — Search Resy for a venue by name
# Usage: ./resy-search-venue.sh <query> [lat] [long]
# Output: JSON array of matching venues with venue_id, name, slug, location
#
# Auto-authenticates via resy-auth.sh if RESY_AUTH_TOKEN is not already set.

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ $# -lt 1 ]]; then
  echo '{"error": "Usage: resy-search-venue.sh <query> [lat] [long]"}' >&2
  exit 1
fi

QUERY="$1"
LAT="${2:-40.7128}"
LONG="${3:--74.0060}"

if [[ -z "${RESY_API_KEY:-}" ]]; then
  echo '{"error": "RESY_API_KEY is not set"}' >&2
  exit 1
fi

# Auto-authenticate if no token is set
if [[ -z "${RESY_AUTH_TOKEN:-}" ]]; then
  RESY_AUTH_TOKEN=$(bash "${SCRIPTS_DIR}/resy-auth.sh" 2>&1) || {
    echo "$RESY_AUTH_TOKEN" >&2
    exit 1
  }
fi

auth_header='Authorization: ResyAPI api_key="'"${RESY_API_KEY}"'"'
response=$(curl -s -w "\n%{http_code}" -G "https://api.resy.com/3/venuesearch/search" \
  --data-urlencode "query=${QUERY}" \
  --data-urlencode "geo.lat=${LAT}" \
  --data-urlencode "geo.long=${LONG}" \
  --data-urlencode "per_page=10" \
  --data-urlencode "types=venue" \
  -H "${auth_header}")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" != "200" ]]; then
  # Fallback: try the /4/find endpoint with location search
  future_date=$(date -v+7d +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d -d '+7 days')
  fallback_payload='{"lat":'"${LAT}"',"long":'"${LONG}"',"day":"'"${future_date}"'","party_size":2}'
  response2=$(curl -s -w "\n%{http_code}" -X POST "https://api.resy.com/4/find" \
    -H "${auth_header}" \
    -H "Content-Type: application/json" \
    -d "${fallback_payload}")

  http_code2=$(echo "$response2" | tail -1)
  body2=$(echo "$response2" | sed '$d')

  if [[ "$http_code2" != "200" ]]; then
    echo "{\"error\": \"Venue search failed (HTTP ${http_code}). Try finding the venue_id from the restaurant's Resy URL.\"}" >&2
    exit 1
  fi

  echo "$body2" | jq --arg query "$QUERY" '[
    .results.venues[]
    | select(.venue.name | ascii_downcase | contains($query | ascii_downcase))
    | {
        venue_id: .venue.id.resy,
        name: .venue.name,
        slug: .venue.slug,
        city: .venue.location.city,
        neighborhood: .venue.location.neighborhood
      }
  ]'
  exit 0
fi

echo "$body" | jq '[
  .search.hits[]
  | {
      venue_id: .id.resy,
      name: .name,
      slug: .url_slug,
      city: (.location.city // null),
      neighborhood: (.location.neighborhood // null)
    }
]'
