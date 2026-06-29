#!/bin/bash
# list-checkpoints.sh - List all agent checkpoints from Solvr
# Usage: ./list-checkpoints.sh [--json]
#
# Calls GET /v1/agents/me/checkpoints to retrieve checkpoint history.
# Displays CID, name, date, status, death_count for each checkpoint.
# Latest checkpoint highlighted at top.

set -euo pipefail

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }
command -v curl &>/dev/null || { echo "FATAL: curl required but not found" >&2; exit 2; }

CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"

JSON_OUTPUT=false

usage() {
  cat <<EOF
proactive-amcp checkpoints — List all agent checkpoints from Solvr

Usage: $(basename "$0") [options]

Options:
  --json       Output raw JSON (machine-readable)
  -h, --help   Show this help

Config (~/.amcp/config.json):
  solvr.apiKey   Solvr API key (required)

Environment:
  SOLVR_API_URL  API base URL (default: https://api.solvr.dev/v1)
EOF
  exit 0
}

# ============================================================
# Parse arguments
# ============================================================
for arg in "$@"; do
  case "$arg" in
    --json) JSON_OUTPUT=true ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

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
  echo "ERROR: No Solvr API key configured" >&2
  echo "Run: proactive-amcp config set solvr.apiKey YOUR_KEY" >&2
  exit 1
fi

# ============================================================
# Fetch checkpoints from Solvr
# ============================================================
RESPONSE=$(curl -s --max-time 30 -X GET "${SOLVR_API_URL}/agents/me/checkpoints" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -H "Accept: application/json" 2>/dev/null || echo '{"error":"connection_failed"}')

# Check for errors
IS_ERROR=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if 'error' in d:
        e = d['error']
        msg = e.get('message','') if isinstance(e, dict) else str(e)
        print(msg or 'unknown error')
    else:
        print('')
except Exception as ex:
    print(str(ex))
" 2>/dev/null || echo "parse error")

if [ -n "$IS_ERROR" ]; then
  echo "ERROR: Failed to fetch checkpoints from Solvr: $IS_ERROR" >&2
  exit 1
fi

# ============================================================
# Output: JSON mode
# ============================================================
if [ "$JSON_OUTPUT" = true ]; then
  echo "$RESPONSE" | python3 -c "import sys,json; json.dump(json.load(sys.stdin), sys.stdout, indent=2); print()"
  exit 0
fi

# ============================================================
# Output: Human-readable table
# ============================================================
python3 -c "
import sys, json
from datetime import datetime

try:
    data = json.loads('''$RESPONSE''')
except Exception:
    data = json.load(sys.stdin)

count = data.get('count', 0)
results = data.get('results', [])
latest = data.get('latest', None)

if count == 0:
    print('No checkpoints found.')
    print('')
    print('Create one with: proactive-amcp checkpoint')
    sys.exit(0)

print(f'Checkpoints: {count} total')
print('')

# Determine latest CID for highlighting
latest_cid = ''
if latest and isinstance(latest, dict):
    latest_cid = latest.get('cid', '')
elif results:
    latest_cid = results[0].get('cid', '')

# Header
print(f'  {\"#\":<4} {\"CID\":<20} {\"Name\":<35} {\"Date\":<20} {\"Deaths\":<7}')
print(f'  {\"-\"*4} {\"-\"*20} {\"-\"*35} {\"-\"*20} {\"-\"*7}')

for i, cp in enumerate(results):
    cid = cp.get('cid', 'N/A')
    name = cp.get('metadata', {}).get('name', '') or cp.get('name', 'unnamed')
    created = cp.get('created_at', '') or cp.get('created', '')
    deaths = cp.get('metadata', {}).get('death_count', '-')
    if deaths is None:
        deaths = '-'

    # Format date
    date_str = created
    if created:
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d %H:%M')
        except (ValueError, AttributeError):
            date_str = created[:19] if len(created) > 19 else created

    # Truncate long fields
    cid_short = (cid[:17] + '...') if len(str(cid)) > 20 else str(cid)
    name_short = (name[:32] + '...') if len(str(name)) > 35 else str(name)

    # Highlight latest
    marker = ' *' if str(cid) == str(latest_cid) else '  '
    print(f'{marker}{i+1:<4} {cid_short:<20} {name_short:<35} {date_str:<20} {str(deaths):<7}')

print('')
if latest_cid:
    print(f'  * = latest checkpoint')
print('')
" <<< "$RESPONSE"
