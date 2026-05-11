#!/usr/bin/env bash

set -euo pipefail

aquaclaw_mirror_default_label() {
  echo "${AQUACLAW_MIRROR_LABEL:-ai.aquaclaw.mirror-sync}"
}

aquaclaw_mirror_default_workspace_root() {
  echo "${OPENCLAW_WORKSPACE_ROOT:-$HOME/.openclaw/workspace}"
}

aquaclaw_mirror_resolve_path_field() {
  local field="$1"
  local workspace_root="${2:-$(aquaclaw_mirror_default_workspace_root)}"
  local script_dir
  script_dir="$(aquaclaw_mirror_script_dir)"
  node "${script_dir}/resolve-aquaclaw-paths.mjs" \
    --workspace-root "${workspace_root}" \
    --mode "$(aquaclaw_mirror_default_mode)" \
    --field "${field}"
}

aquaclaw_mirror_default_hub_url() {
  echo "${AQUACLAW_HUB_URL:-http://127.0.0.1:8787}"
}

aquaclaw_mirror_default_mode() {
  echo "${AQUACLAW_MIRROR_MODE:-auto}"
}

aquaclaw_mirror_default_hosted_config() {
  local workspace_root="${1:-$(aquaclaw_mirror_default_workspace_root)}"
  if [[ -n "${AQUACLAW_HOSTED_CONFIG:-}" ]]; then
    echo "${AQUACLAW_HOSTED_CONFIG}"
    return
  fi
  aquaclaw_mirror_resolve_path_field "hosted-config" "${workspace_root}"
}

aquaclaw_mirror_default_mirror_dir() {
  local workspace_root="${1:-$(aquaclaw_mirror_default_workspace_root)}"
  if [[ -n "${AQUACLAW_MIRROR_DIR:-}" ]]; then
    echo "${AQUACLAW_MIRROR_DIR}"
    return
  fi
  aquaclaw_mirror_resolve_path_field "mirror-dir" "${workspace_root}"
}

aquaclaw_mirror_default_state_file() {
  local mirror_dir="${1:-}"
  if [[ -n "${AQUACLAW_MIRROR_STATE_FILE:-}" ]]; then
    echo "${AQUACLAW_MIRROR_STATE_FILE}"
    return
  fi
  if [[ -n "${mirror_dir}" ]]; then
    echo "${mirror_dir}/state.json"
    return
  fi
  local workspace_root
  workspace_root="$(aquaclaw_mirror_default_workspace_root)"
  echo "$(aquaclaw_mirror_default_mirror_dir "${workspace_root}")/state.json"
}

aquaclaw_mirror_default_reconnect_seconds() {
  echo "${AQUACLAW_MIRROR_RECONNECT_SECONDS:-5}"
}

aquaclaw_mirror_default_public_thread_limit() {
  echo "${AQUACLAW_MIRROR_PUBLIC_THREAD_LIMIT:-20}"
}

aquaclaw_mirror_default_hydrate_conversations() {
  echo "${AQUACLAW_MIRROR_HYDRATE_CONVERSATIONS:-0}"
}

aquaclaw_mirror_default_hydrate_public_threads() {
  echo "${AQUACLAW_MIRROR_HYDRATE_PUBLIC_THREADS:-0}"
}

aquaclaw_mirror_default_stdout_log() {
  echo "${AQUACLAW_MIRROR_STDOUT_LOG:-$HOME/.openclaw/logs/aquaclaw-mirror-sync.log}"
}

aquaclaw_mirror_default_stderr_log() {
  echo "${AQUACLAW_MIRROR_STDERR_LOG:-$HOME/.openclaw/logs/aquaclaw-mirror-sync.err.log}"
}

aquaclaw_mirror_detect_platform() {
  case "$(uname -s)" in
    Darwin)
      echo "darwin"
      ;;
    Linux)
      echo "linux"
      ;;
    *)
      return 1
      ;;
  esac
}

aquaclaw_mirror_node_bin() {
  local node_bin
  node_bin="$(command -v node || true)"
  if [[ -z "${node_bin}" ]]; then
    echo "could not find node in PATH" >&2
    return 1
  fi
  echo "${node_bin}"
}

aquaclaw_mirror_script_dir() {
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

aquaclaw_mirror_script_path() {
  local script_dir
  script_dir="$(aquaclaw_mirror_script_dir)"
  echo "${script_dir}/aqua-mirror-sync.mjs"
}

aquaclaw_mirror_service_file() {
  local platform="$1"
  local label="$2"
  case "${platform}" in
    darwin)
      echo "${HOME}/Library/LaunchAgents/${label}.plist"
      ;;
    linux)
      echo "${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/${label}.service"
      ;;
    *)
      echo "unsupported platform: ${platform}" >&2
      return 1
      ;;
  esac
}

aquaclaw_mirror_print_command() {
  printf '%q ' "$@"
  printf '\n'
}

aquaclaw_mirror_render_file() {
  local platform="$1"
  local label="$2"
  local workspace_root="$3"
  local node_bin="$4"
  local script_path="$5"
  local hub_url="$6"
  local mode="$7"
  local hosted_config="$8"
  local mirror_dir="$9"
  local state_file="${10}"
  local reconnect_seconds="${11}"
  local hydrate_conversations="${12}"
  local hydrate_public_threads="${13}"
  local public_thread_limit="${14}"
  local stdout_log="${15}"
  local stderr_log="${16}"

  case "${platform}" in
    darwin)
      cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>${label}</string>
    <key>Comment</key>
    <string>AquaClaw mirror follow service</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>5</integer>
    <key>WorkingDirectory</key>
    <string>${workspace_root}</string>
    <key>ProgramArguments</key>
    <array>
      <string>${node_bin}</string>
      <string>${script_path}</string>
      <string>--follow</string>
    </array>
    <key>StandardOutPath</key>
    <string>${stdout_log}</string>
    <key>StandardErrorPath</key>
    <string>${stderr_log}</string>
    <key>EnvironmentVariables</key>
    <dict>
      <key>HOME</key>
      <string>${HOME}</string>
      <key>OPENCLAW_WORKSPACE_ROOT</key>
      <string>${workspace_root}</string>
      <key>AQUACLAW_HUB_URL</key>
      <string>${hub_url}</string>
      <key>AQUACLAW_MIRROR_MODE</key>
      <string>${mode}</string>
      <key>AQUACLAW_HOSTED_CONFIG</key>
      <string>${hosted_config}</string>
      <key>AQUACLAW_MIRROR_DIR</key>
      <string>${mirror_dir}</string>
      <key>AQUACLAW_MIRROR_STATE_FILE</key>
      <string>${state_file}</string>
      <key>AQUACLAW_MIRROR_RECONNECT_SECONDS</key>
      <string>${reconnect_seconds}</string>
      <key>AQUACLAW_MIRROR_HYDRATE_CONVERSATIONS</key>
      <string>${hydrate_conversations}</string>
      <key>AQUACLAW_MIRROR_HYDRATE_PUBLIC_THREADS</key>
      <string>${hydrate_public_threads}</string>
      <key>AQUACLAW_MIRROR_PUBLIC_THREAD_LIMIT</key>
      <string>${public_thread_limit}</string>
    </dict>
  </dict>
</plist>
EOF
      ;;
    linux)
      cat <<EOF
[Unit]
Description=AquaClaw mirror follow service
After=network-online.target

[Service]
Type=simple
WorkingDirectory=${workspace_root}
ExecStart=${node_bin} ${script_path} --follow
Restart=always
RestartSec=5
Environment=HOME=${HOME}
Environment=OPENCLAW_WORKSPACE_ROOT=${workspace_root}
Environment=AQUACLAW_HUB_URL=${hub_url}
Environment=AQUACLAW_MIRROR_MODE=${mode}
Environment=AQUACLAW_HOSTED_CONFIG=${hosted_config}
Environment=AQUACLAW_MIRROR_DIR=${mirror_dir}
Environment=AQUACLAW_MIRROR_STATE_FILE=${state_file}
Environment=AQUACLAW_MIRROR_RECONNECT_SECONDS=${reconnect_seconds}
Environment=AQUACLAW_MIRROR_HYDRATE_CONVERSATIONS=${hydrate_conversations}
Environment=AQUACLAW_MIRROR_HYDRATE_PUBLIC_THREADS=${hydrate_public_threads}
Environment=AQUACLAW_MIRROR_PUBLIC_THREAD_LIMIT=${public_thread_limit}
StandardOutput=append:${stdout_log}
StandardError=append:${stderr_log}

[Install]
WantedBy=default.target
EOF
      ;;
    *)
      echo "unsupported platform: ${platform}" >&2
      return 1
      ;;
  esac
}
