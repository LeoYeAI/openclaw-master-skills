#!/bin/bash
# WAL Capture Script - Write-Ahead Log Protocol
# Part of learning-loop skill v1.3.0
#
# Usage: bash wal-capture.sh <workspace> <type> <content>
# Types: correction, decision, preference, fact, blocker
#
# This script appends critical details to SESSION-STATE.md
# BEFORE responding to Greg. Part of the WAL Protocol.

WORKSPACE="${1:-/Users/gregborden/.openclaw/workspace}"
TYPE="$2"
CONTENT="$3"

if [ -z "$TYPE" ] || [ -z "$CONTENT" ]; then
    echo "Usage: $0 <workspace> <type> <content>"
    echo "Types: correction, decision, preference, fact, blocker"
    exit 1
fi

SESSION_STATE="$WORKSPACE/SESSION-STATE.md"
TIMESTAMP=$(date '+%Y-%m-%d %I:%M%p EST')

# Ensure SESSION-STATE.md exists
if [ ! -f "$SESSION_STATE" ]; then
    cat > "$SESSION_STATE" << 'EOF'
# SESSION-STATE.md - Active Working Memory (WAL Target)
_Write here BEFORE responding. This file survives compaction._
_Last updated: Never_

## Current Task
<!-- What we're working on right now -->

## Active Context
<!-- Current state, recent decisions -->

## Key Decisions (This Session)
<!-- Append: [timestamp] Decision made -->

## Corrections & Preferences
<!-- Append here when Greg corrects anything -->

## Pending Actions
<!-- What's queued up next -->
EOF
fi

# Append based on type
case "$TYPE" in
    correction)
        echo "" >> "$SESSION_STATE"
        echo "- [$TIMESTAMP] CORRECTION: $CONTENT" >> "$SESSION_STATE"
        ;;
    decision)
        echo "" >> "$SESSION_STATE"
        echo "- [$TIMESTAMP] DECISION: $CONTENT" >> "$SESSION_STATE"
        ;;
    preference)
        echo "" >> "$SESSION_STATE"
        echo "- [$TIMESTAMP] PREFERENCE: $CONTENT" >> "$SESSION_STATE"
        ;;
    fact)
        echo "" >> "$SESSION_STATE"
        echo "- [$TIMESTAMP] FACT: $CONTENT" >> "$SESSION_STATE"
        ;;
    blocker)
        echo "" >> "$SESSION_STATE"
        echo "- [$TIMESTAMP] BLOCKER: $CONTENT" >> "$SESSION_STATE"
        ;;
    *)
        echo "" >> "$SESSION_STATE"
        echo "- [$TIMESTAMP] $TYPE: $CONTENT" >> "$SESSION_STATE"
        ;;
esac

# Update the timestamp line
sed -i '' "s/_Last updated:.*/_Last updated: $TIMESTAMP _/" "$SESSION_STATE" 2>/dev/null || \
    sed -i "s/_Last updated:.*/_Last updated: $TIMESTAMP _/" "$SESSION_STATE" 2>/dev/null

echo "WAL captured: $TYPE"
