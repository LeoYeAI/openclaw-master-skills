#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/aqua-runtime-heartbeat-service-common.sh"

platform="$(aquaclaw_hb_detect_platform || true)"
if [[ -z "${platform}" ]]; then
  echo "unsupported platform: $(uname -s)" >&2
  exit 1
fi

label="$(aquaclaw_hb_default_label)"
workspace_root="$(aquaclaw_hb_default_workspace_root)"
mode="$(aquaclaw_hb_default_mode)"
hosted_config="$(aquaclaw_hb_default_hosted_config "${workspace_root}")"
state_file="$(aquaclaw_hb_default_state_file "${workspace_root}")"
stdout_log="$(aquaclaw_hb_default_stdout_log)"
stderr_log="$(aquaclaw_hb_default_stderr_log)"
hosted_config_explicit=0
state_file_explicit=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label)
      label="$2"
      shift 2
      ;;
    --workspace-root)
      workspace_root="$2"
      if [[ "${hosted_config_explicit}" -ne 1 ]]; then
        hosted_config="$(aquaclaw_hb_default_hosted_config "${workspace_root}")"
      fi
      if [[ "${state_file_explicit}" -ne 1 ]]; then
        state_file="$(aquaclaw_hb_default_state_file "${workspace_root}")"
      fi
      shift 2
      ;;
    --mode)
      mode="$2"
      shift 2
      ;;
    --hosted-config)
      hosted_config="$2"
      hosted_config_explicit=1
      shift 2
      ;;
    --state-file)
      state_file="$2"
      state_file_explicit=1
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
Usage: show-aquaclaw-runtime-heartbeat-service.sh [options]

Options:
  --label <label>         Service label
  --workspace-root <dir>  OpenClaw workspace root
  --mode <mode>           auto|local|hosted
  --hosted-config <path>  Hosted Aqua config path override
  --state-file <path>     Heartbeat state file path
  --stdout-log <path>     Service stdout log path
  --stderr-log <path>     Service stderr log path
EOF
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 1
      ;;
  esac
done

service_file="$(aquaclaw_hb_service_file "${platform}" "${label}")"

echo "Platform: ${platform}"
echo "Label: ${label}"
echo "Mode: ${mode}"
echo "Service file: ${service_file}"
echo "Hosted config: ${hosted_config}"
echo "State file: ${state_file}"
echo "Stdout log: ${stdout_log}"
echo "Stderr log: ${stderr_log}"

if [[ ! -f "${service_file}" ]]; then
  echo "Service file does not exist yet."
  exit 0
fi

case "${platform}" in
  darwin)
    launchctl print "gui/$(id -u)/${label}" 2>/dev/null || echo "Service is not currently loaded."
    ;;
  linux)
    systemctl --user status --no-pager --full "${label}.service" 2>/dev/null || echo "Service is not currently loaded."
    ;;
esac
