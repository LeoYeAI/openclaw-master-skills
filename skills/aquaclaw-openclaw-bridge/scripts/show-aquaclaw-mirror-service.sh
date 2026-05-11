#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/aqua-mirror-service-common.sh"

platform="$(aquaclaw_mirror_detect_platform || true)"
if [[ -z "${platform}" ]]; then
  echo "unsupported platform: $(uname -s)" >&2
  exit 1
fi

label="$(aquaclaw_mirror_default_label)"
workspace_root="$(aquaclaw_mirror_default_workspace_root)"
mode="$(aquaclaw_mirror_default_mode)"
hosted_config="$(aquaclaw_mirror_default_hosted_config "${workspace_root}")"
mirror_dir="$(aquaclaw_mirror_default_mirror_dir "${workspace_root}")"
state_file="$(aquaclaw_mirror_default_state_file "${mirror_dir}")"
reconnect_seconds="$(aquaclaw_mirror_default_reconnect_seconds)"
hydrate_conversations="$(aquaclaw_mirror_default_hydrate_conversations)"
hydrate_public_threads="$(aquaclaw_mirror_default_hydrate_public_threads)"
public_thread_limit="$(aquaclaw_mirror_default_public_thread_limit)"
stdout_log="$(aquaclaw_mirror_default_stdout_log)"
stderr_log="$(aquaclaw_mirror_default_stderr_log)"
hosted_config_explicit=0
mirror_dir_explicit=0
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
        hosted_config="$(aquaclaw_mirror_default_hosted_config "${workspace_root}")"
      fi
      if [[ "${mirror_dir_explicit}" -ne 1 ]]; then
        mirror_dir="$(aquaclaw_mirror_default_mirror_dir "${workspace_root}")"
      fi
      if [[ "${state_file_explicit}" -ne 1 ]]; then
        state_file="$(aquaclaw_mirror_default_state_file "${mirror_dir}")"
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
    --mirror-dir)
      mirror_dir="$2"
      mirror_dir_explicit=1
      if [[ "${state_file_explicit}" -ne 1 ]]; then
        state_file="$(aquaclaw_mirror_default_state_file "${mirror_dir}")"
      fi
      shift 2
      ;;
    --state-file)
      state_file="$2"
      state_file_explicit=1
      shift 2
      ;;
    --reconnect-seconds)
      reconnect_seconds="$2"
      shift 2
      ;;
    --hydrate-conversations)
      hydrate_conversations=1
      shift
      ;;
    --hydrate-public-threads)
      hydrate_public_threads=1
      shift
      ;;
    --public-thread-limit)
      public_thread_limit="$2"
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
Usage: show-aquaclaw-mirror-service.sh [options]

Options:
  --label <label>                Service label
  --workspace-root <dir>         OpenClaw workspace root
  --mode <mode>                  auto|local|hosted
  --hosted-config <path>         Hosted Aqua config path override
  --mirror-dir <path>            Mirror root directory
  --state-file <path>            Mirror state file path
  --reconnect-seconds <n>        Stream reconnect delay for follow mode
  --hydrate-conversations        Show config with conversation hydration enabled
  --hydrate-public-threads       Show config with public-thread hydration enabled
  --public-thread-limit <n>      Public thread hydration list size
  --stdout-log <path>            Service stdout log path
  --stderr-log <path>            Service stderr log path
EOF
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 1
      ;;
  esac
done

service_file="$(aquaclaw_mirror_service_file "${platform}" "${label}")"

echo "Platform: ${platform}"
echo "Label: ${label}"
echo "Mode: ${mode}"
echo "Service file: ${service_file}"
echo "Hosted config: ${hosted_config}"
echo "Mirror dir: ${mirror_dir}"
echo "State file: ${state_file}"
echo "Reconnect seconds: ${reconnect_seconds}"
echo "Hydrate conversations: ${hydrate_conversations}"
echo "Hydrate public threads: ${hydrate_public_threads}"
echo "Public thread limit: ${public_thread_limit}"
echo "Stdout log: ${stdout_log}"
echo "Stderr log: ${stderr_log}"

if [[ ! -f "${service_file}" ]]; then
  echo "Service file does not exist yet."
else
  case "${platform}" in
    darwin)
      launchctl print "gui/$(id -u)/${label}" 2>/dev/null || echo "Service is not currently loaded."
      ;;
    linux)
      systemctl --user status --no-pager --full "${label}.service" 2>/dev/null || echo "Service is not currently loaded."
      ;;
  esac
fi

echo
echo "Mirror status:"
bash "${script_dir}/aqua-mirror-status.sh" \
  --workspace-root "${workspace_root}" \
  --config-path "${hosted_config}" \
  --mirror-dir "${mirror_dir}" \
  --state-file "${state_file}" \
  --expect-mode "${mode}"
