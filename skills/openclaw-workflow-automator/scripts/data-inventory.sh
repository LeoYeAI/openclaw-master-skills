#!/usr/bin/env bash
set -eo pipefail

# data-inventory.sh — Show and manage all persistent data stored by this skill.
# Gives users full visibility and control over what's on their disk.

BASE_DIR="$HOME/.openclaw/workflow-automator"

usage() {
    cat <<'EOF'
Usage: data-inventory.sh <subcommand> [options]

Show and manage all persistent data stored by workflow-automator.

Subcommands:
  show              Show all stored data with disk usage and permissions
  purge <category>  Delete data for a category
                    Categories: schedules, approvals, sessions, screenshots,
                                runs, audit, all
  purge-workflow <name>  Delete ALL data for a specific workflow

Options:
  --force    Skip confirmation prompt for purge
  --help     Show this help message

Data location: ~/.openclaw/workflow-automator/

Categories:
  schedules/    — Workflow schedule definitions (JSON)
  approvals/    — Plan approval records with SHA-256 hashes
  sessions/     — Browser session data (cookies, localStorage)
  screenshots/  — Browser screenshots for audit trail
  runs/         — Execution logs per workflow run
  audit.log     — Append-only execution audit log
EOF
    exit 0
}

[ "${1:-}" = "--help" ] && usage
[ $# -lt 1 ] && { echo "Error: No subcommand provided. Use --help for usage." >&2; exit 1; }

SUBCMD="$1"
shift
FORCE="false"
for arg in "$@"; do
    [ "$arg" = "--force" ] && FORCE="true"
done

# Helper: get directory size
dir_size() {
    if [ -d "$1" ]; then
        du -sh "$1" 2>/dev/null | awk '{print $1}'
    else
        echo "0B"
    fi
}

# Helper: count files in directory
file_count() {
    if [ -d "$1" ]; then
        find "$1" -type f 2>/dev/null | wc -l | tr -d ' '
    else
        echo "0"
    fi
}

# Helper: get permissions
dir_perms() {
    if [ -d "$1" ]; then
        ls -ld "$1" | awk '{print $1}'
    elif [ -f "$1" ]; then
        ls -l "$1" | awk '{print $1}'
    else
        echo "(not created)"
    fi
}

case "$SUBCMD" in
    show)
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║           WORKFLOW AUTOMATOR — DATA INVENTORY              ║"
        echo "╠══════════════════════════════════════════════════════════════╣"
        echo "║ Base directory: ~/.openclaw/workflow-automator/             ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""

        TOTAL_SIZE=$(dir_size "$BASE_DIR")
        echo "Total disk usage: $TOTAL_SIZE"
        echo ""

        printf "%-15s %-8s %-8s %-12s %s\n" "CATEGORY" "FILES" "SIZE" "PERMISSIONS" "SENSITIVITY"
        printf "%-15s %-8s %-8s %-12s %s\n" "--------" "-----" "----" "-----------" "-----------"

        # Schedules
        printf "%-15s %-8s %-8s %-12s %s\n" \
            "schedules/" \
            "$(file_count "$BASE_DIR/schedules")" \
            "$(dir_size "$BASE_DIR/schedules")" \
            "$(dir_perms "$BASE_DIR/schedules")" \
            "low — workflow definitions"

        # Approvals
        printf "%-15s %-8s %-8s %-12s %s\n" \
            "approvals/" \
            "$(file_count "$BASE_DIR/approvals")" \
            "$(dir_size "$BASE_DIR/approvals")" \
            "$(dir_perms "$BASE_DIR/approvals")" \
            "medium — plan hashes"

        # Sessions
        sess_count=$(file_count "$BASE_DIR/sessions")
        printf "%-15s %-8s %-8s %-12s %s\n" \
            "sessions/" \
            "$sess_count" \
            "$(dir_size "$BASE_DIR/sessions")" \
            "$(dir_perms "$BASE_DIR/sessions")" \
            "HIGH — browser cookies/auth"

        # Screenshots
        printf "%-15s %-8s %-8s %-12s %s\n" \
            "screenshots/" \
            "$(file_count "$BASE_DIR/screenshots")" \
            "$(dir_size "$BASE_DIR/screenshots")" \
            "$(dir_perms "$BASE_DIR/screenshots")" \
            "medium — may contain sensitive data"

        # Runs
        printf "%-15s %-8s %-8s %-12s %s\n" \
            "runs/" \
            "$(file_count "$BASE_DIR/runs")" \
            "$(dir_size "$BASE_DIR/runs")" \
            "$(dir_perms "$BASE_DIR/runs")" \
            "low — execution logs"

        # Audit log
        audit_lines=0
        [ -f "$BASE_DIR/audit.log" ] && audit_lines=$(wc -l < "$BASE_DIR/audit.log" | tr -d ' ')
        printf "%-15s %-8s %-8s %-12s %s\n" \
            "audit.log" \
            "$audit_lines" \
            "$([ -f "$BASE_DIR/audit.log" ] && du -sh "$BASE_DIR/audit.log" | awk '{print $1}' || echo "0B")" \
            "$(dir_perms "$BASE_DIR/audit.log")" \
            "low — execution history"

        # Env check cache
        printf "%-15s %-8s %-8s %-12s %s\n" \
            ".env-check" \
            "$([ -f "$BASE_DIR/.env-check-cache" ] && echo "1" || echo "0")" \
            "4B" \
            "$(dir_perms "$BASE_DIR/.env-check-cache")" \
            "none — cached check result"

        echo ""

        # Session detail if any exist
        if [ "$sess_count" -gt 0 ] && [ -d "$BASE_DIR/sessions" ]; then
            echo "Active browser sessions:"
            for d in "$BASE_DIR/sessions"/*/; do
                [ ! -d "$d" ] && continue
                wf=$(basename "$d")
                auth_file="$d/.last-auth"
                has_profile="no"
                [ -d "$d/chrome-profile" ] && has_profile="yes"
                if [ -f "$auth_file" ]; then
                    auth_date=$(cat "$auth_file")
                    echo "  $wf — last auth: $auth_date, profile on disk: $has_profile"
                fi
            done
            echo ""
        fi

        echo "To purge a category: data-inventory.sh purge <category>"
        echo "To purge everything: data-inventory.sh purge all"
        ;;

    purge)
        [ $# -lt 1 ] && { echo "Error: purge requires a category (schedules/approvals/sessions/screenshots/runs/audit/all)" >&2; exit 1; }
        CATEGORY="$1"

        case "$CATEGORY" in
            schedules)   TARGET="$BASE_DIR/schedules" ;;
            approvals)   TARGET="$BASE_DIR/approvals" ;;
            sessions)    TARGET="$BASE_DIR/sessions" ;;
            screenshots) TARGET="$BASE_DIR/screenshots" ;;
            runs)        TARGET="$BASE_DIR/runs" ;;
            audit)       TARGET="$BASE_DIR/audit.log" ;;
            all)         TARGET="$BASE_DIR" ;;
            *) echo "Error: Unknown category '$CATEGORY'" >&2; exit 1 ;;
        esac

        if [ "$FORCE" = "false" ]; then
            if [ "$CATEGORY" = "all" ]; then
                echo "This will delete ALL workflow-automator data:"
                echo "  $BASE_DIR"
            elif [ "$CATEGORY" = "audit" ]; then
                echo "This will delete the audit log:"
                echo "  $TARGET"
            else
                echo "This will delete all files in:"
                echo "  $TARGET/"
                echo "  ($(file_count "$TARGET") files, $(dir_size "$TARGET"))"
            fi
            printf "Are you sure? (yes/no) "
            read -r confirm
            if [ "$confirm" != "yes" ]; then
                echo "Cancelled."
                exit 0
            fi
        fi

        if [ "$CATEGORY" = "all" ]; then
            rm -rf "$BASE_DIR"
            echo "Purged: all workflow-automator data"
        elif [ "$CATEGORY" = "audit" ]; then
            rm -f "$TARGET"
            echo "Purged: audit log"
        else
            rm -rf "${TARGET:?}"/*
            echo "Purged: $CATEGORY ($(dir_size "$TARGET"))"
        fi
        ;;

    purge-workflow)
        [ $# -lt 1 ] && { echo "Error: purge-workflow requires: <workflow-name>" >&2; exit 1; }
        WF_NAME="$1"
        SLUG=$(echo "$WF_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

        echo "Purging all data for workflow: $WF_NAME ($SLUG)"
        removed=0

        # Schedule
        if [ -f "$BASE_DIR/schedules/${SLUG}.json" ]; then
            rm -f "$BASE_DIR/schedules/${SLUG}.json"
            echo "  Removed: schedules/${SLUG}.json"
            removed=$((removed + 1))
        fi

        # Approval
        if [ -f "$BASE_DIR/approvals/${SLUG}.json" ]; then
            rm -f "$BASE_DIR/approvals/${SLUG}.json"
            echo "  Removed: approvals/${SLUG}.json"
            removed=$((removed + 1))
        fi

        # Session
        if [ -d "$BASE_DIR/sessions/${SLUG}" ]; then
            rm -rf "$BASE_DIR/sessions/${SLUG}"
            echo "  Removed: sessions/${SLUG}/"
            removed=$((removed + 1))
        fi

        # Runs
        if [ -d "$BASE_DIR/runs/${SLUG}" ]; then
            rm -rf "$BASE_DIR/runs/${SLUG}"
            echo "  Removed: runs/${SLUG}/"
            removed=$((removed + 1))
        fi

        # Screenshots
        if [ -d "$BASE_DIR/screenshots" ]; then
            count=$(find "$BASE_DIR/screenshots" -name "${SLUG}_*" 2>/dev/null | wc -l | tr -d ' ')
            if [ "$count" -gt 0 ]; then
                find "$BASE_DIR/screenshots" -name "${SLUG}_*" -delete
                echo "  Removed: $count screenshots"
                removed=$((removed + 1))
            fi
        fi

        if [ "$removed" -eq 0 ]; then
            echo "  No data found for '$WF_NAME'"
        else
            echo "Done. Removed $removed categories."
        fi
        ;;

    *)
        echo "Error: Unknown subcommand '$SUBCMD'. Use --help for usage." >&2
        exit 1
        ;;
esac
