#!/bin/bash
# Learning Loop - Daily Lesson Extractor
# Scans daily log files for uncaptured events and extracts them
# Usage: bash extract.sh [workspace-dir] [date]

set -o pipefail

WORKSPACE="${1:-$(pwd)}"
TARGET_DATE="${2:-$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d yesterday +%Y-%m-%d)}"
LEARNING_DIR="$WORKSPACE/memory/learning"
DAILY_LOG="$WORKSPACE/memory/$TARGET_DATE.md"
EVENTS_FILE="$LEARNING_DIR/events.jsonl"

echo "Learning Loop - Daily Extraction"
echo "Date: $TARGET_DATE"
echo "Daily log: $DAILY_LOG"
echo ""

if [ ! -f "$DAILY_LOG" ]; then
    echo "No daily log found for $TARGET_DATE. Nothing to extract."
    exit 0
fi

if [ ! -f "$EVENTS_FILE" ]; then
    echo "Warning: events.jsonl not found. Run init.sh first."
    echo "Creating empty events.jsonl..."
    mkdir -p "$LEARNING_DIR"
    touch "$EVENTS_FILE"
fi

# Count existing events from this date
EXISTING=$(grep -c "\"ts\":\"$TARGET_DATE" "$EVENTS_FILE" 2>/dev/null | head -1 | tr -d '[:space:]')
EXISTING=${EXISTING:-0}
echo "Existing events from $TARGET_DATE: $EXISTING"

# Look for patterns in the daily log that suggest uncaptured events
echo ""
echo "=== Scanning for patterns ==="

# Pattern 1: Debug/fix mentions
FIXES=$(grep -ciE 'fix|debug|broke|error|issue|problem|solved|workaround' "$DAILY_LOG" 2>/dev/null | head -1 | tr -d '[:space:]')
FIXES=${FIXES:-0}
echo "Debug/fix mentions: $FIXES"

# Pattern 2: Lesson/learning mentions
LESSONS=$(grep -ciE 'lesson|learned|realized|mistake|wrong|correct|should have' "$DAILY_LOG" 2>/dev/null | head -1 | tr -d '[:space:]')
LESSONS=${LESSONS:-0}
echo "Lesson mentions: $LESSONS"

# Pattern 3: Feedback signals
FEEDBACK=$(grep -ciE 'unacceptable|perfect|exactly|wrong|great|annoying|frustrated' "$DAILY_LOG" 2>/dev/null | head -1 | tr -d '[:space:]')
FEEDBACK=${FEEDBACK:-0}
echo "Feedback signals: $FEEDBACK"

# Pattern 4: New capability mentions
CAPABILITIES=$(grep -ciE 'built|created|configured|set up|installed|authenticated|connected' "$DAILY_LOG" 2>/dev/null | head -1 | tr -d '[:space:]')
CAPABILITIES=${CAPABILITIES:-0}
echo "New capabilities: $CAPABILITIES"

TOTAL_SIGNAL=$((FIXES + LESSONS + FEEDBACK + CAPABILITIES))
echo ""
echo "Total signal strength: $TOTAL_SIGNAL"

if [ "$TOTAL_SIGNAL" -eq 0 ]; then
    echo "No actionable patterns found. Clean day."
    exit 0
fi

echo ""
echo "=== Sections with signal ==="
# Extract relevant sections for the agent to process
grep -B1 -A3 -iE 'fix|debug|broke|error|lesson|learned|mistake|built|created|configured|unacceptable|perfect' "$DAILY_LOG" 2>/dev/null | head -60

echo ""
echo "=== Action needed ==="
echo "Review the above sections and:"
echo "  1. Create events for any uncaptured debugging sessions"
echo "  2. Create events for any mistakes or corrections"
echo "  3. Create events for any new capabilities learned"
echo "  4. Update rules.json if any lesson is now proven (3+ occurrences)"
echo ""
echo "Append events to: $EVENTS_FILE"
