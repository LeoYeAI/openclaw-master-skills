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
Usage: disable-aquaclaw-mirror-service.sh [options]

Options:
  --apply         Actually stop and disable the service
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
      launchctl disable "gui/${uid}/${label}" >/dev/null 2>&1 || true
      echo "disabled ${label}"
    else
      aquaclaw_mirror_print_command launchctl bootout "gui/${uid}" "${service_file}"
      aquaclaw_mirror_print_command launchctl disable "gui/${uid}/${label}"
    fi
    ;;
  linux)
    if [[ "${apply}" -eq 1 ]]; then
      systemctl --user disable --now "${label}.service"
      echo "disabled ${label}.service"
    else
      aquaclaw_mirror_print_command systemctl --user disable --now "${label}.service"
    fi
    ;;
esac
