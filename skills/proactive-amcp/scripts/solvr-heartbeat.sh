#!/bin/bash
# solvr-heartbeat.sh - Send heartbeat to Solvr and display agent status briefing
# Usage: ./solvr-heartbeat.sh [--json] [--quiet]
#
# Calls POST /v1/agents/me/heartbeat to record liveness,
# then displays a status briefing: reputation, checkpoint age,
# stale approaches, and suggested actions from Solvr.

set -euo pipefail

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }
command -v curl &>/dev/null || { echo "FATAL: curl required but not found" >&2; exit 2; }

# Configurable paths (overridable via env vars)
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
LAST_CHECKPOINT_FILE="${LAST_CHECKPOINT_FILE:-$HOME/.amcp/last-checkpoint.json}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"
CHECKPOINT_AGE_WARN_HOURS="${CHECKPOINT_AGE_WARN_HOURS:-24}"

# Flags
JSON_OUTPUT=false
QUIET=false

usage() {
  cat <<EOF
proactive-amcp heartbeat — Send heartbeat and display agent status briefing

Usage: $(basename "$0") [options]

Records agent liveness with Solvr, then shows a status briefing:
  - Agent status, reputation, death count
  - Checkpoint age warning (if > ${CHECKPOINT_AGE_WARN_HOURS}h)
  - Stale approaches needing status updates
  - Suggested actions from Solvr

Options:
  --json       Output raw JSON (machine-readable)
  --quiet      Only output warnings and errors (skip normal status display)
  -h, --help   Show this help

Config (~/.amcp/config.json):
  solvr.apiKey   Solvr API key (required)

Environment:
  SOLVR_API_URL              API base URL (default: https://api.solvr.dev/v1)
  CHECKPOINT_AGE_WARN_HOURS  Hours before checkpoint age warning (default: 24)
EOF
  exit 0
}

# ============================================================
# Parse arguments
# ============================================================
for arg in "$@"; do
  case "$arg" in
    --json) JSON_OUTPUT=true ;;
    --quiet|-q) QUIET=true ;;
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
# Step 1: Record heartbeat (POST /v1/agents/me/heartbeat)
# ============================================================
HEARTBEAT_RESPONSE=$(curl -s --max-time 15 -X POST "${SOLVR_API_URL}/agents/me/heartbeat" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" 2>/dev/null || echo '{"error":"connection_failed"}')

HEARTBEAT_OK=$(python3 -c "
import sys, json
try:
    d = json.loads('''$HEARTBEAT_RESPONSE''')
    if d.get('recorded') or d.get('timestamp'):
        print('true')
    elif 'error' in d:
        print('false')
    else:
        print('true')
except Exception:
    print('false')
" 2>/dev/null || echo "false")

HEARTBEAT_TS=$(python3 -c "
import sys, json
try:
    d = json.loads('''$HEARTBEAT_RESPONSE''')
    print(d.get('timestamp',''))
except Exception:
    print('')
" 2>/dev/null || echo "")

# ============================================================
# Step 2: Fetch agent profile (GET /v1/agents/me)
# ============================================================
AGENT_RESPONSE=$(curl -s --max-time 15 -X GET "${SOLVR_API_URL}/agents/me" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -H "Accept: application/json" 2>/dev/null || echo '{"error":"connection_failed"}')

# ============================================================
# Step 3: Fetch checkpoint info (GET /v1/agents/me/checkpoints)
# ============================================================
CHECKPOINTS_RESPONSE=$(curl -s --max-time 15 -X GET "${SOLVR_API_URL}/agents/me/checkpoints" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -H "Accept: application/json" 2>/dev/null || echo '{"error":"connection_failed"}')

# ============================================================
# Step 4: Check local checkpoint age
# ============================================================
LOCAL_CHECKPOINT_AGE_HOURS=""
LOCAL_CHECKPOINT_TS=""
if [ -f "$LAST_CHECKPOINT_FILE" ]; then
  LOCAL_CHECKPOINT_TS=$(python3 -c "
import json
try:
    d = json.load(open('$LAST_CHECKPOINT_FILE'))
    print(d.get('timestamp',''))
except Exception:
    print('')
" 2>/dev/null || echo "")
  if [ -n "$LOCAL_CHECKPOINT_TS" ]; then
    LOCAL_CHECKPOINT_AGE_HOURS=$(python3 -c "
from datetime import datetime, timezone
import sys
ts = '''$LOCAL_CHECKPOINT_TS'''
try:
    if ts.endswith('Z'):
        ts = ts[:-1] + '+00:00'
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    hours = (now - dt).total_seconds() / 3600
    print(int(hours))
except Exception:
    print('')
" 2>/dev/null || echo "")
  fi
fi

# ============================================================
# Build consolidated JSON result
# ============================================================
RESULT_JSON=$(python3 -c "
import json, sys

heartbeat_ok = '$HEARTBEAT_OK' == 'true'
heartbeat_ts = '$HEARTBEAT_TS'

# Parse agent profile
agent = {}
try:
    agent = json.loads('''$AGENT_RESPONSE''')
    if 'error' in agent:
        agent = {}
except Exception:
    agent = {}

# Parse checkpoints
checkpoints = {}
try:
    checkpoints = json.loads('''$CHECKPOINTS_RESPONSE''')
    if 'error' in checkpoints:
        checkpoints = {}
except Exception:
    checkpoints = {}

# Local checkpoint age
local_age = '$LOCAL_CHECKPOINT_AGE_HOURS'
local_ts = '$LOCAL_CHECKPOINT_TS'
checkpoint_age_warn_hours = int('$CHECKPOINT_AGE_WARN_HOURS')

# Build result
result = {
    'heartbeat': {
        'recorded': heartbeat_ok,
        'timestamp': heartbeat_ts
    },
    'agent': {
        'name': agent.get('display_name', '') or agent.get('name', ''),
        'id': agent.get('id', ''),
        'status': agent.get('status', 'unknown'),
        'death_count': agent.get('death_count', None),
        'created_at': agent.get('created_at', '')
    },
    'reputation': agent.get('reputation', {}),
    'checkpoints': {
        'count': checkpoints.get('count', 0),
        'latest_cid': '',
        'latest_date': ''
    },
    'local_checkpoint': {
        'timestamp': local_ts,
        'age_hours': int(local_age) if local_age else None
    },
    'warnings': [],
    'suggested_actions': agent.get('suggested_actions', [])
}

# Extract latest checkpoint info
latest = checkpoints.get('latest')
if latest and isinstance(latest, dict):
    result['checkpoints']['latest_cid'] = latest.get('cid', '')
    result['checkpoints']['latest_date'] = latest.get('created_at', '')

# Stale approaches
stale = agent.get('stale_approaches', [])
result['stale_approaches'] = stale

# Warnings
if local_age and int(local_age) > checkpoint_age_warn_hours:
    result['warnings'].append(f'Checkpoint is {local_age}h old (threshold: {checkpoint_age_warn_hours}h)')
elif not local_ts:
    result['warnings'].append('No local checkpoint found')

if stale:
    result['warnings'].append(f'{len(stale)} stale approach(es) need status updates')

if not heartbeat_ok:
    result['warnings'].append('Heartbeat recording failed — check Solvr API key')

json.dump(result, sys.stdout, indent=2)
print()
" 2>/dev/null)

if [ -z "$RESULT_JSON" ]; then
  echo "ERROR: Failed to build heartbeat result" >&2
  exit 1
fi

# ============================================================
# Output: JSON mode
# ============================================================
if [ "$JSON_OUTPUT" = true ]; then
  echo "$RESULT_JSON"
  exit 0
fi

# ============================================================
# Output: Human-readable status briefing
# ============================================================
if [ "$QUIET" = false ]; then
  python3 -c "
import json, sys

data = json.loads('''$RESULT_JSON''')

hb = data['heartbeat']
ag = data['agent']
rep = data.get('reputation', {})
cp = data['checkpoints']
local_cp = data['local_checkpoint']
warnings = data.get('warnings', [])
actions = data.get('suggested_actions', [])
stale = data.get('stale_approaches', [])

print()
print('  HEARTBEAT')
if hb['recorded']:
    ts_display = hb['timestamp'][:19] if hb['timestamp'] else 'now'
    print(f'    Recorded: {ts_display}')
else:
    print('    FAILED — could not record heartbeat')
print()

# Agent info
name = ag.get('name', 'Unknown')
agent_id = ag.get('id', '')
status = ag.get('status', 'unknown')
deaths = ag.get('death_count')
death_str = str(deaths) if deaths is not None else '-'

print('  AGENT')
print(f'    Name:     {name}')
if agent_id:
    print(f'    ID:       {agent_id}')
print(f'    Status:   {status}')
print(f'    Deaths:   {death_str}')
print()

# Reputation
total = rep.get('total', None)
if total is not None:
    print('  REPUTATION')
    print(f'    Total:    {total}')
    # Show breakdown if available
    for key in ['ideas', 'approaches', 'problems', 'solutions']:
        val = rep.get(key)
        if val is not None:
            print(f'    {key.capitalize():<10} {val}')
    print()

# Checkpoints
print('  CHECKPOINTS')
print(f'    Solvr:    {cp[\"count\"]} stored')
if cp.get('latest_cid'):
    cid_short = cp['latest_cid'][:20] + '...' if len(cp['latest_cid']) > 20 else cp['latest_cid']
    print(f'    Latest:   {cid_short}')
if cp.get('latest_date'):
    print(f'    Date:     {cp[\"latest_date\"][:19]}')

if local_cp.get('age_hours') is not None:
    age = local_cp['age_hours']
    print(f'    Local:    {age}h ago ({local_cp[\"timestamp\"][:19]})')
elif local_cp.get('timestamp'):
    print(f'    Local:    {local_cp[\"timestamp\"][:19]}')
else:
    print('    Local:    none')
print()

# Warnings
if warnings:
    print('  WARNINGS')
    for w in warnings:
        print(f'    ! {w}')
    print()

# Stale approaches
if stale:
    print('  STALE APPROACHES (need status update)')
    for i, approach in enumerate(stale[:5]):
        title = approach.get('title', '') or approach.get('description', 'untitled')
        approach_id = approach.get('id', '')
        if len(title) > 60:
            title = title[:57] + '...'
        print(f'    {i+1}. {title}')
        if approach_id:
            print(f'       ID: {approach_id}')
    if len(stale) > 5:
        print(f'    ... and {len(stale) - 5} more')
    print()

# Suggested actions
if actions:
    print('  SUGGESTED ACTIONS')
    for i, action in enumerate(actions[:5]):
        if isinstance(action, str):
            print(f'    {i+1}. {action}')
        elif isinstance(action, dict):
            desc = action.get('description', '') or action.get('action', '')
            print(f'    {i+1}. {desc}')
    if len(actions) > 5:
        print(f'    ... and {len(actions) - 5} more')
    print()

if not warnings and not stale and not actions:
    print('  All clear — no warnings or pending actions.')
    print()
" <<< "$RESULT_JSON"
fi

# ============================================================
# Print warnings to stderr (for --quiet mode or scripting)
# ============================================================
WARN_COUNT=$(python3 -c "
import json
d = json.loads('''$RESULT_JSON''')
warnings = d.get('warnings', [])
print(len(warnings))
" 2>/dev/null || echo "0")

if [ "$QUIET" = true ] && [ "$WARN_COUNT" -gt 0 ]; then
  python3 -c "
import json, sys
d = json.loads('''$RESULT_JSON''')
for w in d.get('warnings', []):
    print(f'WARNING: {w}', file=sys.stderr)
" <<< "$RESULT_JSON" 2>&1 >&2
fi

# ============================================================
# Smart checkpoint trigger (proactive self-checkpointing)
# ============================================================
CHECKPOINT_SCRIPT="$SCRIPT_DIR/checkpoint.sh"
if [ -x "$CHECKPOINT_SCRIPT" ]; then
  "$CHECKPOINT_SCRIPT" --trigger heartbeat --quiet 2>/dev/null || true
fi

exit 0
