#!/bin/bash
# smart-checkpoint-filter.sh - Groq-powered checkpoint content selection
# Evaluates each memory file for "checkpoint worthiness" and produces an
# exclude list. Identity-critical files are always included. Debug/temp
# files are excluded for smaller, faster checkpoints.
#
# Usage:
#   smart-checkpoint-filter.sh --content-dir DIR [--dry-run] [--config FILE]
#
# Output:
#   Writes JSON manifest to stdout:
#   { "include": ["file1.md", ...], "exclude": ["file2.md", ...], "decisions": [...] }
#
# Exit codes:
#   0 = manifest written
#   1 = error (no Groq key, API failure, etc.)
#   2 = missing dependency
#
# Config keys (in ~/.amcp/config.json):
#   groq.apiKey    - Groq API key (required — agent's own key)
#   groq.model     - Model name (default: openai/gpt-oss-20b)
#
# Environment:
#   CONFIG_FILE          Override config path (default: ~/.amcp/config.json)
#   SMART_THRESHOLD      Minimum score to include in checkpoint (default: 0.3)
#   SMART_MAX_FILE_SIZE  Max file size to evaluate (default: 50000 bytes)
#
# SECURITY: This script only uses keys from config, never from environment.
#           Agent must configure its own Groq API key.

set -euo pipefail

command -v curl &>/dev/null || { echo "FATAL: curl required but not found" >&2; exit 2; }
command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
GROQ_USAGE_FILE="${GROQ_USAGE_FILE:-$HOME/.amcp/groq-usage.json}"
GROQ_API_URL="https://api.groq.com/openai/v1/chat/completions"
SMART_THRESHOLD="${SMART_THRESHOLD:-0.3}"
SMART_MAX_FILE_SIZE="${SMART_MAX_FILE_SIZE:-50000}"

DRY_RUN=false
CONTENT_DIR=""

# --- Argument parsing ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --config) CONFIG_FILE="${2:?--config requires a path}"; shift 2 ;;
    --content-dir) CONTENT_DIR="${2:?--content-dir requires a path}"; shift 2 ;;
    --help|-h)
      echo "Usage: smart-checkpoint-filter.sh --content-dir DIR [--dry-run] [--config FILE]"
      echo ""
      echo "Evaluates memory files for checkpoint worthiness using Groq."
      echo "Outputs JSON manifest of include/exclude decisions to stdout."
      echo ""
      echo "Options:"
      echo "  --content-dir DIR  Workspace directory (required)"
      echo "  --dry-run          Show decisions without producing manifest"
      echo "  --config FILE      Config path (default: ~/.amcp/config.json)"
      echo ""
      echo "Environment:"
      echo "  SMART_THRESHOLD      Min score to include (default: 0.3)"
      echo "  SMART_MAX_FILE_SIZE  Max file bytes to evaluate (default: 50000)"
      exit 0
      ;;
    *) shift ;;
  esac
done

if [ -z "$CONTENT_DIR" ]; then
  echo "ERROR: --content-dir is required" >&2
  exit 1
fi
CONTENT_DIR="${CONTENT_DIR/#\~/$HOME}"

# --- Config helpers ---
read_config_key() {
  local key="$1"
  python3 -c "
import json, os, functools, operator
try:
    with open(os.path.expanduser('$CONFIG_FILE')) as f:
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
  echo "[smart-checkpoint-filter] ERROR: No groq.apiKey in ~/.amcp/config.json" >&2
  echo "[smart-checkpoint-filter] Set with: proactive-amcp config set groq.apiKey gsk_YOUR_KEY" >&2
  return 1
}

get_groq_model() {
  local model
  model=$(read_config_key "groq.model")
  echo "${model:-openai/gpt-oss-20b}"
}

# --- Files that are ALWAYS included (identity-critical) ---
# These are never evaluated — they always go into the checkpoint.
ALWAYS_INCLUDE_PATTERNS=(
  "SOUL.md"
  "USER.md"
  "AGENTS.md"
  "MEMORY.md"
  "TOOLS.md"
)

is_always_include() {
  local filename="$1"
  for pat in "${ALWAYS_INCLUDE_PATTERNS[@]}"; do
    if [ "$filename" = "$pat" ]; then
      return 0
    fi
  done
  return 1
}

# --- Evaluate a single file via Groq ---
evaluate_file() {
  local file_path="$1"
  local api_key="$2"
  local model="$3"

  local filename
  filename=$(basename "$file_path")
  local file_size
  file_size=$(wc -c < "$file_path" 2>/dev/null || echo "0")

  # Truncate content for API (max 4000 chars for speed)
  local file_content
  file_content=$(head -c 4000 "$file_path" 2>/dev/null || true)

  local request_json
  request_json=$(CONTENT_INPUT="$file_content" python3 << 'PYEOF'
import json, os, sys

filename = os.environ.get("_EVAL_FILENAME", "unknown")
model = os.environ.get("_EVAL_MODEL", "openai/gpt-oss-20b")
file_size = os.environ.get("_EVAL_FILE_SIZE", "0")
content = os.environ.get("CONTENT_INPUT", "")

prompt = f"""Decide if this agent memory file should be included in a checkpoint backup.

INCLUDE if: identity-critical, lessons learned, user preferences, project decisions, important context.
EXCLUDE if: debug output, temporary notes, build logs, stale task lists, verbose session transcripts.

File: {filename} ({file_size} bytes)

---
{content}"""

body = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You decide which agent memory files belong in a checkpoint. Respond with JSON only."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0,
    "max_tokens": 150,
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "checkpoint_decision",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "include": {"type": "boolean", "description": "True if file should be in checkpoint"},
                    "score": {"type": "number", "description": "Importance 0.0-1.0"},
                    "reason": {"type": "string", "description": "Brief reason (max 50 chars)"}
                },
                "required": ["include", "score", "reason"],
                "additionalProperties": False
            }
        }
    }
}

print(json.dumps(body))
PYEOF
  ) || { echo '{"include":true,"score":0.5,"reason":"eval error: fallback to include"}'; return 0; }

  local tmpfile
  tmpfile=$(mktemp)
  echo "$request_json" > "$tmpfile"

  local response
  response=$(curl -sf --max-time 30 \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d "@$tmpfile" \
    "$GROQ_API_URL" 2>/dev/null) || { rm -f "$tmpfile"; echo '{"include":true,"score":0.5,"reason":"API error: fallback to include"}'; return 0; }
  rm -f "$tmpfile"

  # Extract decision and usage
  python3 -c "
import json, sys
resp = json.loads(sys.stdin.read())
content = resp.get('choices', [{}])[0].get('message', {}).get('content', '{}')
usage = resp.get('usage', {})
decision = json.loads(content)
decision['_usage'] = {
    'prompt_tokens': usage.get('prompt_tokens', 0),
    'completion_tokens': usage.get('completion_tokens', 0),
    'total_tokens': usage.get('total_tokens', 0)
}
print(json.dumps(decision))
" <<< "$response" 2>/dev/null || echo '{"include":true,"score":0.5,"reason":"parse error: fallback to include"}'
}

# Track token usage
track_usage() {
  local prompt_tokens="$1"
  local completion_tokens="$2"
  local total_tokens="$3"
  local model="$4"

  python3 << PYEOF
import json, os
from datetime import datetime, timezone

usage_file = os.path.expanduser("$GROQ_USAGE_FILE")
os.makedirs(os.path.dirname(usage_file), exist_ok=True)

try:
    with open(usage_file) as f:
        usage = json.load(f)
except (IOError, json.JSONDecodeError):
    usage = {"total_prompt_tokens": 0, "total_completion_tokens": 0, "total_tokens": 0, "evaluations": 0, "sessions": []}

usage["total_prompt_tokens"] += $prompt_tokens
usage["total_completion_tokens"] += $completion_tokens
usage["total_tokens"] += $total_tokens
usage["evaluations"] += 1
usage["last_model"] = "$model"
usage["last_used"] = datetime.now(timezone.utc).isoformat()

usage["sessions"] = usage.get("sessions", [])[-49:] + [{
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "prompt_tokens": $prompt_tokens,
    "completion_tokens": $completion_tokens,
    "total_tokens": $total_tokens,
    "model": "$model",
    "source": "smart-filter"
}]

with open(usage_file, "w") as f:
    json.dump(usage, f, indent=2)
PYEOF
}

# --- Main ---
main() {
  local memory_dir="$CONTENT_DIR/memory"

  if [ ! -d "$memory_dir" ]; then
    echo "No memory directory at $memory_dir — including all content" >&2
    echo '{"include":[],"exclude":[],"decisions":[],"note":"no memory dir"}'
    exit 0
  fi

  # Collect candidate files (*.md in memory/, not in always-include subdirs)
  local -a candidate_files=()
  while IFS= read -r f; do
    candidate_files+=("$f")
  done < <(find "$memory_dir" -maxdepth 1 -name '*.md' -type f 2>/dev/null | sort)

  # Also check memory/daily/ or memory/notes/ for ephemeral files
  for subdir in daily notes scratch; do
    if [ -d "$memory_dir/$subdir" ]; then
      while IFS= read -r f; do
        candidate_files+=("$f")
      done < <(find "$memory_dir/$subdir" -name '*.md' -type f 2>/dev/null | sort)
    fi
  done

  if [ ${#candidate_files[@]} -eq 0 ]; then
    echo "No memory files to evaluate" >&2
    echo '{"include":[],"exclude":[],"decisions":[],"note":"no memory files"}'
    exit 0
  fi

  # Get Groq API key
  local api_key
  api_key=$(get_groq_api_key) || {
    echo "No Groq API key — cannot run smart filter, including all files" >&2
    echo '{"include":[],"exclude":[],"decisions":[],"note":"no groq key"}'
    exit 0
  }

  local model
  model=$(get_groq_model)

  echo "=== Smart Checkpoint Filter ===" >&2
  echo "  Model: $model" >&2
  echo "  Threshold: $SMART_THRESHOLD" >&2
  echo "  Files to evaluate: ${#candidate_files[@]}" >&2
  $DRY_RUN && echo "  Mode: DRY RUN" >&2
  echo "" >&2

  local -a include_files=()
  local -a exclude_files=()
  local -a decisions=()
  local total_prompt=0
  local total_completion=0
  local total_tokens_sum=0

  export _EVAL_MODEL="$model"

  for file in "${candidate_files[@]}"; do
    local filename
    filename=$(basename "$file")
    local relpath="${file#$CONTENT_DIR/}"

    # Always-include files skip evaluation
    if is_always_include "$filename"; then
      echo "  INCLUDE $relpath (identity-critical, auto-include)" >&2
      include_files+=("$relpath")
      decisions+=("{\"file\":\"$relpath\",\"include\":true,\"score\":1.0,\"reason\":\"identity-critical (auto-include)\"}")
      continue
    fi

    # Skip empty files
    if [ ! -s "$file" ]; then
      echo "  EXCLUDE $relpath (empty)" >&2
      exclude_files+=("$relpath")
      decisions+=("{\"file\":\"$relpath\",\"include\":false,\"score\":0.0,\"reason\":\"empty file\"}")
      continue
    fi

    # Skip very large files (include them anyway - too big to evaluate cheaply)
    local fsize
    fsize=$(wc -c < "$file" 2>/dev/null || echo "0")
    if [ "$fsize" -gt "$SMART_MAX_FILE_SIZE" ]; then
      echo "  INCLUDE $relpath (${fsize}B, too large to evaluate — included by default)" >&2
      include_files+=("$relpath")
      decisions+=("{\"file\":\"$relpath\",\"include\":true,\"score\":0.5,\"reason\":\"too large to evaluate\"}")
      continue
    fi

    echo -n "  Evaluating $relpath... " >&2

    export _EVAL_FILENAME="$filename"
    export _EVAL_FILE_SIZE="$fsize"
    export CONTENT_INPUT
    CONTENT_INPUT=$(head -c 4000 "$file" 2>/dev/null || true)

    local result
    result=$(evaluate_file "$file" "$api_key" "$model") || {
      echo "ERROR (fallback: include)" >&2
      include_files+=("$relpath")
      decisions+=("{\"file\":\"$relpath\",\"include\":true,\"score\":0.5,\"reason\":\"eval error\"}")
      continue
    }

    local score include_decision reason
    score=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('score', 0.5))" <<< "$result" 2>/dev/null || echo "0.5")
    include_decision=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('include', True))" <<< "$result" 2>/dev/null || echo "True")
    reason=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('reason', 'unknown')[:60])" <<< "$result" 2>/dev/null || echo "unknown")

    # Track usage
    local p_tokens c_tokens t_tokens
    p_tokens=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('_usage',{}).get('prompt_tokens',0))" <<< "$result" 2>/dev/null || echo "0")
    c_tokens=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('_usage',{}).get('completion_tokens',0))" <<< "$result" 2>/dev/null || echo "0")
    t_tokens=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('_usage',{}).get('total_tokens',0))" <<< "$result" 2>/dev/null || echo "0")
    total_prompt=$((total_prompt + p_tokens))
    total_completion=$((total_completion + c_tokens))
    total_tokens_sum=$((total_tokens_sum + t_tokens))

    # Apply threshold: if score >= threshold OR Groq says include, keep it
    local use_score_threshold
    use_score_threshold=$(python3 -c "print('yes' if float('$score') >= float('$SMART_THRESHOLD') else 'no')" 2>/dev/null || echo "yes")

    if [ "$use_score_threshold" = "yes" ] || [ "$include_decision" = "True" ]; then
      echo "INCLUDE (score=$score) — $reason" >&2
      include_files+=("$relpath")
      decisions+=("{\"file\":\"$relpath\",\"include\":true,\"score\":$score,\"reason\":\"$reason\"}")
    else
      echo "EXCLUDE (score=$score) — $reason" >&2
      exclude_files+=("$relpath")
      decisions+=("{\"file\":\"$relpath\",\"include\":false,\"score\":$score,\"reason\":\"$reason\"}")
    fi
  done

  # Track cumulative usage
  if [ "$total_tokens_sum" -gt 0 ]; then
    track_usage "$total_prompt" "$total_completion" "$total_tokens_sum" "$model"
  fi

  echo "" >&2
  echo "=== Summary ===" >&2
  echo "  Include: ${#include_files[@]} files" >&2
  echo "  Exclude: ${#exclude_files[@]} files" >&2
  echo "  Tokens used: $total_tokens_sum" >&2
  $DRY_RUN && echo "  (DRY RUN — manifest not used)" >&2

  # Build JSON manifest (output to stdout)
  python3 -c "
import json, sys

include = json.loads(sys.argv[1])
exclude = json.loads(sys.argv[2])
decisions = [json.loads(d) for d in json.loads(sys.argv[3])]

manifest = {
    'include': include,
    'exclude': exclude,
    'decisions': decisions,
    'total_evaluated': len(decisions),
    'threshold': float(sys.argv[4])
}
print(json.dumps(manifest, indent=2))
" "$(printf '%s\n' "${include_files[@]}" | python3 -c 'import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')" \
  "$(printf '%s\n' "${exclude_files[@]}" | python3 -c 'import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')" \
  "$(printf '%s\n' "${decisions[@]}" | python3 -c 'import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')" \
  "$SMART_THRESHOLD"
}

main
