#!/bin/bash
# register-checkpoint-solvr.sh - Register checkpoint via Solvr unified API
# Usage: ./register-checkpoint-solvr.sh --cid <CID> --checkpoint-path <PATH> --name <NAME> [options]
#
# Uses POST /v1/agents/me/checkpoints (unified API) instead of separate pin + metadata calls.
# Reads death_count from amcp-stats.json, computes memory_hash from checkpoint file.
# Graceful: failures are logged but never block the checkpoint flow.
#
# Called by checkpoint.sh and full-checkpoint.sh after successful IPFS pinning.

set -euo pipefail

CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"
CONTENT_DIR="${CONTENT_DIR:-$HOME/.openclaw/workspace}"

# ============================================================
# Parse arguments
# ============================================================
CID=""
CHECKPOINT_PATH=""
CHECKPOINT_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cid) CID="$2"; shift 2 ;;
    --checkpoint-path) CHECKPOINT_PATH="$2"; shift 2 ;;
    --name) CHECKPOINT_NAME="$2"; shift 2 ;;
    --content-dir) CONTENT_DIR="$2"; shift 2 ;;
    -h|--help)
      cat <<EOF
register-checkpoint-solvr.sh — Register checkpoint via Solvr unified API

Usage: $(basename "$0") --cid <CID> --checkpoint-path <PATH> --name <NAME> [options]

Required:
  --cid <CID>                IPFS content identifier
  --checkpoint-path <PATH>   Path to checkpoint file (for memory_hash)
  --name <NAME>              Checkpoint name (e.g. amcp-full-AgentName-timestamp)

Optional:
  --content-dir <DIR>        Content directory for amcp-stats.json (default: ~/.openclaw/workspace)
  -h, --help                 Show this help

Config (~/.amcp/config.json):
  solvr.apiKey               Solvr API key (required)

Environment:
  SOLVR_API_URL              API base URL (default: https://api.solvr.dev/v1)
  CONTENT_DIR                Content directory (default: ~/.openclaw/workspace)
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

if [ -z "$CHECKPOINT_NAME" ]; then
  CHECKPOINT_NAME="amcp-checkpoint-$(date +%Y%m%d-%H%M%S)"
fi

# ============================================================
# Resolve Solvr API key from config
# ============================================================
SOLVR_API_KEY=""
if [ -f "$CONFIG_FILE" ]; then
  SOLVR_API_KEY=$(python3 -c "
import json
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
  echo "SKIP: No Solvr API key — checkpoint not registered with Solvr" >&2
  exit 0
fi

# ============================================================
# Read death_count from amcp-stats.json (best-effort)
# ============================================================
DEATH_COUNT=0
STATS_PATH="$CONTENT_DIR/memory/amcp-stats.json"
if [ -f "$STATS_PATH" ]; then
  DEATH_COUNT=$(python3 -c "
import json
try:
    d = json.load(open('$STATS_PATH'))
    print(d.get('totalDeaths', 0))
except Exception:
    print(0)
" 2>/dev/null || echo "0")
fi

# ============================================================
# Compute memory_hash from sha256 of checkpoint file
# ============================================================
MEMORY_HASH=""
if [ -n "$CHECKPOINT_PATH" ] && [ -f "$CHECKPOINT_PATH" ]; then
  MEMORY_HASH=$(sha256sum "$CHECKPOINT_PATH" | cut -d' ' -f1)
fi

# ============================================================
# POST to Solvr unified checkpoint API
# ============================================================
PAYLOAD=$(python3 -c "
import json
data = {
    'cid': '$CID',
    'metadata': {
        'name': '$CHECKPOINT_NAME',
        'death_count': int('$DEATH_COUNT'),
        'memory_hash': '$MEMORY_HASH'
    }
}
# Remove empty values from metadata
data['metadata'] = {k: v for k, v in data['metadata'].items() if v or v == 0}
print(json.dumps(data))
" 2>/dev/null)

if [ -z "$PAYLOAD" ]; then
  echo "WARN: Failed to build Solvr checkpoint payload" >&2
  exit 0
fi

RESULT=$(curl -s --max-time 15 -X POST "${SOLVR_API_URL}/agents/me/checkpoints" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" 2>/dev/null || echo '{}')

# Check for success
CP_ID=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")

if [ -n "$CP_ID" ] && [ "$CP_ID" != "null" ]; then
  echo "Solvr: checkpoint registered (id: $CP_ID)"
else
  ERROR_MSG=$(echo "$RESULT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    e = d.get('error', {})
    print(e.get('message','') if isinstance(e,dict) else str(e))
except: print('unknown')
" 2>/dev/null || echo "unknown")
  echo "WARN: Solvr checkpoint registration failed: $ERROR_MSG" >&2
fi
