#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/aqua-hosted-pulse-service-common.sh"

platform="$(aquaclaw_hp_detect_platform || true)"
if [[ -z "${platform}" ]]; then
  echo "unsupported platform: $(uname -s)" >&2
  exit 1
fi

label="$(aquaclaw_hp_default_label)"
workspace_root="$(aquaclaw_hp_default_workspace_root)"
service_path="$(aquaclaw_hp_default_service_path)"
hosted_config="$(aquaclaw_hp_default_hosted_config)"
pulse_state_file="$(aquaclaw_hp_default_pulse_state_file)"
loop_state_file="$(aquaclaw_hp_default_loop_state_file)"
min_seconds="$(aquaclaw_hp_default_min_seconds)"
jitter_seconds="$(aquaclaw_hp_default_jitter_seconds)"
failure_min_seconds="$(aquaclaw_hp_default_failure_min_seconds)"
failure_jitter_seconds="$(aquaclaw_hp_default_failure_jitter_seconds)"
timeout_ms="$(aquaclaw_hp_default_timeout_ms)"
timezone="$(aquaclaw_hp_default_timezone)"
author_agent="$(aquaclaw_hp_default_author_agent)"
quiet_hours="$(aquaclaw_hp_default_quiet_hours)"
feed_limit="$(aquaclaw_hp_default_feed_limit)"
social_cooldown_minutes="$(aquaclaw_hp_default_social_cooldown_minutes)"
dm_cooldown_minutes="$(aquaclaw_hp_default_dm_cooldown_minutes)"
dm_target_cooldown_minutes="$(aquaclaw_hp_default_dm_target_cooldown_minutes)"
stdout_log="$(aquaclaw_hp_default_stdout_log)"
stderr_log="$(aquaclaw_hp_default_stderr_log)"
openclaw_bin="${OPENCLAW_BIN:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label)
      label="$2"
      shift 2
      ;;
    --workspace-root)
      workspace_root="$2"
      shift 2
      ;;
    --service-path)
      service_path="$2"
      shift 2
      ;;
    --hosted-config)
      hosted_config="$2"
      shift 2
      ;;
    --state-file)
      pulse_state_file="$2"
      shift 2
      ;;
    --loop-state-file)
      loop_state_file="$2"
      shift 2
      ;;
    --openclaw-bin)
      openclaw_bin="$2"
      shift 2
      ;;
    --author-agent)
      author_agent="$2"
      shift 2
      ;;
    --stdout-log)
      stdout_log="$2"
      shift 2
      ;;
    --stderr-log)
      stderr_log="$2"
      shift 2
      ;;
    -h|--help)
      cat <<'EOF'
Usage: show-aquaclaw-hosted-pulse-service.sh [options]

Options:
  --label <label>             Service label
  --workspace-root <dir>      OpenClaw workspace root
  --service-path <path-list>  PATH exposed to the service runtime
  --hosted-config <path>      Hosted Aqua config path override
  --state-file <path>         Hosted pulse state file override
  --loop-state-file <path>    Hosted pulse loop state file override
  --openclaw-bin <path>       Explicit openclaw binary for authoring
  --author-agent <mode>       Requested authoring lane: auto|community|main
  --stdout-log <path>         Service stdout log path
  --stderr-log <path>         Service stderr log path
EOF
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if resolved_openclaw_bin="$(aquaclaw_hp_resolve_openclaw_bin "${service_path}" "${openclaw_bin}" 2>/dev/null)"; then
  openclaw_bin="${resolved_openclaw_bin}"
fi

service_file="$(aquaclaw_hp_service_file "${platform}" "${label}")"
resolved_paths_json="$(
  aquaclaw_hp_resolve_paths_json "${workspace_root}" "${hosted_config}" "${pulse_state_file}" "${loop_state_file}"
)"
resolved_config_path="$(PATHS_JSON="${resolved_paths_json}" node -e 'const data = JSON.parse(process.env.PATHS_JSON); process.stdout.write(String(data.configPath ?? ""));')"
resolved_pulse_state_file="$(PATHS_JSON="${resolved_paths_json}" node -e 'const data = JSON.parse(process.env.PATHS_JSON); process.stdout.write(String(data.pulseStateFile ?? ""));')"
resolved_loop_state_file="$(PATHS_JSON="${resolved_paths_json}" node -e 'const data = JSON.parse(process.env.PATHS_JSON); process.stdout.write(String(data.loopStateFile ?? ""));')"
preflight_json="$(
  aquaclaw_hp_authoring_preflight_json "${workspace_root}" "${author_agent}" "${service_path}" "${openclaw_bin}"
)"

echo "Platform: ${platform}"
echo "Label: ${label}"
echo "Service file: ${service_file}"
echo "Workspace root: ${workspace_root}"
echo "Service PATH: ${service_path}"
echo "Requested author agent: ${author_agent}"
echo "Resolved OPENCLAW_BIN: ${openclaw_bin:-<auto-detect failed>}"
echo "Hosted config override: ${hosted_config:-<profile-aware default>}"
echo "Resolved hosted config: ${resolved_config_path}"
echo "Pulse state override: ${pulse_state_file:-<profile-aware default>}"
echo "Resolved pulse state: ${resolved_pulse_state_file}"
echo "Loop state override: ${loop_state_file:-<profile-aware default>}"
echo "Resolved loop state: ${resolved_loop_state_file}"
echo "Interval seconds: min=${min_seconds}, jitter=${jitter_seconds}"
echo "Failure retry seconds: min=${failure_min_seconds}, jitter=${failure_jitter_seconds}"
echo "Timeout ms: ${timeout_ms}"
echo "Fallback timezone: ${timezone}"
echo "Fallback quiet hours: ${quiet_hours:-<disabled>}"
echo "Feed limit: ${feed_limit}"
echo "Fallback social cooldown minutes: ${social_cooldown_minutes}"
echo "Fallback DM cooldown minutes: ${dm_cooldown_minutes}"
echo "Fallback DM target cooldown minutes: ${dm_target_cooldown_minutes}"
echo "Stdout log: ${stdout_log}"
echo "Stderr log: ${stderr_log}"
echo
echo "Authoring preflight:"
printf '%s\n' "${preflight_json}"

if [[ -n "${openclaw_bin}" ]]; then
  echo
  echo "OpenClaw agents:"
  env PATH="${service_path}" OPENCLAW_BIN="${openclaw_bin}" "${openclaw_bin}" agents list --json 2>&1 || true
fi

if [[ -f "${resolved_loop_state_file}" ]]; then
  echo
  echo "Loop state:"
  sed -n '1,220p' "${resolved_loop_state_file}"
else
  echo
  echo "Loop state file does not exist yet."
fi

if [[ ! -f "${service_file}" ]]; then
  echo
  echo "Service file does not exist yet."
  exit 0
fi

echo
case "${platform}" in
  darwin)
    launchctl print "gui/$(id -u)/${label}" 2>/dev/null || echo "Service is not currently loaded."
    ;;
  linux)
    systemctl --user status --no-pager --full "${label}.service" 2>/dev/null || echo "Service is not currently loaded."
    ;;
esac
