#!/bin/bash
# resurrect-from-solvr.sh - Resurrect agent from Solvr resurrection bundle
# Usage: ./resurrect-from-solvr.sh [--agent-id <id>] [--json] [--dry-run]
#
# Calls GET /v1/agents/{id}/resurrection-bundle to get a full recovery package:
#   - identity info
#   - knowledge (ideas, approaches, problems)
#   - reputation
#   - latest checkpoint CID
#   - death_count
#
# If a checkpoint CID is present, downloads from IPFS and applies it
# using existing restore logic (amcp resuscitate CLI).
# Imports knowledge as local cache for agent context.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }
command -v curl &>/dev/null || { echo "FATAL: curl required but not found" >&2; exit 2; }

# Configurable paths (overridable via env vars)
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"
CONTENT_DIR="${CONTENT_DIR:-$HOME/.openclaw/workspace}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"
AGENT_NAME="${AGENT_NAME:-$(hostname -s 2>/dev/null || echo Agent)}"
KNOWLEDGE_CACHE_DIR="${KNOWLEDGE_CACHE_DIR:-$HOME/.amcp/solvr-knowledge}"

# Ensure Node.js webcrypto is available for amcp CLI
case "${NODE_OPTIONS:-}" in
  *--experimental-global-webcrypto*) ;;
  *) export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--experimental-global-webcrypto" ;;
esac

# Flags
AGENT_ID="me"
JSON_OUTPUT=false
DRY_RUN=false

usage() {
  cat <<EOF
proactive-amcp resurrect — Resurrect agent from Solvr resurrection bundle

Usage: $(basename "$0") [options]

Fetches the Solvr resurrection bundle (identity, knowledge, reputation,
latest checkpoint) and restores the agent from the latest checkpoint.

Options:
  --agent-id <ID>   Solvr agent ID (default: me — uses authenticated agent)
  --json            Output bundle as JSON without applying (inspection mode)
  --dry-run         Fetch and display bundle but don't apply changes
  -h, --help        Show this help

Config (~/.amcp/config.json):
  solvr.apiKey      Solvr API key (required)

Environment:
  SOLVR_API_URL     API base URL (default: https://api.solvr.dev/v1)
  CONTENT_DIR       Workspace directory (default: ~/.openclaw/workspace)
  IDENTITY_PATH     AMCP identity file (default: ~/.amcp/identity.json)
EOF
  exit 0
}

# ============================================================
# Parse arguments
# ============================================================
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent-id) AGENT_ID="$2"; shift 2 ;;
    --json) JSON_OUTPUT=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# ============================================================
# Resolve Solvr API key from config (same fallback chain as other scripts)
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
# Build API URL for agent
# ============================================================
if [ "$AGENT_ID" = "me" ]; then
  BUNDLE_URL="${SOLVR_API_URL}/agents/me/resurrection-bundle"
else
  BUNDLE_URL="${SOLVR_API_URL}/agents/${AGENT_ID}/resurrection-bundle"
fi

# ============================================================
# Fetch resurrection bundle from Solvr
# ============================================================
echo "Fetching resurrection bundle from Solvr..."
echo "  Agent: $AGENT_ID"
echo "  URL: $BUNDLE_URL"
echo ""

RESPONSE=$(curl -s --max-time 30 -X GET "$BUNDLE_URL" \
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
  echo "ERROR: Failed to fetch resurrection bundle: $IS_ERROR" >&2
  exit 1
fi

# ============================================================
# JSON output mode — dump and exit
# ============================================================
if [ "$JSON_OUTPUT" = true ]; then
  echo "$RESPONSE" | python3 -c "import sys,json; json.dump(json.load(sys.stdin), sys.stdout, indent=2); print()"
  exit 0
fi

# ============================================================
# Parse bundle contents
# ============================================================
PARSED=$(echo "$RESPONSE" | python3 -c "
import sys, json

data = json.load(sys.stdin)

# Identity
identity = data.get('identity', {})
agent_name = identity.get('display_name', '') or identity.get('name', '') or 'Unknown'
agent_id = identity.get('id', '') or identity.get('agent_id', '')
solvr_name = identity.get('solvr_name', '') or identity.get('name', '')

# Reputation
reputation = data.get('reputation', {})
rep_total = reputation.get('total', 0) if isinstance(reputation, dict) else 0

# Death count
death_count = data.get('death_count', None)
if death_count is None:
    death_count = 'unknown'

# Latest checkpoint
cp = data.get('latest_checkpoint', None)
cp_cid = ''
cp_name = ''
cp_date = ''
if cp and isinstance(cp, dict):
    cp_cid = cp.get('cid', '') or ''
    cp_name = cp.get('metadata', {}).get('name', '') or cp.get('name', '') or ''
    cp_date = cp.get('created_at', '') or cp.get('created', '') or ''

# Knowledge counts
knowledge = data.get('knowledge', {})
ideas = knowledge.get('ideas', []) if isinstance(knowledge, dict) else []
approaches = knowledge.get('approaches', []) if isinstance(knowledge, dict) else []
problems = knowledge.get('problems', []) if isinstance(knowledge, dict) else []
n_ideas = len(ideas) if isinstance(ideas, list) else 0
n_approaches = len(approaches) if isinstance(approaches, list) else 0
n_problems = len(problems) if isinstance(problems, list) else 0

result = {
    'agent_name': str(agent_name),
    'agent_id': str(agent_id),
    'solvr_name': str(solvr_name),
    'rep_total': int(rep_total) if rep_total else 0,
    'death_count': str(death_count),
    'cp_cid': str(cp_cid),
    'cp_name': str(cp_name),
    'cp_date': str(cp_date),
    'n_ideas': n_ideas,
    'n_approaches': n_approaches,
    'n_problems': n_problems,
}
print(json.dumps(result))
" 2>/dev/null)

if [ -z "$PARSED" ]; then
  echo "ERROR: Failed to parse resurrection bundle" >&2
  exit 1
fi

# Extract fields
BUNDLE_AGENT_NAME=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['agent_name'])")
BUNDLE_AGENT_ID=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")
BUNDLE_REP=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['rep_total'])")
BUNDLE_DEATHS=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['death_count'])")
BUNDLE_CID=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['cp_cid'])")
BUNDLE_CP_NAME=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['cp_name'])")
BUNDLE_CP_DATE=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['cp_date'])")
N_IDEAS=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['n_ideas'])")
N_APPROACHES=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['n_approaches'])")
N_PROBLEMS=$(echo "$PARSED" | python3 -c "import sys,json; print(json.load(sys.stdin)['n_problems'])")

# ============================================================
# Display bundle summary
# ============================================================
echo "=== Solvr Resurrection Bundle ==="
echo ""
echo "  Agent:       $BUNDLE_AGENT_NAME"
[ -n "$BUNDLE_AGENT_ID" ] && echo "  Agent ID:    $BUNDLE_AGENT_ID"
echo "  Reputation:  $BUNDLE_REP"
echo "  Deaths:      $BUNDLE_DEATHS"
echo ""
echo "  Knowledge:"
echo "    Ideas:      $N_IDEAS"
echo "    Approaches: $N_APPROACHES"
echo "    Problems:   $N_PROBLEMS"
echo ""

if [ -n "$BUNDLE_CID" ]; then
  echo "  Latest Checkpoint:"
  echo "    CID:  $BUNDLE_CID"
  [ -n "$BUNDLE_CP_NAME" ] && echo "    Name: $BUNDLE_CP_NAME"
  [ -n "$BUNDLE_CP_DATE" ] && echo "    Date: $BUNDLE_CP_DATE"
else
  echo "  Latest Checkpoint: none"
fi
echo ""

# ============================================================
# Dry-run mode — display only, no changes
# ============================================================
if [ "$DRY_RUN" = true ]; then
  echo "(dry-run: no changes applied)"
  exit 0
fi

# ============================================================
# Step 1: Import knowledge to local cache
# ============================================================
echo "=== Step 1: Import knowledge ==="

mkdir -p "$KNOWLEDGE_CACHE_DIR"

# Write knowledge cache as a structured JSON file
echo "$RESPONSE" | python3 -c "
import sys, json, os
from datetime import datetime

data = json.load(sys.stdin)
cache_dir = '$KNOWLEDGE_CACHE_DIR'

knowledge = data.get('knowledge', {})
ideas = knowledge.get('ideas', []) if isinstance(knowledge, dict) else []
approaches = knowledge.get('approaches', []) if isinstance(knowledge, dict) else []
problems = knowledge.get('problems', []) if isinstance(knowledge, dict) else []

# Write knowledge cache
cache = {
    'fetched_at': datetime.now().isoformat(),
    'agent_id': (data.get('identity', {}) or {}).get('id', ''),
    'ideas': ideas[:50] if isinstance(ideas, list) else [],
    'approaches': approaches[:50] if isinstance(approaches, list) else [],
    'problems': problems[:50] if isinstance(problems, list) else [],
}

cache_file = os.path.join(cache_dir, 'knowledge-cache.json')
with open(cache_file, 'w') as f:
    json.dump(cache, f, indent=2)

print(f'  Cached {len(cache[\"ideas\"])} ideas, {len(cache[\"approaches\"])} approaches, {len(cache[\"problems\"])} problems')
print(f'  Written to: {cache_file}')

# Write human-readable summary for agent context
summary_file = os.path.join(cache_dir, 'knowledge-summary.md')
with open(summary_file, 'w') as f:
    f.write('# Solvr Knowledge Summary\n\n')
    f.write(f'Fetched: {cache[\"fetched_at\"]}\n\n')

    if ideas:
        f.write('## Top Ideas\n\n')
        for idea in ideas[:10]:
            title = idea.get('title', '') if isinstance(idea, dict) else str(idea)
            f.write(f'- {title}\n')
        f.write('\n')

    if problems:
        f.write('## Open Problems\n\n')
        for prob in problems[:10]:
            title = prob.get('title', '') if isinstance(prob, dict) else str(prob)
            status = prob.get('status', '') if isinstance(prob, dict) else ''
            f.write(f'- [{status}] {title}\n')
        f.write('\n')

    if approaches:
        f.write('## Recent Approaches\n\n')
        for appr in approaches[:10]:
            method = appr.get('method', '') if isinstance(appr, dict) else str(appr)
            status = appr.get('status', '') if isinstance(appr, dict) else ''
            f.write(f'- [{status}] {method}\n')
        f.write('\n')

print(f'  Summary: {summary_file}')
" 2>/dev/null || echo "  WARN: Failed to cache knowledge (continuing)"

echo ""

# ============================================================
# Step 2: Download and apply checkpoint (if CID present)
# ============================================================
if [ -z "$BUNDLE_CID" ]; then
  echo "=== Step 2: No checkpoint to restore ==="
  echo "  No checkpoint CID in bundle — knowledge imported only."
  echo ""
  echo "Done. Knowledge cached at: $KNOWLEDGE_CACHE_DIR"
  exit 0
fi

echo "=== Step 2: Restore from checkpoint ==="
echo "  CID: $BUNDLE_CID"
echo ""

# Validate AMCP identity exists
if [ ! -f "$IDENTITY_PATH" ]; then
  echo "ERROR: No AMCP identity at $IDENTITY_PATH" >&2
  echo "Cannot decrypt checkpoint without identity. Create one with: amcp identity create" >&2
  exit 1
fi

# Validate identity
if [ -x "$AMCP_CLI" ] || command -v amcp &>/dev/null; then
  if ! "$AMCP_CLI" identity validate --identity "$IDENTITY_PATH" 2>/dev/null; then
    echo "ERROR: Invalid AMCP identity at $IDENTITY_PATH" >&2
    exit 1
  fi
fi

# Download checkpoint from IPFS via Solvr gateway (with fallbacks)
CHECKPOINT_TMP=$(mktemp "/tmp/resurrect-checkpoint-XXXXXX.amcp")
trap 'rm -f "$CHECKPOINT_TMP"' EXIT

echo "  Downloading checkpoint from IPFS..."

# Gateway priority: Solvr > Pinata > IPFS.io > Cloudflare
GATEWAYS=(
  "solvr|https://ipfs.solvr.dev/ipfs/${BUNDLE_CID}"
  "pinata|https://gateway.pinata.cloud/ipfs/${BUNDLE_CID}"
  "ipfs.io|https://ipfs.io/ipfs/${BUNDLE_CID}"
  "cloudflare|https://cloudflare-ipfs.com/ipfs/${BUNDLE_CID}"
)

DOWNLOADED=false
for gw in "${GATEWAYS[@]}"; do
  GW_NAME="${gw%%|*}"
  GW_URL="${gw#*|}"
  echo "    Trying: $GW_NAME"
  if curl -sf --max-time 120 "$GW_URL" -o "$CHECKPOINT_TMP" 2>/dev/null && [ -s "$CHECKPOINT_TMP" ]; then
    echo "    Downloaded from $GW_NAME"
    DOWNLOADED=true
    break
  fi
done

if [ "$DOWNLOADED" = false ]; then
  echo "ERROR: Failed to download checkpoint from all IPFS gateways" >&2
  echo "  CID: $BUNDLE_CID" >&2
  echo "  Knowledge was cached. Checkpoint restore failed." >&2
  exit 1
fi

# Apply checkpoint using AMCP CLI
echo ""
echo "  Decrypting and restoring checkpoint..."

SECRETS_TMP=$(mktemp "/tmp/resurrect-secrets-XXXXXX.json")
CONTENT_TMP=$(mktemp -d "/tmp/resurrect-content-XXXXXX")
trap 'rm -f "$CHECKPOINT_TMP" "$SECRETS_TMP"; rm -rf "$CONTENT_TMP"' EXIT

if ! "$AMCP_CLI" resuscitate \
     --checkpoint "$CHECKPOINT_TMP" \
     --identity "$IDENTITY_PATH" \
     --out-content "$CONTENT_TMP" \
     --out-secrets "$SECRETS_TMP" 2>&1; then
  echo "ERROR: Failed to decrypt/verify checkpoint" >&2
  echo "  The checkpoint may have been created with a different identity." >&2
  exit 1
fi

echo "  Checkpoint verified and decrypted"

# Restore content to workspace
if [ -d "$CONTENT_TMP" ] && [ "$(ls -A "$CONTENT_TMP" 2>/dev/null)" ]; then
  echo "  Restoring content to $CONTENT_DIR..."
  mkdir -p "$CONTENT_DIR"

  for item in "$CONTENT_TMP"/*; do
    [ -e "$item" ] || continue
    basename_item=$(basename "$item")
    # Skip directories that look like code repos
    case "$basename_item" in
      solvr|amcp-protocol|openclaw-*|proactive-*)
        echo "    Skipping code repo: $basename_item"
        continue
        ;;
    esac
    cp -r "$item" "$CONTENT_DIR/" 2>/dev/null || true
    echo "    Restored: $basename_item"
  done
fi

# Inject secrets
if [ -f "$SECRETS_TMP" ] && [ -s "$SECRETS_TMP" ]; then
  echo "  Injecting secrets..."
  if [ -x "$SCRIPT_DIR/load-credentials.sh" ]; then
    "$SCRIPT_DIR/load-credentials.sh" "$SECRETS_TMP" 2>&1 || echo "  WARN: Secret injection had errors (non-fatal)"
  else
    echo "  WARN: load-credentials.sh not found, skipping secret injection"
  fi
fi

# Validate learning storage (if present)
LEARNING_DIR="$CONTENT_DIR/memory/learning"
if [ -d "$LEARNING_DIR" ]; then
  echo "  Validating learning storage..."
  python3 -c "
import json, os, sys
learning_dir = '$LEARNING_DIR'
for fname in ('problems.jsonl', 'learnings.jsonl'):
    fpath = os.path.join(learning_dir, fname)
    if not os.path.isfile(fpath):
        continue
    errors = 0
    with open(fpath) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            try: json.loads(line)
            except json.JSONDecodeError:
                errors += 1
    if errors:
        print(f'    WARN: {fname} has {errors} invalid line(s)', file=sys.stderr)
    else:
        print(f'    {fname}: OK')
" 2>&1 || echo "  WARN: learning validation failed (non-fatal)"
fi

# Validate ontology graph (if present)
ONTOLOGY_GRAPH="$CONTENT_DIR/memory/ontology/graph.jsonl"
if [ -f "$ONTOLOGY_GRAPH" ] && [ -f "$SCRIPT_DIR/validate-ontology.py" ]; then
  echo "  Validating ontology graph..."
  python3 "$SCRIPT_DIR/validate-ontology.py" "$ONTOLOGY_GRAPH" 2>&1 || echo "  WARN: ontology validation failed (non-fatal)"
fi

# Recreate virtual environments from manifest (if present)
VENVS_MANIFEST="$CONTENT_DIR/memory/venvs-manifest.json"
if [ -x "$SCRIPT_DIR/recreate-venvs.sh" ]; then
  "$SCRIPT_DIR/recreate-venvs.sh" "$VENVS_MANIFEST" 2>&1 || echo "  WARN: venv recreation failed (non-fatal)"
fi

# Notify on success
[ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "Resurrection complete for $AGENT_NAME (via Solvr bundle, CID: ${BUNDLE_CID:0:20}...)"

echo ""
echo "=== Resurrection Complete ==="
echo ""
echo "  Agent:        $BUNDLE_AGENT_NAME"
echo "  Checkpoint:   $BUNDLE_CID"
echo "  Content:      $CONTENT_DIR"
echo "  Knowledge:    $KNOWLEDGE_CACHE_DIR"
echo ""
echo "  Next steps:"
echo "    1. Verify workspace: ls $CONTENT_DIR"
echo "    2. Review knowledge: cat $KNOWLEDGE_CACHE_DIR/knowledge-summary.md"
echo "    3. Check status: proactive-amcp status"
echo ""
