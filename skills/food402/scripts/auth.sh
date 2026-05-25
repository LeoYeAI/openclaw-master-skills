#!/usr/bin/env bash
# scripts/auth.sh - TGO Yemek Authentication Helper
# Usage: {baseDir}/scripts/auth.sh <command>
# Commands: get-token, login, check-token, clear-token

set -euo pipefail

USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
TOKEN_FILE="/tmp/food402-token"
EXPIRY_FILE="/tmp/food402-token-expiry"

# Check required environment variables
check_credentials() {
  if [ -z "${TGO_EMAIL:-}" ] || [ -z "${TGO_PASSWORD:-}" ]; then
    echo '{"error": "TGO_EMAIL and TGO_PASSWORD environment variables are required"}' >&2
    exit 1
  fi
}

# Decode JWT payload to extract expiry
decode_jwt_expiry() {
  local token="$1"
  # Extract payload (second part), base64 decode, parse exp field
  local payload
  payload=$(echo "$token" | cut -d. -f2)
  # Add padding if needed
  local padding=$((4 - ${#payload} % 4))
  if [ $padding -ne 4 ]; then
    payload="${payload}$(printf '%*s' $padding | tr ' ' '=')"
  fi
  # Decode and extract exp (multiply by 1000 for milliseconds)
  echo "$payload" | base64 -d 2>/dev/null | sed -n 's/.*"exp":\([0-9]*\).*/\1/p' | awk '{print $1 * 1000}'
}

# Perform fresh login
do_login() {
  check_credentials

  # Step 1: Get CSRF token
  local csrf_response
  csrf_response=$(curl -s -c - "https://tgoyemek.com/api/auth/csrf" \
    -H "User-Agent: $USER_AGENT" 2>/dev/null)

  local csrf_token
  csrf_token=$(echo "$csrf_response" | grep -o 'tgo-csrf-token[[:space:]]*[^[:space:]]*' | awk '{print $2}' | head -1)

  if [ -z "$csrf_token" ]; then
    echo '{"error": "Failed to get CSRF token"}' >&2
    exit 1
  fi

  # Step 2: Login with credentials
  local login_response
  login_response=$(curl -s -c - -X POST "https://tgoyemek.com/api/auth/login" \
    -H "Content-Type: text/plain;charset=UTF-8" \
    -H "Cookie: tgo-csrf-token=$csrf_token" \
    -H "User-Agent: $USER_AGENT" \
    -d "{\"username\":\"$TGO_EMAIL\",\"password\":\"$TGO_PASSWORD\",\"csrfToken\":\"$csrf_token\"}" 2>/dev/null)

  # Step 3: Extract tgo-token from cookies
  local token
  token=$(echo "$login_response" | grep -o 'tgo-token[[:space:]]*[^[:space:]]*' | awk '{print $2}' | head -1)

  if [ -z "$token" ]; then
    echo '{"error": "Login failed - no token received. Check credentials."}' >&2
    exit 1
  fi

  # Cache token and expiry
  echo "$token" > "$TOKEN_FILE"
  local expiry
  expiry=$(decode_jwt_expiry "$token")
  echo "$expiry" > "$EXPIRY_FILE"

  echo "$token"
}

# Check if cached token is still valid (with 60s buffer)
is_token_valid() {
  if [ ! -f "$TOKEN_FILE" ] || [ ! -f "$EXPIRY_FILE" ]; then
    return 1
  fi

  local expiry
  expiry=$(cat "$EXPIRY_FILE" 2>/dev/null || echo "0")
  local now
  now=$(date +%s)
  now=$((now * 1000))

  # Check if token expires within 60 seconds
  local buffer=60000
  if [ "$now" -lt "$((expiry - buffer))" ]; then
    return 0
  fi
  return 1
}

# Get token (cached or fresh)
get_token() {
  if is_token_valid; then
    cat "$TOKEN_FILE"
  else
    do_login
  fi
}

# Clear cached token
clear_token() {
  rm -f "$TOKEN_FILE" "$EXPIRY_FILE"
  echo '{"success": true, "message": "Token cache cleared"}'
}

# Check token status
check_token() {
  if [ ! -f "$TOKEN_FILE" ]; then
    echo '{"valid": false, "reason": "No cached token"}'
    return
  fi

  if is_token_valid; then
    local expiry
    expiry=$(cat "$EXPIRY_FILE")
    local now
    now=$(date +%s)
    now=$((now * 1000))
    local remaining=$((($expiry - $now) / 1000))
    echo "{\"valid\": true, \"expiresIn\": ${remaining}}"
  else
    echo '{"valid": false, "reason": "Token expired"}'
  fi
}

# Main command dispatcher
case "${1:-}" in
  get-token)
    get_token
    ;;
  login)
    do_login
    ;;
  check-token)
    check_token
    ;;
  clear-token)
    clear_token
    ;;
  *)
    echo "Usage: $0 {get-token|login|check-token|clear-token}" >&2
    exit 1
    ;;
esac
