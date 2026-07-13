#!/usr/bin/env bash
# resy-check.sh — Query Resy availability for a single venue
# Usage: ./resy-check.sh <venue_id> <date> <party_size>
# Output: JSON with venue info and available slots
#
# Auto-authenticates via resy-auth.sh if RESY_AUTH_TOKEN is not already set.
# On HTTP 419 (token expired), forces a re-auth and retries once.

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPTS_DIR")"
DATA_DIR="$HOME/.openclaw/data/resy-hunter"

if [[ $# -lt 3 ]]; then
  echo '{"error": "Usage: resy-check.sh <venue_id> <date> <party_size>"}' >&2
  exit 1
fi

VENUE_ID="$1"
DATE="$2"
PARTY_SIZE="$3"

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

_resy_find() {
  local auth_header='Authorization: ResyAPI api_key="'"${RESY_API_KEY}"'"'
  local payload='{"lat":0,"long":0,"day":"'"${DATE}"'","party_size":'"${PARTY_SIZE}"',"venue_id":'"${VENUE_ID}"'}'
  curl -s -w "\n%{http_code}" -X POST "https://api.resy.com/4/find" \
    -H "${auth_header}" \
    -H "x-resy-auth-token: ${RESY_AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "${payload}"
}

response=$(_resy_find)
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

# On 419 (token expired), force re-auth and retry once
if [[ "$http_code" == "419" ]]; then
  rm -f "${DATA_DIR}/.resy-token"
  RESY_AUTH_TOKEN=$(bash "${SCRIPTS_DIR}/resy-auth.sh" --force 2>&1) || {
    echo "$RESY_AUTH_TOKEN" >&2
    exit 1
  }
  response=$(_resy_find)
  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | sed '$d')
fi

if [[ "$http_code" != "200" ]]; then
  echo "{\"error\": \"Resy API returned HTTP ${http_code}\", \"body\": $(echo "$body" | jq -Rs .)}" >&2
  exit 1
fi

echo "$body" | jq --arg date "$DATE" --argjson party_size "$PARTY_SIZE" '
def to12h:
  split(":") | (.[0] | tonumber) as $h | .[1] as $m |
  if $h == 0 then "12:\($m) AM"
  elif $h < 12 then "\($h):\($m) AM"
  elif $h == 12 then "12:\($m) PM"
  else "\($h - 12):\($m) PM"
  end;
def get_24h:
  split(" ") | last | split("T") | last | split(":") | .[0:2] | join(":");
def fmt_time:
  get_24h | to12h;
{
  platform: "resy",
  venue_id: (.results.venues[0].venue.id.resy // null),
  venue_name: (.results.venues[0].venue.name // "unknown"),
  venue_slug: (.results.venues[0].venue.slug // .results.venues[0].venue.url_slug // null),
  venue_city: (.results.venues[0].venue.location.city // null),
  venue_region: (.results.venues[0].venue.location.region // null),
  date: $date,
  party_size: $party_size,
  slots: [
    (.results.venues[0].slots // [])[] | {
      time_start: (.date.start | fmt_time),
      time_end: (.date.end | fmt_time),
      time_24h: (.date.start | get_24h),
      type: .config.type,
      config_token: .config.token,
      deposit_fee: (.payment.deposit_fee // null)
    }
  ]
}'
