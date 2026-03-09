#!/usr/bin/env bash

set -euo pipefail

CONFIG_FILE="${HOME}/.claude/mac-notify.env"
LOG_FILE="${HOME}/.claude/mac-task-notify.log"

if [[ -f "$CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
fi

log() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$*" >>"$LOG_FILE"
}

emit_result() {
  printf '{"continue":true,"suppressOutput":true}\n'
}

json="$(cat)"

readarray -t META < <(
  python3 - <<'PY' "$json"
import json
import os
import sys

payload = json.loads(sys.argv[1] or "{}")
event = payload.get("hook_event_name", "")
cwd = payload.get("cwd", "")
reason = payload.get("reason", "")
task_id = payload.get("task_id", "")
task_kind = payload.get("task_kind", "")
task_description = (
    payload.get("task_description")
    or payload.get("description")
    or payload.get("title")
    or ""
)
assistant_message = (
    payload.get("last_assistant_message")
    or payload.get("assistant_message")
    or payload.get("result")
    or payload.get("summary")
    or ""
)

assistant_message = " ".join(str(assistant_message).split())
assistant_message = assistant_message[:180]
if event == "TaskCompleted":
    opener = "Claude has finished."
else:
    opener = "Claude has finished."

title = ""
message = opener

print(event)
print(title)
print(message)
PY
)

EVENT_NAME="${META[0]:-unknown}"
TITLE="${META[1]:-}"
MESSAGE="${META[2]:-Claude has finished.}"

if [[ "${NOTIFY_PRINT_MESSAGE:-0}" == "1" ]]; then
  printf 'TITLE: %s\nMESSAGE:\n%s\n' "$TITLE" "$MESSAGE" >&2
fi

notify_openclaw_whatsapp() {
  local target self_target channel

  target="${OPENCLAW_NOTIFY_TARGET:-}"
  self_target="${OPENCLAW_NOTIFY_SELF_TARGET:-}"
  channel="${OPENCLAW_NOTIFY_CHANNEL:-whatsapp}"

  if [[ -z "$target" ]]; then
    log "Skipping ${EVENT_NAME}: OPENCLAW_NOTIFY_TARGET is not configured"
    return 0
  fi

  if [[ "$channel" != "whatsapp" ]]; then
    log "Skipping ${EVENT_NAME}: OPENCLAW channel must stay whatsapp, got ${channel}"
    return 0
  fi

  if [[ -n "$self_target" && "$target" != "$self_target" ]]; then
    log "Skipping ${EVENT_NAME}: refusing to send to non-self WhatsApp target ${target}"
    return 0
  fi

  if ! openclaw message send \
    --channel "$channel" \
    --target "$target" \
    --message "${MESSAGE}" \
    --json >/dev/null 2>&1; then
    log "Failed ${EVENT_NAME} notification via OpenClaw channel"
  fi
}

MODE="${MAC_NOTIFY_MODE:-openclaw_whatsapp}"

case "$MODE" in
  off)
    ;;
  openclaw_whatsapp)
    notify_openclaw_whatsapp
    ;;
  *)
    log "Skipping ${EVENT_NAME}: unsupported MAC_NOTIFY_MODE=${MODE}"
    ;;
esac

emit_result
