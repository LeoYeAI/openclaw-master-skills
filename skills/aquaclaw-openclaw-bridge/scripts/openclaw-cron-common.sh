#!/usr/bin/env bash

set -euo pipefail

aquaclaw_default_repo() {
  echo "${AQUACLAW_REPO:-$HOME/.openclaw/workspace/gateway-hub}"
}

aquaclaw_default_interval() {
  echo "${AQUACLAW_PULSE_EVERY:-37m}"
}

aquaclaw_default_timezone() {
  if [[ -n "${AQUACLAW_TIMEZONE:-}" ]]; then
    echo "${AQUACLAW_TIMEZONE}"
    return 0
  fi
  aquaclaw_resolve_user_timezone
}

aquaclaw_default_quiet_hours() {
  echo "${AQUACLAW_QUIET_HOURS:-00:00-08:00}"
}

aquaclaw_default_job_name() {
  echo "${AQUACLAW_PULSE_JOB_NAME:-aquaclaw-pulse}"
}

aquaclaw_default_session() {
  echo "${AQUACLAW_PULSE_SESSION:-isolated}"
}

aquaclaw_default_thinking() {
  echo "${AQUACLAW_PULSE_THINKING:-low}"
}

aquaclaw_default_timeout_seconds() {
  echo "${AQUACLAW_PULSE_TIMEOUT_SECONDS:-120}"
}

aquaclaw_default_description() {
  echo "AquaClaw pulse tick template (disabled by default)"
}

aquaclaw_build_message() {
  local repo="$1"
  local timezone="$2"
  local quiet_hours="$3"

  cat <<EOF
Use \$aquaclaw-openclaw-bridge. Read TOOLS.md for the preferred AquaClaw wrappers on this machine. Run the Aqua pulse wrapper against ${repo} with a live pulse tick, using --timezone ${timezone} --quiet-hours ${quiet_hours} --format markdown. Report whether the runtime heartbeat was written, whether a scene was generated, and why the pulse chose that branch. Do not create, edit, enable, disable, or remove cron jobs from inside the job itself. If AquaClaw is unavailable, say so directly.
EOF
}

aquaclaw_print_command() {
  printf '%q ' "$@"
  printf '\n'
}

aquaclaw_print_cron_schema_mismatch_hint() {
  cat >&2 <<'EOF'

AquaClaw diagnosis:
- the heartbeat/pulse/diary installer is asking OpenClaw to create an isolated cron agent-turn job
- your local OpenClaw gateway rejected that cron payload schema before the Aqua script even ran
- this points to a local OpenClaw CLI / Gateway version mismatch or an older Gateway scheduler schema on that machine
- it is not an Aqua remote-hub failure

Recommended local checks on that machine:
- `openclaw --version`
- `openclaw gateway status`
- `openclaw doctor --fix`
- `openclaw update`
- `openclaw gateway restart`

If the Gateway service is older than the CLI, update/restart the Gateway so they match, then rerun the AquaClaw onboarding step.
If AquaClaw already tried a local `doctor --fix` + `gateway restart` pass and the same schema error still remains, the next likely fix is `openclaw update`.
EOF
}

aquaclaw_should_auto_repair_cron_schema_mismatch() {
  local enabled="${AQUACLAW_OPENCLAW_AUTO_REPAIR_ON_CRON_SCHEMA_MISMATCH:-1}"
  case "${enabled}" in
    0|false|FALSE|no|NO)
      return 1
      ;;
    *)
      return 0
      ;;
  esac
}

aquaclaw_is_cron_schema_mismatch_output() {
  local output="$1"
  [[ "$output" == *"invalid cron.add params"* || "$output" == *"invalid cron.update params"* ]]
}

aquaclaw_attempt_local_openclaw_cron_repair() {
  local doctor_output=""
  local doctor_status=0
  local restart_output=""
  local restart_status=0

  echo "AquaClaw: attempting one local OpenClaw repair pass (doctor --fix + gateway restart) before retrying cron install." >&2

  set +e
  doctor_output="$(openclaw doctor --fix --non-interactive --yes 2>&1)"
  doctor_status=$?
  set -e
  if [[ -n "$doctor_output" ]]; then
    printf '%s\n' "$doctor_output" >&2
  fi
  if [[ "$doctor_status" -ne 0 ]]; then
    echo "AquaClaw: local OpenClaw doctor repair failed." >&2
    return "$doctor_status"
  fi

  set +e
  restart_output="$(openclaw gateway restart 2>&1)"
  restart_status=$?
  set -e
  if [[ -n "$restart_output" ]]; then
    printf '%s\n' "$restart_output" >&2
  fi
  if [[ "$restart_status" -ne 0 ]]; then
    echo "AquaClaw: local OpenClaw gateway restart failed." >&2
    return "$restart_status"
  fi

  sleep 2
  echo "AquaClaw: local OpenClaw repair pass completed; retrying cron install once." >&2
  return 0
}

aquaclaw_run_cron_command() {
  local output=""
  local status=0
  local mismatch=0

  set +e
  output="$("$@" 2>&1)"
  status=$?
  set -e

  if [[ "$status" -ne 0 ]]; then
    if aquaclaw_is_cron_schema_mismatch_output "$output"; then
      mismatch=1
    fi

    if [[ "$mismatch" -eq 1 ]] && aquaclaw_should_auto_repair_cron_schema_mismatch; then
      if [[ -n "$output" ]]; then
        printf '%s\n' "$output" >&2
      fi
      if aquaclaw_attempt_local_openclaw_cron_repair; then
        set +e
        output="$("$@" 2>&1)"
        status=$?
        set -e
        if [[ "$status" -eq 0 ]]; then
          echo "AquaClaw: cron install succeeded after local OpenClaw repair." >&2
          if [[ -n "$output" ]]; then
            printf '%s\n' "$output"
          fi
          return 0
        fi
        if aquaclaw_is_cron_schema_mismatch_output "$output"; then
          mismatch=1
        else
          mismatch=0
        fi
      fi
    fi

    if [[ -n "$output" ]]; then
      printf '%s\n' "$output" >&2
    fi
    if [[ "$mismatch" -eq 1 ]]; then
      aquaclaw_print_cron_schema_mismatch_hint
    fi
    return "$status"
  fi

  if [[ -n "$output" ]]; then
    printf '%s\n' "$output"
  fi
}

aquaclaw_resolve_delivery_target_script() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  echo "${script_dir}/resolve-openclaw-delivery-target.mjs"
}

aquaclaw_resolve_user_timezone_script() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  echo "${script_dir}/resolve-openclaw-user-timezone.mjs"
}

aquaclaw_resolve_delivery_target_json() {
  node "$(aquaclaw_resolve_delivery_target_script)" --json
}

aquaclaw_resolve_delivery_target_field() {
  local field="$1"
  node "$(aquaclaw_resolve_delivery_target_script)" --field "${field}"
}

aquaclaw_resolve_user_timezone_json() {
  node "$(aquaclaw_resolve_user_timezone_script)" --json
}

aquaclaw_resolve_user_timezone_field() {
  local field="$1"
  node "$(aquaclaw_resolve_user_timezone_script)" --field "${field}"
}

aquaclaw_resolve_user_timezone() {
  aquaclaw_resolve_user_timezone_field timezone
}

aquaclaw_find_job_json() {
  local name="$1"
  local json
  local helper_script_dir
  json="$(openclaw cron list --json)"
  helper_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  NAME="$name" node "${helper_script_dir}/openclaw-cron-job-find.mjs" <<<"${json}"
}
