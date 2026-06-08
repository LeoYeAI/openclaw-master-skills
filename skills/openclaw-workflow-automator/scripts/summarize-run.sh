#!/usr/bin/env bash
set -euo pipefail

# summarize-run.sh — Generate a completion summary for a workflow run.
# Reads step result files and schedule info to produce a formatted summary.

BASE_DIR="$HOME/.openclaw/workflow-automator"

usage() {
    cat <<'EOF'
Usage: summarize-run.sh <plan.json> [options]

Generate a completion summary for a workflow run.

Arguments:
  plan.json    Path to the workflow plan JSON file

Options:
  --run-dir PATH    Override the run results directory
  --help            Show this help message

Output:
  Formatted summary including:
  - Step-by-step results (pass/fail/skip)
  - Total duration
  - Files created/modified
  - Schedule info (next run, frequency)
  - Screenshots taken
  - Notification status
EOF
    exit 0
}

[ "${1:-}" = "--help" ] && usage
[ $# -lt 1 ] && { echo "Error: No plan file provided. Use --help for usage." >&2; exit 1; }

PLAN_FILE="$1"
shift
CUSTOM_RUN_DIR=""

while [ $# -gt 0 ]; do
    case "$1" in
        --run-dir)
            CUSTOM_RUN_DIR="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            shift
            ;;
    esac
done

[ ! -f "$PLAN_FILE" ] && { echo "Error: Plan file not found: $PLAN_FILE" >&2; exit 1; }

WORKFLOW_NAME=$(jq -r '.workflow_name // "Unnamed Workflow"' "$PLAN_FILE")
STEP_COUNT=$(jq '.steps | length' "$PLAN_FILE")
WORKFLOW_SLUG=$(echo "$WORKFLOW_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

# Find run results
if [ -n "$CUSTOM_RUN_DIR" ]; then
    RUN_DIR="$CUSTOM_RUN_DIR"
else
    RUN_DIR="$BASE_DIR/runs/$WORKFLOW_SLUG"
fi

# Collect step results
PASSED=0
FAILED=0
SKIPPED=0
TOTAL_DURATION=0
SCREENSHOTS=()
OUTPUT_FILES=()

for i in $(seq 1 "$STEP_COUNT"); do
    # Find the most recent result for this step
    RESULT_FILE=$(ls -t "$RUN_DIR"/step${i}_*.json 2>/dev/null | head -1 || true)

    if [ -z "$RESULT_FILE" ] || [ ! -f "$RESULT_FILE" ]; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    step_exit=$(jq -r '.exit_code // 1' "$RESULT_FILE")
    step_duration=$(jq -r '.duration_seconds // 0' "$RESULT_FILE")
    TOTAL_DURATION=$((TOTAL_DURATION + step_duration))

    if [ "$step_exit" -eq 0 ]; then
        PASSED=$((PASSED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

# Find screenshots for this workflow
SCREENSHOT_DIR="$BASE_DIR/screenshots"
if [ -d "$SCREENSHOT_DIR" ]; then
    while IFS= read -r f; do
        [ -n "$f" ] && SCREENSHOTS+=("$f")
    done < <(ls "$SCREENSHOT_DIR"/${WORKFLOW_SLUG}_*.png 2>/dev/null || true)
fi

# Get schedule info
SCHEDULE_FILE="$BASE_DIR/schedules/${WORKFLOW_SLUG}.json"
SCHEDULE_INFO=""
NEXT_RUN=""
NOTIFY_CHANNEL=""

if [ -f "$SCHEDULE_FILE" ]; then
    SCHEDULE_CRON=$(jq -r '.cron_expression // .cron // empty' "$SCHEDULE_FILE")
    SCHEDULE_STATUS=$(jq -r '.status // "unknown"' "$SCHEDULE_FILE")
    NEXT_RUN=$(jq -r '.next_run // empty' "$SCHEDULE_FILE")
    NOTIFY_CHANNEL=$(jq -r '.notification_channel // .notify_channel // empty' "$SCHEDULE_FILE")

    if [ -n "$SCHEDULE_CRON" ]; then
        SCHEDULE_INFO="Cron: $SCHEDULE_CRON (status: $SCHEDULE_STATUS)"
    fi
fi

# Also check plan-level schedule/notify
if [ -z "$SCHEDULE_INFO" ]; then
    plan_cron=$(jq -r '.schedule.cron // empty' "$PLAN_FILE" 2>/dev/null || true)
    if [ -n "$plan_cron" ]; then
        SCHEDULE_INFO="Cron: $plan_cron"
    fi
fi

if [ -z "$NOTIFY_CHANNEL" ]; then
    NOTIFY_CHANNEL=$(jq -r '.notify.channel // empty' "$PLAN_FILE" 2>/dev/null || true)
fi

# Format duration
if [ "$TOTAL_DURATION" -ge 60 ]; then
    DURATION_FMT="$((TOTAL_DURATION / 60))m $((TOTAL_DURATION % 60))s"
else
    DURATION_FMT="${TOTAL_DURATION}s"
fi

# Determine overall status
if [ "$FAILED" -gt 0 ]; then
    OVERALL_STATUS="Workflow completed with errors."
elif [ "$SKIPPED" -gt 0 ]; then
    OVERALL_STATUS="Workflow completed with skipped steps."
else
    OVERALL_STATUS="Workflow completed successfully."
fi

# Output summary
echo "WORKFLOW COMPLETE: $WORKFLOW_NAME"
echo "═════════════════════════"
echo "Total steps:  $STEP_COUNT"
echo "Passed:       $PASSED"
echo "Failed:       $FAILED"
if [ "$SKIPPED" -gt 0 ]; then
    echo "Skipped:      $SKIPPED"
fi
echo "Duration:     $DURATION_FMT"

# Step details
echo ""
echo "Steps:"
for i in $(seq 1 "$STEP_COUNT"); do
    RESULT_FILE=$(ls -t "$RUN_DIR"/step${i}_*.json 2>/dev/null | head -1 || true)
    step_desc=$(jq -r ".steps[$((i-1))].description // \"Step $i\"" "$PLAN_FILE")

    if [ -z "$RESULT_FILE" ] || [ ! -f "$RESULT_FILE" ]; then
        echo "  $i. $step_desc — SKIPPED"
    else
        step_exit=$(jq -r '.exit_code // 1' "$RESULT_FILE")
        step_dur=$(jq -r '.duration_seconds // 0' "$RESULT_FILE")
        if [ "$step_exit" -eq 0 ]; then
            echo "  $i. $step_desc — SUCCESS (${step_dur}s)"
        else
            echo "  $i. $step_desc — FAILED (exit $step_exit, ${step_dur}s)"
        fi
    fi
done

# Screenshots
if [ ${#SCREENSHOTS[@]} -gt 0 ]; then
    echo ""
    echo "Screenshots:"
    for s in "${SCREENSHOTS[@]}"; do
        echo "  - $s"
    done
fi

# Schedule info
if [ -n "$SCHEDULE_INFO" ]; then
    echo ""
    echo "Schedule: $SCHEDULE_INFO"
    if [ -n "$NEXT_RUN" ]; then
        echo "Next run: $NEXT_RUN"
    fi
fi

# Notification info
if [ -n "$NOTIFY_CHANNEL" ]; then
    echo "Notification: Results will be sent to $NOTIFY_CHANNEL"
fi

echo ""
echo "Status: $OVERALL_STATUS"
