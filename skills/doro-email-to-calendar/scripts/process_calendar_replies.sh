#!/bin/bash
# Process and disposition calendar reply emails (accepts, declines, tentatives)
# Usage: process_calendar_replies.sh [--dry-run] [--provider <provider>]
#
# Finds unread calendar reply emails from calendar-notification@google.com
# and dispositions them based on config settings.
#
# Options:
#   --dry-run           Show what would be processed without making changes
#   --provider <name>   Provider to use (default: from config)
#
# Calendar reply patterns matched:
#   - "Accepted: ..."
#   - "Declined: ..."
#   - "Tentative: ..."
#   - "Updated invitation: ..."
#   - "Cancelled: ..." / "Canceled: ..."

SCRIPT_DIR="$(dirname "$0")"
UTILS_DIR="$SCRIPT_DIR/utils"

DRY_RUN=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Check if auto_dispose_calendar_replies is enabled
SETTINGS=$(python3 "$UTILS_DIR/disposition_ops.py" settings 2>/dev/null)
AUTO_DISPOSE=$(echo "$SETTINGS" | jq -r '.auto_dispose_calendar_replies // true')

if [ "$AUTO_DISPOSE" != "true" ]; then
    echo '{"success": true, "message": "Calendar reply auto-disposition is disabled in config", "processed": 0}'
    exit 0
fi

# Search for unread calendar notification emails
SEARCH_QUERY="from:calendar-notification@google.com is:unread"
SEARCH_ARGS=(--query "$SEARCH_QUERY" --max 50)
if [ -n "$PROVIDER" ]; then
    SEARCH_ARGS+=(--provider "$PROVIDER")
fi
SEARCH_RESULT=$("$SCRIPT_DIR/email_search.sh" "${SEARCH_ARGS[@]}" 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$SEARCH_RESULT" ]; then
    echo '{"success": false, "error": "Failed to search for calendar reply emails"}'
    exit 1
fi

# Check if search was successful
SUCCESS=$(echo "$SEARCH_RESULT" | jq -r '.success // false')
if [ "$SUCCESS" != "true" ]; then
    echo "$SEARCH_RESULT"
    exit 1
fi

# Extract emails from search result
EMAILS=$(echo "$SEARCH_RESULT" | jq -r '.data // []')
EMAIL_COUNT=$(echo "$EMAILS" | jq 'length')

if [ "$EMAIL_COUNT" = "0" ] || [ "$EMAIL_COUNT" = "null" ]; then
    echo '{"success": true, "message": "No unread calendar reply emails found", "processed": 0}'
    exit 0
fi

# Process each email
PROCESSED=0
SKIPPED=0
ERRORS=0
PROCESSED_IDS=()

echo "$EMAILS" | jq -c '.[]' | while read -r email; do
    EMAIL_ID=$(echo "$email" | jq -r '.id // empty')
    SUBJECT=$(echo "$email" | jq -r '.subject // ""')

    if [ -z "$EMAIL_ID" ]; then
        continue
    fi

    # Check if subject matches calendar reply patterns
    SUBJECT_LOWER=$(echo "$SUBJECT" | tr '[:upper:]' '[:lower:]')
    IS_CALENDAR_REPLY=""

    case "$SUBJECT_LOWER" in
        accepted:*|declined:*|tentative:*|"updated invitation:"*|cancelled:*|canceled:*)
            IS_CALENDAR_REPLY="true"
            ;;
    esac

    if [ "$IS_CALENDAR_REPLY" != "true" ]; then
        echo "Skipping non-calendar-reply: $SUBJECT" >&2
        continue
    fi

    if [ "$DRY_RUN" = "true" ]; then
        echo "Would disposition: $EMAIL_ID - $SUBJECT" >&2
    else
        # Disposition the email
        DISPOSITION_ARGS=(--email-id "$EMAIL_ID")
        if [ -n "$PROVIDER" ]; then
            DISPOSITION_ARGS+=(--provider "$PROVIDER")
        fi
        RESULT=$("$SCRIPT_DIR/disposition_email.sh" "${DISPOSITION_ARGS[@]}" 2>/dev/null)
        if echo "$RESULT" | jq -e '.success' > /dev/null 2>&1; then
            echo "Dispositioned: $EMAIL_ID - $SUBJECT" >&2
        else
            echo "Failed to disposition: $EMAIL_ID - $SUBJECT" >&2
        fi
    fi
done

# Count results (need to re-process since while loop runs in subshell)
PROCESSED_COUNT=0
if [ "$DRY_RUN" != "true" ]; then
    echo "$EMAILS" | jq -c '.[]' | while read -r email; do
        SUBJECT=$(echo "$email" | jq -r '.subject // ""')
        SUBJECT_LOWER=$(echo "$SUBJECT" | tr '[:upper:]' '[:lower:]')
        case "$SUBJECT_LOWER" in
            accepted:*|declined:*|tentative:*|"updated invitation:"*|cancelled:*|canceled:*)
                PROCESSED_COUNT=$((PROCESSED_COUNT + 1))
                ;;
        esac
    done
fi

# Output summary
if [ "$DRY_RUN" = "true" ]; then
    echo "{\"success\": true, \"dry_run\": true, \"message\": \"Dry run complete\", \"emails_found\": $EMAIL_COUNT}"
else
    echo "{\"success\": true, \"message\": \"Calendar replies processed\", \"emails_found\": $EMAIL_COUNT}"
fi
