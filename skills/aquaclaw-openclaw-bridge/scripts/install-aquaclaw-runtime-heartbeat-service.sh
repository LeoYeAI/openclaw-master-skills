#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/aqua-runtime-heartbeat-service-common.sh"

apply=0
replace_existing=0
hosted_config_explicit=0
state_file_explicit=0

platform="$(aquaclaw_hb_detect_platform || true)"
if [[ -z "${platform}" ]]; then
  echo "unsupported platform: $(uname -s). This installer supports macOS launchd and Linux systemd user services." >&2
  exit 1
fi

label="$(aquaclaw_hb_default_label)"
workspace_root="$(aquaclaw_hb_default_workspace_root)"
hub_url="$(aquaclaw_hb_default_hub_url)"
mode="$(aquaclaw_hb_default_mode)"
hosted_config="$(aquaclaw_hb_default_hosted_config "${workspace_root}")"
min_seconds="$(aquaclaw_hb_default_min_seconds)"
jitter_seconds="$(aquaclaw_hb_default_jitter_seconds)"
timeout_ms="$(aquaclaw_hb_default_timeout_ms)"
state_file="$(aquaclaw_hb_default_state_file "${workspace_root}")"
stdout_log="$(aquaclaw_hb_default_stdout_log)"
stderr_log="$(aquaclaw_hb_default_stderr_log)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      apply=1
      shift
      ;;
    --replace)
      replace_existing=1
      shift
      ;;
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
    --hub-url)
      hub_url="$2"
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
    --min-seconds)
      min_seconds="$2"
      shift 2
      ;;
    --jitter-seconds)
      jitter_seconds="$2"
      shift 2
      ;;
    --timeout-ms)
      timeout_ms="$2"
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
Usage: install-aquaclaw-runtime-heartbeat-service.sh [options]

Options:
  --apply                 Actually write and start the service
  --replace               Overwrite an existing service file
  --label <label>         Service label
  --workspace-root <dir>  OpenClaw workspace root
  --hub-url <url>         AquaClaw hub base URL
  --mode <mode>           auto|local|hosted
  --hosted-config <path>  Hosted Aqua config path override
  --min-seconds <n>       Base heartbeat interval in seconds
  --jitter-seconds <n>    Extra random interval in seconds
  --timeout-ms <n>        Request timeout in milliseconds
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
node_bin="$(aquaclaw_hb_node_bin)"
script_path="$(aquaclaw_hb_script_path)"
rendered="$(
  aquaclaw_hb_render_file \
    "${platform}" \
    "${label}" \
    "${workspace_root}" \
    "${node_bin}" \
    "${script_path}" \
    "${hub_url}" \
    "${mode}" \
    "${hosted_config}" \
    "${min_seconds}" \
    "${jitter_seconds}" \
    "${timeout_ms}" \
    "${state_file}" \
    "${stdout_log}" \
    "${stderr_log}"
)"

if [[ -f "${service_file}" && "${replace_existing}" -ne 1 ]]; then
  echo "service file already exists: ${service_file}" >&2
  echo "rerun with --replace to overwrite it" >&2
  exit 1
fi

if [[ "${apply}" -ne 1 ]]; then
  echo "# Preview: ${service_file}"
  printf '%s\n' "${rendered}"
  exit 0
fi

mkdir -p "$(dirname "${service_file}")"
mkdir -p "$(dirname "${state_file}")"
mkdir -p "$(dirname "${stdout_log}")"
mkdir -p "$(dirname "${stderr_log}")"
printf '%s\n' "${rendered}" > "${service_file}"

case "${platform}" in
  darwin)
    uid="$(id -u)"
    launchctl enable "gui/${uid}/${label}" >/dev/null 2>&1 || true
    launchctl bootout "gui/${uid}" "${service_file}" >/dev/null 2>&1 || true
    launchctl bootstrap "gui/${uid}" "${service_file}"
    launchctl enable "gui/${uid}/${label}" >/dev/null 2>&1 || true
    launchctl kickstart -k "gui/${uid}/${label}"
    ;;
  linux)
    systemctl --user daemon-reload
    systemctl --user enable --now "${label}.service"
    systemctl --user restart "${label}.service"
    ;;
esac

echo "installed ${label} at ${service_file}"
