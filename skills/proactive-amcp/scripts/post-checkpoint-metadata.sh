#!/bin/bash
# post-checkpoint-metadata.sh - POST checkpoint metadata to Solvr
# Usage: ./post-checkpoint-metadata.sh --cid <CID> --timestamp <ISO> --size <SIZE> [options]
#
# Posts checkpoint metadata to Solvr so other agents can discover checkpoints.
# Graceful: failures are logged but never block the checkpoint flow.
#
# Called by checkpoint.sh and full-checkpoint.sh after successful IPFS pinning.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"

# ============================================================
# Parse arguments
# ============================================================
CID=""
TIMESTAMP=""
SIZE=""
PREVIOUS_CID=""
CHECKPOINT_TYPE="quick"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cid) CID="$2"; shift 2 ;;
    --timestamp) TIMESTAMP="$2"; shift 2 ;;
    --size) SIZE="$2"; shift 2 ;;
    --previous-cid) PREVIOUS_CID="$2"; shift 2 ;;
    --type) CHECKPOINT_TYPE="$2"; shift 2 ;;
    -h|--help)
      cat <<EOF
post-checkpoint-metadata.sh — POST checkpoint metadata to Solvr

Usage: $(basename "$0") --cid <CID> --timestamp <ISO> --size <SIZE> [options]

Required:
  --cid <CID>             IPFS content identifier
  --timestamp <ISO>       Checkpoint timestamp (ISO-8601)
  --size <SIZE>           Checkpoint file size (e.g. "4.2M")

Optional:
  --previous-cid <CID>   Previous checkpoint CID (chain link)
  --type <TYPE>           Checkpoint type: quick or full (default: quick)
  -h, --help              Show this help

Config (~/.amcp/config.json):
  solvr.apiKey            Solvr API key (required)

Environment:
  SOLVR_API_URL           API base URL (default: https://api.solvr.dev/v1)
  IDENTITY_PATH           Path to identity.json (default: ~/.amcp/identity.json)
EOF
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [ -z "$CID" ]; then
  echo "ERROR: --cid is required" >&2
  exit 1
fi

if [ -z "$TIMESTAMP" ]; then
  TIMESTAMP=$(date -Iseconds)
fi

# ============================================================
# Resolve Solvr API key from config (no env fallback for security)
# ============================================================
SOLVR_API_KEY=""
if [ -f "$CONFIG_FILE" ]; then
  SOLVR_API_KEY=$(python3 -c "
import json, sys
try:
    d = json.load(open('$CONFIG_FILE'))
    key = (d.get('apiKeys',{}).get('solvr','') or
           d.get('solvr',{}).get('apiKey','') or
           d.get('pinning',{}).get('solvr',{}).get('apiKey',''))
    if key: print(key)
except Exception:
    pass
" 2>/dev/null || echo "")
fi

if [ -z "$SOLVR_API_KEY" ]; then
  echo "SKIP: No Solvr API key — checkpoint metadata not posted" >&2
  exit 0
fi

# ============================================================
# Extract AID from identity.json
# ============================================================
AGENT_AID=""
if [ -f "$IDENTITY_PATH" ]; then
  AGENT_AID=$(python3 -c "
import json
with open('$IDENTITY_PATH') as f:
    d = json.load(f)
print(d.get('aid', ''))
" 2>/dev/null || echo "")
fi

# ============================================================
# POST metadata to Solvr
# ============================================================
PAYLOAD=$(python3 -c "
import json
data = {
    'type': 'idea',
    'title': 'AMCP checkpoint: $CID',
    'description': 'Checkpoint metadata for agent discovery',
    'tags': ['amcp', 'checkpoint', '$CHECKPOINT_TYPE'],
    'metadata': {
        'cid': '$CID',
        'timestamp': '$TIMESTAMP',
        'size': '$SIZE',
        'checkpoint_type': '$CHECKPOINT_TYPE',
        'agent_id': '$AGENT_AID',
        'previous_cid': '$PREVIOUS_CID'
    }
}
# Remove empty values from metadata
data['metadata'] = {k: v for k, v in data['metadata'].items() if v}
print(json.dumps(data))
" 2>/dev/null)

if [ -z "$PAYLOAD" ]; then
  echo "WARN: Failed to build metadata payload" >&2
  exit 0
fi

RESULT=$(curl -s --max-time 15 -X POST "${SOLVR_API_URL}/posts" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" 2>/dev/null || echo '{}')

# Check for success
POST_ID=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id', d.get('data',{}).get('id','')))" 2>/dev/null || echo "")

if [ -n "$POST_ID" ] && [ "$POST_ID" != "null" ]; then
  echo "Solvr: checkpoint metadata posted (id: $POST_ID)"
else
  # Log but don't fail — metadata posting is best-effort
  ERROR_MSG=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','') if isinstance(d.get('error'),dict) else d.get('error','unknown'))" 2>/dev/null || echo "unknown")
  echo "WARN: Solvr metadata post failed: $ERROR_MSG" >&2
fi
