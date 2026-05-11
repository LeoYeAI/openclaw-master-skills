#!/usr/bin/env bash
set -euo pipefail

# Minimal CLI wrapper for Time Profiler recording via xctrace.
# Supports attach or launch and always writes a .trace output.

usage() {
  cat <<'USAGE'
Usage:
  record_time_profiler.sh --attach <pid> --trace <path> [--duration 90s]
  record_time_profiler.sh --launch <binary> --trace <path> [--duration 90s]
USAGE
}

attach_pid=""
launch_cmd=""
trace_path=""
duration="90s"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --attach)
      attach_pid="$2"; shift 2 ;;
    --launch)
      launch_cmd="$2"; shift 2 ;;
    --trace)
      trace_path="$2"; shift 2 ;;
    --duration)
      duration="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$trace_path" ]]; then
  echo "--trace is required"; usage; exit 1
fi

if [[ -n "$attach_pid" && -n "$launch_cmd" ]]; then
  echo "Use either --attach or --launch, not both"; exit 1
fi

if [[ -z "$attach_pid" && -z "$launch_cmd" ]]; then
  echo "Must supply --attach or --launch"; usage; exit 1
fi

if [[ -n "$attach_pid" ]]; then
  xcrun xctrace record --template 'Time Profiler' --time-limit "$duration" \
    --output "$trace_path" --attach "$attach_pid"
else
  xcrun xctrace record --template 'Time Profiler' --time-limit "$duration" \
    --output "$trace_path" --launch -- "$launch_cmd"
fi
