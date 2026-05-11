#!/usr/bin/env bash
set -euo pipefail

# semantic-runtime-check.sh
#
# Backend-aware semantic runtime diagnostic helper.
# Designed for backends like qmd where config path, cache path,
# runtime-reported index path, and representative query checks all matter.
#
# v1 goal:
# - capture a baseline
# - verify path-alignment inputs
# - run status
# - run a small set of representative queries
# - avoid pretending this is a universal backend-neutral checker

usage() {
  cat <<'EOF'
Usage:
  semantic-runtime-check.sh \
    --cmd /path/to/runtime \
    --config-home /path/to/xdg-config \
    [--cache-home /path/to/xdg-cache] \
    [--query "system state"] \
    [--query "weekly review status"] \
    [--json]

Options:
  --cmd           Semantic CLI command path
  --config-home   XDG_CONFIG_HOME to use for the runtime check
  --cache-home    XDG_CACHE_HOME to use for the runtime check (recommended)
  --query         Representative query to run (repeatable)
  --json          Emit a best-effort JSON summary
  --help          Show this help

Semantics:
  - status must succeed
  - every query must succeed
  - any failed check makes the script exit 2

Exit codes:
  0  all checks completed successfully
  1  invalid arguments or missing paths
  2  one or more runtime checks failed
EOF
}

CMD=""
CONFIG_HOME=""
CACHE_HOME=""
JSON_MODE=0
QUERIES=()
FAILS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cmd)
      CMD="${2:-}"
      shift 2
      ;;
    --config-home)
      CONFIG_HOME="${2:-}"
      shift 2
      ;;
    --cache-home)
      CACHE_HOME="${2:-}"
      shift 2
      ;;
    --query)
      QUERIES+=("${2:-}")
      shift 2
      ;;
    --json)
      JSON_MODE=1
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "ERR: unknown arg: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$CMD" || -z "$CONFIG_HOME" ]]; then
  echo "ERR: --cmd and --config-home are required" >&2
  usage >&2
  exit 1
fi

if [[ ! -x "$CMD" ]]; then
  echo "ERR: command is not executable: $CMD" >&2
  exit 1
fi

if [[ ! -d "$CONFIG_HOME" ]]; then
  echo "ERR: config home not found: $CONFIG_HOME" >&2
  exit 1
fi

if [[ -n "$CACHE_HOME" && ! -d "$CACHE_HOME" ]]; then
  echo "ERR: cache home not found: $CACHE_HOME" >&2
  exit 1
fi

run_with_env() {
  if [[ -n "$CACHE_HOME" ]]; then
    XDG_CONFIG_HOME="$CONFIG_HOME" XDG_CACHE_HOME="$CACHE_HOME" "$@"
  else
    XDG_CONFIG_HOME="$CONFIG_HOME" "$@"
  fi
}

echo "== Semantic Runtime Check =="
echo "cmd: $CMD"
echo "XDG_CONFIG_HOME: $CONFIG_HOME"
if [[ -n "$CACHE_HOME" ]]; then
  echo "XDG_CACHE_HOME: $CACHE_HOME"
else
  echo "XDG_CACHE_HOME: (not set)"
  echo "WARN: cache home is unset; path-alignment conclusions may be incomplete"
fi
echo

echo "== Baseline: status =="
STATUS_OUT=""
if STATUS_OUT=$(run_with_env "$CMD" status 2>&1); then
  printf '%s\n' "$STATUS_OUT"
else
  rc=$?
  FAILS=$((FAILS + 1))
  printf '%s\n' "$STATUS_OUT"
  echo "ERR: status check failed with exit code $rc"
fi
echo

if [[ ${#QUERIES[@]} -eq 0 ]]; then
  QUERIES=("system state" "weekly review status")
fi

echo "== Representative queries =="
for q in "${QUERIES[@]}"; do
  echo "-- query: $q"
  QUERY_OUT=""
  if QUERY_OUT=$(run_with_env "$CMD" query "$q" 2>&1); then
    printf '%s\n' "$QUERY_OUT"
  else
    rc=$?
    FAILS=$((FAILS + 1))
    printf '%s\n' "$QUERY_OUT"
    echo "ERR: query failed with exit code $rc"
  fi
  echo
  echo "----"
  echo
done

if [[ "$JSON_MODE" -eq 1 ]]; then
  echo "== Summary (best effort) =="
  printf '{"cmd":"%s","configHome":"%s","cacheHome":"%s","queries":"%s","fails":%d}\n' \
    "$CMD" "$CONFIG_HOME" "$CACHE_HOME" "${QUERIES[*]}" "$FAILS"
fi

if [[ "$FAILS" -gt 0 ]]; then
  echo "Summary: FAIL ($FAILS failed check(s))"
  exit 2
fi

echo "Summary: PASS (all checks completed)"
