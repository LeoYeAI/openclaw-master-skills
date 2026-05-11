#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/aqua-hosted-pulse-service-common.sh"

apply=0
replace_existing=0

platform="$(aquaclaw_hp_detect_platform || true)"
if [[ -z "${platform}" ]]; then
  echo "unsupported platform: $(uname -s). This installer supports macOS launchd and Linux systemd user services." >&2
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
provision_community=1
replace_community_agent=0
community_model="${AQUACLAW_HOSTED_PULSE_COMMUNITY_MODEL:-}"

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
    --min-seconds)
      min_seconds="$2"
      shift 2
      ;;
    --jitter-seconds)
      jitter_seconds="$2"
      shift 2
      ;;
    --failure-min-seconds)
      failure_min_seconds="$2"
      shift 2
      ;;
    --failure-jitter-seconds)
      failure_jitter_seconds="$2"
      shift 2
      ;;
    --timeout-ms)
      timeout_ms="$2"
      shift 2
      ;;
    --timezone)
      timezone="$2"
      shift 2
      ;;
    --openclaw-bin)
      openclaw_bin="$2"
      shift 2
      ;;
    --skip-community-provision)
      provision_community=0
      shift
      ;;
    --replace-community-agent)
      replace_community_agent=1
      shift
      ;;
    --community-model)
      community_model="$2"
      shift 2
      ;;
    --author-agent)
      author_agent="$2"
      shift 2
      ;;
    --quiet-hours)
      if [[ "$2" == "none" ]]; then
        quiet_hours=""
      else
        quiet_hours="$2"
      fi
      shift 2
      ;;
    --feed-limit)
      feed_limit="$2"
      shift 2
      ;;
    --social-pulse-cooldown-minutes)
      social_cooldown_minutes="$2"
      shift 2
      ;;
    --social-pulse-dm-cooldown-minutes)
      dm_cooldown_minutes="$2"
      shift 2
      ;;
    --social-pulse-dm-target-cooldown-minutes)
      dm_target_cooldown_minutes="$2"
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
Usage: install-aquaclaw-hosted-pulse-service.sh [options]

Options:
  --apply                                   Actually write and start the service
  --replace                                 Overwrite an existing service file
  --label <label>                           Service label
  --workspace-root <dir>                    OpenClaw workspace root
  --service-path <path-list>                PATH exposed to the service runtime
  --hosted-config <path>                    Hosted Aqua config path override
  --state-file <path>                       Hosted pulse state file override
  --loop-state-file <path>                  Hosted pulse loop state file override
  --min-seconds <n>                         Base interval seconds
  --jitter-seconds <n>                      Extra random interval seconds
  --failure-min-seconds <n>                 Failure retry base seconds
  --failure-jitter-seconds <n>              Failure retry extra random seconds
  --timeout-ms <n>                          Per-tick timeout in milliseconds
  --timezone <iana>                         Fallback timezone
  --openclaw-bin <path>                     Explicit openclaw binary for authoring
  --skip-community-provision                Do not provision the community authoring agent during install
  --replace-community-agent                 Replace an existing mismatched community agent
  --community-model <id>                    Model to use when creating the community agent
  --author-agent <auto|community|main>      Authoring lane selection
  --quiet-hours <HH:MM-HH:MM|none>          Fallback quiet hours; use "none" to disable
  --feed-limit <n>                          Sea feed limit passed to hosted pulse
  --social-pulse-cooldown-minutes <n>       Fallback public-expression cooldown
  --social-pulse-dm-cooldown-minutes <n>    Fallback global DM cooldown
  --social-pulse-dm-target-cooldown-minutes <n>
                                            Fallback per-target DM cooldown
  --stdout-log <path>                       Service stdout log path
  --stderr-log <path>                       Service stderr log path
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
node_bin="$(aquaclaw_hp_node_bin)"
script_path="$(aquaclaw_hp_script_path)"
community_agent_note=""
if [[ "${author_agent}" != "main" && "${provision_community}" -eq 1 ]]; then
  community_agent_note="will ensure community authoring agent exists before install"
fi
preflight_json="$(
  aquaclaw_hp_authoring_preflight_json "${workspace_root}" "${author_agent}" "${service_path}" "${openclaw_bin}"
)"
preflight_summary="$(
  PREFLIGHT_JSON="${preflight_json}" node -e '
    const data = JSON.parse(process.env.PREFLIGHT_JSON);
    const fields = [
      `ready=${data.ready === true}`,
      `requested=${data.requestedAgentMode ?? "unknown"}`,
      `selected=${data.agentId ?? "none"}`,
      `reason=${data.selectionReason ?? data.errorCode ?? "unknown"}`,
      `bin=${data.openclawBin ?? "missing"}`,
    ];
    if (Array.isArray(data.warnings) && data.warnings.length > 0) {
      fields.push(`warnings=${data.warnings.join(" | ")}`);
    }
    process.stdout.write(fields.join("; "));
  '
)"
rendered="$(
  aquaclaw_hp_render_file \
    "${platform}" \
    "${label}" \
    "${workspace_root}" \
    "${node_bin}" \
    "${script_path}" \
    "${service_path}" \
    "${openclaw_bin}" \
    "${author_agent}" \
    "${hosted_config}" \
    "${pulse_state_file}" \
    "${loop_state_file}" \
    "${min_seconds}" \
    "${jitter_seconds}" \
    "${failure_min_seconds}" \
    "${failure_jitter_seconds}" \
    "${timeout_ms}" \
    "${timezone}" \
    "${quiet_hours}" \
    "${feed_limit}" \
    "${social_cooldown_minutes}" \
    "${dm_cooldown_minutes}" \
    "${dm_target_cooldown_minutes}" \
    "${stdout_log}" \
    "${stderr_log}"
)"

if [[ -f "${service_file}" && "${replace_existing}" -ne 1 ]]; then
  echo "service file already exists: ${service_file}" >&2
  echo "rerun with --replace to overwrite it" >&2
  exit 1
fi

if [[ "${apply}" -ne 1 ]]; then
  if [[ -n "${community_agent_note}" ]]; then
    echo "# Community agent: ${community_agent_note}"
  fi
  echo "# Authoring preflight: ${preflight_summary}"
  echo "# Preview: ${service_file}"
  printf '%s\n' "${rendered}"
  exit 0
fi

if [[ "${author_agent}" != "main" && "${provision_community}" -eq 1 ]]; then
  community_args=(--workspace-root "${workspace_root}")
  if [[ -n "${openclaw_bin}" ]]; then
    community_args+=(--openclaw-bin "${openclaw_bin}")
  fi
  if [[ "${replace_community_agent}" -eq 1 ]]; then
    community_args+=(--replace)
  fi
  if [[ -n "${community_model}" ]]; then
    community_args+=(--model "${community_model}")
  fi
  bash "${script_dir}/ensure-aquaclaw-community-agent.sh" "${community_args[@]}"
  preflight_json="$(
    aquaclaw_hp_authoring_preflight_json "${workspace_root}" "${author_agent}" "${service_path}" "${openclaw_bin}"
  )"
  preflight_summary="$(
    PREFLIGHT_JSON="${preflight_json}" node -e '
      const data = JSON.parse(process.env.PREFLIGHT_JSON);
      const fields = [
        `ready=${data.ready === true}`,
        `requested=${data.requestedAgentMode ?? "unknown"}`,
        `selected=${data.agentId ?? "none"}`,
        `reason=${data.selectionReason ?? data.errorCode ?? "unknown"}`,
        `bin=${data.openclawBin ?? "missing"}`,
      ];
      if (Array.isArray(data.warnings) && data.warnings.length > 0) {
        fields.push(`warnings=${data.warnings.join(" | ")}`);
      }
      process.stdout.write(fields.join("; "));
    '
  )"
fi

preflight_ready="$(
  PREFLIGHT_JSON="${preflight_json}" node -e '
    const data = JSON.parse(process.env.PREFLIGHT_JSON);
    process.stdout.write(data.ready === true ? "true" : "false");
  '
)"

if [[ "${preflight_ready}" != "true" ]]; then
  echo "authoring preflight failed: ${preflight_summary}" >&2
  echo "${preflight_json}" >&2
  exit 1
fi

echo "authoring preflight passed: ${preflight_summary}"

mkdir -p "$(dirname "${service_file}")"
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
