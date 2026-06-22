#!/usr/bin/env bash
set -euo pipefail

# Minimal curl helpers for Jules REST API (v1alpha).
# Requires: JULES_API_KEY env var.
#
# Examples:
#   ./scripts/jules_api.sh sources
#   ./scripts/jules_api.sh sessions --page-size 10
#   ./scripts/jules_api.sh new-session --source "sources/github/owner/repo" --title "My Task" --prompt "Do X" --branch main --auto-pr
#   ./scripts/jules_api.sh activities --session 31415926535897932384

BASE="https://jules.googleapis.com/v1alpha"

usage() {
  cat >&2 <<'EOF'
Usage:
  jules_api.sh sources
  jules_api.sh sessions [--page-size N]
  jules_api.sh activities --session <id> [--page-size N]
  jules_api.sh send-message --session <id> --prompt "..."
  jules_api.sh approve-plan --session <id>
  jules_api.sh new-session --source "sources/github/owner/repo" --title "..." --prompt "..." [--branch main] [--auto-pr] [--no-plan-approval]
EOF
  exit 2
}

if [[ "${JULES_API_KEY:-}" == "" ]]; then
  echo "Missing JULES_API_KEY" >&2
  exit 1
fi

cmd="${1:-}"; shift || true
[[ "$cmd" == "" ]] && usage

hdr=( -H "x-goog-api-key: $JULES_API_KEY" )

page_size=20
session_id=""
prompt=""
source=""
title=""
branch="main"
auto_pr=0
require_plan_approval=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --page-size) page_size="$2"; shift 2;;
    --session) session_id="$2"; shift 2;;
    --prompt) prompt="$2"; shift 2;;
    --source) source="$2"; shift 2;;
    --title) title="$2"; shift 2;;
    --branch) branch="$2"; shift 2;;
    --auto-pr) auto_pr=1; shift 1;;
    --require-plan-approval) require_plan_approval=1; shift 1;;
    --no-plan-approval) require_plan_approval=0; shift 1;;
    -h|--help) usage;;
    *) echo "Unknown arg: $1" >&2; usage;;
  esac
done

case "$cmd" in
  sources)
    curl -sS "${BASE}/sources" "${hdr[@]}"
    ;;
  sessions)
    curl -sS "${BASE}/sessions?pageSize=${page_size}" "${hdr[@]}"
    ;;
  activities)
    [[ "$session_id" == "" ]] && echo "Missing --session" >&2 && exit 2
    curl -sS "${BASE}/sessions/${session_id}/activities?pageSize=${page_size}" "${hdr[@]}"
    ;;
  send-message)
    [[ "$session_id" == "" ]] && echo "Missing --session" >&2 && exit 2
    [[ "$prompt" == "" ]] && echo "Missing --prompt" >&2 && exit 2
    curl -sS -X POST "${BASE}/sessions/${session_id}:sendMessage" \
      -H "Content-Type: application/json" \
      "${hdr[@]}" \
      -d "{\"prompt\": $(python3 - <<PY
import json
print(json.dumps('''$prompt'''))
PY
)}"
    ;;
  approve-plan)
    [[ "$session_id" == "" ]] && echo "Missing --session" >&2 && exit 2
    curl -sS -X POST "${BASE}/sessions/${session_id}:approvePlan" \
      -H "Content-Type: application/json" \
      "${hdr[@]}"
    ;;
  new-session)
    [[ "$source" == "" ]] && echo "Missing --source" >&2 && exit 2
    [[ "$title" == "" ]] && echo "Missing --title" >&2 && exit 2
    [[ "$prompt" == "" ]] && echo "Missing --prompt" >&2 && exit 2

    automation=""
    if [[ $auto_pr -eq 1 ]]; then
      automation=",\n  \"automationMode\": \"AUTO_CREATE_PR\""
    fi
    rpa="false"
    if [[ $require_plan_approval -eq 1 ]]; then
      rpa="true"
    fi

    curl -sS -X POST "${BASE}/sessions" \
      -H "Content-Type: application/json" \
      "${hdr[@]}" \
      -d "{\n  \"prompt\": $(python3 - <<PY
import json
print(json.dumps('''$prompt'''))
PY
),\n  \"title\": $(python3 - <<PY
import json
print(json.dumps('''$title'''))
PY
),\n  \"requirePlanApproval\": ${rpa},\n  \"sourceContext\": {\n    \"source\": $(python3 - <<PY
import json
print(json.dumps('''$source'''))
PY
),\n    \"githubRepoContext\": {\n      \"startingBranch\": $(python3 - <<PY
import json
print(json.dumps('''$branch'''))
PY
)\n    }\n  }${automation}\n}"
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    usage
    ;;
esac
