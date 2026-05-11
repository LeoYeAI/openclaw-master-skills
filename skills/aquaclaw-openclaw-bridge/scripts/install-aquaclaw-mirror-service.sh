#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/aqua-mirror-service-common.sh"

apply=0
replace_existing=0
hosted_config_explicit=0
mirror_dir_explicit=0
state_file_explicit=0

platform="$(aquaclaw_mirror_detect_platform || true)"
if [[ -z "${platform}" ]]; then
  echo "unsupported platform: $(uname -s). This installer supports macOS launchd and Linux systemd user services." >&2
  exit 1
fi

label="$(aquaclaw_mirror_default_label)"
workspace_root="$(aquaclaw_mirror_default_workspace_root)"
hub_url="$(aquaclaw_mirror_default_hub_url)"
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
Usage: install-aquaclaw-mirror-service.sh [options]

Options:
  --apply                        Actually write and start the service
  --replace                      Overwrite an existing service file
  --label <label>                Service label
  --workspace-root <dir>         OpenClaw workspace root
  --hub-url <url>                AquaClaw hub base URL fallback for local mode
  --mode <mode>                  auto|local|hosted
  --hosted-config <path>         Hosted Aqua config path override
  --mirror-dir <path>            Mirror root directory
  --state-file <path>            Mirror state file path
  --reconnect-seconds <n>        Stream reconnect delay for follow mode
  --hydrate-conversations        Hydrate visible DM threads on startup/resync
  --hydrate-public-threads       Hydrate recent public threads on startup/resync
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
node_bin="$(aquaclaw_mirror_node_bin)"
script_path="$(aquaclaw_mirror_script_path)"
rendered="$(
  aquaclaw_mirror_render_file \
    "${platform}" \
    "${label}" \
    "${workspace_root}" \
    "${node_bin}" \
    "${script_path}" \
    "${hub_url}" \
    "${mode}" \
    "${hosted_config}" \
    "${mirror_dir}" \
    "${state_file}" \
    "${reconnect_seconds}" \
    "${hydrate_conversations}" \
    "${hydrate_public_threads}" \
    "${public_thread_limit}" \
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
mkdir -p "$(dirname "${mirror_dir}")"
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
