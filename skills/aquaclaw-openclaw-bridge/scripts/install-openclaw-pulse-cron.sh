#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/openclaw-cron-common.sh"

apply=0
enable_after_create=0
replace_existing=0

repo="$(aquaclaw_default_repo)"
interval="$(aquaclaw_default_interval)"
timezone="$(aquaclaw_default_timezone)"
quiet_hours="$(aquaclaw_default_quiet_hours)"
job_name="$(aquaclaw_default_job_name)"
session_target="$(aquaclaw_default_session)"
thinking_level="$(aquaclaw_default_thinking)"
timeout_seconds="$(aquaclaw_default_timeout_seconds)"

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
    --repo)
      repo="$2"
      shift 2
      ;;
    --every)
      interval="$2"
      shift 2
      ;;
    --timezone)
      timezone="$2"
      shift 2
      ;;
    --quiet-hours)
      quiet_hours="$2"
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
    -h|--help)
      cat <<'EOF'
Usage: install-openclaw-pulse-cron.sh [options]

Options:
  --apply                 Actually create or update the cron job
  --enable                Leave the job enabled after install/update
  --replace               Update an existing job with the same name instead of failing
  --repo <path>           AquaClaw repo path
  --every <duration>      Cron interval, for example 37m
  --timezone <iana>       Timezone passed to aqua-pulse
  --quiet-hours <range>   Quiet hours passed to aqua-pulse, for example 00:00-08:00
  --name <name>           Cron job name
  --session <target>      OpenClaw cron session target
  --thinking <level>      OpenClaw cron thinking level
  --timeout-seconds <n>   OpenClaw cron timeout
EOF
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 1
      ;;
  esac
done

message="$(aquaclaw_build_message "$repo" "$timezone" "$quiet_hours")"
description="$(aquaclaw_default_description)"

if existing_json="$(aquaclaw_find_job_json "$job_name" 2>/dev/null)"; then
  job_id="$(JOB_JSON="$existing_json" node -e 'const job = JSON.parse(process.env.JOB_JSON); process.stdout.write(String(job.id ?? ""));')"
  if [[ -z "$job_id" ]]; then
    echo "existing job named ${job_name} has no usable id" >&2
    exit 1
  fi

  edit_cmd=(
    openclaw cron edit "$job_id"
    --every "$interval"
    --session "$session_target"
    --wake next-heartbeat
    --light-context
    --thinking "$thinking_level"
    --timeout-seconds "$timeout_seconds"
    --description "$description"
    --message "$message"
  )

  if [[ "$enable_after_create" -eq 1 ]]; then
    edit_cmd+=(--enable)
  else
    edit_cmd+=(--disable)
  fi

  if [[ "$replace_existing" -ne 1 ]]; then
    echo "job already exists:" >&2
    echo "$existing_json" >&2
    echo "rerun with --replace to patch it, or inspect it with show-openclaw-pulse-cron.sh" >&2
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
  --every "$interval"
  --session "$session_target"
  --wake next-heartbeat
  --light-context
  --thinking "$thinking_level"
  --timeout-seconds "$timeout_seconds"
  --description "$description"
  --message "$message"
)

if [[ "$enable_after_create" -ne 1 ]]; then
  add_cmd+=(--disabled)
fi

if [[ "$apply" -eq 1 ]]; then
  aquaclaw_run_cron_command "${add_cmd[@]}"
else
  aquaclaw_print_command "${add_cmd[@]}"
fi
