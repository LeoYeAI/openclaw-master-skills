#!/bin/bash
# _diagnose-condense.sh - Groq-powered error log condensing
# Internal implementation for: diagnose.sh condense
# Takes a verbose error log snippet and returns a condensed version (<100 chars).
#
# Usage (via diagnose.sh):
#   diagnose.sh condense "long error message here"
#   diagnose.sh condense --input /path/to/logfile
#   echo "error log" | diagnose.sh condense --stdin
#
# Config keys (in ~/.amcp/config.json):
#   groq.apiKey    - Groq API key (required)
#   groq.model     - Model name (default: openai/gpt-oss-20b)
#
# Cache:
#   Condensed errors cached in ~/.amcp/error-cache.json to avoid re-processing.
#   Cache key is sha256 of first 500 chars of input.
#
# Environment:
#   CONFIG_FILE    Override config path (default: ~/.amcp/config.json)
#   ERROR_CACHE    Override cache path (default: ~/.amcp/error-cache.json)
#
# SECURITY: This script only uses keys from config, never from environment.
#           Agent must configure its own Groq API key.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
ERROR_CACHE="${ERROR_CACHE:-$HOME/.amcp/error-cache.json}"
GROQ_API_URL="https://api.groq.com/openai/v1/chat/completions"
GROQ_USAGE_FILE="${GROQ_USAGE_FILE:-$HOME/.amcp/groq-usage.json}"

usage() {
  cat <<'USAGE'
condense-error.sh - Condense verbose error logs to ~100 char summaries

Usage:
  condense-error.sh "error message"        Condense inline argument
  condense-error.sh --input FILE           Condense file contents
  echo "error" | condense-error.sh --stdin Read from stdin
  condense-error.sh --clear-cache          Clear the error cache

Options:
  --input FILE     Read error from file
  --stdin          Read error from stdin
  --no-cache       Skip cache lookup and storage
  --clear-cache    Clear the error cache and exit
  --config FILE    Override config path
  --help, -h       Show this help

Output:
  Condensed error on stdout (<100 chars, preserving root cause).
  Exit 0 on success, exit 1 on failure (original message echoed as fallback).
USAGE
  exit 0
}

# --- Argument parsing ---
INPUT_MODE="arg"
INPUT_FILE=""
NO_CACHE=false
RAW_INPUT=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --input) INPUT_MODE="file"; INPUT_FILE="${2:?--input requires a file path}"; shift 2 ;;
    --stdin) INPUT_MODE="stdin"; shift ;;
    --no-cache) NO_CACHE=true; shift ;;
    --clear-cache)
      rm -f "$ERROR_CACHE"
      echo "Cache cleared: $ERROR_CACHE"
      exit 0
      ;;
    --config) CONFIG_FILE="${2:?--config requires a path}"; shift 2 ;;
    --help|-h) usage ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      # First positional arg is the error message
      if [ -z "$RAW_INPUT" ]; then
        RAW_INPUT="$1"
      fi
      shift
      ;;
  esac
done

# --- Read input ---
case "$INPUT_MODE" in
  arg)
    if [ -z "$RAW_INPUT" ]; then
      echo "ERROR: No error message provided" >&2
      echo "Usage: condense-error.sh \"error message\"" >&2
      exit 1
    fi
    ;;
  file)
    if [ ! -f "$INPUT_FILE" ]; then
      echo "ERROR: File not found: $INPUT_FILE" >&2
      exit 1
    fi
    RAW_INPUT=$(cat "$INPUT_FILE")
    ;;
  stdin)
    RAW_INPUT=$(cat)
    ;;
esac

# If input is already short enough, return as-is
if [ "${#RAW_INPUT}" -le 100 ]; then
  echo "$RAW_INPUT"
  exit 0
fi

# --- Config helpers ---
read_config_key() {
  local key="$1"
  local cfg_path="$CONFIG_FILE"
  python3 -c "
import json, os, functools, operator
try:
    with open(os.path.expanduser('$cfg_path')) as f:
        cfg = json.load(f)
    keys = '$key'.split('.')
    val = functools.reduce(operator.getitem, keys, cfg)
    print(val)
except (KeyError, TypeError, IOError, json.JSONDecodeError):
    pass
" 2>/dev/null || true
}

get_groq_api_key() {
  # SECURITY: Only use config key, never env. Agent must have its own key.
  local key
  key=$(read_config_key "groq.apiKey")
  [ -n "$key" ] && { echo "$key"; return; }
  echo "[condense-error] ERROR: No groq.apiKey in ~/.amcp/config.json" >&2
  echo "[condense-error] Set with: proactive-amcp config set groq.apiKey gsk_YOUR_KEY" >&2
  return 1
}

get_groq_model() {
  local model
  model=$(read_config_key "groq.model")
  echo "${model:-openai/gpt-oss-20b}"
}

# --- Cache ---
# Cache key: sha256 of first 500 chars of input
compute_cache_key() {
  printf '%s' "${RAW_INPUT:0:500}" | python3 -c "import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest()[:16])"
}

cache_lookup() {
  local cache_key="$1"
  if $NO_CACHE || [ ! -f "$ERROR_CACHE" ]; then
    return 1
  fi
  python3 -c "
import json, sys, os, time
try:
    with open(os.path.expanduser('$ERROR_CACHE')) as f:
        cache = json.load(f)
    entry = cache.get('$cache_key')
    if entry:
        # Expire after 7 days
        if time.time() - entry.get('timestamp', 0) < 604800:
            print(entry['condensed'])
            sys.exit(0)
    sys.exit(1)
except (IOError, json.JSONDecodeError, KeyError):
    sys.exit(1)
" 2>/dev/null
}

cache_store() {
  local cache_key="$1"
  local condensed="$2"
  if $NO_CACHE; then
    return
  fi
  mkdir -p "$(dirname "$ERROR_CACHE")"
  python3 -c "
import json, os, time
cache_path = os.path.expanduser('$ERROR_CACHE')
try:
    with open(cache_path) as f:
        cache = json.load(f)
except (IOError, json.JSONDecodeError):
    cache = {}
# Limit cache to 200 entries (evict oldest)
if len(cache) >= 200:
    oldest = sorted(cache.items(), key=lambda x: x[1].get('timestamp',0))
    for k, _ in oldest[:len(cache)-199]:
        del cache[k]
import sys
cache[sys.argv[1]] = {
    'condensed': sys.argv[2],
    'timestamp': time.time()
}
with open(cache_path, 'w') as f:
    json.dump(cache, f, indent=2)
" "$cache_key" "$condensed" 2>/dev/null || true
}

# --- Token usage tracking ---
track_usage() {
  local prompt_tokens="${1:-0}"
  local completion_tokens="${2:-0}"
  python3 -c "
import json, os, time
usage_path = os.path.expanduser('$GROQ_USAGE_FILE')
try:
    with open(usage_path) as f:
        usage = json.load(f)
except (IOError, json.JSONDecodeError):
    usage = {'total_prompt_tokens': 0, 'total_completion_tokens': 0, 'sessions': []}
usage['total_prompt_tokens'] = usage.get('total_prompt_tokens', 0) + $prompt_tokens
usage['total_completion_tokens'] = usage.get('total_completion_tokens', 0) + $completion_tokens
usage.setdefault('sessions', [])
usage['sessions'].append({
    'timestamp': time.time(),
    'prompt_tokens': $prompt_tokens,
    'completion_tokens': $completion_tokens,
    'source': 'condense-error'
})
# Keep last 50 sessions
usage['sessions'] = usage['sessions'][-50:]
with open(usage_path, 'w') as f:
    json.dump(usage, f, indent=2)
" 2>/dev/null || true
}

# --- Groq API call ---
condense_via_groq() {
  local api_key="$1"
  local model="$2"
  local error_text="$3"

  # Truncate input to 2000 chars (error logs can be huge, keep API cost low)
  local truncated="${error_text:0:2000}"

  # Build request JSON via python3 (handles escaping safely)
  local request_file
  request_file=$(mktemp)
  trap "rm -f '$request_file'" RETURN

  python3 << PYEOF > "$request_file"
import json, sys, os

content = """${truncated}"""

request = {
    "model": "$model",
    "messages": [
        {
            "role": "system",
            "content": "You condense error logs. Output ONLY the condensed error, nothing else. Max 100 characters. Preserve the root cause."
        },
        {
            "role": "user",
            "content": f"Condense this error to <100 chars preserving root cause:\n\n{content}"
        }
    ],
    "temperature": 0,
    "max_tokens": 60
}

json.dump(request, sys.stdout)
PYEOF

  # Call Groq API
  local response
  response=$(curl -sf --max-time 15 \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d "@$request_file" \
    "$GROQ_API_URL" 2>/dev/null) || return 1

  # Parse response
  local condensed
  condensed=$(python3 -c "
import json, sys
try:
    r = json.loads(sys.stdin.read())
    msg = r['choices'][0]['message']['content'].strip()
    # Enforce 100 char limit
    if len(msg) > 100:
        msg = msg[:97] + '...'
    print(msg)
except (KeyError, IndexError, json.JSONDecodeError) as e:
    print(f'Parse error: {e}', file=sys.stderr)
    sys.exit(1)
" <<< "$response") || return 1

  # Track token usage
  local prompt_tokens completion_tokens
  prompt_tokens=$(python3 -c "import json,sys; r=json.loads(sys.stdin.read()); print(r.get('usage',{}).get('prompt_tokens',0))" <<< "$response" 2>/dev/null || echo 0)
  completion_tokens=$(python3 -c "import json,sys; r=json.loads(sys.stdin.read()); print(r.get('usage',{}).get('completion_tokens',0))" <<< "$response" 2>/dev/null || echo 0)
  track_usage "$prompt_tokens" "$completion_tokens"

  echo "$condensed"
}

# ============================================================
# Main
# ============================================================

# Check cache first
CACHE_KEY=$(compute_cache_key 2>/dev/null || echo "")
if [ -n "$CACHE_KEY" ]; then
  cached=$(cache_lookup "$CACHE_KEY" 2>/dev/null || true)
  if [ -n "$cached" ]; then
    echo "$cached"
    exit 0
  fi
fi

# Get API key
GROQ_KEY=$(get_groq_api_key 2>/dev/null || true)
if [ -z "$GROQ_KEY" ]; then
  # No Groq key — fall back to simple truncation
  echo "${RAW_INPUT:0:97}..." >&2
  echo "${RAW_INPUT:0:97}..."
  exit 0
fi

MODEL=$(get_groq_model)

# Call Groq
condensed=$(condense_via_groq "$GROQ_KEY" "$MODEL" "$RAW_INPUT" 2>/dev/null || true)

if [ -z "$condensed" ]; then
  # API failed — fall back to simple truncation
  echo "${RAW_INPUT:0:97}..."
  exit 0
fi

# Cache the result
if [ -n "$CACHE_KEY" ]; then
  cache_store "$CACHE_KEY" "$condensed"
fi

echo "$condensed"
