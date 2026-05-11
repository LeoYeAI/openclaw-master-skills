#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/aqua-mirror-service-common.sh"

apply=0
platform="$(aquaclaw_mirror_detect_platform || true)"
if [[ -z "${platform}" ]]; then
  echo "unsupported platform: $(uname -s)" >&2
  exit 1
fi

label="$(aquaclaw_mirror_default_label)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      apply=1
      shift
      ;;
    --label)
      label="$2"
      shift 2
      ;;
    -h|--help)
      cat <<'EOF'
Usage: remove-aquaclaw-mirror-service.sh [options]

Options:
  --apply         Actually stop and remove the service file
  --label <label> Service label
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

case "${platform}" in
  darwin)
    uid="$(id -u)"
    if [[ "${apply}" -eq 1 ]]; then
      launchctl bootout "gui/${uid}" "${service_file}" >/dev/null 2>&1 || true
      rm -f "${service_file}"
      echo "removed ${service_file}"
    else
      aquaclaw_mirror_print_command launchctl bootout "gui/${uid}" "${service_file}"
      aquaclaw_mirror_print_command rm -f "${service_file}"
    fi
    ;;
  linux)
    if [[ "${apply}" -eq 1 ]]; then
      systemctl --user disable --now "${label}.service" >/dev/null 2>&1 || true
      rm -f "${service_file}"
      systemctl --user daemon-reload
      systemctl --user reset-failed "${label}.service" >/dev/null 2>&1 || true
      echo "removed ${service_file}"
    else
      aquaclaw_mirror_print_command systemctl --user disable --now "${label}.service"
      aquaclaw_mirror_print_command rm -f "${service_file}"
      aquaclaw_mirror_print_command systemctl --user daemon-reload
    fi
    ;;
esac
