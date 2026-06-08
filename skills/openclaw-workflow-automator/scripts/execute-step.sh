#!/usr/bin/env bash
set -euo pipefail

# execute-step.sh — Execute a single workflow step with safety checks,
# approval flow, browser support, and screenshot capture.

BASE_DIR="$HOME/.openclaw/workflow-automator"
SCREENSHOT_DIR="$BASE_DIR/screenshots"
LOG_FILE="$BASE_DIR/execution.log"
DEFAULT_TIMEOUT=60
BROWSER_TIMEOUT=120
AUTONOMOUS="false"
CUSTOM_TIMEOUT=""
CUSTOM_SCREENSHOT_DIR=""

BROWSER_TYPES="browser-navigate browser-click browser-fill browser-extract browser-screenshot browser-wait"
UNSAFE_PATTERNS="rm -rf /|mkfs|dd if=.*of=/dev|chmod -R 777 /|:(){ :|:& };:"
EXFIL_PATTERNS='\| *curl |\| *wget |> */dev/tcp|\| *nc |\| *netcat |> */dev/udp'
ENCODING_PATTERNS='base64|\\\\x[0-9a-fA-F]|\$\x27\\\\x|eval |exec |source /dev'
INTERPRETER_PATTERN='^(py[a-z]*[23]?|perl|ruby|node|php|lua)$'

usage() {
    cat <<'EOF'
Usage: execute-step.sh <plan.json> <step-number> [options]

Execute a single step from a workflow plan.

Arguments:
  plan.json      Path to the workflow plan JSON file
  step-number    Step number to execute (1-based)

Options:
  --autonomous           Skip user confirmation (for scheduled runs).
                         Verifies plan approval hash before executing.
                         Blocks if plan was modified since approval.
  --screenshot-dir PATH  Override screenshot directory
  --timeout SECONDS      Override default timeout
  --help                 Show this help message

Behavior:
  - Shows the exact command/action before execution
  - Waits for user approval (unless --autonomous)
  - Captures stdout, stderr, exit code, and duration
  - For browser steps: describes action, captures screenshots
  - On failure: captures debug screenshot for browser steps
  - Logs everything to ~/.openclaw/workflow-automator/execution.log

Exit codes:
  0  Step succeeded
  1  Step failed
  2  User rejected step
  3  Invalid input
EOF
    exit 0
}

# Parse arguments
[ "${1:-}" = "--help" ] && usage

if [ $# -lt 2 ]; then
    echo "Error: Missing required arguments. Use --help for usage." >&2
    exit 3
fi

PLAN_FILE="$1"
STEP_NUM="$2"
shift 2

while [ $# -gt 0 ]; do
    case "$1" in
        --autonomous)
            AUTONOMOUS="true"
            shift
            ;;
        --screenshot-dir)
            CUSTOM_SCREENSHOT_DIR="$2"
            shift 2
            ;;
        --timeout)
            CUSTOM_TIMEOUT="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo "Error: Unknown option: $1" >&2
            exit 3
            ;;
    esac
done

# Environment preflight check (runs once, cached for 1 hour)
SCRIPT_DIR_PRE="$(cd "$(dirname "$0")" && pwd)"
if [ -x "$SCRIPT_DIR_PRE/check-environment.sh" ]; then
    if ! "$SCRIPT_DIR_PRE/check-environment.sh" >/dev/null 2>&1; then
        echo "Error: Environment check failed. Run 'check-environment.sh --verbose' for details." >&2
        "$SCRIPT_DIR_PRE/check-environment.sh" --no-cache 2>&1
        exit 3
    fi
fi

# Validate inputs
[ ! -f "$PLAN_FILE" ] && { echo "Error: Plan file not found: $PLAN_FILE" >&2; exit 3; }

if ! jq empty "$PLAN_FILE" 2>/dev/null; then
    echo "Error: Invalid JSON: $PLAN_FILE" >&2
    exit 3
fi

STEP_COUNT=$(jq '.steps | length' "$PLAN_FILE")
STEP_INDEX=$((STEP_NUM - 1))

if [ "$STEP_INDEX" -lt 0 ] || [ "$STEP_INDEX" -ge "$STEP_COUNT" ]; then
    echo "Error: Step $STEP_NUM out of range (1-$STEP_COUNT)" >&2
    exit 3
fi

# Set up directories
if [ -n "$CUSTOM_SCREENSHOT_DIR" ]; then
    SCREENSHOT_DIR="$CUSTOM_SCREENSHOT_DIR"
fi
mkdir -p "$SCREENSHOT_DIR" "$(dirname "$LOG_FILE")"

# Extract step details
WORKFLOW_NAME=$(jq -r '.workflow_name // "unnamed"' "$PLAN_FILE")
STEP_DESC=$(jq -r ".steps[$STEP_INDEX].description // \"Step $STEP_NUM\"" "$PLAN_FILE")
STEP_TYPE=$(jq -r ".steps[$STEP_INDEX].type // \"unknown\"" "$PLAN_FILE")
STEP_CMD=$(jq -r ".steps[$STEP_INDEX].command // empty" "$PLAN_FILE")
STEP_INPUT=$(jq -r ".steps[$STEP_INDEX].input // \"(none)\"" "$PLAN_FILE")
STEP_OUTPUT=$(jq -r ".steps[$STEP_INDEX].output // \"(none)\"" "$PLAN_FILE")

# Browser-specific fields
STEP_URL=$(jq -r ".steps[$STEP_INDEX].url // empty" "$PLAN_FILE")
STEP_SELECTOR=$(jq -r ".steps[$STEP_INDEX].selector // .steps[$STEP_INDEX].element // empty" "$PLAN_FILE")
STEP_VALUE=$(jq -r ".steps[$STEP_INDEX].value // empty" "$PLAN_FILE")

# Determine timeout
is_browser_step() {
    for bt in $BROWSER_TYPES; do
        [ "$STEP_TYPE" = "$bt" ] && return 0
    done
    return 1
}

if [ -n "$CUSTOM_TIMEOUT" ]; then
    TIMEOUT="$CUSTOM_TIMEOUT"
elif is_browser_step; then
    TIMEOUT="$BROWSER_TIMEOUT"
else
    TIMEOUT="$DEFAULT_TIMEOUT"
fi

# Slug for file naming
WORKFLOW_SLUG=$(echo "$WORKFLOW_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TIMESTAMP_FILE=$(date -u +"%Y-%m-%d_%H-%M-%S")

# Log helper
log_entry() {
    echo "[$TIMESTAMP] [step:$STEP_NUM] $1" >> "$LOG_FILE"
}

# Screenshot helper
take_screenshot() {
    local label="$1"
    local filename="${WORKFLOW_SLUG}_step${STEP_NUM}_${label}_${TIMESTAMP_FILE}.png"
    local filepath="$SCREENSHOT_DIR/$filename"
    # In real execution, OpenClaw's browser primitive captures the screenshot.
    # This script outputs the instruction for the agent runtime.
    echo "{\"action\": \"screenshot\", \"path\": \"$filepath\"}"
    echo "$filepath"
}

# Comprehensive command validation — runs in BOTH interactive and autonomous modes
validate_command() {
    local cmd="$1"
    local blocked="false"
    local needs_confirmation="false"
    local warnings=""

    # 1. Destructive patterns (hard block — BOTH modes)
    if echo "$cmd" | grep -qE "$UNSAFE_PATTERNS"; then
        echo "BLOCKED: Destructive command pattern: $cmd" >&2
        log_entry "BLOCKED destructive command: $cmd"
        blocked="true"
    fi

    # 2. Data exfiltration patterns
    if echo "$cmd" | grep -qE "$EXFIL_PATTERNS"; then
        log_entry "DETECTED exfiltration pattern: $cmd"
        if [ "$AUTONOMOUS" = "true" ]; then
            echo "BLOCKED: Exfiltration pattern not allowed in autonomous mode: $cmd" >&2
            blocked="true"
        else
            warnings="${warnings}  ⚠ EXFILTRATION: This command pipes data to an external endpoint\n"
            needs_confirmation="true"
        fi
    fi

    # 3. Encoding/obfuscation patterns
    if echo "$cmd" | grep -qE "$ENCODING_PATTERNS"; then
        log_entry "DETECTED encoding pattern: $cmd"
        if [ "$AUTONOMOUS" = "true" ]; then
            echo "BLOCKED: Obfuscated commands not allowed in autonomous mode: $cmd" >&2
            blocked="true"
        else
            warnings="${warnings}  ⚠ OBFUSCATION: This command uses encoding/eval patterns\n"
            needs_confirmation="true"
        fi
    fi

    # 4. Restricted mode: check allowed_commands and interpreter rule
    RESTRICTED_MODE=$(jq -r '.restricted_mode // false' "$PLAN_FILE" 2>/dev/null || echo "false")
    if [ "$RESTRICTED_MODE" = "true" ]; then
        local base_cmd
        base_cmd=$(echo "$cmd" | sed 's/[|;&].*//' | awk '{print $1}' | sed 's|.*/||')

        # No-interpreter rule
        if echo "$base_cmd" | grep -qE "$INTERPRETER_PATTERN"; then
            if echo "$cmd" | grep -qE ' -[ce] '; then
                echo "BLOCKED: Inline interpreter execution forbidden in restricted mode: $cmd" >&2
                log_entry "BLOCKED interpreter in restricted mode: $cmd"
                blocked="true"
            fi
        fi

        # Allowed commands check
        local allowed_commands
        allowed_commands=$(jq -r '.allowed_commands // empty' "$PLAN_FILE" 2>/dev/null || true)
        if [ -n "$allowed_commands" ] && [ "$allowed_commands" != "null" ]; then
            local cmd_allowed="false"
            while IFS= read -r allowed; do
                if [ "$base_cmd" = "$allowed" ]; then
                    cmd_allowed="true"
                    break
                fi
            done < <(jq -r '.allowed_commands[]' "$PLAN_FILE" 2>/dev/null)
            if [ "$cmd_allowed" = "false" ]; then
                echo "BLOCKED: Command '$base_cmd' not in allowed_commands (restricted mode)" >&2
                log_entry "BLOCKED unlisted command in restricted mode: $base_cmd"
                blocked="true"
            fi
        fi
    fi

    # 5. Interactive mode: require secondary confirmation for dangerous patterns
    if [ "$needs_confirmation" = "true" ] && [ "$AUTONOMOUS" = "false" ] && [ "$blocked" = "false" ]; then
        echo "" >&2
        echo "╔══════════════════════════════════════════╗" >&2
        echo "║     ⚠  DANGEROUS PATTERN DETECTED  ⚠    ║" >&2
        echo "╠══════════════════════════════════════════╣" >&2
        printf "%b" "$warnings" >&2
        echo "║                                          ║" >&2
        echo "║  Command: $cmd" >&2
        echo "╚══════════════════════════════════════════╝" >&2
        echo "" >&2
        printf "This command has been flagged. Type CONFIRM to proceed, or anything else to block: " >&2
        read -r danger_confirm
        if [ "$danger_confirm" != "CONFIRM" ]; then
            echo "BLOCKED: User declined dangerous command" >&2
            log_entry "BLOCKED by user confirmation: $cmd"
            blocked="true"
        else
            log_entry "USER CONFIRMED dangerous command: $cmd"
        fi
    fi

    if [ "$blocked" = "true" ]; then
        return 1
    fi
    return 0
}

# Legacy wrapper for backwards compatibility
safety_check() {
    validate_command "$1"
}

# Display step info
echo "STEP $STEP_NUM of $STEP_COUNT: $STEP_DESC"
echo "─────────────────────────"
echo "  Type:   $STEP_TYPE"
echo "  Input:  $STEP_INPUT"
echo "  Output: $STEP_OUTPUT"

# For browser steps, describe what will happen
if is_browser_step; then
    echo ""
    echo "  Browser action:"
    case "$STEP_TYPE" in
        browser-navigate)
            echo "    Navigate to: $STEP_URL"
            ;;
        browser-click)
            echo "    Click element: $STEP_SELECTOR"
            ;;
        browser-fill)
            echo "    Fill field '$STEP_SELECTOR' with value"
            ;;
        browser-extract)
            echo "    Extract content from: ${STEP_SELECTOR:-page}"
            ;;
        browser-screenshot)
            echo "    Capture screenshot of: ${STEP_SELECTOR:-full page}"
            ;;
        browser-wait)
            echo "    Wait for element: $STEP_SELECTOR"
            ;;
    esac
else
    if [ -n "$STEP_CMD" ]; then
        echo "  Command: $STEP_CMD"
    fi
fi

echo ""

# Approval flow (unless autonomous)
if [ "$AUTONOMOUS" = "false" ]; then
    printf "Execute this step? (yes / no / skip) "
    read -r approval
    case "$approval" in
        yes|y|go|approved)
            ;;
        skip|s)
            echo "Status: SKIPPED"
            log_entry "SKIPPED by user"
            exit 0
            ;;
        *)
            echo "Status: REJECTED"
            log_entry "REJECTED by user"
            exit 2
            ;;
    esac
fi

# Plan approval check (autonomous mode only)
if [ "$AUTONOMOUS" = "true" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    if [ -x "$SCRIPT_DIR/plan-approval.sh" ]; then
        approval_result=$("$SCRIPT_DIR/plan-approval.sh" check "$PLAN_FILE" 2>&1) || {
            echo "BLOCKED: Plan approval check failed in autonomous mode" >&2
            echo "  $approval_result" >&2
            log_entry "BLOCKED: Autonomous execution denied — $approval_result"
            NOTIFY_CHANNEL=$(jq -r '.notify.channel // empty' "$PLAN_FILE" 2>/dev/null || true)
            if [ -n "$NOTIFY_CHANNEL" ] && [ -x "$SCRIPT_DIR/notify.sh" ]; then
                "$SCRIPT_DIR/notify.sh" "$NOTIFY_CHANNEL" \
                    "Workflow '$WORKFLOW_NAME' BLOCKED: Plan integrity check failed. Re-approve the plan to continue." \
                    --urgent >/dev/null 2>&1 || true
            fi
            exit 1
        }
        log_entry "Plan approval verified: $approval_result"
    fi
fi

log_entry "EXECUTING: type=$STEP_TYPE desc=\"$STEP_DESC\""

# Session guard for autonomous browser steps
if [ "$AUTONOMOUS" = "true" ] && is_browser_step; then
    SESSION_GUARD="$(cd "$(dirname "$0")" && pwd)/session-guard.sh"
    if [ -x "$SESSION_GUARD" ]; then
        MAX_SESSION_AGE=$(jq -r '.max_session_age_days // 7' "$PLAN_FILE" 2>/dev/null || echo 7)
        session_result=$("$SESSION_GUARD" check "$WORKFLOW_NAME" --max-age "$MAX_SESSION_AGE" 2>&1) || {
            echo "BLOCKED: Browser session check failed" >&2
            echo "  $session_result" >&2
            log_entry "BLOCKED: Session guard — $session_result"
            NOTIFY_CHANNEL=$(jq -r '.notify.channel // empty' "$PLAN_FILE" 2>/dev/null || true)
            if [ -n "$NOTIFY_CHANNEL" ] && [ -x "$(cd "$(dirname "$0")" && pwd)/notify.sh" ]; then
                "$(cd "$(dirname "$0")" && pwd)/notify.sh" "$NOTIFY_CHANNEL" \
                    "Workflow '$WORKFLOW_NAME' PAUSED: Browser session expired. Please re-authenticate." \
                    --urgent >/dev/null 2>&1 || true
            fi
            exit 1
        }
        log_entry "Session guard passed: $session_result"
    fi
fi

# Post-run session cleanup check
CLEAR_SESSION=$(jq -r '.clear_session // false' "$PLAN_FILE" 2>/dev/null || echo "false")

# Take pre-screenshot for critical browser actions
if is_browser_step; then
    case "$STEP_TYPE" in
        browser-click|browser-fill)
            pre_screenshot=$(take_screenshot "before")
            log_entry "Pre-screenshot: $pre_screenshot"
            ;;
    esac
fi

# Execute the step
START_TIME=$(date +%s)
EXIT_CODE=0
STDOUT_FILE=$(mktemp)
STDERR_FILE=$(mktemp)

if is_browser_step; then
    # Browser steps: output a JSON instruction for the agent runtime
    # The agent runtime interprets these and drives the actual browser
    browser_instruction=""
    case "$STEP_TYPE" in
        browser-navigate)
            browser_instruction="{\"action\": \"goto\", \"url\": \"$STEP_URL\", \"timeout\": $TIMEOUT}"
            ;;
        browser-click)
            browser_instruction="{\"action\": \"click\", \"selector\": \"$STEP_SELECTOR\", \"timeout\": $TIMEOUT}"
            ;;
        browser-fill)
            browser_instruction="{\"action\": \"fill\", \"selector\": \"$STEP_SELECTOR\", \"value\": \"$STEP_VALUE\", \"timeout\": $TIMEOUT}"
            ;;
        browser-extract)
            browser_instruction="{\"action\": \"extract\", \"selector\": \"${STEP_SELECTOR:-body}\", \"timeout\": $TIMEOUT}"
            ;;
        browser-screenshot)
            browser_instruction="{\"action\": \"screenshot\", \"selector\": \"${STEP_SELECTOR:-}\", \"path\": \"$SCREENSHOT_DIR/${WORKFLOW_SLUG}_step${STEP_NUM}_${TIMESTAMP_FILE}.png\"}"
            ;;
        browser-wait)
            browser_instruction="{\"action\": \"wait\", \"selector\": \"$STEP_SELECTOR\", \"timeout\": $TIMEOUT}"
            ;;
    esac
    echo "$browser_instruction" > "$STDOUT_FILE"
    echo "$browser_instruction"
    # In real execution, the agent runtime would execute this and return results.
    # For now, we output the instruction and mark success.
    EXIT_CODE=0
elif [ -n "$STEP_CMD" ]; then
    # Shell command execution
    if ! safety_check "$STEP_CMD"; then
        EXIT_CODE=1
        echo "Command blocked by safety check" > "$STDERR_FILE"
    else
        # Execute with timeout (use gtimeout on macOS if timeout unavailable)
        TIMEOUT_CMD="timeout"
        if ! command -v timeout >/dev/null 2>&1; then
            if command -v gtimeout >/dev/null 2>&1; then
                TIMEOUT_CMD="gtimeout"
            else
                TIMEOUT_CMD=""
            fi
        fi
        if [ -n "$TIMEOUT_CMD" ]; then
            if "$TIMEOUT_CMD" "$TIMEOUT" bash -c "$STEP_CMD" > "$STDOUT_FILE" 2> "$STDERR_FILE"; then
                EXIT_CODE=0
            else
                EXIT_CODE=$?
            fi
        else
            if bash -c "$STEP_CMD" > "$STDOUT_FILE" 2> "$STDERR_FILE"; then
                EXIT_CODE=0
            else
                EXIT_CODE=$?
            fi
        fi
    fi
else
    # No command — step is an instruction for the agent runtime
    echo "Agent instruction: $STEP_DESC" > "$STDOUT_FILE"
    EXIT_CODE=0
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Capture output
STDOUT_CONTENT=$(head -50 "$STDOUT_FILE" 2>/dev/null || true)
STDERR_CONTENT=$(cat "$STDERR_FILE" 2>/dev/null || true)

# Take post-screenshot for browser steps
if is_browser_step; then
    if [ $EXIT_CODE -eq 0 ]; then
        post_screenshot=$(take_screenshot "after")
        log_entry "Post-screenshot: $post_screenshot"
    else
        # Failure screenshot for debugging
        fail_screenshot=$(take_screenshot "failure")
        log_entry "Failure screenshot: $fail_screenshot"
    fi
fi

# Display results
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "Status:   SUCCESS (exit code 0)"
else
    echo "Status:   FAILED (exit code $EXIT_CODE)"
fi
echo "Duration: ${DURATION}s"
echo "Timeout:  ${TIMEOUT}s"

if [ -n "$STDOUT_CONTENT" ]; then
    echo ""
    echo "Output:"
    echo "$STDOUT_CONTENT" | sed 's/^/  /'
fi

if [ -n "$STDERR_CONTENT" ]; then
    echo ""
    echo "Errors:"
    echo "$STDERR_CONTENT" | sed 's/^/  /'
fi

# Log the result
log_entry "RESULT: exit=$EXIT_CODE duration=${DURATION}s"

# Audit log entry
AUDIT_SCRIPT="$(cd "$(dirname "$0")" && pwd)/audit-log.sh"
if [ -x "$AUDIT_SCRIPT" ]; then
    AUDIT_MODE="interactive"
    [ "$AUTONOMOUS" = "true" ] && AUDIT_MODE="autonomous"
    AUDIT_CMD="${STEP_CMD:-$STEP_DESC}"
    AUDIT_HASH_FLAG=""
    [ "$AUTONOMOUS" = "true" ] && AUDIT_HASH_FLAG="--hash-verified"
    "$AUDIT_SCRIPT" write "$WORKFLOW_NAME" "$STEP_NUM" "$STEP_TYPE" "$AUDIT_CMD" "$EXIT_CODE" "$AUDIT_MODE" $AUDIT_HASH_FLAG 2>/dev/null || true
fi

# Write step result JSON for run log
RUNS_DIR="$BASE_DIR/runs/$WORKFLOW_SLUG"
mkdir -p "$RUNS_DIR"
RESULT_FILE="$RUNS_DIR/step${STEP_NUM}_${TIMESTAMP_FILE}.json"

jq -n \
    --arg wf "$WORKFLOW_NAME" \
    --arg desc "$STEP_DESC" \
    --arg type "$STEP_TYPE" \
    --argjson num "$STEP_NUM" \
    --argjson exit_code "$EXIT_CODE" \
    --argjson duration "$DURATION" \
    --arg stdout "$STDOUT_CONTENT" \
    --arg stderr "$STDERR_CONTENT" \
    --arg ts "$TIMESTAMP" \
    --arg mode "$([ "$AUTONOMOUS" = "true" ] && echo "autonomous" || echo "interactive")" \
    '{
        workflow_name: $wf,
        step_number: $num,
        description: $desc,
        type: $type,
        exit_code: $exit_code,
        duration_seconds: $duration,
        stdout: $stdout,
        stderr: $stderr,
        mode: $mode,
        executed_at: $ts
    }' > "$RESULT_FILE"

# Clean up temp files
rm -f "$STDOUT_FILE" "$STDERR_FILE"

# Prompt for next step (unless autonomous)
if [ "$AUTONOMOUS" = "false" ] && [ $EXIT_CODE -eq 0 ]; then
    NEXT_STEP=$((STEP_NUM + 1))
    if [ "$NEXT_STEP" -le "$STEP_COUNT" ]; then
        echo ""
        echo "→ Continue to Step $NEXT_STEP? (yes / no / retry)"
    fi
fi

# Post-run session cleanup (if clear_session is true and this is the last step)
if [ "$CLEAR_SESSION" = "true" ] && [ "$STEP_NUM" -eq "$STEP_COUNT" ]; then
    CLEANUP_SCRIPT="$(cd "$(dirname "$0")" && pwd)/session-guard.sh"
    if [ -x "$CLEANUP_SCRIPT" ]; then
        "$CLEANUP_SCRIPT" cleanup "$WORKFLOW_NAME" 2>/dev/null || true
        log_entry "Session cleared after final step (clear_session=true)"
    fi
fi

exit $EXIT_CODE
