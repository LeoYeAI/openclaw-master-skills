#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 <log_file> <action> <agent_id> <summary> [operator]"
  exit 1
fi

LOG_FILE="$1"
ACTION="$2"
AGENT_ID="$3"
SUMMARY="$4"
OPERATOR="${5:-agent-manager}"
TS="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

if [[ ! -f "$LOG_FILE" ]]; then
  cat > "$LOG_FILE" <<'EOF'
# Agent Lifecycle Change Log

| UTC Time | Action | Agent ID | Summary | Operator |
|---|---|---|---|---|
EOF
fi

printf "| %s | %s | %s | %s | %s |\n" "$TS" "$ACTION" "$AGENT_ID" "$SUMMARY" "$OPERATOR" >> "$LOG_FILE"

echo "logged"
