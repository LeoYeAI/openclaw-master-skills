#!/usr/bin/env bash
set -euo pipefail

# check-schedules.sh — Lightweight heartbeat script for OpenClaw cron.
# Checks all active schedules and outputs plan paths for any that match
# the current time. Always exits 0 (failures logged, not thrown).

SCHEDULES_DIR="$HOME/.openclaw/workflow-automator/schedules"
LOG_FILE="$HOME/.openclaw/workflow-automator/execution.log"

usage() {
    cat <<'EOF'
Usage: check-schedules.sh [options]

Check all active workflow schedules against the current time.
Outputs the plan JSON path for any schedule that should run now.

This script is designed to be called by OpenClaw's cron system
every minute. When it finds a matching schedule, the agent picks
up the plan and runs it autonomously.

Options:
  --dry-run    Show what would match without triggering
  --verbose    Show all schedules checked, not just matches
  --help       Show this help message

Output:
  One line per matching schedule: <schedule-name> <plan-json-path>
  Exit code is always 0 (errors are logged, not thrown).
EOF
    exit 0
}

DRY_RUN="false"
VERBOSE="false"

for arg in "$@"; do
    case "$arg" in
        --help) usage ;;
        --dry-run) DRY_RUN="true" ;;
        --verbose) VERBOSE="true" ;;
    esac
done

mkdir -p "$(dirname "$LOG_FILE")"

log_msg() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] [check-schedules] $1" >> "$LOG_FILE"
}

# Get current time components
NOW_MIN=$(date +"%M" | sed 's/^0//')
NOW_HOUR=$(date +"%H" | sed 's/^0//')
NOW_DOM=$(date +"%d" | sed 's/^0//')
NOW_MON=$(date +"%m" | sed 's/^0//')
# Convert to cron dow (0=Sun..6=Sat)
NOW_DOW_U=$(date +"%u")  # 1=Mon..7=Sun
NOW_DOW=$(( NOW_DOW_U % 7 ))

[ -z "$NOW_MIN" ] && NOW_MIN=0
[ -z "$NOW_HOUR" ] && NOW_HOUR=0

# Cron field matcher
field_matches() {
    local field="$1"
    local value="$2"

    [ "$field" = "*" ] && return 0

    # Step: */N
    if echo "$field" | grep -qE '^\*/[0-9]+$'; then
        local step
        step=$(echo "$field" | cut -d'/' -f2)
        [ $((value % step)) -eq 0 ] && return 0
        return 1
    fi

    # Range: N-M
    if echo "$field" | grep -qE '^[0-9]+-[0-9]+$'; then
        local low high
        low=$(echo "$field" | cut -d'-' -f1)
        high=$(echo "$field" | cut -d'-' -f2)
        [ "$value" -ge "$low" ] && [ "$value" -le "$high" ] && return 0
        return 1
    fi

    # Comma list
    if echo "$field" | grep -q ','; then
        local item
        for item in $(echo "$field" | tr ',' ' '); do
            [ "$item" -eq "$value" ] 2>/dev/null && return 0
        done
        return 1
    fi

    # Exact match
    [ "$field" -eq "$value" ] 2>/dev/null && return 0
    return 1
}

# Auto-expire stale browser sessions before checking schedules
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SESSIONS_DIR="$HOME/.openclaw/workflow-automator/sessions"
if [ -d "$SESSIONS_DIR" ] && [ -x "$SCRIPT_DIR/session-guard.sh" ]; then
    for sess_dir in "$SESSIONS_DIR"/*/; do
        [ ! -d "$sess_dir" ] && continue
        auth_file="$sess_dir/.last-auth"
        [ ! -f "$auth_file" ] && continue
        # Check age and auto-cleanup if stale (> 7 days)
        now_ts=$(date +%s)
        if stat -f %m "$auth_file" >/dev/null 2>&1; then
            file_ts=$(stat -f %m "$auth_file")
        elif stat -c %Y "$auth_file" >/dev/null 2>&1; then
            file_ts=$(stat -c %Y "$auth_file")
        else
            continue
        fi
        age_days=$(( (now_ts - file_ts) / 86400 ))
        if [ "$age_days" -gt 7 ]; then
            wf_name=$(basename "$sess_dir")
            # Wipe stale session data
            rm -rf "${sess_dir}chrome-profile" 2>/dev/null || true
            rm -f "$auth_file" 2>/dev/null || true
            log_msg "AUTO-EXPIRED stale session: $wf_name (${age_days} days old)"
            [ "$VERBOSE" = "true" ] && echo "AUTO-EXPIRED: $wf_name session (${age_days} days old)"
        fi
    done
fi

# Check each schedule
if [ ! -d "$SCHEDULES_DIR" ]; then
    [ "$VERBOSE" = "true" ] && echo "No schedules directory found."
    exit 0
fi

MATCH_COUNT=0

for sfile in "$SCHEDULES_DIR"/*.json; do
    [ ! -f "$sfile" ] && continue

    name=$(jq -r '.name // "unknown"' "$sfile" 2>/dev/null || continue)
    status=$(jq -r '.status // "unknown"' "$sfile" 2>/dev/null || continue)
    cron=$(jq -r '.cron // ""' "$sfile" 2>/dev/null || continue)
    plan_path=$(jq -r '.plan_path // ""' "$sfile" 2>/dev/null || continue)

    # Skip non-active schedules
    if [ "$status" != "active" ]; then
        [ "$VERBOSE" = "true" ] && echo "SKIP: $name (status: $status)"
        continue
    fi

    # Skip if no cron
    if [ -z "$cron" ]; then
        [ "$VERBOSE" = "true" ] && echo "SKIP: $name (no cron expression)"
        continue
    fi

    # Parse cron fields (disable globbing so * doesn't expand)
    local_min="" local_hour="" local_dom="" local_mon="" local_dow=""
    set -f
    # shellcheck disable=SC2086
    read -r local_min local_hour local_dom local_mon local_dow <<< $cron 2>/dev/null || {
        set +f
        log_msg "ERROR: Failed to parse cron for '$name': $cron"
        [ "$VERBOSE" = "true" ] && echo "ERROR: $name (bad cron: $cron)"
        continue
    }
    set +f

    # Check if current time matches
    if field_matches "$local_min" "$NOW_MIN" && \
       field_matches "$local_hour" "$NOW_HOUR" && \
       field_matches "$local_dom" "$NOW_DOM" && \
       field_matches "$local_mon" "$NOW_MON" && \
       field_matches "$local_dow" "$NOW_DOW"; then

        if [ "$DRY_RUN" = "true" ]; then
            echo "MATCH (dry-run): $name $plan_path"
        else
            echo "$name $plan_path"
            log_msg "TRIGGERED: $name (cron: $cron, plan: $plan_path)"

            # Update last_run in schedule file
            TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
            jq --arg ts "$TS" \
                '.last_run = $ts | .run_count = (.run_count // 0) + 1 | .updated_at = $ts' \
                "$sfile" > "${sfile}.tmp" && mv "${sfile}.tmp" "$sfile"
        fi
        MATCH_COUNT=$((MATCH_COUNT + 1))
    else
        [ "$VERBOSE" = "true" ] && echo "NO MATCH: $name (cron: $cron)"
    fi
done

[ "$VERBOSE" = "true" ] && echo "Checked complete. Matches: $MATCH_COUNT"

exit 0
