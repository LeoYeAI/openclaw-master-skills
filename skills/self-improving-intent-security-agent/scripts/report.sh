#!/usr/bin/env bash
# Generate summary report of agent activity
#
# This script reads intent, violation, and learning files from the .agent/ directory
# and generates a summary report.
# It does NOT require any environment variables or credentials.
# All data is read locally and displayed to stdout.
# No data is transmitted externally.

set -e

AGENT_DIR="${1:-.agent}"

if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent directory not found: $AGENT_DIR"
    exit 1
fi

echo "========================================="
echo "  Intent Security Agent Report"
echo "========================================="
echo ""

# Count active intents
ACTIVE_INTENTS=$(grep -l "Status\*\*: active" "$AGENT_DIR"/intents/*.md 2>/dev/null | wc -l | tr -d ' ')
COMPLETED_INTENTS=$(grep -l "Status\*\*: completed" "$AGENT_DIR"/intents/*.md 2>/dev/null | wc -l | tr -d ' ')
VIOLATED_INTENTS=$(grep -l "Status\*\*: violated" "$AGENT_DIR"/intents/*.md 2>/dev/null | wc -l | tr -d ' ')

echo "📋 Intents"
echo "  Active: $ACTIVE_INTENTS"
echo "  Completed: $COMPLETED_INTENTS"
echo "  Violated: $VIOLATED_INTENTS"
echo ""

# Count violations by severity
if [ -d "$AGENT_DIR/violations" ]; then
    CRITICAL=$(grep -l "Severity\*\*: critical" "$AGENT_DIR"/violations/*.md 2>/dev/null | wc -l | tr -d ' ')
    HIGH=$(grep -l "Severity\*\*: high" "$AGENT_DIR"/violations/*.md 2>/dev/null | wc -l | tr -d ' ')
    MEDIUM=$(grep -l "Severity\*\*: medium" "$AGENT_DIR"/violations/*.md 2>/dev/null | wc -l | tr -d ' ')
    LOW=$(grep -l "Severity\*\*: low" "$AGENT_DIR"/violations/*.md 2>/dev/null | wc -l | tr -d ' ')

    echo "🚨 Violations"
    echo "  Critical: $CRITICAL"
    echo "  High: $HIGH"
    echo "  Medium: $MEDIUM"
    echo "  Low: $LOW"
    echo ""
fi

# Count learnings
if [ -d "$AGENT_DIR/learnings" ]; then
    TOTAL_LEARNINGS=$(find "$AGENT_DIR/learnings" -name "LRN-*.md" 2>/dev/null | wc -l | tr -d ' ')
    PENDING=$(grep -l "Status\*\*: pending" "$AGENT_DIR"/learnings/LRN-*.md 2>/dev/null | wc -l | tr -d ' ')
    VALIDATED=$(grep -l "Status\*\*: validated" "$AGENT_DIR"/learnings/LRN-*.md 2>/dev/null | wc -l | tr -d ' ')
    PROMOTED=$(grep -l "Status\*\*: promoted" "$AGENT_DIR"/learnings/LRN-*.md 2>/dev/null | wc -l | tr -d ' ')

    echo "🧠 Learnings"
    echo "  Total: $TOTAL_LEARNINGS"
    echo "  Pending: $PENDING"
    echo "  Validated: $VALIDATED"
    echo "  Promoted: $PROMOTED"
    echo ""
fi

# Count strategies
if [ -f "$AGENT_DIR/learnings/STRATEGIES.md" ]; then
    TESTING=$(grep -c "Status\*\*: testing" "$AGENT_DIR/learnings/STRATEGIES.md" 2>/dev/null || echo "0")
    ADOPTED=$(grep -c "Status\*\*: adopted" "$AGENT_DIR/learnings/STRATEGIES.md" 2>/dev/null || echo "0")
    REJECTED=$(grep -c "Status\*\*: rejected" "$AGENT_DIR/learnings/STRATEGIES.md" 2>/dev/null || echo "0")

    echo "📊 Strategies"
    echo "  Testing: $TESTING"
    echo "  Adopted: $ADOPTED"
    echo "  Rejected: $REJECTED"
    echo ""
fi

# Count rollbacks
if [ -f "$AGENT_DIR/audit/ROLLBACKS.md" ]; then
    ROLLBACKS=$(grep -c "^## \[RBK-" "$AGENT_DIR/audit/ROLLBACKS.md" 2>/dev/null || echo "0")
    echo "↩️  Rollbacks: $ROLLBACKS"
    echo ""
fi

# Recent activity
echo "📅 Recent Activity (last 7 days)"
echo ""

# Find files modified in last 7 days
RECENT=$(find "$AGENT_DIR" -name "*.md" -mtime -7 2>/dev/null | wc -l | tr -d ' ')
echo "  Modified files: $RECENT"

# Show latest violations if any
if [ -d "$AGENT_DIR/violations" ]; then
    LATEST_VIOLATION=$(ls -t "$AGENT_DIR"/violations/*.md 2>/dev/null | head -1)
    if [ -n "$LATEST_VIOLATION" ]; then
        echo ""
        echo "  Latest violation:"
        grep "^## \[" "$LATEST_VIOLATION" | sed 's/^/    /'
    fi
fi

# Show latest learning if any
if [ -d "$AGENT_DIR/learnings" ]; then
    LATEST_LEARNING=$(find "$AGENT_DIR/learnings" -name "LRN-*.md" -type f 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
    if [ -n "$LATEST_LEARNING" ]; then
        echo ""
        echo "  Latest learning:"
        grep "^## \[" "$LATEST_LEARNING" | sed 's/^/    /'
    fi
fi

echo ""
echo "========================================="
echo ""
echo "For detailed analysis:"
echo "  Violations: ls -lt $AGENT_DIR/violations/"
echo "  Learnings: cat $AGENT_DIR/learnings/LEARNINGS.md"
echo "  Strategies: cat $AGENT_DIR/learnings/STRATEGIES.md"
