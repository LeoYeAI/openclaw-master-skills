#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/openclaw-heartbeat-cron-common.sh"

job_name="$(aquaclaw_heartbeat_default_job_name)"
json_output=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      job_name="$2"
      shift 2
      ;;
    --json)
      json_output=1
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Usage: show-openclaw-heartbeat-cron.sh [options]

Options:
  --name <name>   Cron job name to inspect
  --json          Print raw matched job JSON
EOF
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if ! job_json="$(aquaclaw_find_job_json "$job_name" 2>/dev/null)"; then
  echo "No OpenClaw cron job named ${job_name}."
  exit 0
fi

if [[ "$json_output" -eq 1 ]]; then
  echo "$job_json"
  exit 0
fi

JOB_JSON="$job_json" node - <<'EOF'
const job = JSON.parse(process.env.JOB_JSON);
const delivery = job.raw?.delivery ?? {};
const state = job.raw?.state ?? {};
console.log(`Name: ${job.name}`);
console.log(`Id: ${job.id ?? 'unknown'}`);
console.log(`Enabled: ${job.enabled === null ? 'unknown' : job.enabled ? 'yes' : 'no'}`);
console.log(`Schedule: ${job.schedule ?? 'unknown'}`);
console.log(`Session key: ${job.sessionKey ?? 'unset'}`);
console.log(`Delivery mode: ${delivery.mode ?? 'none'}`);
console.log(`Delivery channel: ${delivery.channel ?? 'none'}`);
console.log(`Delivery to: ${delivery.to ?? (job.sessionKey ? 'session/last-route' : 'unset')}`);
console.log(`Last status: ${state.lastStatus ?? 'unknown'}`);
console.log(`Last delivery status: ${state.lastDeliveryStatus ?? 'unknown'}`);
if (state.lastError) {
  console.log(`Last error: ${state.lastError}`);
}
EOF
