#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <agent_id> [archive_root]"
  exit 1
fi

AGENT_ID="$1"
ARCHIVE_ROOT="${2:-$(pwd)/state/archive}"
TS="$(date -u +'%Y%m%dT%H%M%SZ')"
OUT="$ARCHIVE_ROOT/$AGENT_ID/$TS"

mkdir -p "$OUT"

cp -a "$HOME/.openclaw/agents/$AGENT_ID" "$OUT/agents-dir" 2>/dev/null || true
cp -a "$HOME/.openclaw/workspace-$AGENT_ID" "$OUT/workspace" 2>/dev/null || true

openclaw agents list --json > "$OUT/openclaw.agents.list.json"
openclaw status --json > "$OUT/openclaw.status.json"
openclaw gateway status --json > "$OUT/openclaw.gateway.status.json"

echo "$OUT"
