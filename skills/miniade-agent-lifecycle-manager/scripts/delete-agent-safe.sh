#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  delete-agent-safe.sh <agent_id> [--yes] [--archive-root <path>] [--root <workspace_root>] [--operator <name>]

Flow:
  1) Archive agent files + status snapshots
  2) Require explicit confirmation (unless --yes)
  3) Remove bindings entries for this agent
  4) Remove telegram channel account for this agent
  5) Delete agent via openclaw agents delete --force
  6) Refresh dashboard + append lifecycle log
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

AGENT_ID="$1"
shift

YES=0
ARCHIVE_ROOT=""
ROOT="$(pwd)"
OPERATOR="agent-manager"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes)
      YES=1
      shift
      ;;
    --archive-root)
      ARCHIVE_ROOT="$2"
      shift 2
      ;;
    --root)
      ROOT="$2"
      shift 2
      ;;
    --operator)
      OPERATOR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE_SCRIPT="$SCRIPT_DIR/archive-agent.sh"
REFRESH_SCRIPT="$SCRIPT_DIR/refresh-dashboard.sh"
LOG_SCRIPT="$SCRIPT_DIR/lifecycle-log.sh"

if [[ -z "$ARCHIVE_ROOT" ]]; then
  ARCHIVE_ROOT="$ROOT/state/archive"
fi

# precheck: agent exists
AGENTS_JSON="$(openclaw agents list --json)"
if ! jq -e --arg aid "$AGENT_ID" 'any(.[]?; .id == $aid)' <<<"$AGENTS_JSON" >/dev/null; then
  echo "Agent not found: $AGENT_ID"
  exit 1
fi

# 1) archive first
ARCHIVE_OUT="$($ARCHIVE_SCRIPT "$AGENT_ID" "$ARCHIVE_ROOT")"
if [[ ! -f "$ARCHIVE_OUT/openclaw.agents.list.json" || ! -f "$ARCHIVE_OUT/openclaw.status.json" || ! -f "$ARCHIVE_OUT/openclaw.gateway.status.json" ]]; then
  echo "Archive verification failed: missing status snapshots under $ARCHIVE_OUT"
  exit 1
fi

echo "Archive created: $ARCHIVE_OUT"

# 2) confirmation
if [[ $YES -ne 1 ]]; then
  echo "Type exactly: DELETE $AGENT_ID"
  read -r CONFIRM
  if [[ "$CONFIRM" != "DELETE $AGENT_ID" ]]; then
    echo "Cancelled. Agent not deleted. Archive kept at: $ARCHIVE_OUT"
    exit 2
  fi
fi

# 3) remove bindings
BINDINGS_JSON="$(openclaw config get bindings --json 2>/dev/null || echo '[]')"
NEW_BINDINGS="$(jq -c --arg aid "$AGENT_ID" '[.[]? | select(.agentId != $aid)]' <<< "$BINDINGS_JSON")"
if [[ "$NEW_BINDINGS" != "$(jq -c '.' <<< "$BINDINGS_JSON")" ]]; then
  openclaw config set bindings "$NEW_BINDINGS" --json
  echo "Removed bindings for agent=$AGENT_ID"
else
  echo "No bindings found for agent=$AGENT_ID"
fi

# 4) remove telegram channel account (best effort)
if openclaw channels remove --channel telegram --account "$AGENT_ID" --delete; then
  echo "Removed telegram account for agent=$AGENT_ID"
else
  echo "Warning: failed to remove telegram account for agent=$AGENT_ID (continuing)"
fi

# 5) delete agent
openclaw agents delete "$AGENT_ID" --force --json >/tmp/openclaw.agent-delete.$AGENT_ID.json

echo "Deleted agent: $AGENT_ID"

# 6) refresh + log (best effort)
if "$REFRESH_SCRIPT" "$ROOT"; then
  echo "Dashboard refreshed"
else
  echo "Warning: dashboard refresh failed"
fi

LOG_FILE="$ROOT/AGENT_LIFECYCLE_LOG.md"
SUMMARY="safe-delete; archive=$ARCHIVE_OUT"
if "$LOG_SCRIPT" "$LOG_FILE" "delete" "$AGENT_ID" "$SUMMARY" "$OPERATOR"; then
  echo "Lifecycle log updated: $LOG_FILE"
else
  echo "Warning: lifecycle log update failed"
fi

echo "Done"
