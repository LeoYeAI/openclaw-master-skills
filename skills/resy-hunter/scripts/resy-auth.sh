#!/usr/bin/env bash
# resy-auth.sh — Authenticate with Resy and return a fresh auth token
# Usage: ./resy-auth.sh [--force]
# Output: auth token string (stdout)
#
# Caches the token to ~/.openclaw/data/resy-hunter/.resy-token
# Returns cached token if less than 12 hours old (unless --force)
#
# Requires: RESY_API_KEY, RESY_EMAIL, RESY_PASSWORD

set -euo pipefail

SKILL_DIR="$HOME/.openclaw/skills/resy-hunter"
DATA_DIR="$HOME/.openclaw/data/resy-hunter"
mkdir -p "$DATA_DIR"

# Migrate old token file if it exists
if [[ -f "${SKILL_DIR}/.resy-token" && ! -f "${DATA_DIR}/.resy-token" ]]; then
  cp "${SKILL_DIR}/.resy-token" "${DATA_DIR}/.resy-token"
fi

TOKEN_FILE="${DATA_DIR}/.resy-token"
MAX_AGE_SECONDS=43200  # 12 hours

FORCE=false
if [[ "${1:-}" == "--force" ]]; then
  FORCE=true
fi

if [[ -z "${RESY_API_KEY:-}" ]]; then
  echo '{"error": "RESY_API_KEY is not set"}' >&2
  exit 1
fi

if [[ -z "${RESY_EMAIL:-}" ]]; then
  echo '{"error": "RESY_EMAIL is not set"}' >&2
  exit 1
fi

if [[ -z "${RESY_PASSWORD:-}" ]]; then
  echo '{"error": "RESY_PASSWORD is not set"}' >&2
  exit 1
fi

# Check for cached token
if [[ "$FORCE" == "false" && -f "$TOKEN_FILE" ]]; then
  cached_token=$(jq -r '.token // empty' "$TOKEN_FILE" 2>/dev/null || true)
  cached_at=$(jq -r '.cached_at // 0' "$TOKEN_FILE" 2>/dev/null || echo "0")
  now=$(date +%s)

  if [[ -n "$cached_token" && "$cached_at" != "0" ]]; then
    age=$(( now - cached_at ))
    if [[ $age -lt $MAX_AGE_SECONDS ]]; then
      echo "$cached_token"
      exit 0
    fi
  fi
fi

# Authenticate with Resy
auth_header='Authorization: ResyAPI api_key="'"${RESY_API_KEY}"'"'
response=$(curl -s -w "\n%{http_code}" -X POST "https://api.resy.com/3/auth/password" \
  -H "${auth_header}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "email=${RESY_EMAIL}" \
  --data-urlencode "password=${RESY_PASSWORD}")

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" == "401" || "$http_code" == "403" ]]; then
  echo '{"error": "Resy login failed (HTTP '"$http_code"'). Check RESY_EMAIL and RESY_PASSWORD."}' >&2
  exit 1
fi

if [[ "$http_code" != "200" ]]; then
  echo "{\"error\": \"Resy auth returned HTTP ${http_code}\", \"body\": $(echo "$body" | jq -Rs .)}" >&2
  exit 1
fi

# Extract the token
token=$(echo "$body" | jq -r '.token // empty')

if [[ -z "$token" ]]; then
  echo '{"error": "No token in Resy auth response", "body": '"$body"'}' >&2
  exit 1
fi

# Cache the token
now=$(date +%s)
jq -n --arg token "$token" --argjson cached_at "$now" \
  '{token: $token, cached_at: $cached_at}' > "$TOKEN_FILE"

echo "$token"
