#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${script_dir}/openclaw-diary-cron-common.sh"

job_name="$(aquaclaw_diary_default_job_name)"
apply=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      apply=1
      shift
      ;;
    --name)
      job_name="$2"
      shift 2
      ;;
    -h|--help)
      cat <<'EOF'
Usage: remove-openclaw-diary-cron.sh [options]

Options:
  --apply         Actually remove the cron job
  --name <name>   Cron job name
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

job_id="$(JOB_JSON="$job_json" node -e 'const job = JSON.parse(process.env.JOB_JSON); process.stdout.write(String(job.id ?? ""));')"
cmd=(openclaw cron rm "$job_id")

if [[ "$apply" -eq 1 ]]; then
  "${cmd[@]}"
else
  aquaclaw_print_command "${cmd[@]}"
fi
