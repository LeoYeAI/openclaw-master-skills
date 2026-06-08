#!/usr/bin/env bash
set -eo pipefail

# audit-log.sh — Append-only audit log for workflow executions.
# Every autonomous execution writes a single line for quick review.

AUDIT_FILE="$HOME/.openclaw/workflow-automator/audit.log"

usage() {
    cat <<'EOF'
Usage: audit-log.sh <subcommand> [arguments]

Append-only audit log for workflow executions.

Subcommands:
  write <workflow> <step> <type> <command> <exit_code> <mode> [--hash-verified]
      Append an entry to the audit log.

  read [options]
      Read the audit log.
      --last <N>         Show last N entries (default: 20)
      --workflow <name>  Filter by workflow name
      --failures         Show only failures (exit code != 0)
      --today            Show only today's entries

  stats
      Show summary statistics from the audit log.

  path
      Print the audit log file path.

Options:
  --help    Show this help message

Log format (tab-separated):
  timestamp | mode | workflow | step | type | command | exit_code | hash_verified

Log file: ~/.openclaw/workflow-automator/audit.log
EOF
    exit 0
}

[ "${1:-}" = "--help" ] && usage
[ $# -lt 1 ] && { echo "Error: No subcommand provided. Use --help for usage." >&2; exit 1; }

SUBCMD="$1"
shift

mkdir -p "$(dirname "$AUDIT_FILE")"

case "$SUBCMD" in
    write)
        if [ $# -lt 6 ]; then
            echo "Error: write requires: <workflow> <step> <type> <command> <exit_code> <mode>" >&2
            exit 1
        fi
        WORKFLOW="$1"
        STEP="$2"
        TYPE="$3"
        CMD="$4"
        EXIT_CODE="$5"
        MODE="$6"
        HASH_VERIFIED="no"
        [ "${7:-}" = "--hash-verified" ] && HASH_VERIFIED="yes"

        TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        # Sanitize command — replace tabs and newlines with spaces, truncate to 200 chars
        CLEAN_CMD=$(echo "$CMD" | tr '\t\n' '  ' | cut -c1-200)

        printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
            "$TS" "$MODE" "$WORKFLOW" "$STEP" "$TYPE" "$CLEAN_CMD" "$EXIT_CODE" "$HASH_VERIFIED" \
            >> "$AUDIT_FILE"

        echo "Audit entry recorded for $WORKFLOW step $STEP"
        ;;

    read)
        if [ ! -f "$AUDIT_FILE" ]; then
            echo "(no audit log found)"
            exit 0
        fi

        LAST=20
        FILTER_WF=""
        FAILURES_ONLY="false"
        TODAY_ONLY="false"

        while [ $# -gt 0 ]; do
            case "$1" in
                --last) LAST="$2"; shift 2 ;;
                --workflow) FILTER_WF="$2"; shift 2 ;;
                --failures) FAILURES_ONLY="true"; shift ;;
                --today) TODAY_ONLY="true"; shift ;;
                *) shift ;;
            esac
        done

        # Build filter pipeline
        result=$(cat "$AUDIT_FILE")

        if [ -n "$FILTER_WF" ]; then
            result=$(echo "$result" | grep "$FILTER_WF" || true)
        fi

        if [ "$FAILURES_ONLY" = "true" ]; then
            # Filter lines where exit_code (7th field) is not 0
            result=$(echo "$result" | awk -F'\t' '$7 != "0"' || true)
        fi

        if [ "$TODAY_ONLY" = "true" ]; then
            TODAY=$(date -u +"%Y-%m-%d")
            result=$(echo "$result" | grep "^$TODAY" || true)
        fi

        if [ -z "$result" ]; then
            echo "(no matching entries)"
            exit 0
        fi

        # Header
        printf "%-20s %-11s %-20s %-5s %-18s %-40s %-5s %-5s\n" \
            "TIMESTAMP" "MODE" "WORKFLOW" "STEP" "TYPE" "COMMAND" "EXIT" "HASH"
        printf "%-20s %-11s %-20s %-5s %-18s %-40s %-5s %-5s\n" \
            "---------" "----" "--------" "----" "----" "-------" "----" "----"

        echo "$result" | tail -"$LAST" | while IFS=$'\t' read -r ts mode wf step type cmd exit_code hash_v; do
            # Truncate command for display
            short_cmd=$(echo "$cmd" | cut -c1-38)
            printf "%-20s %-11s %-20s %-5s %-18s %-40s %-5s %-5s\n" \
                "$ts" "$mode" "$wf" "$step" "$type" "$short_cmd" "$exit_code" "$hash_v"
        done
        ;;

    stats)
        if [ ! -f "$AUDIT_FILE" ]; then
            echo "(no audit log found)"
            exit 0
        fi

        total=$(wc -l < "$AUDIT_FILE" | tr -d ' ')
        successes=$(awk -F'\t' '$7 == "0"' "$AUDIT_FILE" | wc -l | tr -d ' ')
        failures=$(awk -F'\t' '$7 != "0"' "$AUDIT_FILE" | wc -l | tr -d ' ')
        autonomous=$(awk -F'\t' '$2 == "autonomous"' "$AUDIT_FILE" | wc -l | tr -d ' ')
        interactive=$(awk -F'\t' '$2 == "interactive"' "$AUDIT_FILE" | wc -l | tr -d ' ')
        hash_verified=$(awk -F'\t' '$8 == "yes"' "$AUDIT_FILE" | wc -l | tr -d ' ')
        unique_wfs=$(awk -F'\t' '{print $3}' "$AUDIT_FILE" | sort -u | wc -l | tr -d ' ')

        echo "Audit Log Statistics"
        echo "===================="
        echo "Total executions:    $total"
        echo "Successes:           $successes"
        echo "Failures:            $failures"
        echo "Autonomous runs:     $autonomous"
        echo "Interactive runs:    $interactive"
        echo "Hash-verified runs:  $hash_verified"
        echo "Unique workflows:    $unique_wfs"

        if [ "$failures" -gt 0 ]; then
            echo ""
            echo "Recent failures:"
            awk -F'\t' '$7 != "0"' "$AUDIT_FILE" | tail -5 | while IFS=$'\t' read -r ts mode wf step type cmd exit_code hash_v; do
                echo "  $ts  $wf step $step ($type) exit=$exit_code"
            done
        fi
        ;;

    path)
        echo "$AUDIT_FILE"
        ;;

    *)
        echo "Error: Unknown subcommand '$SUBCMD'. Use --help for usage." >&2
        exit 1
        ;;
esac
