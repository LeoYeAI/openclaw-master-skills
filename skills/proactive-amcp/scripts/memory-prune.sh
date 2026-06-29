#!/bin/bash
# memory-prune.sh - Groq-powered memory pruning
# Evaluates memory files for importance using reasoning models.
# Archives low-importance, condenses medium, keeps high-importance.
#
# Usage:
#   memory-prune.sh [--dry-run] [--config FILE] [--content-dir DIR]
#
# Config keys (in ~/.amcp/config.json):
#   groq.apiKey    - Groq API key (required)
#   groq.model     - Model name (default: openai/gpt-oss-20b)
#
# Pruning thresholds:
#   importance < 0.3  -> archive to memory/archive/
#   0.3 <= importance < 0.7 -> condense inline
#   importance >= 0.7  -> keep unchanged
#
# Environment:
#   CONFIG_FILE   Override config path (default: ~/.amcp/config.json)
#   CONTENT_DIR   Override workspace (default: from openclaw.json)
#   GROQ_API_KEY  Override Groq API key from config

set -euo pipefail

command -v curl &>/dev/null || { echo "FATAL: curl required but not found" >&2; exit 2; }
command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
GROQ_USAGE_FILE="${GROQ_USAGE_FILE:-$HOME/.amcp/groq-usage.json}"
GROQ_API_URL="https://api.groq.com/openai/v1/chat/completions"

DRY_RUN=false
CONTENT_DIR="${CONTENT_DIR:-}"

usage() {
  cat <<'USAGE'
memory-prune.sh - Groq-powered memory pruning

Usage: memory-prune.sh [OPTIONS]

Options:
  --dry-run          Preview what would be pruned (no changes)
  --batch            Use Groq batch API (50% cost savings, async)
  --config FILE      Override config path (default: ~/.amcp/config.json)
  --content-dir DIR  Override workspace directory
  --help, -h         Show this help

Batch mode (--batch):
  --submit           Prepare and submit batch job (default batch action)
  --poll             Check status of pending batch jobs
  --apply            Download results and apply pruning decisions

Config keys (in ~/.amcp/config.json):
  groq.apiKey    Groq API key (required, or set GROQ_API_KEY env)
  groq.model     Model name (default: openai/gpt-oss-20b)

Thresholds:
  < 0.3   -> archive to memory/archive/
  0.3-0.7 -> condense inline (replace with shorter version)
  >= 0.7  -> keep unchanged
USAGE
  exit 0
}

# --- Argument parsing ---
BATCH_MODE=false
BATCH_ARGS=()
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; BATCH_ARGS+=("--dry-run"); shift ;;
    --batch) BATCH_MODE=true; shift ;;
    --submit|--poll|--apply) BATCH_MODE=true; BATCH_ARGS+=("$1"); shift ;;
    --config) CONFIG_FILE="${2:?--config requires a path}"; BATCH_ARGS+=("--config" "$2"); shift 2 ;;
    --content-dir) CONTENT_DIR="${2:?--content-dir requires a path}"; BATCH_ARGS+=("--content-dir" "$2"); shift 2 ;;
    --help|-h) usage ;;
    *) shift ;;
  esac
done

# Delegate to batch script if --batch mode
if $BATCH_MODE; then
  exec "$SCRIPT_DIR/memory-prune-batch.sh" "${BATCH_ARGS[@]}"
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

resolve_content_dir() {
  if [ -n "$CONTENT_DIR" ]; then
    echo "${CONTENT_DIR/#\~/$HOME}"
    return
  fi
  local oc="$HOME/.openclaw/openclaw.json"
  if [ -f "$oc" ]; then
    local dir
    dir=$(python3 -c "
import json
with open('$oc') as f:
    d = json.load(f)
print(d.get('agents',{}).get('defaults',{}).get('workspace','~/.openclaw/workspace'))
" 2>/dev/null || echo "~/.openclaw/workspace")
    echo "${dir/#\~/$HOME}"
  else
    echo "$HOME/.openclaw/workspace"
  fi
}

# --- Groq API ---
get_groq_api_key() {
  local key="${GROQ_API_KEY:-}"
  [ -n "$key" ] && { echo "$key"; return; }
  key=$(read_config_key "groq.apiKey")
  [ -n "$key" ] && { echo "$key"; return; }
  return 1
}

get_groq_model() {
  local model
  model=$(read_config_key "groq.model")
  echo "${model:-openai/gpt-oss-20b}"
}

# Call Groq API to evaluate a memory file
evaluate_memory() {
  local file_path="$1"
  local api_key="$2"
  local model="$3"

  local filename
  filename=$(basename "$file_path")

  # Read file content (truncate to 8000 chars for API)
  local file_content
  file_content=$(head -c 8000 "$file_path" 2>/dev/null || true)

  # Build request JSON via python3 (handles escaping safely)
  local request_json
  request_json=$(python3 << 'PYEOF'
import json, sys, os

filename = os.environ["_EVAL_FILENAME"]
model = os.environ["_EVAL_MODEL"]
content = sys.stdin.read()

prompt = f"""Evaluate this agent memory file for importance. Consider:
- Core identity, preferences, failure lessons = HIGH (0.7-1.0)
- Project context, architectural decisions = MEDIUM-HIGH (0.5-0.7)
- Routine task logs, status updates = MEDIUM (0.3-0.5)
- Debug output, temporary notes, stale context = LOW (0.1-0.3)

File: {filename}

---
{content}"""

body = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a memory importance evaluator for an AI agent. Be concise and accurate."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1,
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "memory_evaluation",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "importance_score": {"type": "number", "description": "Score 0.0-1.0"},
                    "should_keep": {"type": "boolean", "description": "Whether to keep this memory"},
                    "condensed_version": {"type": ["string", "null"], "description": "Shorter version if condensing, null if keeping or archiving"},
                    "reasoning": {"type": "string", "description": "Brief explanation of score"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Category tags for this memory"
                    }
                },
                "required": ["importance_score", "should_keep", "condensed_version", "reasoning", "tags"],
                "additionalProperties": False
            }
        }
    }
}

print(json.dumps(body))
PYEOF
  ) < "$file_path" || { echo "ERROR: Failed to build request for $filename" >&2; return 1; }

  # Write request to temp file (avoids shell escaping issues with curl -d)
  local tmpfile
  tmpfile=$(mktemp)
  echo "$request_json" > "$tmpfile"

  local response
  response=$(curl -sf --max-time 60 \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d "@$tmpfile" \
    "$GROQ_API_URL" 2>/dev/null) || { rm -f "$tmpfile"; echo "ERROR: Groq API call failed for $filename" >&2; return 1; }
  rm -f "$tmpfile"

  # Extract evaluation and token usage
  python3 -c "
import json, sys
resp = json.loads(sys.stdin.read())
content = resp.get('choices', [{}])[0].get('message', {}).get('content', '{}')
usage = resp.get('usage', {})
eval_data = json.loads(content)
eval_data['_usage'] = {
    'prompt_tokens': usage.get('prompt_tokens', 0),
    'completion_tokens': usage.get('completion_tokens', 0),
    'total_tokens': usage.get('total_tokens', 0)
}
print(json.dumps(eval_data))
" <<< "$response"
}

# Parse a field from evaluation JSON
parse_eval_field() {
  local json_str="$1"
  local field="$2"
  local default="$3"
  python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    v = d.get('$field', $default)
    print(v if v is not None else '')
except:
    print($default)
" <<< "$json_str" 2>/dev/null || echo "$default"
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

# Keep last 50 session entries
usage["sessions"] = usage.get("sessions", [])[-49:] + [{
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "prompt_tokens": $prompt_tokens,
    "completion_tokens": $completion_tokens,
    "total_tokens": $total_tokens,
    "model": "$model"
}]

with open(usage_file, "w") as f:
    json.dump(usage, f, indent=2)
PYEOF
}

# --- Main ---
main() {
  local content_dir
  content_dir=$(resolve_content_dir)
  local memory_dir="$content_dir/memory"
  local archive_dir="$memory_dir/archive"

  if [ ! -d "$memory_dir" ]; then
    echo "No memory directory found at $memory_dir" >&2
    exit 0
  fi

  # Collect .md files in memory/ (not subdirectories like ontology/, learning/, archive/)
  local -a memory_files=()
  while IFS= read -r f; do
    memory_files+=("$f")
  done < <(find "$memory_dir" -maxdepth 1 -name '*.md' -type f 2>/dev/null | sort)

  if [ ${#memory_files[@]} -eq 0 ]; then
    echo "No memory files (*.md) found in $memory_dir"
    exit 0
  fi

  # Get Groq API key
  local api_key
  api_key=$(get_groq_api_key) || {
    echo "FATAL: No Groq API key. Set GROQ_API_KEY env or groq.apiKey in config." >&2
    exit 1
  }

  local model
  model=$(get_groq_model)

  echo "=== Groq Memory Pruning ==="
  echo "  Model: $model"
  echo "  Memory dir: $memory_dir"
  echo "  Files to evaluate: ${#memory_files[@]}"
  $DRY_RUN && echo "  Mode: DRY RUN (no changes)"
  echo ""

  local archived=0
  local condensed=0
  local kept=0
  local errors=0
  local total_prompt=0
  local total_completion=0
  local total_tokens_sum=0

  export _EVAL_MODEL="$model"

  for file in "${memory_files[@]}"; do
    local filename
    filename=$(basename "$file")

    if [ ! -s "$file" ]; then
      echo "  SKIP $filename (empty)"
      continue
    fi

    echo -n "  Evaluating $filename... "

    export _EVAL_FILENAME="$filename"
    local result
    result=$(evaluate_memory "$file" "$api_key" "$model") || {
      echo "ERROR (API call failed)"
      errors=$((errors + 1))
      continue
    }

    # Parse result fields
    local score reasoning
    score=$(parse_eval_field "$result" "importance_score" "-1")
    reasoning=$(parse_eval_field "$result" "reasoning" "'N/A'")

    # Track usage
    local p_tokens c_tokens t_tokens
    p_tokens=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('_usage',{}).get('prompt_tokens',0))" <<< "$result" 2>/dev/null || echo "0")
    c_tokens=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('_usage',{}).get('completion_tokens',0))" <<< "$result" 2>/dev/null || echo "0")
    t_tokens=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('_usage',{}).get('total_tokens',0))" <<< "$result" 2>/dev/null || echo "0")
    total_prompt=$((total_prompt + p_tokens))
    total_completion=$((total_completion + c_tokens))
    total_tokens_sum=$((total_tokens_sum + t_tokens))

    # Determine action based on score thresholds
    local action
    action=$(python3 -c "
s = float('$score')
if s < 0.3: print('archive')
elif s < 0.7: print('condense')
else: print('keep')
" 2>/dev/null || echo "keep")

    case "$action" in
      archive)
        echo "ARCHIVE (score=$score) — $reasoning"
        if ! $DRY_RUN; then
          mkdir -p "$archive_dir"
          mv "$file" "$archive_dir/$filename"
          echo "    -> Moved to $archive_dir/$filename"
        fi
        archived=$((archived + 1))
        ;;
      condense)
        local condensed_text
        condensed_text=$(python3 -c "
import json, sys
r = json.loads(sys.stdin.read())
cv = r.get('condensed_version')
if cv and str(cv) != 'null' and str(cv).strip():
    print(cv)
" <<< "$result" 2>/dev/null || echo "")

        if [ -n "$condensed_text" ]; then
          local orig_size new_size
          orig_size=$(wc -c < "$file")
          new_size=${#condensed_text}
          echo "CONDENSE (score=$score, ${orig_size}B -> ${new_size}B) — $reasoning"
          if ! $DRY_RUN; then
            printf '%s\n' "$condensed_text" > "$file"
            echo "    -> Condensed inline"
          fi
          condensed=$((condensed + 1))
        else
          echo "KEEP (score=$score, no condensed version available) — $reasoning"
          kept=$((kept + 1))
        fi
        ;;
      keep)
        echo "KEEP (score=$score) — $reasoning"
        kept=$((kept + 1))
        ;;
    esac
  done

  # Track cumulative usage to file
  if [ "$total_tokens_sum" -gt 0 ]; then
    track_usage "$total_prompt" "$total_completion" "$total_tokens_sum" "$model"
  fi

  echo ""
  echo "=== Summary ==="
  echo "  Archived: $archived"
  echo "  Condensed: $condensed"
  echo "  Kept: $kept"
  echo "  Errors: $errors"
  echo "  Tokens used: $total_tokens_sum (prompt: $total_prompt, completion: $total_completion)"
  $DRY_RUN && echo "  (DRY RUN — no files were modified)"
}

main
