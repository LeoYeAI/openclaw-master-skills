#!/usr/bin/env bash
set -euo pipefail

# manage-schedule.sh — Create, list, pause, resume, cancel, update, and show
# workflow schedules for the workflow-automator skill.

SCHEDULES_DIR="$HOME/.openclaw/workflow-automator/schedules"

usage() {
    cat <<'EOF'
Usage: manage-schedule.sh <subcommand> [arguments]

Manage workflow schedules.

Subcommands:
  create <name> <cron> <plan-json> <notify-channel>
      Create a new schedule for a workflow.

  list
      List all schedules with status, cron, last run, next run.

  pause <name>
      Pause a schedule (keeps the cron, skips execution).

  resume <name>
      Resume a paused schedule.

  cancel <name>
      Cancel a schedule (keeps file for audit trail).

  update <name> <new-cron>
      Update the cron expression for a schedule.

  show <name>
      Show full details of a schedule.

  next <name> [count]
      Show next N run times (default: 5).

Options:
  --help    Show this help message

Schedule files are stored in:
  ~/.openclaw/workflow-automator/schedules/<name>.json
EOF
    exit 0
}

[ "${1:-}" = "--help" ] && usage
[ $# -lt 1 ] && { echo "Error: No subcommand provided. Use --help for usage." >&2; exit 1; }

SUBCMD="$1"
shift

mkdir -p "$SCHEDULES_DIR"

# Helper: slugify a name
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//'
}

# Helper: get current timestamp
now_ts() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Helper: get schedule file path
schedule_path() {
    local slug
    slug=$(slugify "$1")
    echo "$SCHEDULES_DIR/${slug}.json"
}

# Helper: validate cron has 5 fields
validate_cron_basic() {
    local cron="$1"
    local count
    count=$(echo "$cron" | wc -w | tr -d ' ')
    if [ "$count" -ne 5 ]; then
        echo "Error: Cron expression must have 5 fields, got $count: $cron" >&2
        return 1
    fi
    return 0
}

# Helper: calculate next run times from cron expression
# Simple implementation: checks each minute from now for matches
cron_field_matches() {
    local field="$1"
    local value="$2"

    # Wildcard matches everything
    [ "$field" = "*" ] && return 0

    # Step values: */N
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

    # Comma-separated list
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

calc_next_runs() {
    local cron="$1"
    local count="${2:-5}"
    local found=0

    # Parse cron fields
    local c_min c_hour c_dom c_mon c_dow
    # Disable globbing so * doesn't expand to filenames
    set -f
    # shellcheck disable=SC2086
    read -r c_min c_hour c_dom c_mon c_dow <<< $cron
    set +f

    # Iterate day by day for up to 400 days, checking matching hours/minutes
    # This is much faster than minute-by-minute iteration
    local now_ts
    now_ts=$(date +%s)
    local max_days=400
    local day=0

    # Round to start of current day
    local day_start
    if date -r "$now_ts" +"%Y-%m-%d" >/dev/null 2>&1; then
        day_start=$(date -j -f "%Y-%m-%d %H:%M:%S" "$(date -r "$now_ts" +"%Y-%m-%d") 00:00:00" +%s 2>/dev/null || date -r "$now_ts" +%s)
    else
        day_start=$(date -d "$(date -d "@$now_ts" +"%Y-%m-%d")" +%s)
    fi

    while [ "$found" -lt "$count" ] && [ "$day" -lt "$max_days" ]; do
        local ts=$((day_start + day * 86400))
        local dom mon dow

        if date -r "$ts" +"%d %m %u" >/dev/null 2>&1; then
            read -r dom mon dow <<< "$(date -r "$ts" +"%d %m %u")"
        else
            read -r dom mon dow <<< "$(date -d "@$ts" +"%d %m %u")"
        fi

        dom=$((10#$dom))
        mon=$((10#$mon))
        dow=$((dow % 7))

        # Check day-level fields first (fast reject)
        if cron_field_matches "$c_dom" "$dom" && \
           cron_field_matches "$c_mon" "$mon" && \
           cron_field_matches "$c_dow" "$dow"; then

            # Now check each matching hour and minute within this day
            local h=0
            while [ "$h" -lt 24 ] && [ "$found" -lt "$count" ]; do
                if cron_field_matches "$c_hour" "$h"; then
                    local m=0
                    while [ "$m" -lt 60 ] && [ "$found" -lt "$count" ]; do
                        if cron_field_matches "$c_min" "$m"; then
                            local candidate_ts=$((ts + h * 3600 + m * 60))
                            # Only include future times
                            if [ "$candidate_ts" -gt "$now_ts" ]; then
                                if date -r "$candidate_ts" +"%Y-%m-%d %H:%M (%A)" >/dev/null 2>&1; then
                                    date -r "$candidate_ts" +"%Y-%m-%d %H:%M (%A)"
                                else
                                    date -d "@$candidate_ts" +"%Y-%m-%d %H:%M (%A)"
                                fi
                                found=$((found + 1))
                            fi
                        fi
                        m=$((m + 1))
                    done
                fi
                h=$((h + 1))
            done
        fi

        day=$((day + 1))
    done

    if [ "$found" -eq 0 ]; then
        echo "(no matching times found within the next year)"
    fi
}

case "$SUBCMD" in
    create)
        if [ $# -lt 4 ]; then
            echo "Error: create requires: <name> <cron> <plan-json> <notify-channel>" >&2
            exit 1
        fi
        NAME="$1"
        CRON="$2"
        PLAN_PATH="$3"
        NOTIFY="$4"
        SFILE=$(schedule_path "$NAME")

        validate_cron_basic "$CRON" || exit 1

        if [ -f "$SFILE" ]; then
            existing_status=$(jq -r '.status' "$SFILE")
            if [ "$existing_status" = "active" ] || [ "$existing_status" = "paused" ]; then
                echo "Error: Schedule '$NAME' already exists (status: $existing_status). Use 'update' or 'cancel' first." >&2
                exit 1
            fi
        fi

        [ ! -f "$PLAN_PATH" ] && { echo "Error: Plan file not found: $PLAN_PATH" >&2; exit 1; }

        TS=$(now_ts)
        jq -n \
            --arg name "$NAME" \
            --arg slug "$(slugify "$NAME")" \
            --arg cron "$CRON" \
            --arg plan "$PLAN_PATH" \
            --arg notify "$NOTIFY" \
            --arg ts "$TS" \
            '{
                name: $name,
                slug: $slug,
                cron: $cron,
                plan_path: $plan,
                notify_channel: $notify,
                status: "active",
                created_at: $ts,
                updated_at: $ts,
                last_run: null,
                last_status: null,
                run_count: 0
            }' > "$SFILE"

        echo "Schedule created: $NAME"
        echo "  Cron: $CRON"
        echo "  Plan: $PLAN_PATH"
        echo "  Notify: $NOTIFY"
        echo "  File: $SFILE"
        echo ""
        echo "Next runs:"
        calc_next_runs "$CRON" 3
        ;;

    list)
        found=0
        printf "%-25s %-18s %-10s %-20s\n" "NAME" "CRON" "STATUS" "LAST RUN"
        printf "%-25s %-18s %-10s %-20s\n" "----" "----" "------" "--------"

        for f in "$SCHEDULES_DIR"/*.json; do
            [ ! -f "$f" ] && continue
            found=1
            name=$(jq -r '.name // "?"' "$f")
            cron=$(jq -r '.cron // "?"' "$f")
            status=$(jq -r '.status // "?"' "$f")
            last_run=$(jq -r '.last_run // "never"' "$f")
            [ "$last_run" = "null" ] && last_run="never"
            printf "%-25s %-18s %-10s %-20s\n" "$name" "$cron" "$status" "$last_run"
        done

        if [ "$found" -eq 0 ]; then
            echo "(no schedules found)"
        fi
        ;;

    pause)
        [ $# -lt 1 ] && { echo "Error: pause requires: <name>" >&2; exit 1; }
        NAME="$1"
        SFILE=$(schedule_path "$NAME")
        [ ! -f "$SFILE" ] && { echo "Error: Schedule not found: $NAME" >&2; exit 1; }

        current_status=$(jq -r '.status' "$SFILE")
        if [ "$current_status" != "active" ]; then
            echo "Warning: Schedule '$NAME' is not active (current: $current_status)"
        fi

        TS=$(now_ts)
        jq --arg ts "$TS" '.status = "paused" | .updated_at = $ts' "$SFILE" > "${SFILE}.tmp" && mv "${SFILE}.tmp" "$SFILE"
        echo "Schedule paused: $NAME"
        ;;

    resume)
        [ $# -lt 1 ] && { echo "Error: resume requires: <name>" >&2; exit 1; }
        NAME="$1"
        SFILE=$(schedule_path "$NAME")
        [ ! -f "$SFILE" ] && { echo "Error: Schedule not found: $NAME" >&2; exit 1; }

        current_status=$(jq -r '.status' "$SFILE")
        if [ "$current_status" != "paused" ]; then
            echo "Warning: Schedule '$NAME' is not paused (current: $current_status)"
        fi

        TS=$(now_ts)
        jq --arg ts "$TS" '.status = "active" | .updated_at = $ts' "$SFILE" > "${SFILE}.tmp" && mv "${SFILE}.tmp" "$SFILE"
        echo "Schedule resumed: $NAME"
        ;;

    cancel)
        [ $# -lt 1 ] && { echo "Error: cancel requires: <name>" >&2; exit 1; }
        NAME="$1"
        SFILE=$(schedule_path "$NAME")
        [ ! -f "$SFILE" ] && { echo "Error: Schedule not found: $NAME" >&2; exit 1; }

        TS=$(now_ts)
        jq --arg ts "$TS" '.status = "cancelled" | .updated_at = $ts' "$SFILE" > "${SFILE}.tmp" && mv "${SFILE}.tmp" "$SFILE"
        echo "Schedule cancelled: $NAME (file kept for audit trail)"
        ;;

    update)
        if [ $# -lt 2 ]; then
            echo "Error: update requires: <name> <new-cron>" >&2
            exit 1
        fi
        NAME="$1"
        NEW_CRON="$2"
        SFILE=$(schedule_path "$NAME")
        [ ! -f "$SFILE" ] && { echo "Error: Schedule not found: $NAME" >&2; exit 1; }

        validate_cron_basic "$NEW_CRON" || exit 1

        OLD_CRON=$(jq -r '.cron' "$SFILE")
        TS=$(now_ts)
        jq --arg cron "$NEW_CRON" --arg ts "$TS" \
            '.cron = $cron | .updated_at = $ts' "$SFILE" > "${SFILE}.tmp" && mv "${SFILE}.tmp" "$SFILE"

        echo "Schedule updated: $NAME"
        echo "  Old cron: $OLD_CRON"
        echo "  New cron: $NEW_CRON"
        echo ""
        echo "Next runs:"
        calc_next_runs "$NEW_CRON" 3
        ;;

    show)
        [ $# -lt 1 ] && { echo "Error: show requires: <name>" >&2; exit 1; }
        NAME="$1"
        SFILE=$(schedule_path "$NAME")
        [ ! -f "$SFILE" ] && { echo "Error: Schedule not found: $NAME" >&2; exit 1; }

        echo "Schedule: $NAME"
        echo "═══════════════════════════"
        jq -r '
            "  Slug:           \(.slug // "?")",
            "  Cron:           \(.cron // "?")",
            "  Plan:           \(.plan_path // "?")",
            "  Notify:         \(.notify_channel // "?")",
            "  Status:         \(.status // "?")",
            "  Run count:      \(.run_count // 0)",
            "  Last run:       \(.last_run // "never")",
            "  Last status:    \(.last_status // "n/a")",
            "  Created:        \(.created_at // "?")",
            "  Updated:        \(.updated_at // "?")"
        ' "$SFILE"

        CRON=$(jq -r '.cron' "$SFILE")
        echo ""
        echo "Next runs:"
        calc_next_runs "$CRON" 5
        ;;

    next)
        [ $# -lt 1 ] && { echo "Error: next requires: <name>" >&2; exit 1; }
        NAME="$1"
        COUNT="${2:-5}"
        SFILE=$(schedule_path "$NAME")
        [ ! -f "$SFILE" ] && { echo "Error: Schedule not found: $NAME" >&2; exit 1; }

        CRON=$(jq -r '.cron' "$SFILE")
        echo "Next $COUNT runs for '$NAME' (cron: $CRON):"
        calc_next_runs "$CRON" "$COUNT"
        ;;

    *)
        echo "Error: Unknown subcommand '$SUBCMD'. Use --help for usage." >&2
        exit 1
        ;;
esac
