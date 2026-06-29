#!/bin/bash
# watchdog.sh - Health check, diagnosis, and intelligent recovery
# Usage: ./watchdog.sh [--continuous]
#
# Uses diagnose.sh to detect issues, then routes to the right fix:
#   session_corrupted       → session-fix.sh + gateway restart (lightweight)
#   gateway_down            → full resurrection
#   gateway_unresponsive    → gateway restart
#   config_invalid          → resurrection (config fix tier)
#   config_semantic_invalid → openclaw doctor --fix

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"

# Ensure Node.js webcrypto is available for amcp CLI (fixes "crypto.subtle must be defined")
# Node 18 needs this flag; Node 20+ has webcrypto by default (flag is a harmless no-op)
# Critical for systemd/cron contexts where env may be minimal
case "${NODE_OPTIONS:-}" in
  *--experimental-global-webcrypto*) ;;
  *) export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--experimental-global-webcrypto" ;;
esac
STATE_FILE="$HOME/.amcp/watchdog-state.json"
LOCK_FILE="$HOME/.amcp/resurrection.lock"
AGENT_NAME="${AGENT_NAME:-ClaudiusThePirateEmperor}"
CONTINUOUS="${1:-}"
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"  # seconds
FAIL_THRESHOLD="${FAIL_THRESHOLD:-2}"   # consecutive failures before DEAD
RETRY_DELAY_INITIAL="${RETRY_DELAY_INITIAL:-300}"  # 5 min initial retry delay
RETRY_DELAY_MAX="${RETRY_DELAY_MAX:-1800}"          # 30 min max retry delay
ESCALATION_THRESHOLD="${ESCALATION_THRESHOLD:-5}"   # same error N times → escalate
CRASH_LOOP_THRESHOLD="${CRASH_LOOP_THRESHOLD:-10}"  # restarts per hour before escalation
SESSION_DIR="${SESSION_DIR:-$HOME/.openclaw/agents/main/sessions}"

# ============================================================
# Identity pre-flight — validate before operating
# ============================================================
validate_identity() {
  if [ ! -f "$IDENTITY_PATH" ]; then
    echo "FATAL: Invalid AMCP identity — run amcp identity create or amcp identity validate for details"
    exit 1
  fi
  if ! "$AMCP_CLI" identity validate --identity "$IDENTITY_PATH" 2>/dev/null; then
    echo "FATAL: Invalid AMCP identity — run amcp identity create or amcp identity validate for details"
    exit 1
  fi
}

validate_identity

# Warn if secrets found in identity.json (they belong in config.json)
warn_identity_secrets() {
  python3 -c "
import json, os, sys
p = os.path.expanduser('$IDENTITY_PATH')
if not os.path.exists(p): sys.exit(0)
d = json.load(open(p))
bad = [k for k in d if k in ('pinata_jwt','pinata_api_key','solvr_api_key','api_key','apiKey','jwt','token','secret','password','mnemonic','email','notifyTarget')]
if bad:
    print(f'WARNING: Secrets found in identity.json: {\", \".join(bad)}', file=sys.stderr)
    print('  Migrate with: proactive-amcp config set <key> <value>', file=sys.stderr)
" 2>&1 || true
}
warn_identity_secrets

mkdir -p "$(dirname "$STATE_FILE")"

# Initialize state if not exists
if [ ! -f "$STATE_FILE" ]; then
  cat > "$STATE_FILE" << 'EOJSON'
{
  "state": "HEALTHY",
  "consecutiveFailures": 0,
  "lastCheck": null,
  "lastHealthy": null,
  "resurrectionPid": null,
  "lastResurrectionAttempt": null,
  "retryDelay": 0,
  "restart_history": []
}
EOJSON
fi

# ============================================================
# Diagnose — delegates to diagnose.sh, returns structured JSON
# ============================================================
run_diagnosis() {
  local diag_output
  local diag_status=0
  diag_output=$("$SCRIPT_DIR/diagnose.sh" 2>/dev/null) || diag_status=$?
  echo "$diag_output"
  return $diag_status
}

# Extract finding types from diagnose JSON
get_finding_types() {
  local diag_json="$1"
  echo "$diag_json" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    for f in d.get('findings', []):
        print(f['type'])
except:
    pass
"
}

# Extract error summary string from diagnose JSON (for state file)
get_error_summary() {
  local diag_json="$1"
  echo "$diag_json" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    types = [f['type'] for f in d.get('findings', [])]
    print(' '.join(types))
except:
    print('diagnosis_failed')
"
}

# Check if a specific finding type exists
has_finding() {
  local diag_json="$1"
  local finding_type="$2"
  echo "$diag_json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for f in d.get('findings', []):
    if f['type'] == '$finding_type':
        print('yes')
        exit(0)
print('no')
"
}

# Get the fix command for a finding type
get_fix_command() {
  local diag_json="$1"
  local finding_type="$2"
  echo "$diag_json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for f in d.get('findings', []):
    if f['type'] == '$finding_type':
        print(f.get('fix_command', ''))
        exit(0)
"
}

# ============================================================
# State management
# ============================================================
update_state() {
  local new_state="$1"
  local failures="$2"
  local errors="$3"

  WATCHDOG_STATE_FILE="$STATE_FILE" \
  WATCHDOG_NEW_STATE="$new_state" \
  WATCHDOG_FAILURES="$failures" \
  WATCHDOG_ERRORS="$errors" \
  python3 << 'EOF'
import json, os
from datetime import datetime

state_file = os.environ["WATCHDOG_STATE_FILE"]
new_state = os.environ["WATCHDOG_NEW_STATE"]
failures = int(os.environ["WATCHDOG_FAILURES"])
errors_str = os.environ["WATCHDOG_ERRORS"]

try:
    with open(state_file) as f:
        state = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    state = {"state": "HEALTHY", "consecutiveFailures": 0, "lastCheck": None,
             "lastHealthy": None, "resurrectionPid": None,
             "lastResurrectionAttempt": None, "retryDelay": 0}

state["state"] = new_state
state["consecutiveFailures"] = failures
state["lastCheck"] = datetime.now().isoformat()
state["errors"] = errors_str.split() if errors_str else []

# Track error history for stuck-state detection (keep last 20 entries)
if "errorHistory" not in state:
    state["errorHistory"] = []
if errors_str:
    state["errorHistory"].append(errors_str)
    state["errorHistory"] = state["errorHistory"][-20:]

if new_state == "HEALTHY":
    state["lastHealthy"] = datetime.now().isoformat()
    state["retryDelay"] = 0
    state["resurrectionPid"] = None
    state["errorHistory"] = []
    state["restart_history"] = []

tmp = state_file + ".tmp"
with open(tmp, "w") as f:
    json.dump(state, f, indent=2)
os.replace(tmp, state_file)
EOF
}

get_state() {
  python3 -c "
import json
try:
    print(json.load(open('$STATE_FILE')).get('state', 'UNKNOWN'))
except (json.JSONDecodeError, FileNotFoundError):
    print('UNKNOWN')
"
}

get_failures() {
  python3 -c "
import json
try:
    print(json.load(open('$STATE_FILE')).get('consecutiveFailures', 0))
except (json.JSONDecodeError, FileNotFoundError):
    print(0)
"
}

# ============================================================
# Error history — track stability to detect stuck states
# ============================================================

# Read last N error summaries from state file
get_previous_errors() {
  local count="${1:-$ESCALATION_THRESHOLD}"
  WATCHDOG_STATE_FILE="$STATE_FILE" \
  WATCHDOG_COUNT="$count" \
  python3 << 'PYEOF'
import json, os
state_file = os.environ["WATCHDOG_STATE_FILE"]
count = int(os.environ["WATCHDOG_COUNT"])
try:
    with open(state_file) as f:
        state = json.load(f)
    history = state.get("errorHistory", [])
    for entry in history[-count:]:
        print(entry)
except (json.JSONDecodeError, FileNotFoundError):
    pass
PYEOF
}

# Check if same error has persisted for N consecutive checks
# Returns 0 (true) if stuck, 1 (false) if not
# Prints the stuck error type to stdout when stuck
check_error_stability() {
  local current_errors="$1"
  WATCHDOG_STATE_FILE="$STATE_FILE" \
  WATCHDOG_THRESHOLD="$ESCALATION_THRESHOLD" \
  WATCHDOG_CURRENT="$current_errors" \
  python3 << 'PYEOF'
import json, os, sys

state_file = os.environ["WATCHDOG_STATE_FILE"]
threshold = int(os.environ["WATCHDOG_THRESHOLD"])
current = os.environ["WATCHDOG_CURRENT"]

try:
    with open(state_file) as f:
        state = json.load(f)
    history = state.get("errorHistory", [])
except (json.JSONDecodeError, FileNotFoundError):
    sys.exit(1)

if not current or not history:
    sys.exit(1)

# Count consecutive matching errors from end of history
consecutive = 0
for entry in reversed(history):
    if entry == current:
        consecutive += 1
    else:
        break

# Current check makes it consecutive+1
if consecutive + 1 >= threshold:
    print(current)
    sys.exit(0)
sys.exit(1)
PYEOF
}

# ============================================================
# Resurrection management (lock, PID, retry backoff)
# ============================================================
is_resurrection_running() {
  if [ ! -f "$LOCK_FILE" ]; then
    return 1
  fi
  local pid
  pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    return 0
  fi
  rm -f "$LOCK_FILE"
  return 1
}

get_retry_delay() {
  python3 -c "
import json
try:
    print(json.load(open('$STATE_FILE')).get('retryDelay', 0))
except (json.JSONDecodeError, FileNotFoundError):
    print(0)
"
}

get_last_resurrection_attempt() {
  python3 -c "
import json
from datetime import datetime
try:
    s = json.load(open('$STATE_FILE'))
except (json.JSONDecodeError, FileNotFoundError):
    print(0)
    exit(0)
ts = s.get('lastResurrectionAttempt')
if ts:
    try:
        print(int(datetime.fromisoformat(ts).timestamp()))
    except:
        print(0)
else:
    print(0)
"
}

record_resurrection_launch() {
  local pid="$1"
  local current_delay
  current_delay=$(get_retry_delay)
  local next_delay
  if [ "$current_delay" -eq 0 ]; then
    next_delay="$RETRY_DELAY_INITIAL"
  else
    next_delay=$((current_delay * 2))
    if [ "$next_delay" -gt "$RETRY_DELAY_MAX" ]; then
      next_delay="$RETRY_DELAY_MAX"
    fi
  fi

  WATCHDOG_STATE_FILE="$STATE_FILE" \
  WATCHDOG_RES_PID="$pid" \
  WATCHDOG_NEXT_DELAY="$next_delay" \
  python3 << 'PYEOF'
import json, os
from datetime import datetime, timezone

state_file = os.environ["WATCHDOG_STATE_FILE"]
try:
    with open(state_file) as f:
        state = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    state = {"state": "DEAD", "consecutiveFailures": 0, "lastCheck": None,
             "lastHealthy": None, "resurrectionPid": None,
             "lastResurrectionAttempt": None, "retryDelay": 0,
             "restart_history": []}
now = datetime.now(timezone.utc)
state["resurrectionPid"] = int(os.environ["WATCHDOG_RES_PID"])
state["lastResurrectionAttempt"] = now.isoformat()
state["retryDelay"] = int(os.environ["WATCHDOG_NEXT_DELAY"])

# Track restart timestamp for crash-loop detection (keep last 50)
history = state.get("restart_history", [])
history.append(now.isoformat())
state["restart_history"] = history[-50:]

tmp = state_file + ".tmp"
with open(tmp, "w") as f:
    json.dump(state, f, indent=2)
os.replace(tmp, state_file)
PYEOF
}

launch_resurrection() {
  if is_resurrection_running; then
    echo "⏳ Resurrection already in progress (PID $(cat "$LOCK_FILE"))"
    return 0
  fi
  echo "🔄 Launching resurrection..."
  "$SCRIPT_DIR/restore-agent.sh" &
  local res_pid=$!
  record_resurrection_launch "$res_pid"
  echo "🔄 Resurrection PID: $res_pid"
}

should_retry_resurrection() {
  local retry_delay
  retry_delay=$(get_retry_delay)
  if [ "$retry_delay" -eq 0 ]; then
    return 0
  fi
  local last_attempt
  last_attempt=$(get_last_resurrection_attempt)
  local now
  now=$(date +%s)
  local elapsed=$((now - last_attempt))
  if [ "$elapsed" -ge "$retry_delay" ]; then
    return 0
  fi
  echo "⏳ Retry cooldown: ${elapsed}s / ${retry_delay}s"
  return 1
}

# ============================================================
# Error condensing — use Groq to shorten error msgs in notifications
# ============================================================
condense_error_msg() {
  local msg="$1"
  # Only condense if diagnose.sh exists and message is long
  if [ "${#msg}" -le 100 ] || [ ! -x "$SCRIPT_DIR/diagnose.sh" ]; then
    echo "$msg"
    return
  fi
  local condensed
  condensed=$("$SCRIPT_DIR/diagnose.sh" condense "$msg" 2>/dev/null || true)
  echo "${condensed:-$msg}"
}

# ============================================================
# Escalation context — structured reports for human notifications
# ============================================================

# Map finding types to suggested manual fixes
get_suggested_fix() {
  local finding_type="$1"
  case "$finding_type" in
    gateway_down)
      echo "systemctl --user status openclaw-gateway; journalctl --user -u openclaw-gateway --since '1h ago'" ;;
    gateway_unresponsive)
      echo "curl -sf http://localhost:18789/health; jq . ~/.openclaw/openclaw.json" ;;
    config_invalid|config_semantic_invalid)
      echo "jq . ~/.openclaw/openclaw.json; ls ~/.amcp/config-backups/ and restore latest" ;;
    session_corrupted|session_stuck)
      echo "proactive-amcp session-fix; systemctl --user restart openclaw-gateway" ;;
    crash_loop_detected)
      echo "STOP auto-recovery. Review ~/.amcp/recovery-*.log for root cause" ;;
    auth_expired)
      echo "Renew OAuth at console.anthropic.com; restart gateway" ;;
    auth_expiring|auth_check_timeout)
      echo "Renew OAuth at console.anthropic.com before it expires" ;;
    soul_evil_hook_detected)
      echo "Check hooks: openclaw hooks list; disable soul-evil hook immediately" ;;
    *)
      echo "Review: ls -lt ~/.amcp/recovery-*.log | head -3" ;;
  esac
}

# Build structured ISSUE → TRIED → RESULT → NEXT report for notifications
build_escalation_report() {
  local icon="$1"
  local agent="$2"
  local issues="$3"
  local tried="$4"
  local result="$5"
  local failures="$6"

  local report="${icon} [${agent}] Recovery Report"
  report+=$'\n'"ISSUE: ${issues}"
  report+=$'\n'"TRIED: ${tried}"
  report+=$'\n'"RESULT: ${result}"
  report+=$'\n'"FAILURES: ${failures} consecutive"

  # Suggested manual fix based on primary finding type
  local primary
  primary=$(echo "$issues" | awk '{print $1}')
  if [ -n "$primary" ]; then
    local suggestion
    suggestion=$(get_suggested_fix "$primary")
    report+=$'\n'"MANUAL FIX: ${suggestion}"
  fi

  echo "$report"
}

# ============================================================
# Fix routing — pick the right fix based on diagnosis
# ============================================================
try_fix_session() {
  local fix_cmd="$1"
  echo "🔧 Fixing corrupted session..."
  if eval "$fix_cmd" 2>&1; then
    echo "✅ Session repaired"
    # Restart gateway to pick up the fixed session
    if systemctl --user restart openclaw-gateway 2>/dev/null; then
      echo "✅ Gateway restarted after session fix"
      return 0
    fi
  fi
  echo "❌ Session fix failed"
  return 1
}

restart_gateway() {
  if systemctl --user restart openclaw-gateway 2>/dev/null; then
    echo "✅ Gateway restarted"
    return 0
  fi
  echo "⚠️ Gateway restart failed (systemctl)"
  return 1
}

# ============================================================
# Stuck session recovery — 3-tier fix before resurrection
# ============================================================
try_fix_stuck_session() {
  local diag_json="$1"

  # Get the base fix command from the finding (includes session-dir and session-id)
  local fix_cmd
  fix_cmd=$(get_fix_command "$diag_json" "session_stuck")
  if [ -z "$fix_cmd" ]; then
    echo "⚠️ No fix command for session_stuck finding"
    return 1
  fi

  # Tier 1: Truncate trailing error turns from the session
  echo "🔧 [Stuck Session T1] Truncating error turns..."
  if eval "$fix_cmd --truncate-errors" 2>&1; then
    echo "✅ Error turns truncated"
    if restart_gateway; then
      return 0
    fi
  fi

  # Tier 2: Try gateway session reset via openclaw CLI (if available)
  echo "🔧 [Stuck Session T2] Attempting session context reset..."
  local openclaw_bin
  openclaw_bin=$(command -v openclaw 2>/dev/null || echo "")
  if [ -n "$openclaw_bin" ]; then
    if timeout 30 "$openclaw_bin" session reset 2>/dev/null; then
      echo "✅ Session context reset via openclaw CLI"
      if restart_gateway; then
        return 0
      fi
    fi
  else
    echo "⚠️ openclaw CLI not available, skipping T2"
  fi

  # Tier 3: Archive stuck session and start fresh (last resort before resurrection)
  echo "🔧 [Stuck Session T3] Archiving stuck session, starting fresh..."
  if eval "$fix_cmd --archive" 2>&1; then
    echo "✅ Session archived"
    if restart_gateway; then
      return 0
    fi
  fi

  echo "❌ All stuck session tiers failed"
  return 1
}

# ============================================================
# Solvr workflow — search for solutions, post problems
# ============================================================
run_solvr_workflow() {
  local error_summary="$1"
  
  if [ ! -x "$SCRIPT_DIR/solvr-workflow.sh" ]; then
    echo "⚠️ Solvr workflow not available"
    return 1
  fi
  
  echo "🔍 Searching Solvr for existing solutions..."
  local result
  result=$("$SCRIPT_DIR/solvr-workflow.sh" workflow "$error_summary" "$AGENT_NAME" 2>&1) || true
  
  local action
  action=$(echo "$result" | grep -o '"action":\s*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"/\1/' || echo "")
  
  if [ "$action" = "try_existing" ]; then
    echo "✅ Solvr has solutions — check output above"
    return 0
  elif [ "$action" = "posted_problem" ]; then
    local problem_id
    problem_id=$(echo "$result" | grep -o '"problem_id":\s*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"/\1/' || echo "")
    echo "📌 Posted to Solvr: $problem_id"
    # Store problem_id for later approach updates
    echo "$problem_id" > "$HOME/.amcp/current-solvr-problem.txt"
    return 1
  fi
  
  return 1
}

# Update Solvr approach after fix attempt
update_solvr_approach() {
  local status="$1"  # succeeded or failed
  local method="$2"
  
  local problem_id
  problem_id=$(cat "$HOME/.amcp/current-solvr-problem.txt" 2>/dev/null || echo "")
  
  if [ -z "$problem_id" ] || [ ! -x "$SCRIPT_DIR/solvr-workflow.sh" ]; then
    return 0
  fi
  
  echo "📝 Updating Solvr: approach $status"
  "$SCRIPT_DIR/solvr-workflow.sh" approach "$problem_id" "$method" "$status" 2>/dev/null || true
  
  if [ "$status" = "succeeded" ]; then
    rm -f "$HOME/.amcp/current-solvr-problem.txt"
  fi
}

# ============================================================
# Main check — diagnose then route
# ============================================================
do_check() {
  local current_state=$(get_state)
  local failures=$(get_failures)

  echo "[$(date -Iseconds)] Checking health..."

  local diag_json=""
  local diag_status=0
  diag_json=$(run_diagnosis) || diag_status=$?

  if [ "$diag_status" -eq 0 ]; then
    # Healthy — clear everything
    if [ "$current_state" != "HEALTHY" ]; then
      echo "✅ Recovered! State: $current_state -> HEALTHY"
      [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Recovered from $current_state"
      rm -f "$LOCK_FILE"
    fi
    update_state "HEALTHY" 0 ""
    # Backup config on healthy check (only when valid and changed)
    [ -x "$SCRIPT_DIR/config.sh" ] && "$SCRIPT_DIR/config.sh" backup 2>/dev/null || true
    echo "✅ HEALTHY"
    return 0
  fi

  # Auth expiry — handle before normal failure flow
  local has_auth_expiring
  has_auth_expiring=$(has_finding "$diag_json" "auth_expiring")
  if [ "$has_auth_expiring" = "yes" ]; then
    echo "⚠️ OAuth token expiring soon"
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "⚠️ [$AGENT_NAME] OAuth expiring soon — renew at console.anthropic.com"
  fi

  local has_auth_expired
  has_auth_expired=$(has_finding "$diag_json" "auth_expired")
  if [ "$has_auth_expired" = "yes" ]; then
    echo "🔑 OAuth token expired — triggering immediate resurrection"
    failures=$((failures + 1))
    update_state "DEAD" "$failures" "auth_expired"
    local report
    report=$(build_escalation_report "🔑" "$AGENT_NAME" \
      "OAuth token expired" \
      "Immediate resurrection (auth failure is fatal)" \
      "Recovery in progress" "$failures")
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
    launch_resurrection
    return 2
  fi

  # Soul-evil hook — security alert (notify but don't trigger resurrection)
  if [ "$(has_finding "$diag_json" "soul_evil_hook_detected")" = "yes" ]; then
    echo "🚨 WARNING: soul-evil hook detected — personality may be overridden"
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "🚨 [$AGENT_NAME] soul-evil hook detected — personality override risk! Investigate immediately."
  fi

  # Issues found — determine what and how to fix
  local errors
  errors=$(get_error_summary "$diag_json")
  failures=$((failures + 1))
  echo "⚠️ Check failed ($failures/$FAIL_THRESHOLD): $errors"

  # *** SOLVR WORKFLOW: Search for existing solutions first ***
  run_solvr_workflow "$errors" || true

  # Crash-loop detection — immediate escalation, skip normal fix routing
  local has_crash_loop
  has_crash_loop=$(has_finding "$diag_json" "crash_loop_detected")
  if [ "$has_crash_loop" = "yes" ]; then
    echo "🚨 CRASH-LOOP DETECTED: Too many restarts in the last hour"
    echo "🚨 Stopping automatic recovery to prevent further damage"
    update_state "DEAD" "$failures" "crash_loop_detected $errors"
    local condensed_errors
    condensed_errors=$(condense_error_msg "$errors")
    local report
    report=$(build_escalation_report "🚨🔁" "$AGENT_NAME" \
      "crash_loop_detected $condensed_errors" \
      "Automatic recovery PAUSED (exceeded ${CRASH_LOOP_THRESHOLD}/hour)" \
      "Manual intervention required" "$failures")
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
    return 2
  fi

  local has_session_corrupt
  has_session_corrupt=$(has_finding "$diag_json" "session_corrupted")
  local has_gateway_down
  has_gateway_down=$(has_finding "$diag_json" "gateway_down")
  local has_config_semantic
  has_config_semantic=$(has_finding "$diag_json" "config_semantic_invalid")

  # Semantic config errors — try openclaw doctor --fix before escalating
  if [ "$has_config_semantic" = "yes" ]; then
    echo "🔍 Diagnosis: semantic config errors detected"
    local fix_cmd
    fix_cmd=$(get_fix_command "$diag_json" "config_semantic_invalid")
    if [ -n "$fix_cmd" ]; then
      echo "🔧 Running: $fix_cmd"
      if eval "$fix_cmd" 2>&1; then
        echo "✅ Config fix applied, restarting gateway..."
        if systemctl --user restart openclaw-gateway 2>/dev/null; then
          update_state "HEALTHY" 0 ""
          [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Semantic config errors auto-fixed via openclaw doctor"
          return 0
        fi
      fi
      echo "❌ Config fix failed, continuing with other checks"
    fi
  fi

  # Session corruption with gateway still running = lightweight fix
  if [ "$has_session_corrupt" = "yes" ] && [ "$has_gateway_down" != "yes" ]; then
    echo "🔍 Diagnosis: session corrupted (gateway still running)"
    local fix_cmd
    fix_cmd=$(get_fix_command "$diag_json" "session_corrupted")
    if [ -n "$fix_cmd" ] && try_fix_session "$fix_cmd"; then
      update_state "HEALTHY" 0 ""
      update_solvr_approach "succeeded" "session-fix.sh for session_corrupted"
      [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Session corruption auto-fixed"
      return 0
    fi
    update_solvr_approach "failed" "session-fix.sh for session_corrupted"
    echo "❌ Session fix failed, escalating to resurrection"
  fi

  # Session stuck (logic errors, 400 loops) with gateway still running = tiered fix
  local has_session_stuck
  has_session_stuck=$(has_finding "$diag_json" "session_stuck")
  if [ "$has_session_stuck" = "yes" ] && [ "$has_gateway_down" != "yes" ]; then
    echo "🔍 Diagnosis: session stuck (gateway still running)"
    if try_fix_stuck_session "$diag_json"; then
      update_state "HEALTHY" 0 ""
      update_solvr_approach "succeeded" "tiered-fix for session_stuck"
      [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Stuck session auto-fixed"
      return 0
    fi
    update_solvr_approach "failed" "tiered-fix for session_stuck"
    echo "❌ Stuck session fix failed, escalating to resurrection"
  fi

  # Check for stuck state — same error persisting beyond escalation threshold
  local stuck_errors=""
  stuck_errors=$(check_error_stability "$errors") || true

  if [ -n "$stuck_errors" ]; then
    echo "🚨 STUCK STATE: Same errors for $ESCALATION_THRESHOLD+ checks: $stuck_errors"
    echo "🚨 Escalating — restarts won't fix this, trying config-level recovery"

    # Route by stuck error type
    if echo "$stuck_errors" | grep -q "config_semantic_invalid"; then
      echo "🔧 Escalation: config_semantic_invalid → skipping restart, direct config restoration"
      if [ -x "$SCRIPT_DIR/config.sh" ]; then
        if "$SCRIPT_DIR/config.sh" fix 2>&1; then
          echo "✅ Config restored via escalation"
          update_state "HEALTHY" 0 ""
          [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Stuck config error auto-fixed via escalation (after $failures failures)"
          return 0
        fi
      fi
      echo "❌ Config fix escalation failed, proceeding to resurrection"
    fi

    if echo "$stuck_errors" | grep -q "gateway_unresponsive"; then
      echo "🔧 Escalation: gateway_unresponsive → trying config fix before resurrection"
      if [ -x "$SCRIPT_DIR/config.sh" ]; then
        if "$SCRIPT_DIR/config.sh" fix 2>&1; then
          echo "✅ Config restored via escalation (gateway was unresponsive)"
          update_state "HEALTHY" 0 ""
          [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "✅ [$AGENT_NAME] Stuck gateway error auto-fixed via config restoration (after $failures failures)"
          return 0
        fi
      fi
      echo "❌ Config fix didn't help, proceeding to resurrection"
    fi

    # Stuck and escalation fixes failed — force resurrection regardless of threshold
    update_state "DEAD" "$failures" "$errors"
    local condensed_errors
    condensed_errors=$(condense_error_msg "$errors")
    local report
    report=$(build_escalation_report "🚨" "$AGENT_NAME" \
      "$condensed_errors" \
      "Escalation fixes failed, launching full resurrection" \
      "Stuck state ($ESCALATION_THRESHOLD+ same failures)" "$failures")
    [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
    launch_resurrection
    return 2
  fi

  # Gateway down or fix failed — use threshold + resurrection flow
  if [ "$failures" -ge "$FAIL_THRESHOLD" ]; then
    if [ "$current_state" != "DEAD" ]; then
      echo "☠️ State: $current_state -> DEAD"
      update_state "DEAD" "$failures" "$errors"
      local condensed_errors
      condensed_errors=$(condense_error_msg "$errors")
      local report
      report=$(build_escalation_report "☠️" "$AGENT_NAME" \
        "$condensed_errors" \
        "Starting resurrection (restart → config fix → rehydrate)" \
        "Recovery in progress" "$failures")
      [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
      launch_resurrection
      return 2
    fi

    # Already DEAD — retry if cooldown elapsed
    update_state "DEAD" "$failures" "$errors"
    if ! is_resurrection_running; then
      if should_retry_resurrection; then
        echo "🔄 Retrying resurrection (previous attempt failed)"
        local condensed_errors
        condensed_errors=$(condense_error_msg "$errors")
        local report
        report=$(build_escalation_report "🔄" "$AGENT_NAME" \
          "$condensed_errors" \
          "Retrying resurrection (previous attempt failed)" \
          "Retry in progress" "$failures")
        [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "$report"
        launch_resurrection
      fi
    fi
  else
    update_state "CHECKING" "$failures" "$errors"
  fi

  return 1
}

# ============================================================
# Main
# ============================================================
echo "=== AMCP Watchdog ==="
echo "Agent: $AGENT_NAME"
echo "State file: $STATE_FILE"

if [ "$CONTINUOUS" = "--continuous" ]; then
  echo "Mode: Continuous (checking every ${CHECK_INTERVAL}s)"
  [ -x "$SCRIPT_DIR/notify.sh" ] && "$SCRIPT_DIR/notify.sh" "🔄 [$AGENT_NAME] Watchdog started (continuous mode)"

  while true; do
    do_check || true
    sleep "$CHECK_INTERVAL"
  done
else
  echo "Mode: Single check"
  do_check
  exit $?
fi
