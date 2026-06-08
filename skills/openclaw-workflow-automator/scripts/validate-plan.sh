#!/usr/bin/env bash
set -euo pipefail

# validate-plan.sh — Validate a workflow plan JSON file
# Checks step structure, types, browser step requirements,
# schedule entries, and notification channels.

VALID_TYPES="file-read file-write file-transform data-parse data-merge compute condition api-call notify script-run browser-navigate browser-click browser-fill browser-extract browser-screenshot browser-wait schedule-set schedule-once webhook-listen"
BROWSER_TYPES="browser-navigate browser-click browser-fill browser-extract browser-screenshot browser-wait"
SCHEDULE_TYPES="schedule-set schedule-once"
EXFIL_PATTERNS='\| *curl |\| *wget |> */dev/tcp|\| *nc |\| *netcat |> */dev/udp'
ENCODING_PATTERNS='base64|\\\\x[0-9a-fA-F]|\$\x27\\\\x|eval |exec |source /dev'
INTERPRETER_PATTERN='^(py[a-z]*[23]?|perl|ruby|node|php|lua)$'
SENSITIVE_SITES="bank|banking|chase|wellsfargo|bofa|citi|paypal|venmo|zelle|crypto|coinbase|binance|robinhood|schwab|fidelity|vanguard|ameritrade|etrade|treasury"

usage() {
    cat <<'EOF'
Usage: validate-plan.sh <plan.json>

Validates a workflow plan JSON file.

Checks:
  - JSON is valid and has required top-level fields
  - Each step has: number, description, type, input, output
  - Step types are recognized
  - Browser steps have target URL and action details
  - Schedule entries have valid cron expressions
  - Notification channel is set when a schedule is present
  - Warns if browser steps reference unnamed sites
  - Warns if commands contain data exfiltration patterns
    (piping to curl/wget/nc, redirecting to /dev/tcp)
  - If plan has 'allowed_commands' array, warns when step
    commands use unlisted base commands
  - Detects encoding/obfuscation patterns (base64, eval, exec, \x)
  - In restricted_mode: blocks unlisted commands and interpreters
  - Calculates plan risk score (LOW/MEDIUM/HIGH)

Input:  Path to a JSON plan file
Output: PASS or FAIL with specific errors and risk score

Options:
  --help    Show this help message
EOF
    exit 0
}

[ "${1:-}" = "--help" ] && usage
[ $# -lt 1 ] && { echo "FAIL: No plan file provided. Use --help for usage." >&2; exit 1; }

PLAN_FILE="$1"

[ ! -f "$PLAN_FILE" ] && { echo "FAIL: File not found: $PLAN_FILE" >&2; exit 1; }

# Check valid JSON
if ! jq empty "$PLAN_FILE" 2>/dev/null; then
    echo "FAIL: Invalid JSON in $PLAN_FILE"
    exit 1
fi

ERRORS=()
WARNINGS=()

# Check top-level fields
for field in workflow_name steps; do
    if [ "$(jq -r "has(\"$field\")" "$PLAN_FILE")" != "true" ]; then
        ERRORS+=("Missing required top-level field: $field")
    fi
done

# Count steps
STEP_COUNT=$(jq '.steps | length' "$PLAN_FILE" 2>/dev/null || echo 0)
if [ "$STEP_COUNT" -eq 0 ]; then
    ERRORS+=("Plan has no steps")
fi

# Check if schedule is present
HAS_SCHEDULE="false"
SCHEDULE_CRON=$(jq -r '.schedule.cron // empty' "$PLAN_FILE" 2>/dev/null || true)
if [ -n "$SCHEDULE_CRON" ]; then
    HAS_SCHEDULE="true"
fi

# If schedule is set, check notification channel
if [ "$HAS_SCHEDULE" = "true" ]; then
    NOTIFY_CHANNEL=$(jq -r '.notify.channel // empty' "$PLAN_FILE" 2>/dev/null || true)
    if [ -z "$NOTIFY_CHANNEL" ]; then
        ERRORS+=("Schedule is set but no notification channel specified (notify.channel)")
    fi
fi

# Validate cron expression (basic: 5 fields, values in range)
validate_cron() {
    local cron="$1"
    local fields
    set -f
    # shellcheck disable=SC2206
    fields=($cron)
    set +f
    if [ "${#fields[@]}" -ne 5 ]; then
        echo "Cron expression must have exactly 5 fields, got ${#fields[@]}: $cron"
        return
    fi
    # Basic validation: each field is either * or a number or range or step
    local i
    for i in 0 1 2 3 4; do
        local f="${fields[$i]}"
        if ! echo "$f" | grep -qE '^(\*|[0-9]+(-[0-9]+)?)(/[0-9]+)?$'; then
            # Allow comma-separated values too
            if ! echo "$f" | grep -qE '^(\*|[0-9]+(-[0-9]+)?)(,[0-9]+(-[0-9]+)?)*(/[0-9]+)?$'; then
                echo "Invalid cron field $((i+1)): $f in expression: $cron"
                return
            fi
        fi
    done
}

# Validate schedule cron if present
if [ "$HAS_SCHEDULE" = "true" ] && [ -n "$SCHEDULE_CRON" ]; then
    cron_err=$(validate_cron "$SCHEDULE_CRON")
    if [ -n "$cron_err" ]; then
        ERRORS+=("$cron_err")
    fi
fi

# Collect user-specified sites for browser safety check
USER_SITES=$(jq -r '.user_sites // [] | .[]' "$PLAN_FILE" 2>/dev/null || true)

# Validate each step
for i in $(seq 0 $((STEP_COUNT - 1))); do
    STEP_NUM=$((i + 1))
    PREFIX="Step $STEP_NUM"

    # Required fields
    for field in description type; do
        val=$(jq -r ".steps[$i].$field // empty" "$PLAN_FILE" 2>/dev/null || true)
        if [ -z "$val" ]; then
            ERRORS+=("$PREFIX: Missing required field '$field'")
        fi
    done

    STEP_TYPE=$(jq -r ".steps[$i].type // empty" "$PLAN_FILE" 2>/dev/null || true)

    # Check type is valid
    if [ -n "$STEP_TYPE" ]; then
        type_found="false"
        for vt in $VALID_TYPES; do
            if [ "$STEP_TYPE" = "$vt" ]; then
                type_found="true"
                break
            fi
        done
        if [ "$type_found" = "false" ]; then
            ERRORS+=("$PREFIX: Unknown step type '$STEP_TYPE'")
        fi
    fi

    # Check input/output
    for field in input output; do
        val=$(jq -r ".steps[$i].$field // empty" "$PLAN_FILE" 2>/dev/null || true)
        if [ -z "$val" ]; then
            WARNINGS+=("$PREFIX: Missing '$field' field (recommended)")
        fi
    done

    # Browser step validations
    is_browser="false"
    for bt in $BROWSER_TYPES; do
        if [ "$STEP_TYPE" = "$bt" ]; then
            is_browser="true"
            break
        fi
    done

    if [ "$is_browser" = "true" ]; then
        # browser-navigate must have a URL
        if [ "$STEP_TYPE" = "browser-navigate" ]; then
            url=$(jq -r ".steps[$i].url // .steps[$i].input // empty" "$PLAN_FILE" 2>/dev/null || true)
            if [ -z "$url" ]; then
                ERRORS+=("$PREFIX (browser-navigate): Missing target URL")
            else
                # Warn if site not in user_sites list
                if [ -n "$USER_SITES" ]; then
                    site_found="false"
                    while IFS= read -r site; do
                        if echo "$url" | grep -qi "$site" 2>/dev/null; then
                            site_found="true"
                            break
                        fi
                    done <<< "$USER_SITES"
                    if [ "$site_found" = "false" ]; then
                        WARNINGS+=("$PREFIX: URL '$url' not in user-specified sites list")
                    fi
                fi

                # Sensitive site detection
                if echo "$url" | grep -qiE "$SENSITIVE_SITES"; then
                    ERRORS+=("$PREFIX: BLOCKED — URL '$url' matches a sensitive/financial site. Automating banking, payment, or investment sites is not allowed for security reasons.")
                fi
            fi
        fi

        # browser-click, browser-fill, browser-wait need a selector or element
        case "$STEP_TYPE" in
            browser-click|browser-fill|browser-wait)
                selector=$(jq -r ".steps[$i].selector // .steps[$i].element // empty" "$PLAN_FILE" 2>/dev/null || true)
                if [ -z "$selector" ]; then
                    ERRORS+=("$PREFIX ($STEP_TYPE): Missing element selector")
                fi
                ;;
        esac

        # browser-fill also needs a value
        if [ "$STEP_TYPE" = "browser-fill" ]; then
            value=$(jq -r ".steps[$i].value // empty" "$PLAN_FILE" 2>/dev/null || true)
            if [ -z "$value" ]; then
                ERRORS+=("$PREFIX (browser-fill): Missing input value")
            fi
        fi
    fi

    # Schedule step validations
    is_schedule="false"
    for st in $SCHEDULE_TYPES; do
        if [ "$STEP_TYPE" = "$st" ]; then
            is_schedule="true"
            break
        fi
    done

    if [ "$is_schedule" = "true" ]; then
        step_cron=$(jq -r ".steps[$i].cron // empty" "$PLAN_FILE" 2>/dev/null || true)
        step_time=$(jq -r ".steps[$i].time // empty" "$PLAN_FILE" 2>/dev/null || true)
        if [ -z "$step_cron" ] && [ -z "$step_time" ]; then
            ERRORS+=("$PREFIX ($STEP_TYPE): Must have either 'cron' expression or 'time' value")
        fi
        if [ -n "$step_cron" ]; then
            cron_err=$(validate_cron "$step_cron")
            if [ -n "$cron_err" ]; then
                ERRORS+=("$PREFIX: $cron_err")
            fi
        fi
    fi

    # Exfiltration pattern detection
    step_cmd=$(jq -r ".steps[$i].command // empty" "$PLAN_FILE" 2>/dev/null || true)
    if [ -n "$step_cmd" ]; then
        if echo "$step_cmd" | grep -qE "$EXFIL_PATTERNS"; then
            WARNINGS+=("$PREFIX: Command contains potential data exfiltration pattern: $step_cmd")
        fi
    fi

    # Encoding/obfuscation detection
    if [ -n "$step_cmd" ]; then
        if echo "$step_cmd" | grep -qE "$ENCODING_PATTERNS"; then
            WARNINGS+=("$PREFIX: Command contains encoding/obfuscation pattern (base64/eval/exec): $step_cmd")
        fi
    fi

    # Restricted mode + allowed_commands enforcement + no-interpreter rule
    RESTRICTED_MODE=$(jq -r '.restricted_mode // false' "$PLAN_FILE" 2>/dev/null || echo "false")
    if [ -n "$step_cmd" ]; then
        base_cmd=$(echo "$step_cmd" | sed 's/[|;&].*//' | awk '{print $1}' | sed 's|.*/||')

        # No-interpreter rule (restricted mode: ERROR, normal mode: WARNING)
        is_interpreter="false"
        if echo "$base_cmd" | grep -qE "$INTERPRETER_PATTERN"; then
            is_interpreter="true"
        fi
        # Check for -c/-e inline execution patterns
        if [ "$is_interpreter" = "true" ]; then
            if echo "$step_cmd" | grep -qE ' -[ce] '; then
                if [ "$RESTRICTED_MODE" = "true" ]; then
                    ERRORS+=("$PREFIX: Inline interpreter execution blocked in restricted mode: $step_cmd (use a script file instead)")
                else
                    WARNINGS+=("$PREFIX: Inline interpreter execution detected: $base_cmd -c/-e (consider using a script file)")
                fi
            fi
        fi

        # Allowed_commands enforcement
        allowed_commands=$(jq -r '.allowed_commands // empty' "$PLAN_FILE" 2>/dev/null || true)
        if [ -n "$allowed_commands" ] && [ "$allowed_commands" != "null" ]; then
            cmd_allowed="false"
            while IFS= read -r allowed; do
                if [ "$base_cmd" = "$allowed" ]; then
                    cmd_allowed="true"
                    break
                fi
            done < <(jq -r '.allowed_commands[]' "$PLAN_FILE" 2>/dev/null)
            if [ "$cmd_allowed" = "false" ]; then
                if [ "$RESTRICTED_MODE" = "true" ]; then
                    ERRORS+=("$PREFIX: Command '$base_cmd' blocked — not in allowed_commands (restricted mode)")
                else
                    WARNINGS+=("$PREFIX: Command '$base_cmd' not in allowed_commands list")
                fi
            fi
        fi
    fi
done

# --- Plan Risk Score ---
RISK_SCORE=0
SHELL_CMD_COUNT=$(jq '[.steps[] | select(.command != null and .command != "")] | length' "$PLAN_FILE" 2>/dev/null || echo 0)
BROWSER_STEP_COUNT=$(jq '[.steps[] | select(.type | startswith("browser"))] | length' "$PLAN_FILE" 2>/dev/null || echo 0)
FILE_WRITE_COUNT=$(jq '[.steps[] | select(.type == "file-write")] | length' "$PLAN_FILE" 2>/dev/null || echo 0)
RISK_SCORE=$((SHELL_CMD_COUNT + BROWSER_STEP_COUNT * 2 + FILE_WRITE_COUNT))

RISK_LEVEL="LOW"
[ "$RISK_SCORE" -ge 5 ] && RISK_LEVEL="MEDIUM"
[ "$RISK_SCORE" -ge 10 ] && RISK_LEVEL="HIGH"

# Print results
if [ ${#WARNINGS[@]} -gt 0 ]; then
    for w in "${WARNINGS[@]}"; do
        echo "WARNING: $w"
    done
fi

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "FAIL: Plan validation failed with ${#ERRORS[@]} error(s):"
    for e in "${ERRORS[@]}"; do
        echo "  - $e"
    done
    exit 1
else
    echo "PASS: Plan is valid ($STEP_COUNT steps) — Risk: $RISK_LEVEL (score: $RISK_SCORE)"
    exit 0
fi
