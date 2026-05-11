#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/openclaw-cron-common.sh"

aquaclaw_heartbeat_default_interval() {
  echo "${AQUACLAW_HEARTBEAT_EVERY:-15m}"
}

aquaclaw_heartbeat_default_job_name() {
  echo "${AQUACLAW_HEARTBEAT_JOB_NAME:-aquaclaw-heartbeat}"
}

aquaclaw_heartbeat_default_session() {
  echo "${AQUACLAW_HEARTBEAT_SESSION:-isolated}"
}

aquaclaw_heartbeat_default_thinking() {
  echo "${AQUACLAW_HEARTBEAT_THINKING:-low}"
}

aquaclaw_heartbeat_default_timeout_seconds() {
  echo "${AQUACLAW_HEARTBEAT_TIMEOUT_SECONDS:-90}"
}

aquaclaw_heartbeat_default_description() {
  echo "AquaClaw heartbeat tick (disabled by default)"
}

aquaclaw_heartbeat_build_message() {
  local skill_root="$1"

  cat <<EOF
Use \$aquaclaw-openclaw-bridge. Run the Aqua runtime heartbeat one-shot on this machine with:
bash ${skill_root}/scripts/aqua-runtime-heartbeat.sh --once

Report whether heartbeat was written, which mode was used, and which runtime/presence status Aqua returned. Do not create, edit, enable, disable, or remove cron jobs from inside the job itself. If AquaClaw is unavailable, say so directly.
EOF
}
