#!/bin/bash
# Search and select provider/model

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

PROVIDER_SEARCH="$1"
MODEL_SEARCH="${2:-}"

if [ -z "$PROVIDER_SEARCH" ]; then
  echo "Error: PROVIDER_SEARCH required" >&2
  echo "Usage: $0 <provider_name> [model_search]" >&2
  exit 1
fi

# Update cache first
bash "$SCRIPT_DIR/update_providers.sh" >/dev/null

# Find provider
PROVIDER_ID=$(jq -r --arg p "$PROVIDER_SEARCH" \
  '.providers[] | 
   select(
     (.id | ascii_downcase | contains($p | ascii_downcase)) or
     (.name | ascii_downcase | contains($p | ascii_downcase))
   ) | .id' "$SKILL_DIR/providers.json" | head -1)

if [ -z "$PROVIDER_ID" ]; then
  echo "Error: Provider '$PROVIDER_SEARCH' not found" >&2
  echo "Available:" >&2
  jq -r '.providers[] | "- \(.id) (\(.name))"' "$SKILL_DIR/providers.json" >&2
  exit 1
fi

# Find model
if [ -n "$MODEL_SEARCH" ]; then
  MODEL_ID=$(jq -r --arg p "$PROVIDER_ID" --arg m "$MODEL_SEARCH" \
    '.providers[] | select(.id==$p) | 
     .models[] | select(ascii_downcase | contains($m | ascii_downcase))' \
    "$SKILL_DIR/providers.json" | head -1)
else
  MODEL_ID=$(jq -r --arg p "$PROVIDER_ID" \
    '.providers[] | select(.id==$p) | .models[0]' \
    "$SKILL_DIR/providers.json")
fi

if [ -z "$MODEL_ID" ]; then
  echo "Error: Model not found for provider '$PROVIDER_ID'" >&2
  exit 1
fi

echo "$PROVIDER_ID $MODEL_ID"
exit 0