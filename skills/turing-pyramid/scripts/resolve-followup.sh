#!/bin/bash
# Turing Pyramid — Resolve Follow-Up
# Usage: ./resolve-followup.sh <id> [--impact 0.5] [--bulk-expire]
# --bulk-expire: expire all overdue self/auto follow-ups (for post-downtime cleanup)

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FOLLOWUPS_FILE="$SKILL_DIR/assets/followups.jsonl"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"

NOW=$(date +%s)
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Parse arguments
ID=""
IMPACT=""
BULK_EXPIRE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --impact) IMPACT="$2"; shift 2 ;;
        --impact=*) IMPACT="${1#*=}"; shift ;;
        --bulk-expire) BULK_EXPIRE=true; shift ;;
        *) ID="$1"; shift ;;
    esac
done

if [[ "$BULK_EXPIRE" == "true" ]]; then
    if [[ ! -f "$FOLLOWUPS_FILE" ]]; then
        echo "No followups file found."
        exit 0
    fi
    
    # Expire all ripe self/auto follow-ups older than 168h (1 week)
    TTL_SECONDS=604800
    CUTOFF_EPOCH=$((NOW - TTL_SECONDS))
    
    EXPIRED_COUNT=0
    STEWARD_COUNT=0
    TMP_FILE=$(mktemp)
    
    exec 201>"$FOLLOWUPS_FILE.lock"
    flock 201
    
    while IFS= read -r line; do
        status=$(echo "$line" | jq -r '.status')
        source=$(echo "$line" | jq -r '.source')
        check_epoch=$(echo "$line" | jq -r '.check_at_epoch // 0')
        
        if [[ "$status" == "pending" && "$check_epoch" -lt "$NOW" ]]; then
            if [[ "$source" == "steward" && "$check_epoch" -gt "$CUTOFF_EPOCH" ]]; then
                # Steward follow-up not yet past TTL — keep
                echo "$line" >> "$TMP_FILE"
                ((STEWARD_COUNT++))
            elif [[ "$source" == "steward" && "$check_epoch" -le "$CUTOFF_EPOCH" ]]; then
                # Steward follow-up past TTL — warn but keep, mark overdue
                what=$(echo "$line" | jq -r '.what')
                echo "🔴 Steward follow-up overdue (>7d): $what"
                echo "$line" >> "$TMP_FILE"
                ((STEWARD_COUNT++))
            else
                # Self/auto — expire
                echo "$line" | jq -c '.status = "expired" | .expired_at = "'"$NOW_ISO"'"' >> "$TMP_FILE"
                ((EXPIRED_COUNT++))
            fi
        else
            echo "$line" >> "$TMP_FILE"
        fi
    done < "$FOLLOWUPS_FILE"
    
    mv "$TMP_FILE" "$FOLLOWUPS_FILE"
    
    echo "Bulk expire: $EXPIRED_COUNT expired, $STEWARD_COUNT steward kept"
    exit 0
fi

# Single resolve
if [[ -z "$ID" ]]; then
    echo "Usage: $0 <followup-id> [--impact 0.5]"
    echo "       $0 --bulk-expire"
    exit 1
fi

if [[ ! -f "$FOLLOWUPS_FILE" ]]; then
    echo "❌ No followups file found"
    exit 1
fi

# Find the follow-up
ENTRY=$(jq -sc --arg id "$ID" '[.[] | select(.id == $id and .status != "done")] | .[0] // empty' "$FOLLOWUPS_FILE" 2>/dev/null)

if [[ -z "$ENTRY" ]]; then
    echo "❌ Follow-up not found or already resolved: $ID"
    exit 1
fi

NEED=$(echo "$ENTRY" | jq -r '.need')
WHAT=$(echo "$ENTRY" | jq -r '.what')

# Mark as done
exec 201>"$FOLLOWUPS_FILE.lock"
flock 201

TMP_FILE=$(mktemp)
while IFS= read -r line; do
    line_id=$(echo "$line" | jq -r '.id')
    if [[ "$line_id" == "$ID" ]]; then
        echo "$line" | jq -c '.status = "done" | .resolved_at = "'"$NOW_ISO"'"' >> "$TMP_FILE"
    else
        echo "$line" >> "$TMP_FILE"
    fi
done < "$FOLLOWUPS_FILE"
mv "$TMP_FILE" "$FOLLOWUPS_FILE"

echo "✅ Follow-up resolved: $WHAT"

# Optional satisfaction bump
if [[ -n "$IMPACT" ]]; then
    echo "   Bumping $NEED satisfaction by $IMPACT"
    bash "$SKILL_DIR/scripts/mark-satisfied.sh" "$NEED" "$IMPACT" --reason "follow-up resolved: $WHAT"
fi
