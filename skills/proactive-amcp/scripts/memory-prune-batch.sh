#!/bin/bash
# memory-prune-batch.sh - Groq batch API for memory pruning at 50% cost
# Prepares JSONL batch requests, submits to Groq batch API, polls for
# completion, downloads results, and applies pruning decisions.
#
# Usage:
#   memory-prune-batch.sh [--submit] [--poll] [--apply] [--dry-run]
#                         [--config FILE] [--content-dir DIR]
#
# Modes:
#   --submit     Prepare JSONL and submit batch job (default if no mode given)
#   --poll       Check status of pending batch jobs
#   --apply      Download results and apply pruning decisions
#   --dry-run    Preview without changes (works with --submit and --apply)
#
# Config keys (in ~/.amcp/config.json):
#   groq.apiKey    - Groq API key (required)
#   groq.model     - Model name (default: openai/gpt-oss-20b)
#
# Batch jobs tracked in ~/.amcp/batch-jobs.json
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
BATCH_JOBS_FILE="${BATCH_JOBS_FILE:-$HOME/.amcp/batch-jobs.json}"
GROQ_USAGE_FILE="${GROQ_USAGE_FILE:-$HOME/.amcp/groq-usage.json}"
GROQ_API_BASE="https://api.groq.com/openai/v1"

DRY_RUN=false
CONTENT_DIR="${CONTENT_DIR:-}"
MODE=""

usage() {
  cat <<'USAGE'
memory-prune-batch.sh - Groq batch API for memory pruning (50% cost savings)

Usage: memory-prune-batch.sh [OPTIONS]

Modes:
  --submit       Prepare JSONL and submit batch job (default)
  --poll         Check status of pending batch jobs
  --apply        Download completed results and apply pruning
  --dry-run      Preview without making changes

Options:
  --config FILE      Override config path (default: ~/.amcp/config.json)
  --content-dir DIR  Override workspace directory
  --help, -h         Show this help

Workflow:
  1. memory-prune-batch.sh --submit       # Upload batch, submit job
  2. memory-prune-batch.sh --poll         # Check if done (can repeat)
  3. memory-prune-batch.sh --apply        # Download results, prune files

Batch jobs are tracked in ~/.amcp/batch-jobs.json.
USAGE
  exit 0
}

# --- Argument parsing ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --submit) MODE="submit"; shift ;;
    --poll) MODE="poll"; shift ;;
    --apply) MODE="apply"; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --config) CONFIG_FILE="${2:?--config requires a path}"; shift 2 ;;
    --content-dir) CONTENT_DIR="${2:?--content-dir requires a path}"; shift 2 ;;
    --help|-h) usage ;;
    *) shift ;;
  esac
done

# Default mode is submit
[ -z "$MODE" ] && MODE="submit"

# --- Config helpers (shared with memory-prune.sh) ---
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

# --- Batch jobs tracking ---
load_batch_jobs() {
  if [ -f "$BATCH_JOBS_FILE" ]; then
    cat "$BATCH_JOBS_FILE"
  else
    echo '{"jobs":[]}'
  fi
}

save_batch_jobs() {
  local json_data="$1"
  mkdir -p "$(dirname "$BATCH_JOBS_FILE")"
  echo "$json_data" > "$BATCH_JOBS_FILE"
}

# --- SUBMIT mode ---
do_submit() {
  local content_dir
  content_dir=$(resolve_content_dir)
  local memory_dir="$content_dir/memory"

  if [ ! -d "$memory_dir" ]; then
    echo "No memory directory found at $memory_dir" >&2
    exit 0
  fi

  # Collect .md files (maxdepth 1 — not subdirs like ontology/, learning/, archive/)
  local -a memory_files=()
  while IFS= read -r f; do
    [ -s "$f" ] && memory_files+=("$f")
  done < <(find "$memory_dir" -maxdepth 1 -name '*.md' -type f 2>/dev/null | sort)

  if [ ${#memory_files[@]} -eq 0 ]; then
    echo "No non-empty memory files (*.md) found in $memory_dir"
    exit 0
  fi

  local api_key
  api_key=$(get_groq_api_key) || {
    echo "FATAL: No Groq API key. Set GROQ_API_KEY env or groq.apiKey in config." >&2
    exit 1
  }

  local model
  model=$(get_groq_model)

  echo "=== Groq Batch Memory Pruning (Submit) ==="
  echo "  Model: $model"
  echo "  Memory dir: $memory_dir"
  echo "  Files to evaluate: ${#memory_files[@]}"
  $DRY_RUN && echo "  Mode: DRY RUN (no submission)"
  echo ""

  # Prepare JSONL batch file
  local batch_jsonl
  batch_jsonl=$(mktemp --suffix=.jsonl)
  local file_count=0

  for file in "${memory_files[@]}"; do
    local filename
    filename=$(basename "$file")

    python3 << PYEOF >> "$batch_jsonl"
import json, sys

filename = "$filename"
model = "$model"

# Read file content (truncated to 8000 chars)
with open("$file") as f:
    content = f.read()[:8000]

prompt = f"""Evaluate this agent memory file for importance. Consider:
- Core identity, preferences, failure lessons = HIGH (0.7-1.0)
- Project context, architectural decisions = MEDIUM-HIGH (0.5-0.7)
- Routine task logs, status updates = MEDIUM (0.3-0.5)
- Debug output, temporary notes, stale context = LOW (0.1-0.3)

File: {filename}

---
{content}"""

request = {
    "custom_id": f"mem-eval-{filename}",
    "method": "POST",
    "url": "/v1/chat/completions",
    "body": {
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
                            "description": "Category tags"
                        }
                    },
                    "required": ["importance_score", "should_keep", "condensed_version", "reasoning", "tags"],
                    "additionalProperties": False
                }
            }
        }
    }
}
print(json.dumps(request))
PYEOF
    file_count=$((file_count + 1))
    echo "  Prepared: $filename"
  done

  local line_count
  line_count=$(wc -l < "$batch_jsonl")
  echo ""
  echo "  Batch file: $line_count requests in $(du -h "$batch_jsonl" | cut -f1)"

  # Check JSONL size limit (50k lines)
  if [ "$line_count" -gt 50000 ]; then
    echo "ERROR: Batch file exceeds 50,000 line limit ($line_count lines)" >&2
    echo "  Split your memory directory into smaller batches" >&2
    rm -f "$batch_jsonl"
    exit 1
  fi

  if $DRY_RUN; then
    echo ""
    echo "  [DRY RUN] Would upload $batch_jsonl and submit batch job"
    echo "  [DRY RUN] Batch JSONL preview (first 3 lines):"
    head -3 "$batch_jsonl" | python3 -c "
import json, sys
for line in sys.stdin:
    d = json.loads(line)
    print(f'    {d[\"custom_id\"]}: model={d[\"body\"][\"model\"]}')
" 2>/dev/null || true
    rm -f "$batch_jsonl"
    return
  fi

  # Step 1: Upload file to Groq Files API
  echo ""
  echo "  Uploading batch file..."
  local upload_response
  upload_response=$(curl -sf --max-time 120 \
    -H "Authorization: Bearer $api_key" \
    -F purpose="batch" \
    -F "file=@$batch_jsonl" \
    "$GROQ_API_BASE/files" 2>/dev/null) || {
    echo "ERROR: Failed to upload batch file to Groq" >&2
    rm -f "$batch_jsonl"
    exit 1
  }
  rm -f "$batch_jsonl"

  local input_file_id
  input_file_id=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read())['id'])" <<< "$upload_response")
  echo "  Uploaded: $input_file_id"

  # Step 2: Create batch job
  echo "  Creating batch job..."
  local batch_response
  batch_response=$(curl -sf --max-time 60 \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d "{\"input_file_id\": \"$input_file_id\", \"endpoint\": \"/v1/chat/completions\", \"completion_window\": \"24h\"}" \
    "$GROQ_API_BASE/batches" 2>/dev/null) || {
    echo "ERROR: Failed to create batch job" >&2
    exit 1
  }

  local batch_id batch_status
  batch_id=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read())['id'])" <<< "$batch_response")
  batch_status=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('status','unknown'))" <<< "$batch_response")

  echo "  Batch ID: $batch_id"
  echo "  Status: $batch_status"

  # Track batch job
  local jobs_json
  jobs_json=$(load_batch_jobs)
  jobs_json=$(python3 << PYEOF
import json, sys
from datetime import datetime, timezone

jobs = json.loads('''$jobs_json''')
jobs["jobs"].append({
    "batch_id": "$batch_id",
    "input_file_id": "$input_file_id",
    "status": "$batch_status",
    "file_count": $file_count,
    "model": "$model",
    "memory_dir": "$memory_dir",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "completed_at": None,
    "output_file_id": None
})
print(json.dumps(jobs, indent=2))
PYEOF
  )
  save_batch_jobs "$jobs_json"

  echo ""
  echo "  Batch submitted! Check status with:"
  echo "    proactive-amcp memory-prune --batch --poll"
  echo ""
  echo "  When complete, apply results with:"
  echo "    proactive-amcp memory-prune --batch --apply"
}

# --- POLL mode ---
do_poll() {
  local api_key
  api_key=$(get_groq_api_key) || {
    echo "FATAL: No Groq API key. Set GROQ_API_KEY env or groq.apiKey in config." >&2
    exit 1
  }

  local jobs_json
  jobs_json=$(load_batch_jobs)

  local job_count
  job_count=$(python3 -c "import json; print(len(json.loads('''$jobs_json''').get('jobs',[])))" 2>/dev/null)

  if [ "$job_count" = "0" ]; then
    echo "No batch jobs found. Submit one first:"
    echo "  proactive-amcp memory-prune --batch --submit"
    exit 0
  fi

  echo "=== Groq Batch Jobs Status ==="
  echo ""

  # Poll each pending job
  python3 << PYEOF
import json, sys, subprocess

jobs = json.loads('''$jobs_json''')
api_key = "$api_key"
base_url = "$GROQ_API_BASE"
updated = False

for job in jobs["jobs"]:
    bid = job["batch_id"]
    if job["status"] in ("completed", "failed", "expired", "cancelled"):
        print(f'  {bid}: {job["status"]} (created: {job["created_at"][:19]})')
        continue

    # Poll Groq API
    import urllib.request
    req = urllib.request.Request(
        f"{base_url}/batches/{bid}",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        new_status = data.get("status", "unknown")
        job["status"] = new_status
        counts = data.get("request_counts", {})
        total = counts.get("total", 0)
        done = counts.get("completed", 0)
        failed = counts.get("failed", 0)

        if new_status == "completed":
            job["output_file_id"] = data.get("output_file_id")
            job["error_file_id"] = data.get("error_file_id")
            from datetime import datetime, timezone
            job["completed_at"] = datetime.now(timezone.utc).isoformat()

        print(f'  {bid}: {new_status} ({done}/{total} done, {failed} failed)')
        updated = True
    except Exception as e:
        print(f'  {bid}: poll error — {e}')

# Save updated status
if updated:
    with open("$BATCH_JOBS_FILE", "w") as f:
        json.dump(jobs, f, indent=2)
    print("")
    print("  Job statuses updated in $BATCH_JOBS_FILE")
PYEOF
}

# --- APPLY mode ---
do_apply() {
  local api_key
  api_key=$(get_groq_api_key) || {
    echo "FATAL: No Groq API key. Set GROQ_API_KEY env or groq.apiKey in config." >&2
    exit 1
  }

  local jobs_json
  jobs_json=$(load_batch_jobs)

  echo "=== Groq Batch Memory Pruning (Apply) ==="
  $DRY_RUN && echo "  Mode: DRY RUN (no changes)"
  echo ""

  # Find completed jobs with output
  python3 << PYEOF
import json, sys, os, urllib.request, shutil
from datetime import datetime, timezone

jobs = json.loads('''$jobs_json''')
api_key = "$api_key"
base_url = "$GROQ_API_BASE"
dry_run = $( $DRY_RUN && echo "True" || echo "False" )
usage_file = os.path.expanduser("$GROQ_USAGE_FILE")

completed_jobs = [j for j in jobs["jobs"] if j["status"] == "completed" and j.get("output_file_id")]

if not completed_jobs:
    print("No completed batch jobs with results to apply.")
    print("  Run --poll first to check job status.")
    sys.exit(0)

total_archived = 0
total_condensed = 0
total_kept = 0
total_errors = 0
total_tokens = 0

for job in completed_jobs:
    bid = job["batch_id"]
    output_fid = job["output_file_id"]
    memory_dir = job.get("memory_dir", "")

    if not memory_dir or not os.path.isdir(memory_dir):
        print(f"  SKIP {bid}: memory dir '{memory_dir}' not found")
        continue

    archive_dir = os.path.join(memory_dir, "archive")

    print(f"  Processing batch {bid} ({job['file_count']} files)...")

    # Download results
    try:
        req = urllib.request.Request(
            f"{base_url}/files/{output_fid}/content",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            results_text = resp.read().decode()
    except Exception as e:
        print(f"    ERROR: Failed to download results — {e}")
        total_errors += 1
        continue

    # Parse results line by line
    for line in results_text.strip().split("\n"):
        if not line.strip():
            continue
        try:
            result = json.loads(line)
        except json.JSONDecodeError:
            total_errors += 1
            continue

        custom_id = result.get("custom_id", "")
        resp_body = result.get("response", {}).get("body", {})
        error = result.get("error")

        if error:
            print(f"    ERROR {custom_id}: {error}")
            total_errors += 1
            continue

        # Extract filename from custom_id (format: mem-eval-filename.md)
        if custom_id.startswith("mem-eval-"):
            filename = custom_id[len("mem-eval-"):]
        else:
            filename = custom_id

        file_path = os.path.join(memory_dir, filename)
        if not os.path.isfile(file_path):
            print(f"    SKIP {filename}: file not found (may have been pruned already)")
            continue

        # Parse evaluation from response
        try:
            content_str = resp_body.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            evaluation = json.loads(content_str)
        except (json.JSONDecodeError, IndexError, KeyError):
            print(f"    ERROR {filename}: could not parse evaluation response")
            total_errors += 1
            continue

        # Track token usage
        usage = resp_body.get("usage", {})
        total_tokens += usage.get("total_tokens", 0)

        score = float(evaluation.get("importance_score", 1.0))
        reasoning = evaluation.get("reasoning", "N/A")
        condensed_version = evaluation.get("condensed_version")

        # Apply pruning decision
        if score < 0.3:
            print(f"    ARCHIVE {filename} (score={score:.2f}) — {reasoning}")
            if not dry_run:
                os.makedirs(archive_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(archive_dir, filename))
                print(f"      -> Moved to {archive_dir}/{filename}")
            total_archived += 1

        elif score < 0.7 and condensed_version and str(condensed_version).strip() and condensed_version != "null":
            orig_size = os.path.getsize(file_path)
            new_size = len(condensed_version.encode())
            print(f"    CONDENSE {filename} (score={score:.2f}, {orig_size}B -> {new_size}B) — {reasoning}")
            if not dry_run:
                with open(file_path, "w") as f:
                    f.write(condensed_version + "\n")
                print(f"      -> Condensed inline")
            total_condensed += 1

        else:
            print(f"    KEEP {filename} (score={score:.2f}) — {reasoning}")
            total_kept += 1

    # Mark job as applied
    if not dry_run:
        job["status"] = "applied"
        job["applied_at"] = datetime.now(timezone.utc).isoformat()

# Save updated jobs
if not dry_run:
    with open("$BATCH_JOBS_FILE", "w") as f:
        json.dump(jobs, f, indent=2)

# Track cumulative usage
if total_tokens > 0 and not dry_run:
    os.makedirs(os.path.dirname(usage_file), exist_ok=True)
    try:
        with open(usage_file) as f:
            udata = json.load(f)
    except (IOError, json.JSONDecodeError):
        udata = {"total_prompt_tokens": 0, "total_completion_tokens": 0, "total_tokens": 0, "evaluations": 0, "sessions": []}

    udata["total_tokens"] += total_tokens
    udata["evaluations"] += total_archived + total_condensed + total_kept
    udata["last_used"] = datetime.now(timezone.utc).isoformat()
    udata["sessions"] = udata.get("sessions", [])[-49:] + [{
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_tokens": total_tokens,
        "source": "batch",
        "model": completed_jobs[0].get("model", "unknown") if completed_jobs else "unknown"
    }]

    with open(usage_file, "w") as f:
        json.dump(udata, f, indent=2)

print("")
print("=== Summary ===")
print(f"  Archived: {total_archived}")
print(f"  Condensed: {total_condensed}")
print(f"  Kept: {total_kept}")
print(f"  Errors: {total_errors}")
print(f"  Tokens used: {total_tokens} (at 50% batch discount)")
if dry_run:
    print("  (DRY RUN — no files were modified)")
PYEOF
}

# --- Main dispatch ---
case "$MODE" in
  submit) do_submit ;;
  poll) do_poll ;;
  apply) do_apply ;;
  *)
    echo "ERROR: Unknown mode '$MODE'" >&2
    usage
    ;;
esac
