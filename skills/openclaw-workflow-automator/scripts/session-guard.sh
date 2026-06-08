#!/usr/bin/env bash
set -eo pipefail

# session-guard.sh — Browser session safety guardrails.
# Manages session age tracking, per-workflow isolation, and cleanup.

BASE_DIR="$HOME/.openclaw/workflow-automator"
SESSIONS_DIR="$BASE_DIR/sessions"
DEFAULT_MAX_AGE_DAYS=7

usage() {
    cat <<'EOF'
Usage: session-guard.sh <subcommand> [arguments]

Browser session safety guardrails.

Subcommands:
  check <workflow-name> [--max-age <days>]
      Check if browser session is fresh enough for autonomous use.
      Default max age: 7 days. Returns PASS or FAIL.

  touch <workflow-name>
      Record that a browser session was authenticated just now.
      Call this after a user successfully logs in during first run.

  profile-path <workflow-name>
      Print the isolated browser profile directory for this workflow.
      Creates the directory if it doesn't exist.

  cleanup <workflow-name>
      Clear browser session data (cookies, localStorage) for a workflow.
      Use after one-time tasks or when session should not persist.

  list
      Show all tracked sessions with age and status.

  cleanup-all
      Clear all session data across all workflows.

Options:
  --help    Show this help message

Session data is stored in:
  ~/.openclaw/workflow-automator/sessions/<workflow-slug>/
EOF
    exit 0
}

[ "${1:-}" = "--help" ] && usage
[ $# -lt 1 ] && { echo "Error: No subcommand provided. Use --help for usage." >&2; exit 1; }

SUBCMD="$1"
shift

mkdir -p "$SESSIONS_DIR"
# Harden permissions: owner-only access to session data (cookies, tokens)
chmod 700 "$SESSIONS_DIR" 2>/dev/null || true

# Helper: slugify
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//'
}

# Helper: get age in days of a file
file_age_days() {
    local file="$1"
    local now_ts file_ts age_secs
    now_ts=$(date +%s)
    if stat -f %m "$file" >/dev/null 2>&1; then
        file_ts=$(stat -f %m "$file")
    elif stat -c %Y "$file" >/dev/null 2>&1; then
        file_ts=$(stat -c %Y "$file")
    else
        echo "0"
        return
    fi
    age_secs=$((now_ts - file_ts))
    echo $((age_secs / 86400))
}

case "$SUBCMD" in
    check)
        [ $# -lt 1 ] && { echo "Error: check requires: <workflow-name>" >&2; exit 1; }
        WF_NAME="$1"
        shift
        MAX_AGE="$DEFAULT_MAX_AGE_DAYS"

        while [ $# -gt 0 ]; do
            case "$1" in
                --max-age) MAX_AGE="$2"; shift 2 ;;
                *) shift ;;
            esac
        done

        SLUG=$(slugify "$WF_NAME")
        SESSION_DIR="$SESSIONS_DIR/$SLUG"
        AUTH_FILE="$SESSION_DIR/.last-auth"

        if [ ! -f "$AUTH_FILE" ]; then
            echo "FAIL: No session record for '$WF_NAME'. User must authenticate first." >&2
            exit 1
        fi

        AGE=$(file_age_days "$AUTH_FILE")
        AUTH_DATE=$(cat "$AUTH_FILE")

        if [ "$AGE" -gt "$MAX_AGE" ]; then
            echo "FAIL: Session for '$WF_NAME' is $AGE days old (max: $MAX_AGE days). Last auth: $AUTH_DATE. Re-authenticate to continue." >&2
            exit 1
        fi

        echo "PASS: Session for '$WF_NAME' is $AGE days old (max: $MAX_AGE). Last auth: $AUTH_DATE"
        exit 0
        ;;

    touch)
        [ $# -lt 1 ] && { echo "Error: touch requires: <workflow-name>" >&2; exit 1; }
        WF_NAME="$1"
        SLUG=$(slugify "$WF_NAME")
        SESSION_DIR="$SESSIONS_DIR/$SLUG"
        mkdir -p "$SESSION_DIR"

        TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        echo "$TS" > "$SESSION_DIR/.last-auth"

        # Harden permissions
        chmod 700 "$SESSION_DIR" 2>/dev/null || true
        chmod 600 "$SESSION_DIR/.last-auth" 2>/dev/null || true

        echo "Session authenticated: $WF_NAME ($TS)"
        echo "  Profile: $SESSION_DIR (permissions: owner-only)"
        ;;

    profile-path)
        [ $# -lt 1 ] && { echo "Error: profile-path requires: <workflow-name>" >&2; exit 1; }
        WF_NAME="$1"
        SLUG=$(slugify "$WF_NAME")
        SESSION_DIR="$SESSIONS_DIR/$SLUG/chrome-profile"
        mkdir -p "$SESSION_DIR"
        chmod 700 "$SESSION_DIR" 2>/dev/null || true
        echo "$SESSION_DIR"
        ;;

    cleanup)
        [ $# -lt 1 ] && { echo "Error: cleanup requires: <workflow-name>" >&2; exit 1; }
        WF_NAME="$1"
        SLUG=$(slugify "$WF_NAME")
        SESSION_DIR="$SESSIONS_DIR/$SLUG"

        if [ ! -d "$SESSION_DIR" ]; then
            echo "No session data found for '$WF_NAME'"
            exit 0
        fi

        # Remove chrome profile data but keep the .last-auth record
        if [ -d "$SESSION_DIR/chrome-profile" ]; then
            rm -rf "$SESSION_DIR/chrome-profile"
            echo "Browser profile cleared for '$WF_NAME'"
        fi

        # Remove auth record too
        rm -f "$SESSION_DIR/.last-auth"
        echo "Session data cleaned up for '$WF_NAME'"
        ;;

    list)
        found=0
        printf "%-25s %-8s %-20s %-10s\n" "WORKFLOW" "AGE" "LAST AUTH" "STATUS"
        printf "%-25s %-8s %-20s %-10s\n" "--------" "---" "---------" "------"

        for d in "$SESSIONS_DIR"/*/; do
            [ ! -d "$d" ] && continue
            auth_file="$d/.last-auth"
            [ ! -f "$auth_file" ] && continue
            found=1

            wf_name=$(basename "$d")
            auth_date=$(cat "$auth_file")
            age=$(file_age_days "$auth_file")

            status="fresh"
            [ "$age" -gt "$DEFAULT_MAX_AGE_DAYS" ] && status="STALE"

            has_profile="no"
            [ -d "$d/chrome-profile" ] && has_profile="yes"

            printf "%-25s %-8s %-20s %-10s\n" "$wf_name" "${age}d" "$auth_date" "$status"
        done

        if [ "$found" -eq 0 ]; then
            echo "(no sessions found)"
        fi
        ;;

    cleanup-all)
        if [ -d "$SESSIONS_DIR" ]; then
            count=0
            for d in "$SESSIONS_DIR"/*/; do
                [ ! -d "$d" ] && continue
                rm -rf "$d"
                count=$((count + 1))
            done
            echo "Cleaned up $count session(s)"
        else
            echo "No sessions to clean up"
        fi
        ;;

    *)
        echo "Error: Unknown subcommand '$SUBCMD'. Use --help for usage." >&2
        exit 1
        ;;
esac
