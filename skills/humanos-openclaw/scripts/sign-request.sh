#!/usr/bin/env bash
set -euo pipefail

via_curl() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  local base_url="${VIA_API_URL:-https://api.humanos.id}"
  
  # Timestamp em ms
  local timestamp
  timestamp="$(( $(date +%s) * 1000 ))"
  
  # Payload: timestamp.body (com ponto)
  local sign_payload
  if [[ -n "$body" ]]; then
    sign_payload="${timestamp}.${body}"
  else
    sign_payload="${timestamp}"
  fi
  
  # Assinar
  local signature
  signature=$(printf '%s' "$sign_payload" | openssl dgst -sha256 -hmac "$VIA_SIGNATURE_SECRET" | awk '{print $NF}')
  
  # Enviar request
  if [[ -n "$body" ]]; then
    curl -s -X "$method" \
      "${base_url}${path}" \
      -H "Authorization: Bearer ${VIA_API_KEY}" \
      -H "X-Timestamp: ${timestamp}" \
      -H "X-Signature: ${signature}" \
      -H "Content-Type: application/json" \
      -d "$body" | jq .
  else
    curl -s -X "$method" \
      "${base_url}${path}" \
      -H "Authorization: Bearer ${VIA_API_KEY}" \
      -H "X-Timestamp: ${timestamp}" \
      -H "X-Signature: ${signature}" \
      -H "Accept: application/json" | jq .
  fi
}
