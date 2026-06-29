#!/bin/bash
# diagnose.sh — Consolidated diagnostic hub with subcommands
#
# Subcommands:
#   health (default)  Bash health checks → structured JSON findings
#   claude            Claude-powered diagnostics with Solvr integration
#   condense          Condense verbose error logs to ~100 chars (Groq)
#   failure           Detect failure patterns in text, auto-create Problems
#   summary           Generate open problem summary for resurrection
#
# Usage:
#   ./diagnose.sh [health] [--session-dir DIR]
#   ./diagnose.sh claude [--json] [--no-solvr] [--bash-only]
#   ./diagnose.sh condense "error message"
#   ./diagnose.sh failure --input <file>
#   ./diagnose.sh summary [--learning-dir DIR]
#
# Exit codes (health): 0 = healthy, 1 = issues found
# Exit codes (claude): 0 = healthy, 1 = issues, 2 = missing prereqs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"

# ============================================================
# Subcommand dispatch
# ============================================================
case "${1:-}" in
  claude)   shift; exec "$SCRIPT_DIR/_diagnose-claude.sh" "$@" ;;
  condense) shift; exec "$SCRIPT_DIR/_diagnose-condense.sh" "$@" ;;
  failure)  shift; exec python3 "$SCRIPT_DIR/detect-failure.py" "$@" ;;
  summary)  shift; exec python3 "$SCRIPT_DIR/generate-problem-summary.py" "$@" ;;
  health)   shift ;;  # Fall through to health checks below
esac

# ============================================================
# Health checks (default subcommand)
# ============================================================

command -v python3 &>/dev/null || { echo "FATAL: python3 required but not found" >&2; exit 2; }

SESSION_DIR="${SESSION_DIR:-$HOME/.openclaw/agents/main/sessions}"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
DISK_THRESHOLD="${DISK_THRESHOLD:-10}"
MEM_THRESHOLD="${MEM_THRESHOLD:-10}"
CRASH_LOOP_THRESHOLD="${CRASH_LOOP_THRESHOLD:-10}"  # restarts per hour
STATE_FILE="${STATE_FILE:-$HOME/.amcp/watchdog-state.json}"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --session-dir) SESSION_DIR="$2"; shift 2 ;;
    --config) OPENCLAW_CONFIG="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Collect findings as JSON array entries
FINDINGS=()

add_finding() {
  local type="$1"
  local severity="$2"
  local message="$3"
  local path="${4:-}"
  local fix_cmd="${5:-}"

  local entry
  entry=$(python3 -c "
import json
print(json.dumps({
    'type': '$type',
    'severity': '$severity',
    'message': '''$message''',
    'path': '$path',
    'fix_command': '$fix_cmd'
}))
")
  FINDINGS+=("$entry")
}

# ============================================================
# Check 1: Gateway process
# ============================================================
check_gateway_process() {
  if pgrep -f "openclaw-gateway" > /dev/null 2>&1; then
    return 0
  fi
  if pgrep -f "openclaw.*gateway" > /dev/null 2>&1; then
    return 0
  fi
  add_finding "gateway_down" "critical" \
    "Gateway process not running" \
    "" \
    "$SCRIPT_DIR/restore-agent.sh"
  return 1
}

# ============================================================
# Check 2: Gateway health endpoint
# ============================================================
check_gateway_health() {
  # Determine which ports to check: GATEWAY_PORT env > openclaw.json > defaults
  local ports_to_check=()
  if [ -n "${GATEWAY_PORT:-}" ]; then
    ports_to_check=("$GATEWAY_PORT")
  elif [ -f "$OPENCLAW_CONFIG" ]; then
    local cfg_port
    cfg_port=$(python3 -c "import json; print(json.load(open('$OPENCLAW_CONFIG')).get('gateway',{}).get('port',''))" 2>/dev/null || echo '')
    if [ -n "$cfg_port" ]; then
      ports_to_check=("$cfg_port")
    fi
  fi
  # Fall back to default ports if nothing configured
  if [ ${#ports_to_check[@]} -eq 0 ]; then
    ports_to_check=(3141 8080 18789)
  fi

  for port in "${ports_to_check[@]}"; do
    if curl -s --max-time 5 "http://localhost:${port}/health" > /dev/null 2>&1; then
      return 0
    fi
  done
  add_finding "gateway_unresponsive" "warning" \
    "Gateway process exists but health endpoint not responding (checked ports: ${ports_to_check[*]})" \
    "" \
    "systemctl --user restart openclaw-gateway"
  return 1
}

# ============================================================
# Check 3: Session corruption (the 400 error loop)
# ============================================================
check_session_corruption() {
  if [ ! -d "$SESSION_DIR" ]; then
    return 0
  fi

  local sessions_json="$SESSION_DIR/sessions.json"
  if [ ! -f "$sessions_json" ]; then
    return 0
  fi

  # Use Python to find the active session and scan for corruption
  local result
  result=$(SESSION_DIR="$SESSION_DIR" python3 << 'PYEOF'
import json, os, glob

session_dir = os.environ["SESSION_DIR"]
sessions_json = os.path.join(session_dir, "sessions.json")

if not os.path.exists(sessions_json):
    print("no_sessions_json")
    exit(0)

# Find active session IDs
with open(sessions_json) as f:
    sessions = json.load(f)

session_ids = []
for key, val in sessions.items():
    if isinstance(val, dict) and "sessionId" in val:
        session_ids.append(val["sessionId"])

if not session_ids:
    # Fall back to most recent .jsonl files
    files = sorted(glob.glob(os.path.join(session_dir, "*.jsonl")),
                   key=os.path.getmtime, reverse=True)[:3]
    session_ids = [os.path.splitext(os.path.basename(f))[0] for f in files]

# Scan each session for the corruption pattern
corrupted = []
for sid in session_ids:
    filepath = os.path.join(session_dir, f"{sid}.jsonl")
    if not os.path.exists(filepath):
        continue

    has_partial = False
    has_400_loop = False
    error_400_count = 0

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except:
                continue

            msg = obj.get("message", {})

            # Check for partialJson in tool calls
            for block in msg.get("content", []):
                if isinstance(block, dict) and "partialJson" in block:
                    has_partial = True

            # Check for 400 tool_use_id error loop
            err = msg.get("errorMessage", "")
            if "unexpected `tool_use_id` found in `tool_result` blocks" in err:
                error_400_count += 1

    if error_400_count >= 2:
        has_400_loop = True

    if has_partial or has_400_loop:
        corrupted.append({
            "session_id": sid,
            "path": filepath,
            "has_partial_json": has_partial,
            "error_400_count": error_400_count
        })

if corrupted:
    print(json.dumps(corrupted))
else:
    print("clean")
PYEOF
  )

  if [ "$result" = "clean" ] || [ "$result" = "no_sessions_json" ]; then
    return 0
  fi

  # Parse each corrupted session and add findings
  local count
  count=$(echo "$result" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
  local i=0
  while [ "$i" -lt "$count" ]; do
    local session_path
    session_path=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)[$i]['path'])")
    local session_id
    session_id=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)[$i]['session_id'])")
    local err_count
    err_count=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)[$i]['error_400_count'])")

    add_finding "session_corrupted" "critical" \
      "Session $session_id has corrupted tool_use blocks (${err_count} cascading 400 errors)" \
      "$session_path" \
      "$SCRIPT_DIR/session-fix.sh --fix --session-dir $SESSION_DIR --session-id $session_id"

    i=$((i + 1))
  done

  return 1
}

# ============================================================
# Check 4: Config validity
# ============================================================
check_config() {
  if [ ! -f "$OPENCLAW_CONFIG" ]; then
    add_finding "config_missing" "warning" \
      "OpenClaw config not found at $OPENCLAW_CONFIG" \
      "$OPENCLAW_CONFIG" \
      ""
    return 1
  fi

  if ! python3 -c "import json; json.load(open('$OPENCLAW_CONFIG'))" 2>/dev/null; then
    add_finding "config_invalid" "critical" \
      "OpenClaw config is not valid JSON" \
      "$OPENCLAW_CONFIG" \
      "$SCRIPT_DIR/restore-agent.sh"
    return 1
  fi

  return 0
}

# ============================================================
# Check 4b: Semantic config validation (plugins, profiles, etc.)
# ============================================================
check_config_semantic() {
  # Only run if JSON syntax check passed — semantic validation on broken JSON is pointless
  # Also skip if openclaw CLI is not available
  local openclaw_bin
  openclaw_bin=$(command -v openclaw 2>/dev/null || echo "")
  if [ -z "$openclaw_bin" ]; then
    return 0
  fi

  # Run openclaw doctor --non-interactive with timeout
  # Capture both stdout and stderr (warnings go to stderr)
  local doctor_output
  doctor_output=$(timeout 30 "$openclaw_bin" doctor --non-interactive 2>&1 || true)

  # Strip ANSI escape codes for pattern matching
  local clean_output
  clean_output=$(echo "$doctor_output" | sed 's/\x1b\[[0-9;]*m//g')

  # Scan for semantic error patterns
  local semantic_errors=()

  # Plugin-related errors
  if echo "$clean_output" | grep -qi "plugin not found"; then
    semantic_errors+=("plugin not found")
  fi
  if echo "$clean_output" | grep -qi "plugin id mismatch"; then
    semantic_errors+=("plugin id mismatch")
  fi
  if echo "$clean_output" | grep -qi "duplicate plugin id"; then
    semantic_errors+=("duplicate plugin id")
  fi

  # Profile-related errors
  if echo "$clean_output" | grep -qi "profile not found"; then
    semantic_errors+=("profile not found")
  fi
  if echo "$clean_output" | grep -qi "auth-profiles.*not found\|auth profile.*invalid\|auth profile.*missing"; then
    semantic_errors+=("auth profile issue")
  fi

  # General config errors
  if echo "$clean_output" | grep -qi "Invalid config"; then
    semantic_errors+=("invalid config")
  fi

  # Plugin load failures (errors, not warnings)
  if echo "$clean_output" | grep -qi "Errors: [1-9]"; then
    semantic_errors+=("plugin load errors")
  fi

  if [ ${#semantic_errors[@]} -gt 0 ]; then
    local issues_str
    issues_str=$(printf "%s, " "${semantic_errors[@]}")
    issues_str="${issues_str%, }"
    add_finding "config_semantic_invalid" "critical" \
      "OpenClaw config has semantic errors: ${issues_str}" \
      "$OPENCLAW_CONFIG" \
      "openclaw doctor --fix"
    return 1
  fi

  return 0
}

# ============================================================
# Check 4c: Session health — detect stuck sessions (logic-level, not file-level)
# ============================================================
check_session_health() {
  if [ ! -d "$SESSION_DIR" ]; then
    return 0
  fi

  local sessions_json="$SESSION_DIR/sessions.json"
  if [ ! -f "$sessions_json" ]; then
    return 0
  fi

  # Use Python to check recent turns for error patterns indicating a stuck session
  local result
  result=$(SESSION_DIR="$SESSION_DIR" python3 << 'PYEOF'
import json, os, glob, time

session_dir = os.environ["SESSION_DIR"]
sessions_json = os.path.join(session_dir, "sessions.json")

if not os.path.exists(sessions_json):
    print("no_sessions")
    exit(0)

# Find active session IDs
try:
    with open(sessions_json) as f:
        sessions = json.load(f)
except (json.JSONDecodeError, IOError):
    print("no_sessions")
    exit(0)

session_ids = []
for key, val in sessions.items():
    if isinstance(val, dict) and "sessionId" in val:
        session_ids.append(val["sessionId"])

if not session_ids:
    files = sorted(glob.glob(os.path.join(session_dir, "*.jsonl")),
                   key=os.path.getmtime, reverse=True)[:3]
    session_ids = [os.path.splitext(os.path.basename(f))[0] for f in files]

if not session_ids:
    print("no_sessions")
    exit(0)

# Error patterns indicating a stuck session (logic-level, not file corruption)
ERROR_PATTERNS = [
    "400",
    "rate_limit",
    "rate limit",
    "overloaded",
    "capacity",
    "internal_error",
    "server_error",
    "context_length_exceeded",
    "invalid_request_error",
]

# Check the most recent N turns of each active session
RECENT_TURNS = 20
ERROR_THRESHOLD = 10  # If >= this many of recent turns are errors, session is stuck

stuck_sessions = []

for sid in session_ids:
    filepath = os.path.join(session_dir, f"{sid}.jsonl")
    if not os.path.exists(filepath):
        continue

    # Read all turns
    turns = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                turns.append(obj)
            except (json.JSONDecodeError, ValueError):
                continue

    if len(turns) < 5:
        # Too few turns to judge
        continue

    # Look at the most recent turns
    recent = turns[-RECENT_TURNS:]
    error_count = 0
    success_count = 0
    error_types = set()

    for turn in recent:
        msg = turn.get("message", {})
        role = msg.get("role", "")

        # Check for error messages
        err = msg.get("errorMessage", "") or ""
        stop_reason = msg.get("stop_reason", "") or turn.get("stopReason", "") or ""

        has_error = False
        for pattern in ERROR_PATTERNS:
            if pattern in err.lower():
                has_error = True
                error_types.add(pattern)
                break

        # Also check for HTTP error status in tool results
        content = msg.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text", "") or ""
                    for pattern in ERROR_PATTERNS:
                        if pattern in text.lower():
                            has_error = True
                            error_types.add(pattern)
                            break

        if has_error:
            error_count += 1
        elif role == "assistant" and content:
            success_count += 1

    # Stuck = high error rate in recent turns AND low success rate
    if error_count >= ERROR_THRESHOLD and success_count <= 2:
        stuck_sessions.append({
            "session_id": sid,
            "path": filepath,
            "error_count": error_count,
            "success_count": success_count,
            "recent_turns": len(recent),
            "error_types": sorted(error_types)
        })

if stuck_sessions:
    print(json.dumps(stuck_sessions))
else:
    print("healthy")
PYEOF
  )

  if [ "$result" = "healthy" ] || [ "$result" = "no_sessions" ]; then
    return 0
  fi

  # Parse each stuck session and add findings
  local count
  count=$(echo "$result" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
  local i=0
  while [ "$i" -lt "$count" ]; do
    local session_id err_count err_types
    session_id=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)[$i]['session_id'])")
    err_count=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)[$i]['error_count'])")
    err_types=$(echo "$result" | python3 -c "import json,sys; print(', '.join(json.load(sys.stdin)[$i]['error_types']))")

    add_finding "session_stuck" "critical" \
      "Session $session_id is stuck: $err_count errors in last 20 turns (patterns: $err_types)" \
      "$SESSION_DIR" \
      "$SCRIPT_DIR/session-fix.sh --fix --session-dir $SESSION_DIR --session-id $session_id"

    i=$((i + 1))
  done

  return 1
}

# ============================================================
# Check 5: Disk space (auto-cleanup if > 85%)
# ============================================================
check_disk() {
  local disk_pct disk_free
  disk_pct=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}') || return 0
  disk_free=$((100 - disk_pct))

  # Auto-cleanup if disk > 85%
  if [ "$disk_pct" -gt 85 ] 2>/dev/null; then
    echo "[diagnose] Disk at ${disk_pct}%, running auto-cleanup..." >&2
    if [ -x "$SCRIPT_DIR/disk-cleanup.sh" ]; then
      "$SCRIPT_DIR/disk-cleanup.sh" --threshold 85 >&2 || true
      # Re-check after cleanup
      disk_pct=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}') || return 0
      disk_free=$((100 - disk_pct))
    fi
  fi

  if [ "$disk_free" -lt "$DISK_THRESHOLD" ] 2>/dev/null; then
    add_finding "disk_low" "warning" \
      "Disk space low: ${disk_free}% free (threshold: ${DISK_THRESHOLD}%)" \
      "$HOME" \
      "$SCRIPT_DIR/disk-cleanup.sh"
    return 1
  fi
  return 0
}

# ============================================================
# Check 6: Memory
# ============================================================
check_memory() {
  local mem_free
  mem_free=$(free | awk '/Mem:/ {printf "%.0f", $7/$2*100}') || return 0

  if [ "$mem_free" -lt "$MEM_THRESHOLD" ] 2>/dev/null; then
    add_finding "memory_low" "warning" \
      "Memory low: ${mem_free}% available (threshold: ${MEM_THRESHOLD}%)" \
      "" \
      ""
    return 1
  fi
  return 0
}

# ============================================================
# Check 7: Crash-loop detection (restart frequency)
# ============================================================
check_crash_loop() {
  if [ ! -f "$STATE_FILE" ]; then
    return 0
  fi

  local result
  result=$(WATCHDOG_STATE_FILE="$STATE_FILE" \
  WATCHDOG_CRASH_THRESHOLD="$CRASH_LOOP_THRESHOLD" \
  python3 << 'PYEOF'
import json, os, sys
from datetime import datetime, timezone

state_file = os.environ["WATCHDOG_STATE_FILE"]
threshold = int(os.environ["WATCHDOG_CRASH_THRESHOLD"])

try:
    with open(state_file) as f:
        state = json.load(f)
except (json.JSONDecodeError, FileNotFoundError, IOError):
    print("no_state")
    sys.exit(0)

history = state.get("restart_history", [])
if not history:
    print("no_restarts")
    sys.exit(0)

# Count restarts in the last hour (3600 seconds)
now = datetime.now(timezone.utc)
one_hour_ago = now.timestamp() - 3600
count = 0
for ts_str in history:
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if ts.timestamp() >= one_hour_ago:
            count += 1
    except (ValueError, TypeError):
        continue

if count >= threshold:
    print(json.dumps({"count": count, "threshold": threshold, "window": "1h"}))
else:
    print("ok")
PYEOF
  )

  if [ "$result" = "no_state" ] || [ "$result" = "no_restarts" ] || [ "$result" = "ok" ]; then
    return 0
  fi

  local count
  count=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)['count'])")

  add_finding "crash_loop_detected" "critical" \
    "Crash-loop detected: $count restarts in last hour (threshold: $CRASH_LOOP_THRESHOLD)" \
    "$STATE_FILE" \
    ""

  return 1
}

# ============================================================
# Check 8: Auth/OAuth status (catch expiration before death)
# ============================================================
check_auth_status() {
  local openclaw_bin
  openclaw_bin=$(command -v openclaw 2>/dev/null || echo "")
  if [ -z "$openclaw_bin" ]; then
    return 0
  fi

  local auth_exit=0
  timeout 30 "$openclaw_bin" models status --check >/dev/null 2>&1 || auth_exit=$?

  case $auth_exit in
    0) return 0 ;;  # OK
    2)
      add_finding "auth_expiring" "warning" \
        "OAuth token expiring soon — renew at console.anthropic.com" \
        "" \
        ""
      return 1
      ;;
    1)
      add_finding "auth_expired" "critical" \
        "OAuth token expired — agent cannot authenticate to model provider" \
        "" \
        "$SCRIPT_DIR/restore-agent.sh"
      return 1
      ;;
    124)
      # timeout exit code — treat as potential issue
      add_finding "auth_check_timeout" "warning" \
        "Auth status check timed out after 30s" \
        "" \
        ""
      return 1
      ;;
    *)
      # Unknown exit code — skip silently
      return 0
      ;;
  esac
}

# ============================================================
# Check 9: Soul-evil hook detection (personality override risk)
# ============================================================
check_soul_evil_hook() {
  local openclaw_bin
  openclaw_bin=$(command -v openclaw 2>/dev/null || echo "")
  local hook_found=false
  local hook_source=""

  # Method 1: openclaw hooks list (if CLI available)
  if [ -n "$openclaw_bin" ]; then
    local hooks_output
    hooks_output=$(timeout 10 "$openclaw_bin" hooks list 2>/dev/null || true)
    if echo "$hooks_output" | grep -qi "soul-evil"; then
      hook_found=true
      hook_source="openclaw hooks list"
    fi
  fi

  # Method 2: Check openclaw.json for soul-evil references
  if [ "$hook_found" = false ] && [ -f "$OPENCLAW_CONFIG" ]; then
    if DIAGNOSE_CONFIG="$OPENCLAW_CONFIG" python3 -c "
import json, os, sys
try:
    c = json.load(open(os.environ['DIAGNOSE_CONFIG']))
    text = json.dumps(c).lower()
    sys.exit(0 if 'soul-evil' in text or 'soul_evil' in text else 1)
except:
    sys.exit(1)
" 2>/dev/null; then
      hook_found=true
      hook_source="openclaw.json config"
    fi
  fi

  # Method 3: Check hooks directory for soul-evil files
  if [ "$hook_found" = false ]; then
    local hooks_dir="$HOME/.openclaw/hooks"
    if [ -d "$hooks_dir" ] && ls "$hooks_dir" 2>/dev/null | grep -qi "soul-evil"; then
      hook_found=true
      hook_source="hooks directory"
    fi
  fi

  if [ "$hook_found" = false ]; then
    return 0
  fi

  # Suspicious timing: is hook present while agent is in unhealthy state?
  local timing_note=""
  if [ -f "$STATE_FILE" ]; then
    timing_note=$(DIAGNOSE_STATE="$STATE_FILE" python3 -c "
import json, os
try:
    s = json.load(open(os.environ['DIAGNOSE_STATE']))
    state = s.get('state', 'HEALTHY')
    if state in ('DEAD', 'DEGRADED'):
        lh = s.get('lastHealthy', 'unknown')
        print('. Suspicious: hook present while agent in ' + state + ' state (last healthy: ' + lh + ')')
except:
    pass
" 2>/dev/null || true)
  fi

  add_finding "soul_evil_hook_detected" "critical" \
    "soul-evil hook detected via ${hook_source} — personality may be overridden${timing_note}" \
    "" \
    ""

  return 1
}

# ============================================================
# Run all checks
# ============================================================
has_issues=false

check_gateway_process || has_issues=true
# Only check health if gateway process exists
if [ "$has_issues" = false ]; then
  check_gateway_health || has_issues=true
fi
check_session_corruption || has_issues=true
check_session_health || has_issues=true
config_json_ok=true
check_config || { has_issues=true; config_json_ok=false; }
# Only run semantic validation if JSON syntax is valid
if [ "$config_json_ok" = true ]; then
  check_config_semantic || has_issues=true
fi
check_disk || has_issues=true
check_memory || has_issues=true
check_crash_loop || has_issues=true
check_auth_status || has_issues=true
check_soul_evil_hook || has_issues=true

# ============================================================
# Output structured JSON
# ============================================================
status="healthy"
if [ "$has_issues" = true ]; then
  status="unhealthy"
fi

# Build JSON output
findings_json="["
first=true
for f in "${FINDINGS[@]}"; do
  if [ "$first" = true ]; then
    first=false
  else
    findings_json+=","
  fi
  findings_json+="$f"
done
findings_json+="]"

python3 -c "
import json, sys
findings = json.loads('''$findings_json''')
result = {
    'status': '$status',
    'findings': findings,
    'checks_run': 11,
    'findings_count': len(findings)
}
print(json.dumps(result, indent=2))
"

if [ "$has_issues" = true ]; then
  exit 1
fi
exit 0
