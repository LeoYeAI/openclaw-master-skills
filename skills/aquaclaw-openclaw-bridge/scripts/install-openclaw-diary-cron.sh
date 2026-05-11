#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/openclaw-diary-cron-common.sh"

apply=0
enable_after_create=0
replace_existing=0

skill_root="$(cd "${script_dir}/.." && pwd)"
cron_expr="$(aquaclaw_diary_default_cron)"
timezone="$(aquaclaw_diary_default_timezone)"
job_name="$(aquaclaw_diary_default_job_name)"
session_target="$(aquaclaw_diary_default_session)"
thinking_level="$(aquaclaw_diary_default_thinking)"
timeout_seconds="$(aquaclaw_diary_default_timeout_seconds)"
max_events="$(aquaclaw_diary_default_max_events)"
delivery_channel=""
delivery_session_key=""
target_to=""
account_id=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      apply=1
      shift
      ;;
    --enable)
      enable_after_create=1
      shift
      ;;
    --replace)
      replace_existing=1
      shift
      ;;
    --skill-root)
      skill_root="$2"
      shift 2
      ;;
    --cron)
      cron_expr="$2"
      shift 2
      ;;
    --tz|--timezone)
      timezone="$2"
      shift 2
      ;;
    --name)
      job_name="$2"
      shift 2
      ;;
    --session)
      session_target="$2"
      shift 2
      ;;
    --thinking)
      thinking_level="$2"
      shift 2
      ;;
    --timeout-seconds)
      timeout_seconds="$2"
      shift 2
      ;;
    --max-events)
      max_events="$2"
      shift 2
      ;;
    --channel)
      delivery_channel="$2"
      shift 2
      ;;
    --to)
      target_to="$2"
      shift 2
      ;;
    --account)
      account_id="$2"
      shift 2
      ;;
    --session-key)
      delivery_session_key="$2"
      shift 2
      ;;
    -h|--help)
      cat <<'EOF'
Usage: install-openclaw-diary-cron.sh [options]

Options:
  --apply                 Actually create or update the cron job
  --enable                Leave the job enabled after install/update
  --replace               Update an existing job with the same name instead of failing
  --skill-root <path>     AquaClaw skill repo path
  --cron <expr>           Cron expression (default: 0 22 * * *)
  --tz <iana>             Timezone for cron expression
  --name <name>           Cron job name
  --session <target>      OpenClaw cron session target
  --thinking <level>      OpenClaw cron thinking level
  --timeout-seconds <n>   OpenClaw cron timeout
  --max-events <n>        Max diary notable events passed to digest
  --channel <name>        Delivery channel override
  --to <dest>             Delivery target override
  --account <id>          Delivery account id override
  --session-key <key>     Delivery session key override
EOF
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 1
      ;;
  esac
done

resolved_channel="$(aquaclaw_resolve_delivery_target_field channel 2>/dev/null || true)"
resolved_session_key="$(aquaclaw_resolve_delivery_target_field session-key 2>/dev/null || true)"
resolved_to="$(aquaclaw_resolve_delivery_target_field to 2>/dev/null || true)"
resolved_account_id="$(aquaclaw_resolve_delivery_target_field account-id 2>/dev/null || true)"

if [[ -z "${delivery_session_key}" ]]; then
  delivery_session_key="${resolved_session_key}"
fi

if [[ -z "${delivery_channel}" ]]; then
  if [[ -n "${resolved_channel}" ]]; then
    delivery_channel="${resolved_channel}"
  elif [[ -n "${delivery_session_key}" ]]; then
    delivery_channel="last"
  fi
fi

if [[ -z "${target_to}" ]]; then
  target_to="${resolved_to}"
fi

if [[ -z "${account_id}" ]]; then
  account_id="${resolved_account_id}"
fi

if [[ -z "${delivery_channel}" ]]; then
  echo "could not resolve a delivery channel from OpenClaw direct sessions or Telegram allowFrom fallback" >&2
  exit 1
fi

if [[ -z "${delivery_session_key}" && -z "${target_to}" ]]; then
  echo "could not resolve a delivery destination from OpenClaw direct sessions or Telegram allowFrom fallback" >&2
  exit 1
fi

message="$(aquaclaw_diary_build_message "$skill_root" "$timezone" "$max_events")"
description="$(aquaclaw_diary_default_description)"

delivery_args=(--announce --channel "$delivery_channel")
if [[ -n "${delivery_session_key}" ]]; then
  delivery_args+=(--session-key "$delivery_session_key")
fi
if [[ -n "${target_to}" ]]; then
  delivery_args+=(--to "$target_to")
fi
if [[ -n "${account_id}" ]]; then
  delivery_args+=(--account "$account_id")
fi

if existing_json="$(aquaclaw_find_job_json "$job_name" 2>/dev/null)"; then
  job_id="$(JOB_JSON="$existing_json" node -e 'const job = JSON.parse(process.env.JOB_JSON); process.stdout.write(String(job.id ?? ""));')"
  if [[ -z "$job_id" ]]; then
    echo "existing job named ${job_name} has no usable id" >&2
    exit 1
  fi

  edit_cmd=(
    openclaw cron edit "$job_id"
    --cron "$cron_expr"
    --tz "$timezone"
    --session "$session_target"
    --wake next-heartbeat
    --light-context
    --thinking "$thinking_level"
    --timeout-seconds "$timeout_seconds"
    --description "$description"
    --message "$message"
    "${delivery_args[@]}"
  )

  if [[ "$enable_after_create" -eq 1 ]]; then
    edit_cmd+=(--enable)
  else
    edit_cmd+=(--disable)
  fi

  if [[ "$replace_existing" -ne 1 ]]; then
    echo "job already exists:" >&2
    echo "$existing_json" >&2
    echo "rerun with --replace to patch it, or inspect it with show-openclaw-diary-cron.sh" >&2
    exit 1
  fi

  if [[ "$apply" -eq 1 ]]; then
    aquaclaw_run_cron_command "${edit_cmd[@]}"
  else
    aquaclaw_print_command "${edit_cmd[@]}"
  fi

  exit 0
fi

add_cmd=(
  openclaw cron add
  --name "$job_name"
  --cron "$cron_expr"
  --tz "$timezone"
  --session "$session_target"
  --wake next-heartbeat
  --light-context
  --thinking "$thinking_level"
  --timeout-seconds "$timeout_seconds"
  --description "$description"
  --message "$message"
  "${delivery_args[@]}"
)

if [[ "$enable_after_create" -ne 1 ]]; then
  add_cmd+=(--disabled)
fi

if [[ "$apply" -eq 1 ]]; then
  aquaclaw_run_cron_command "${add_cmd[@]}"
else
  aquaclaw_print_command "${add_cmd[@]}"
fi
