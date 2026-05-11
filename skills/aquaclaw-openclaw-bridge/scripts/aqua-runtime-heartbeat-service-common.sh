#!/usr/bin/env bash

set -euo pipefail

aquaclaw_hb_default_label() {
  echo "${AQUACLAW_RUNTIME_HEARTBEAT_LABEL:-ai.aquaclaw.runtime-heartbeat}"
}

aquaclaw_hb_default_workspace_root() {
  echo "${OPENCLAW_WORKSPACE_ROOT:-$HOME/.openclaw/workspace}"
}

aquaclaw_hb_default_hub_url() {
  echo "${AQUACLAW_HUB_URL:-http://127.0.0.1:8787}"
}

aquaclaw_hb_default_mode() {
  echo "${AQUACLAW_HEARTBEAT_MODE:-auto}"
}

aquaclaw_hb_default_hosted_config() {
  echo "${AQUACLAW_HOSTED_CONFIG:-}"
}

aquaclaw_hb_default_min_seconds() {
  echo "${AQUACLAW_HEARTBEAT_MIN_SECONDS:-900}"
}

aquaclaw_hb_default_jitter_seconds() {
  echo "${AQUACLAW_HEARTBEAT_JITTER_SECONDS:-60}"
}

aquaclaw_hb_default_timeout_ms() {
  echo "${AQUACLAW_HEARTBEAT_CONNECT_TIMEOUT_MS:-8000}"
}

aquaclaw_hb_default_state_file() {
  echo "${AQUACLAW_HEARTBEAT_STATE_FILE:-}"
}

aquaclaw_hb_default_stdout_log() {
  echo "${AQUACLAW_HEARTBEAT_STDOUT_LOG:-$HOME/.openclaw/logs/aquaclaw-runtime-heartbeat.log}"
}

aquaclaw_hb_default_stderr_log() {
  echo "${AQUACLAW_HEARTBEAT_STDERR_LOG:-$HOME/.openclaw/logs/aquaclaw-runtime-heartbeat.err.log}"
}

aquaclaw_hb_detect_platform() {
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

aquaclaw_hb_node_bin() {
  local node_bin
  node_bin="$(command -v node || true)"
  if [[ -z "${node_bin}" ]]; then
    echo "could not find node in PATH" >&2
    return 1
  fi
  echo "${node_bin}"
}

aquaclaw_hb_script_dir() {
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

aquaclaw_hb_script_path() {
  local script_dir
  script_dir="$(aquaclaw_hb_script_dir)"
  echo "${script_dir}/aqua-runtime-heartbeat.mjs"
}

aquaclaw_hb_service_file() {
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

aquaclaw_hb_print_command() {
  printf '%q ' "$@"
  printf '\n'
}

aquaclaw_hb_render_file() {
  local platform="$1"
  local label="$2"
  local workspace_root="$3"
  local node_bin="$4"
  local script_path="$5"
  local hub_url="$6"
  local mode="$7"
  local hosted_config="$8"
  local min_seconds="$9"
  local jitter_seconds="${10}"
  local timeout_ms="${11}"
  local state_file="${12}"
  local stdout_log="${13}"
  local stderr_log="${14}"

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
    <string>AquaClaw runtime heartbeat fallback service</string>
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
      <key>AQUACLAW_HEARTBEAT_MODE</key>
      <string>${mode}</string>
      <key>AQUACLAW_HOSTED_CONFIG</key>
      <string>${hosted_config}</string>
      <key>AQUACLAW_HEARTBEAT_MIN_SECONDS</key>
      <string>${min_seconds}</string>
      <key>AQUACLAW_HEARTBEAT_JITTER_SECONDS</key>
      <string>${jitter_seconds}</string>
      <key>AQUACLAW_HEARTBEAT_CONNECT_TIMEOUT_MS</key>
      <string>${timeout_ms}</string>
      <key>AQUACLAW_HEARTBEAT_STATE_FILE</key>
      <string>${state_file}</string>
    </dict>
  </dict>
</plist>
EOF
      ;;
    linux)
      cat <<EOF
[Unit]
Description=AquaClaw runtime heartbeat fallback service
After=network-online.target

[Service]
Type=simple
WorkingDirectory=${workspace_root}
ExecStart=${node_bin} ${script_path}
Restart=always
RestartSec=5
Environment=HOME=${HOME}
Environment=OPENCLAW_WORKSPACE_ROOT=${workspace_root}
Environment=AQUACLAW_HUB_URL=${hub_url}
Environment=AQUACLAW_HEARTBEAT_MODE=${mode}
Environment=AQUACLAW_HOSTED_CONFIG=${hosted_config}
Environment=AQUACLAW_HEARTBEAT_MIN_SECONDS=${min_seconds}
Environment=AQUACLAW_HEARTBEAT_JITTER_SECONDS=${jitter_seconds}
Environment=AQUACLAW_HEARTBEAT_CONNECT_TIMEOUT_MS=${timeout_ms}
Environment=AQUACLAW_HEARTBEAT_STATE_FILE=${state_file}
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
