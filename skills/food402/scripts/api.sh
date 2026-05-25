#!/usr/bin/env bash
# scripts/api.sh - TGO Yemek API Wrapper
# Usage: {baseDir}/scripts/api.sh <method> <endpoint> [data]
# Methods: get, post, put, delete, payment-get, payment-post

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_BASE="https://api.tgoapis.com"
PAYMENT_API_BASE="https://payment.tgoapps.com"
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# Generate UUID
generate_uuid() {
  if command -v uuidgen &>/dev/null; then
    uuidgen | tr '[:upper:]' '[:lower:]'
  else
    # Fallback using /dev/urandom
    cat /proc/sys/kernel/random/uuid 2>/dev/null || \
    od -x /dev/urandom | head -1 | awk '{OFS="-"; print $2$3,$4,$5,$6,$7$8$9}'
  fi
}

# Get auth token
get_token() {
  "$SCRIPT_DIR/auth.sh" get-token
}

# Create main API headers
create_headers() {
  local token="$1"
  local content_type="${2:-}"

  local headers=(
    -H "Accept: application/json, text/plain, */*"
    -H "Authorization: Bearer $token"
    -H "User-Agent: $USER_AGENT"
    -H "Origin: https://tgoyemek.com"
    -H "x-correlationid: $(generate_uuid)"
    -H "pid: $(generate_uuid)"
    -H "sid: $(generate_uuid)"
  )

  if [ -n "$content_type" ]; then
    headers+=(-H "Content-Type: $content_type")
  fi

  printf '%s\n' "${headers[@]}"
}

# Create payment API headers
create_payment_headers() {
  local token="$1"

  cat <<EOF
-H
accept: */*
-H
accept-language: tr-TR
-H
Authorization: bearer $token
-H
Content-Type: application/json
-H
User-Agent: $USER_AGENT
-H
referer: https://payment.tgoapps.com/v3/tgo/card-fragment?application-id=1&storefront-id=1&culture=tr-TR
-H
app-name: TrendyolGo
-H
x-applicationid: 1
-H
x-channelid: 4
-H
x-storefrontid: 1
-H
x-features: OPTIONAL_REBATE;MEAL_CART_ENABLED;MEAL_CARD_TRENDYOL_PROMOTION;PICKUP_FEE_ENABLED;VAS_QUANTITY_ENABLED;
-H
x-supported-payment-options: MULTINET;SODEXO;EDENRED;ON_DELIVERY;SETCARD
-H
x-session-id:
-H
x-personalization-id:
EOF
}

# Make API request with retry on 401
api_request() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  local is_payment="${4:-false}"
  local retry_count=0
  local max_retries=1

  while [ $retry_count -le $max_retries ]; do
    local token
    token=$(get_token)

    local headers_array=()
    if [ "$is_payment" = "true" ]; then
      while IFS= read -r line; do
        headers_array+=("$line")
      done < <(create_payment_headers "$token")
    else
      while IFS= read -r line; do
        headers_array+=("$line")
      done < <(create_headers "$token" "application/json")
    fi

    local response
    local http_code

    if [ -n "$data" ]; then
      response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
        "${headers_array[@]}" \
        -d "$data" 2>/dev/null)
    else
      response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
        "${headers_array[@]}" 2>/dev/null)
    fi

    http_code=$(echo "$response" | tail -1)
    response=$(echo "$response" | sed '$d')

    # Handle 401 - re-authenticate and retry
    if [ "$http_code" = "401" ] && [ $retry_count -lt $max_retries ]; then
      "$SCRIPT_DIR/auth.sh" clear-token >/dev/null
      retry_count=$((retry_count + 1))
      continue
    fi

    # Return response with status info
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
      echo "$response"
    else
      echo "{\"error\": \"HTTP $http_code\", \"response\": $response}" >&2
      exit 1
    fi
    return
  done
}

# Main command dispatcher
case "${1:-}" in
  get)
    api_request "GET" "${API_BASE}${2}"
    ;;
  post)
    api_request "POST" "${API_BASE}${2}" "${3:-}"
    ;;
  put)
    api_request "PUT" "${API_BASE}${2}" "${3:-}"
    ;;
  delete)
    api_request "DELETE" "${API_BASE}${2}"
    ;;
  payment-get)
    api_request "GET" "${PAYMENT_API_BASE}${2}" "" "true"
    ;;
  payment-post)
    api_request "POST" "${PAYMENT_API_BASE}${2}" "${3:-}" "true"
    ;;
  *)
    echo "Usage: $0 {get|post|put|delete|payment-get|payment-post} <endpoint> [data]" >&2
    echo "Examples:" >&2
    echo "  $0 get /web-user-apimemberaddress-santral/addresses" >&2
    echo "  $0 post /web-checkout-apicheckout-santral/shipping '{\"shippingAddressId\":123}'" >&2
    exit 1
    ;;
esac
