#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${VECTCUT_BASE_URL:-https://open.vectcut.com/cut_jianying}"
LLM_BASE_URL="${VECTCUT_LLM_BASE_URL:-https://open.vectcut.com/llm}"
API_KEY="${VECTCUT_API_KEY:-}"

usage() {
  echo "Usage: $0 <generate_speech|fish_clone|voice_assets> '<json_payload>'"
  exit 1
}

fail() {
  local error="$1"
  local output="${2:-\"\"}"
  printf '{"success":false,"error":"%s","output":%s}\n' "$error" "$output"
  exit 0
}

[[ -z "$API_KEY" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1
[[ $# -lt 2 ]] && usage
ACTION="$1"
PAYLOAD="$2"

extract_json_string() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p"
}

extract_json_number() {
  local key="$1"
  printf '%s' "$PAYLOAD" | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([-0-9.][0-9.]*\).*/\1/p"
}

if [[ "$ACTION" == "generate_speech" ]]; then
  TEXT="$(extract_json_string text)"; PROVIDER="$(extract_json_string provider)"; VOICE_ID="$(extract_json_string voice_id)"; MODEL="$(extract_json_string model)"
  [[ -z "$TEXT" || -z "$PROVIDER" || -z "$VOICE_ID" ]] && fail "text/provider/voice_id is required"
  [[ ! "$PROVIDER" =~ ^(azure|volc|minimax|fish)$ ]] && fail "provider must be one of: azure, volc, minimax, fish"
  [[ "$PROVIDER" == "minimax" && -z "$MODEL" ]] && fail "model is required when provider=minimax"
  [[ "$PROVIDER" == "minimax" && ! "$MODEL" =~ ^(speech-2.6-turbo|speech-2.6-hd)$ ]] && fail "model for minimax must be one of: speech-2.6-turbo, speech-2.6-hd"
  VOLUME="$(extract_json_number volume)"; TARGET_START="$(extract_json_number target_start)"
  [[ -n "$VOLUME" && ! "$VOLUME" =~ ^-?[0-9]+(\.[0-9]+)?$ ]] && fail "volume must be a number"
  [[ -n "$TARGET_START" && ! "$TARGET_START" =~ ^-?[0-9]+(\.[0-9]+)?$ ]] && fail "target_start must be a number"
  curl --silent --show-error --location --request POST "${BASE_URL}/generate_speech" --header "Authorization: Bearer ${API_KEY}" --header "Content-Type: application/json" --data-raw "$PAYLOAD"
  echo
  exit 0
fi

if [[ "$ACTION" == "fish_clone" ]]; then
  FILE_URL="$(extract_json_string file_url)"
  [[ -z "$FILE_URL" ]] && fail "file_url is required"
  [[ ! "$FILE_URL" =~ ^https?:// ]] && fail "file_url must start with http:// or https://"
  curl --silent --show-error --location --request POST "${LLM_BASE_URL}/tts/fish/clone_voice" --header "Authorization: Bearer ${API_KEY}" --header "Content-Type: application/json" --data-raw "$PAYLOAD"
  echo
  exit 0
fi

if [[ "$ACTION" == "voice_assets" ]]; then
  LIMIT="$(extract_json_number limit)"; OFFSET="$(extract_json_number offset)"; PROVIDER="$(extract_json_string provider)"
  [[ -n "$LIMIT" && ! "$LIMIT" =~ ^[0-9]+$ ]] && fail "limit must be an integer"
  [[ -n "$OFFSET" && ! "$OFFSET" =~ ^[0-9]+$ ]] && fail "offset must be an integer"
  [[ -n "$PROVIDER" && ! "$PROVIDER" =~ ^(fish|minimax)$ ]] && fail "provider must be one of: fish, minimax"
  URL="${LLM_BASE_URL}/tts/voice_assets"; SEP="?"
  [[ -n "$LIMIT" ]] && URL+="${SEP}limit=${LIMIT}" && SEP="&"
  [[ -n "$OFFSET" ]] && URL+="${SEP}offset=${OFFSET}" && SEP="&"
  [[ -n "$PROVIDER" ]] && URL+="${SEP}provider=${PROVIDER}"
  curl --silent --show-error --location --request GET "$URL" --header "Authorization: Bearer ${API_KEY}"
  echo
  exit 0
fi

usage