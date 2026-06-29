#!/bin/bash
# pin-to-solvr.sh - Pin file to IPFS via Solvr API
# Usage: ./pin-to-solvr.sh <file_path> [name]
#
# Uses curl to call Solvr's /v1/add endpoint directly.
# Reads SOLVR_API_KEY from ~/.amcp/config.json ONLY (no env fallback).
#
# SECURITY: Agent must use its own Solvr key, never inherit from environment.
#           This prevents accidental use of human's API key.
#
# Updated 2026-02-19: No env fallback for security

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"

# ============================================================
# Parse arguments
# ============================================================
DRY_RUN=false
FILE_PATH=""
PIN_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help)
      cat <<EOF
pin-to-solvr.sh — Pin file to IPFS via Solvr API

Usage: $(basename "$0") <file_path> [name] [--dry-run]

Arguments:
  file_path   Path to file to pin (required)
  name        Display name for the pin (optional, defaults to filename)

Options:
  --dry-run   Show what would be pinned without actually pinning
  -h, --help  Show this help

Config (~/.amcp/config.json):
  storage.solvr.apiKey   Agent's Solvr API key (required)

Environment:
  SOLVR_API_URL   API base URL (default: https://api.solvr.dev/v1)

NOTE: This script only uses keys from config, NOT from environment.
      Agent must have its own Solvr API key configured.
EOF
      exit 0
      ;;
    *)
      if [ -z "$FILE_PATH" ]; then
        FILE_PATH="$1"
      elif [ -z "$PIN_NAME" ]; then
        PIN_NAME="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "$FILE_PATH" ]; then
  echo "ERROR: file_path is required" >&2
  echo "Usage: $(basename "$0") <file_path> [name] [--dry-run]" >&2
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "ERROR: File not found: $FILE_PATH" >&2
  exit 1
fi

# Default pin name to filename
if [ -z "$PIN_NAME" ]; then
  PIN_NAME="$(basename "$FILE_PATH")"
fi

# ============================================================
# Resolve SOLVR_API_KEY from config.json ONLY (no env fallback)
# SECURITY: Agent must use its own key, never inherit from env.
# ============================================================
SOLVR_API_KEY=""
if [ -f "$CONFIG_FILE" ]; then
  SOLVR_API_KEY=$(python3 -c "
import json, os
p = os.path.expanduser('$CONFIG_FILE')
d = json.load(open(p))
# Try multiple config locations
key = (d.get('storage',{}).get('solvr',{}).get('apiKey') or
       d.get('solvr',{}).get('apiKey') or
       d.get('pinning',{}).get('solvr',{}).get('apiKey') or '')
print(key)
" 2>/dev/null || echo '')
fi

if [ -z "${SOLVR_API_KEY:-}" ]; then
  echo "ERROR: No Solvr API key in ~/.amcp/config.json" >&2
  echo "Agent must have its own Solvr API key configured." >&2
  echo "Set via: proactive-amcp config set storage.solvr.apiKey <key>" >&2
  exit 1
fi

# ============================================================
# Pin file via API
# ============================================================
if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN: Would pin '$FILE_PATH' as '$PIN_NAME' via Solvr API"
  echo "  File size: $(du -sh "$FILE_PATH" | cut -f1)"
  echo "  API URL: $SOLVR_API_URL/add"
  echo "  API key: ${SOLVR_API_KEY:0:12}..."
  exit 0
fi

echo "Pinning to Solvr: $FILE_PATH..." >&2

# Call Solvr API /v1/add endpoint
RESULT=$(curl -s -X POST "${SOLVR_API_URL}/add" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -F "file=@$FILE_PATH" \
  --max-time 120) || {
  echo "ERROR: Solvr API request failed" >&2
  exit 1
}

# Check for error response
if echo "$RESULT" | grep -q '"error"'; then
  ERROR_MSG=$(echo "$RESULT" | python3 -c "import sys,json; e=json.load(sys.stdin).get('error',{}); print(e.get('message',e))" 2>/dev/null || echo "$RESULT")
  echo "ERROR: Solvr API error: $ERROR_MSG" >&2
  exit 1
fi

# Extract CID from response
CID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cid',''))" 2>/dev/null || echo '')

if [ -z "$CID" ]; then
  # Try regex fallback
  CID=$(echo "$RESULT" | grep -oE '(Qm[a-zA-Z0-9]{44}|baf[a-z2-7]{55,})' | head -1)
fi

if [ -n "$CID" ]; then
  echo "$CID"
  exit 0
else
  echo "ERROR: Could not extract CID from response: $RESULT" >&2
  exit 1
fi
