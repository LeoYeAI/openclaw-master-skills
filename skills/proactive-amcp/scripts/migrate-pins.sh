#!/bin/bash
# migrate-pins.sh - Transfer historical checkpoints from Pinata to Solvr
# Usage: ./migrate-pins.sh [--unpin-pinata] [--dry-run]
#
# Reads all CIDs from ~/.amcp/checkpoints/*.json and last-checkpoint.json,
# checks if each is pinned on Solvr, pins if not, tracks progress.

set -euo pipefail

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }
command -v curl &>/dev/null || { echo "FATAL: curl required but not found" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-$HOME/.amcp/checkpoints}"
LAST_CHECKPOINT_FILE="${LAST_CHECKPOINT_FILE:-$HOME/.amcp/last-checkpoint.json}"
MIGRATION_STATUS_FILE="${MIGRATION_STATUS_FILE:-$HOME/.amcp/migration-status.json}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"
SOLVR_GATEWAY="${SOLVR_GATEWAY:-https://ipfs.solvr.dev/ipfs}"

# ============================================================
# Parse arguments
# ============================================================
DRY_RUN=false
UNPIN_PINATA=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --unpin-pinata) UNPIN_PINATA=true; shift ;;
    -h|--help)
      cat <<EOF
migrate-pins — Transfer historical checkpoints from Pinata to Solvr

Usage: $(basename "$0") [--unpin-pinata] [--dry-run]

Options:
  --unpin-pinata  Remove from Pinata after Solvr pin confirmed
  --dry-run       Show what would be migrated without making changes
  -h, --help      Show this help

Reads CIDs from:
  $CHECKPOINT_DIR/*.json
  $LAST_CHECKPOINT_FILE

Tracks progress in:
  $MIGRATION_STATUS_FILE

Environment:
  SOLVR_API_KEY     Solvr API key (or set via config)
  SOLVR_API_URL     API base URL (default: https://api.solvr.dev/v1)
  PINATA_JWT        Pinata JWT (required for --unpin-pinata)
EOF
      exit 0
      ;;
    *)
      echo "ERROR: Unknown option '$1'" >&2
      exit 1
      ;;
  esac
done

# ============================================================
# Resolve API keys from config.json ONLY (no env fallback)
# SECURITY: Agent must use its own keys, never inherit from env.
# ============================================================
resolve_api_keys() {
  # Solvr API key (config only, no env)
  SOLVR_API_KEY=""
  if [ -f "$CONFIG_FILE" ]; then
    SOLVR_API_KEY=$(python3 -c "
import json, os
p = os.path.expanduser('$CONFIG_FILE')
d = json.load(open(p))
key = (d.get('storage',{}).get('solvr',{}).get('apiKey') or
       d.get('solvr',{}).get('apiKey') or
       d.get('pinning',{}).get('solvr',{}).get('apiKey') or '')
print(key)
" 2>/dev/null || echo '')
  fi

  if [ -z "${SOLVR_API_KEY:-}" ]; then
    echo "ERROR: No Solvr API key in ~/.amcp/config.json" >&2
    echo "Agent must have its own Solvr API key configured." >&2
    echo "Set via: proactive-amcp config set solvr.apiKey <key>" >&2
    exit 1
  fi

  # Pinata JWT (only needed for --unpin-pinata)
  if [ "$UNPIN_PINATA" = true ] && [ -z "${PINATA_JWT:-}" ]; then
    if [ -f "$CONFIG_FILE" ]; then
      PINATA_JWT=$(python3 -c "
import json, os
p = os.path.expanduser('$CONFIG_FILE')
d = json.load(open(p))
print(d.get('pinata',{}).get('jwt',''))
" 2>/dev/null || echo '')
    fi
    if [ -z "${PINATA_JWT:-}" ]; then
      echo "ERROR: --unpin-pinata requires PINATA_JWT (set via config or env)" >&2
      exit 1
    fi
  fi
}

# ============================================================
# Collect all unique CIDs from checkpoint files
# ============================================================
collect_cids() {
  python3 -c "
import json, glob, os, sys

cids = set()
sources = {}

# Read from checkpoint JSON files
checkpoint_dir = os.path.expanduser('$CHECKPOINT_DIR')
for path in sorted(glob.glob(os.path.join(checkpoint_dir, '*.json'))):
    try:
        with open(path) as f:
            data = json.load(f)
        # Extract CID fields
        for field in ('cid', 'pinataCid', 'solvrCid'):
            cid = data.get(field, '')
            if cid and cid not in ('', 'local'):
                cids.add(cid)
                sources.setdefault(cid, []).append(os.path.basename(path))
    except (json.JSONDecodeError, IOError):
        print(f'WARN: Could not parse {path}', file=sys.stderr)

# Read from last-checkpoint.json
last_cp = os.path.expanduser('$LAST_CHECKPOINT_FILE')
if os.path.isfile(last_cp):
    try:
        with open(last_cp) as f:
            data = json.load(f)
        for field in ('cid', 'pinataCid', 'solvrCid'):
            cid = data.get(field, '')
            if cid and cid not in ('', 'local'):
                cids.add(cid)
                sources.setdefault(cid, []).append('last-checkpoint.json')
    except (json.JSONDecodeError, IOError):
        print(f'WARN: Could not parse {last_cp}', file=sys.stderr)

# Output one CID per line
for cid in sorted(cids):
    print(cid)
" 2>&1
}

# ============================================================
# Load migration status (tracks what's already been migrated)
# ============================================================
load_migration_status() {
  if [ -f "$MIGRATION_STATUS_FILE" ]; then
    cat "$MIGRATION_STATUS_FILE"
  else
    echo '{}'
  fi
}

# ============================================================
# Check if CID is already pinned on Solvr
# ============================================================
is_pinned_on_solvr() {
  local cid="$1"

  # Check via gateway HEAD request (fast check)
  local http_code
  http_code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
    "$SOLVR_GATEWAY/$cid" 2>/dev/null || echo '000')

  if [ "$http_code" = "200" ]; then
    return 0
  fi

  return 1
}

# ============================================================
# Pin CID to Solvr via API
# ============================================================
pin_to_solvr() {
  local cid="$1"
  local name="${2:-amcp-migrated-$cid}"

  local response
  response=$(curl -s -X POST "${SOLVR_API_URL}/pins" \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"cid\":\"$cid\",\"name\":\"$name\"}" \
    --max-time 30) || {
    echo "ERROR: Solvr API request failed for CID $cid" >&2
    return 1
  }

  # Check for error
  if echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'error' in data:
    print(data.get('error',{}).get('message', data['error']), file=sys.stderr)
    sys.exit(1)
" 2>&1; then
    return 0
  else
    return 1
  fi
}

# ============================================================
# Wait for pin to complete on Solvr (poll status)
# ============================================================
wait_for_pin() {
  local cid="$1"
  local timeout=300  # 5 minutes
  local elapsed=0
  local interval=10

  while [ $elapsed -lt $timeout ]; do
    if is_pinned_on_solvr "$cid"; then
      return 0
    fi
    sleep $interval
    elapsed=$((elapsed + interval))
    echo "  Waiting for pin... (${elapsed}s/${timeout}s)" >&2
  done

  echo "  WARN: Pin not confirmed after ${timeout}s" >&2
  return 1
}

# ============================================================
# Unpin from Pinata
# ============================================================
unpin_from_pinata() {
  local cid="$1"

  local http_code
  http_code=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE \
    "https://api.pinata.cloud/pinning/unpin/$cid" \
    -H "Authorization: Bearer $PINATA_JWT" \
    --max-time 30 2>/dev/null || echo '000')

  if [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
    # 200 = unpinned, 404 = already not pinned
    return 0
  else
    echo "  WARN: Pinata unpin returned HTTP $http_code for $cid" >&2
    return 1
  fi
}

# ============================================================
# Update migration status file
# ============================================================
update_migration_status() {
  local cid="$1"
  local status="$2"
  local unpinned_pinata="${3:-false}"

  python3 -c "
import json, os
from datetime import datetime

path = os.path.expanduser('$MIGRATION_STATUS_FILE')
os.makedirs(os.path.dirname(path), exist_ok=True)

# Load existing
data = {}
if os.path.isfile(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = {}

# Ensure top-level structure
if 'migrated' not in data:
    data['migrated'] = {}
if 'summary' not in data:
    data['summary'] = {'total': 0, 'pinned': 0, 'failed': 0, 'skipped': 0, 'unpinned_pinata': 0}

# Update entry
data['migrated']['$cid'] = {
    'status': '$status',
    'unpinned_pinata': $unpinned_pinata,
    'timestamp': datetime.now().isoformat()
}

# Recount summary
counts = {'pinned': 0, 'failed': 0, 'skipped': 0, 'unpinned_pinata': 0}
for entry in data['migrated'].values():
    s = entry.get('status', '')
    if s in counts:
        counts[s] += 1
    if entry.get('unpinned_pinata'):
        counts['unpinned_pinata'] += 1
data['summary'] = {
    'total': len(data['migrated']),
    **counts,
    'last_run': datetime.now().isoformat()
}

with open(path, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"
}

# ============================================================
# Check if CID was already migrated (from status file)
# ============================================================
is_already_migrated() {
  local cid="$1"
  if [ ! -f "$MIGRATION_STATUS_FILE" ]; then
    return 1
  fi
  python3 -c "
import json, os
path = os.path.expanduser('$MIGRATION_STATUS_FILE')
with open(path) as f:
    data = json.load(f)
entry = data.get('migrated', {}).get('$cid', {})
if entry.get('status') == 'pinned':
    exit(0)
exit(1)
" 2>/dev/null
}

# ============================================================
# Main
# ============================================================
resolve_api_keys

echo "=== AMCP Pin Migration: Pinata -> Solvr ==="
echo ""

# Collect CIDs
echo "Scanning for checkpoint CIDs..."
CIDS_RAW=$(collect_cids 2>&1)
# Separate warnings from CIDs
WARNINGS=$(echo "$CIDS_RAW" | grep "^WARN:" || true)
CIDS=$(echo "$CIDS_RAW" | grep -v "^WARN:" || true)

if [ -n "$WARNINGS" ]; then
  echo "$WARNINGS"
fi

if [ -z "$CIDS" ]; then
  echo "No checkpoint CIDs found in $CHECKPOINT_DIR/ or $LAST_CHECKPOINT_FILE"
  echo "Nothing to migrate."
  exit 0
fi

CID_COUNT=$(echo "$CIDS" | wc -l | tr -d ' ')
echo "Found $CID_COUNT unique CID(s)"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN — no changes will be made"
  echo ""
fi

# Process each CID
PINNED=0
SKIPPED=0
FAILED=0
UNPINNED=0

while IFS= read -r cid; do
  [ -z "$cid" ] && continue

  echo "[$((PINNED + SKIPPED + FAILED + 1))/$CID_COUNT] CID: $cid"

  # Check migration status first
  if is_already_migrated "$cid"; then
    echo "  Already migrated (from status file), skipping"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Check if already on Solvr
  if is_pinned_on_solvr "$cid"; then
    echo "  Already on Solvr, skipping"
    SKIPPED=$((SKIPPED + 1))
    if [ "$DRY_RUN" = false ]; then
      update_migration_status "$cid" "skipped" "false"
    fi
    continue
  fi

  if [ "$DRY_RUN" = true ]; then
    echo "  Would pin to Solvr"
    if [ "$UNPIN_PINATA" = true ]; then
      echo "  Would unpin from Pinata (after confirmation)"
    fi
    PINNED=$((PINNED + 1))
    continue
  fi

  # Pin to Solvr
  echo "  Pinning to Solvr..."
  if pin_to_solvr "$cid" "amcp-checkpoint-migrated"; then
    echo "  Waiting for pin confirmation..."
    if wait_for_pin "$cid"; then
      echo "  Pinned to Solvr"
      PINNED=$((PINNED + 1))

      # Unpin from Pinata if requested
      local_unpinned="false"
      if [ "$UNPIN_PINATA" = true ]; then
        echo "  Unpinning from Pinata..."
        if unpin_from_pinata "$cid"; then
          echo "  Unpinned from Pinata"
          local_unpinned="true"
          UNPINNED=$((UNPINNED + 1))
        fi
      fi

      update_migration_status "$cid" "pinned" "$local_unpinned"
    else
      echo "  Pin not confirmed within timeout"
      FAILED=$((FAILED + 1))
      update_migration_status "$cid" "failed" "false"
    fi
  else
    echo "  Pin failed"
    FAILED=$((FAILED + 1))
    update_migration_status "$cid" "failed" "false"
  fi
  echo ""
done <<< "$CIDS"

# Summary
echo ""
echo "=== Migration Summary ==="
echo "  Total CIDs:  $CID_COUNT"
echo "  Pinned:      $PINNED"
echo "  Skipped:     $SKIPPED"
echo "  Failed:      $FAILED"
if [ "$UNPIN_PINATA" = true ]; then
  echo "  Unpinned:    $UNPINNED"
fi
if [ "$DRY_RUN" = true ]; then
  echo "  (DRY RUN — no changes made)"
fi
echo "  Status file: $MIGRATION_STATUS_FILE"

# Verify accessibility via Solvr gateway
if [ "$DRY_RUN" = false ] && [ $PINNED -gt 0 ]; then
  echo ""
  echo "=== Verification ==="
  VERIFIED=0
  VERIFY_FAILED=0
  while IFS= read -r cid; do
    [ -z "$cid" ] && continue
    if is_pinned_on_solvr "$cid"; then
      VERIFIED=$((VERIFIED + 1))
    else
      echo "  WARN: $cid not accessible via Solvr gateway"
      VERIFY_FAILED=$((VERIFY_FAILED + 1))
    fi
  done <<< "$CIDS"
  echo "  Accessible via Solvr gateway: $VERIFIED/$CID_COUNT"
  if [ $VERIFY_FAILED -gt 0 ]; then
    echo "  Not accessible: $VERIFY_FAILED (may still be propagating)"
  fi
fi

# Exit code: 0 if no failures, 1 if any failed
if [ $FAILED -gt 0 ]; then
  exit 1
fi
exit 0
