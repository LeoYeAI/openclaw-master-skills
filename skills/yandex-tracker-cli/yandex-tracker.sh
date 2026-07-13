#!/usr/bin/env bash
set -e -o pipefail

# Yandex Tracker CLI
# Используйте: yandex-tracker <command> [args]
# Файл: yandex-tracker.sh (можно скопировать/переименовать в yandex-tracker)

# Приоритет 1: переменные окружения TOKEN и ORG_ID
# Приоритет 2: файл ~/.yandex-tracker-env (читается как key=value, без выполнения кода)

if [[ -z "${TOKEN}" || -z "${ORG_ID}" ]]; then
  CONFIG="${HOME}/.yandex-tracker-env"
  if [[ ! -f "$CONFIG" ]]; then
    echo "Error: Neither TOKEN/ORG_ID env vars nor config file $CONFIG found" >&2
    exit 1
  fi
  # Safe parse: only TOKEN and ORG_ID are read from KEY=value lines (no shell execution)
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" ]] && continue
    if [[ "$line" =~ ^(TOKEN|ORG_ID)=(.+)$ ]]; then
      key="${BASH_REMATCH[1]}"
      value="${BASH_REMATCH[2]}"
      if [[ "$value" =~ ^\'(.*)\'$ ]]; then value="${BASH_REMATCH[1]}"; fi
      if [[ "$value" =~ ^\"(.*)\"$ ]]; then value="${BASH_REMATCH[1]}"; fi
      export "$key=$value"
    fi
  done < "$CONFIG"
fi

# Проверка, что TOKEN и ORG_ID определены
if [[ -z "$TOKEN" || -z "$ORG_ID" ]]; then
  echo "Error: TOKEN and ORG_ID must be set (via env or ~/.yandex-tracker-env)" >&2
  exit 1
fi

BASE="https://api.tracker.yandex.net/v2"
BASE_V3="https://api.tracker.yandex.net/v3"
AUTH="Authorization: OAuth $TOKEN"
ORG="X-Org-Id: $ORG_ID"

# ---- First-run: ask user for attachments directory (only when interactive and not yet set) ----
PREF_FILE="${HOME}/.yandex-tracker-attachments-dir"
DEFAULT_ATTACHMENTS_DIR="${HOME}/Downloads/YandexTrackerCLI"

ensure_attachment_dir_configured() {
  [[ -n "${YANDEX_TRACKER_ATTACHMENTS_DIR}" ]] && return 0
  if [[ -f "$PREF_FILE" && -r "$PREF_FILE" ]]; then
    read -r YANDEX_TRACKER_ATTACHMENTS_DIR < "$PREF_FILE" || true
    [[ -n "$YANDEX_TRACKER_ATTACHMENTS_DIR" ]] && export YANDEX_TRACKER_ATTACHMENTS_DIR
    return 0
  fi
  if [[ ! -t 0 ]]; then
    return 0
  fi
  echo "First run: choose folder for attachments (download/upload)."
  echo "  1) Default: $DEFAULT_ATTACHMENTS_DIR"
  echo "  2) Enter your own path"
  printf "Use default? [Y/n]: "
  read -r reply
  reply="${reply#"${reply%%[![:space:]]*}"}"
  reply="${reply%"${reply##*[![:space:]]}"}"
  if [[ -z "$reply" || "$reply" == [Yy]* ]]; then
    YANDEX_TRACKER_ATTACHMENTS_DIR="$DEFAULT_ATTACHMENTS_DIR"
  else
    printf "Enter path: "
    read -r YANDEX_TRACKER_ATTACHMENTS_DIR
    YANDEX_TRACKER_ATTACHMENTS_DIR="${YANDEX_TRACKER_ATTACHMENTS_DIR#"${YANDEX_TRACKER_ATTACHMENTS_DIR%%[![:space:]]*}"}"
    YANDEX_TRACKER_ATTACHMENTS_DIR="${YANDEX_TRACKER_ATTACHMENTS_DIR%"${YANDEX_TRACKER_ATTACHMENTS_DIR##*[![:space:]]}"}"
    if [[ -z "$YANDEX_TRACKER_ATTACHMENTS_DIR" ]]; then
      YANDEX_TRACKER_ATTACHMENTS_DIR="$DEFAULT_ATTACHMENTS_DIR"
    fi
  fi
  [[ "$YANDEX_TRACKER_ATTACHMENTS_DIR" == ~* ]] && YANDEX_TRACKER_ATTACHMENTS_DIR="${HOME}${YANDEX_TRACKER_ATTACHMENTS_DIR:1}"
  mkdir -p "$YANDEX_TRACKER_ATTACHMENTS_DIR"
  printf '%s\n' "$YANDEX_TRACKER_ATTACHMENTS_DIR" > "$PREF_FILE"
  export YANDEX_TRACKER_ATTACHMENTS_DIR
}

# ---- Attachment path security: resolve to absolute and check under allowed base ----
_resolve_absolute() {
  local path="$1"
  [[ -z "$path" ]] && return 1
  [[ "$path" == ~* ]] && path="${HOME}${path:1}"
  if [[ "$path" != /* ]]; then
    [[ -z "$PWD" ]] && return 1
    path="$PWD/$path"
  fi
  local result="/"
  local part
  while [[ -n "$path" ]]; do
    path="${path#/}"
    part="${path%%/*}"
    path="${path#$part}"
    path="${path#/}"
    [[ -z "$part" || "$part" == . ]] && continue
    if [[ "$part" == .. ]]; then
      result=$(dirname "$result")
      continue
    fi
    result="${result%/}/$part"
  done
  [[ -z "$result" ]] && result="/"
  echo "$result"
}

_get_attachment_base() {
  if [[ -n "${YANDEX_TRACKER_ATTACHMENTS_DIR}" ]]; then
    local expanded="${YANDEX_TRACKER_ATTACHMENTS_DIR}"
    [[ "$expanded" == ~* ]] && expanded="${HOME}${expanded:1}"
    if [[ "$expanded" != /* ]]; then
      expanded="$PWD/$expanded"
    fi
    _resolve_absolute "$expanded"
  else
    _resolve_absolute "$PWD"
  fi
}


_path_under_base() {
  local resolved="$1"
  local base="$2"
  [[ -z "$resolved" || -z "$base" ]] && return 1
  [[ "$resolved" == "$base" ]] && return 0
  [[ "$resolved" == "$base/"* ]] && return 0
  return 1
}

_ensure_attachment_path_allowed() {
  local kind="$1"  # "download" or "upload"
  local path="$2"
  local resolved
  resolved=$(_resolve_absolute "$path") || { echo "Error: invalid path: $path" >&2; return 1; }
  local base
  base=$(_get_attachment_base) || { echo "Error: could not determine allowed attachment directory" >&2; return 1; }
  if ! _path_under_base "$resolved" "$base"; then
    echo "Error: attachment path must be under the allowed directory (current directory or YANDEX_TRACKER_ATTACHMENTS_DIR)." >&2
    return 1
  fi
  return 0
}

urlencode() {
  local s="${1:-}"
  jq -nr --arg s "$s" '$s|@uri'
}

queues() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/queues" \
    | jq -r '.[] | "\(.key)\t\(.name)"'
}

queue_get() {
  local key="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/queues/$(urlencode "$key")"
}

queue_fields() {
  local key="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/queues/$(urlencode "$key")/fields"
}

issue_get() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$id")"
}

issue_create() {
  local queue="$1"
  local summary="$2"
  local extra
  extra=$(cat)
  if [[ -z "$extra" ]]; then
    body="{\"queue\":\"$queue\",\"summary\":\"$summary\",\"tags\":[\"yandex-tracker-cli\"]}"
  else
    # Merge extra JSON fields into base object using jq, and auto-add tag if not present
    base="{\"queue\":\"$queue\",\"summary\":\"$summary\"}"
    body=$(echo "$base" | jq --argjson extra "$extra" '
      . + $extra |
      .tags = ((.tags // [] | map(tostring)) + ["yandex-tracker-cli"] | unique)
    ')
  fi
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$body" "$BASE/issues"
}

issue_update() {
  local id="$1"
  local payload
  payload=$(cat)
  # Auto-add tag yandex-tracker-cli if not present
  payload=$(echo "$payload" | jq '
    .tags = ((.tags // [] | map(tostring)) + ["yandex-tracker-cli"] | unique)
  ')
  curl -sS -X PATCH -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$payload" "$BASE/issues/$(urlencode "$id")"
}

issue_delete() {
  local id="$1"
  curl -sS -X DELETE -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$id")"
}

issue_comment() {
  local id="$1"
  local text="$2"
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "{\"text\":\"$text\"}" "$BASE/issues/$(urlencode "$id")/comments"
}

issue_transitions() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$id")/transitions"
}

issue_transition() {
  local id="$1"
  local transition="$2"
  # Use V3 endpoint with X-Org-ID header (360) or X-Cloud-Org-ID (Cloud)
  curl -sS -X POST -H "$AUTH" -H "X-Org-ID: $ORG_ID" -H "Content-Type: application/json" \
    -d "{}" "$BASE_V3/issues/$(urlencode "$id")/transitions/$(urlencode "$transition")/_execute"
}

issue_close() {
  local id="$1"
  local resolution="$2"
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "{\"resolution\":\"$resolution\"}" "$BASE/issues/$(urlencode "$id")/_close"
}

issue_worklog() {
  local id="$1"
  local duration="$2"
  local comment="${3:-}"
  local body="{\"duration\":\"$duration\"}"
  if [[ -n "$comment" ]]; then
    body="{\"duration\":\"$duration\",\"comment\":\"$comment\"}"
  fi
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$body" "$BASE/issues/$(urlencode "$id")/_worklog"
}

# ---- NEW: Attachments ----
issue_attachments() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$id")/attachments"
}

attachment_download() {
  ensure_attachment_dir_configured
  local issue_id="$1"
  local file_id="$2"
  local output="${3:-/dev/stdout}"
  if [[ -n "$output" && "$output" != "/dev/stdout" ]]; then
    _ensure_attachment_path_allowed "download" "$output" || exit 1
  fi
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$issue_id")/attachments/$(urlencode "$file_id")" -o "$output"
}

attachment_upload() {
  ensure_attachment_dir_configured
  local issue_id="$1"
  local filepath="$2"
  local comment="${3:-}"
  _ensure_attachment_path_allowed "upload" "$filepath" || exit 1
  [[ -f "$filepath" ]] || { echo "Error: file does not exist or is not a regular file: $filepath" >&2; exit 1; }
  [[ -r "$filepath" ]] || { echo "Error: file is not readable: $filepath" >&2; exit 1; }
  local file_name
  file_name=$(basename "$filepath")
  local form_data
  if [[ -n "$comment" ]]; then
    form_data="comment=$comment"
  else
    form_data=""
  fi
  curl -sS -X POST -H "$AUTH" -H "$ORG" \
    -F "file=@$filepath;filename=$file_name" \
    ${form_data:+-F "$form_data"} \
    "$BASE/issues/$(urlencode "$issue_id")/attachments"
}

# ---- NEW: Comments edit/delete ----
issue_comment_edit() {
  local issue_id="$1"
  local comment_id="$2"
  local new_text="$3"
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "{\"text\":\"$new_text\"}" "$BASE/issues/$(urlencode "$issue_id")/comments/$(urlencode "$comment_id")"
}

issue_comment_delete() {
  local issue_id="$1"
  local comment_id="$2"
  curl -sS -X DELETE -H "$AUTH" -H "$ORG" "$BASE/issues/$(urlencode "$issue_id")/comments/$(urlencode "$comment_id")"
}

# ---- NEW: Sprints ----
sprints_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/sprints"
}

sprint_get() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/sprints/$(urlencode "$id")"
}

sprint_issues() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/sprints/$(urlencode "$id")/issues"
}

# ---- NEW: Search issues via YQL (V3) ----
# Usage: echo '{"query":"assignee = 1130000064009131","perPage":100}' | yandex-tracker issues-search
# Note: perPage and page are query parameters, not in JSON body.
issues_search() {
  # Read JSON payload from stdin (may contain query, filter, filterId, expand, etc.)
  local payload
  payload=$(cat)
  # We'll pass perPage/page via URL query string if present in payload (pop them)
  local perPage=""
  local page=""
  # Extract perPage and page from payload using jq (if present)
  if command -v jq >/dev/null; then
    local pp=$(echo "$payload" | jq -r '.perPage // empty')
    local pg=$(echo "$payload" | jq -r '.page // empty')
    if [ -n "$pp" ]; then perPage="?perPage=$pp"; elif [ -n "$pg" ]; then perPage="?perPage=50"; fi
    # If both present, build query
    if [ -n "$pp" ] && [ -n "$pg" ]; then
      perPage="?perPage=$pp&page=$pg"
    elif [ -z "$pp" ] && [ -n "$pg" ]; then
      perPage="?perPage=50&page=$pg"
    fi
  fi
  curl -sS -X POST -H "$AUTH" -H "X-Org-ID: $ORG_ID" -H "Content-Type: application/json" \
    -d "$payload" "$BASE_V3/issues/_search${perPage}"
}

# ---- NEW: Export issues report (V3) ----
issues_export() {
  # Create an export report (XLSX/CSV/XML) of issues.
  # Expect report definition as JSON via stdin.
  # Example:
  #   {"fields":{"summary":"My report","parameters":{"type":"issueFilterExport","format":"xlsx","filter":{"query":"assignee = 1130000064009131"},"fields":["key","summary","status","priority","deadline"]}}}
  local payload
  payload=$(cat)
  curl -sS -X POST -H "$AUTH" -H "X-Org-ID: $ORG_ID" -H "Content-Type: application/json" \
    -d "$payload" "$BASE_V3/entities/report/"
}

# ---- NEW: Projects ----
projects_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/projects"
}

project_get() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/projects/$(urlencode "$id")"
}

project_issues() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/projects/$(urlencode "$id")/issues"
}

# ---- NEW: Reference data (optional but useful) ----
users_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/users"
}

statuses_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/statuses"
}

resolutions_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/resolutions"
}

issue_types_list() {
  curl -sS -H "$AUTH" -H "$ORG" "$BASE/issue-types"
}

# ---- Checklist (API v3 only: /v3/issues/<id>/checklistItems) ----
issue_checklist() {
  local id="$1"
  curl -sS -H "$AUTH" -H "$ORG" "$BASE_V3/issues/$(urlencode "$id")/checklistItems"
}

checklist_add() {
  local issue_id="$1"
  local text="$2"
  # API v3: POST body uses "text", not "content"
  curl -sS -X POST -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$(jq -n --arg t "$text" '{text: $t}')" "$BASE_V3/issues/$(urlencode "$issue_id")/checklistItems"
}

checklist_complete() {
  local issue_id="$1"
  local item_id="$2"
  # API v3: no /complete endpoint; use PATCH with {"text":"...","checked":true}. We need item text — GET first or pass as 3rd arg.
  local text
  text=$(curl -sS -H "$AUTH" -H "$ORG" "$BASE_V3/issues/$(urlencode "$issue_id")/checklistItems" \
    | jq -r --arg id "$item_id" '.[] | select(.id == $id) | .text // empty')
  if [[ -z "$text" ]]; then
    text="(item)"
  fi
  curl -sS -X PATCH -H "$AUTH" -H "$ORG" -H "Content-Type: application/json" \
    -d "$(jq -n --arg t "$text" --argjson ch true '{text: $t, checked: $ch}')" \
    "$BASE_V3/issues/$(urlencode "$issue_id")/checklistItems/$(urlencode "$item_id")"
}

checklist_delete() {
  local issue_id="$1"
  local item_id="$2"
  curl -sS -X DELETE -H "$AUTH" -H "$ORG" "$BASE_V3/issues/$(urlencode "$issue_id")/checklistItems/$(urlencode "$item_id")"
}

case "$1" in
  queues) queues ;;
  queue-get) queue_get "$2" ;;
  queue-fields) queue_fields "$2" ;;
  issue-get) issue_get "$2" ;;
  issue-create) shift; queue="$1"; summary="$2"; issue_create "$queue" "$summary" ;;
  issue-update) issue_update "$2" ;;
  issue-delete) issue_delete "$2" ;;
  issue-comment) shift; issue_comment "$1" "$2" ;;
  issue-comment-edit) shift; issue_comment_edit "$1" "$2" "$3" ;;
  issue-comment-delete) shift; issue_comment_delete "$1" "$2" ;;
  issue-transitions) issue_transitions "$2" ;;
  issue-transition) shift; issue_transition "$1" "$2" ;;
  issue-close) shift; issue_close "$1" "$2" ;;
  issue-worklog) shift; issue_worklog "$1" "$2" "$3" ;;
  issue-attachments) issue_attachments "$2" ;;
  attachment-download) shift; attachment_download "$1" "$2" "$3" ;;
  attachment-upload) shift; attachment_upload "$1" "$2" "$3" ;;
  issues-search) issues_search ;;
  issues-export) issues_export ;;
  projects-list) projects_list ;;
  project-get) project_get "$2" ;;
  project-issues) project_issues "$2" ;;
  sprints-list) sprints_list ;;
  sprint-get) sprint_get "$2" ;;
  sprint-issues) sprint_issues "$2" ;;
  users-list) users_list ;;
  statuses-list) statuses_list ;;
  resolutions-list) resolutions_list ;;
  issue-types-list) issue_types_list ;;
  issue-checklist) issue_checklist "$2" ;;
  checklist-add) shift; checklist_add "$1" "$2" ;;
  checklist-complete) shift; checklist_complete "$1" "$2" ;;
  checklist-delete) shift; checklist_delete "$1" "$2" ;;
  *) echo "Usage: $0 {queues|queue-get <key>|queue-fields <key>|issue-get <id>|issue-create <queue> <summary>|issue-update <id>|issue-delete <id>|issue-comment <id> <text>|issue-comment-edit <id> <comment-id> <new-text>|issue-comment-delete <id> <comment-id>|issue-transitions <id>|issue-transition <id> <transition-id>|issue-close <id> <resolution>|issue-worklog <id> <duration> [comment]|issue-attachments <id>|attachment-download <issue-id> <fileId> [output]|attachment-upload <issue-id> <filepath> [comment]|issues-search|issues-export|projects-list|project-get <id>|project-issues <id>|sprints-list|sprint-get <id>|sprint-issues <id>|users-list|statuses-list|resolutions-list|issue-types-list|issue-checklist <id>|checklist-add <issue-id> <text>|checklist-complete <issue-id> <item-id>|checklist-delete <issue-id> <item-id>}" >&2; exit 1 ;;
esac
