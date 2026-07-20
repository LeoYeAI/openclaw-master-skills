#!/usr/bin/env bash
# meta-experiment.sh — Loop 3: Run a single experiment branch for a failed segment
# Usage: bash scripts/meta-experiment.sh <segment-name> <failure-history-file> <experiment-number> <experiment-prompt-file> [shiploop.yml]
#
# Creates an experiment branch from last-known-good, runs agent with the experiment
# prompt, then runs preflight. Reports pass/fail + diff stats.
#
# Exit 0 = experiment passed preflight (candidate)
# Exit 1 = experiment failed

set -euo pipefail

SEGMENT_NAME="${1:?Usage: meta-experiment.sh <segment-name> <failure-history> <exp-number> <prompt-file> [shiploop.yml]}"
FAILURE_HISTORY="${2:?Usage: meta-experiment.sh <segment-name> <failure-history> <exp-number> <prompt-file>}"
EXPERIMENT_NUM="${3:?Usage: meta-experiment.sh <segment-name> <failure-history> <exp-number> <prompt-file>}"
EXPERIMENT_PROMPT="${4:?Usage: meta-experiment.sh <segment-name> <failure-history> <exp-number> <prompt-file>}"
SHIPLOOP_FILE="${5:-SHIPLOOP.yml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# --------------------------------------------------------------------------
# Parse config
# --------------------------------------------------------------------------
AGENT_COMMAND=$(grep "^agent_command:" "$SHIPLOOP_FILE" 2>/dev/null \
    | sed 's/^agent_command:[[:space:]]*//' \
    | sed 's/^["'"'"']//' | sed 's/["'"'"']$//' \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || echo "")

if [[ -z "$AGENT_COMMAND" ]]; then
    echo "❌ No agent_command in $SHIPLOOP_FILE"
    exit 1
fi

AGENT_TIMEOUT=$(grep -A5 "^timeouts:" "$SHIPLOOP_FILE" 2>/dev/null \
    | grep "agent:" \
    | sed 's/.*agent:[[:space:]]*//' \
    | xargs 2>/dev/null || echo "900")
[[ -z "$AGENT_TIMEOUT" || "$AGENT_TIMEOUT" == "null" ]] && AGENT_TIMEOUT=900

BRANCH_NAME="experiment/${SEGMENT_NAME}-${EXPERIMENT_NUM}"
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Find last known-good commit
LAST_GOOD=$(grep "last_good_commit:" "$SHIPLOOP_FILE" 2>/dev/null \
    | sed 's/.*last_good_commit:[[:space:]]*//' \
    | sed 's/"//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || echo "")

# Handle null/empty — default to HEAD
if [[ -z "$LAST_GOOD" || "$LAST_GOOD" == "null" || "$LAST_GOOD" == "~" ]]; then
    BASE_REF="HEAD"
else
    BASE_REF="$LAST_GOOD"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 EXPERIMENT $EXPERIMENT_NUM: $SEGMENT_NAME"
echo "   Branch: $BRANCH_NAME"
echo "   Base: $BASE_REF"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --------------------------------------------------------------------------
# Create experiment branch
# --------------------------------------------------------------------------
# Clean working tree (caller already discarded failed changes, but be safe)
git checkout -- . 2>/dev/null || true
git clean -fd 2>/dev/null || true

# Delete branch if it exists from a previous run
git branch -D "$BRANCH_NAME" 2>/dev/null || true
git checkout -b "$BRANCH_NAME" "$BASE_REF"

echo "   ✅ Created branch from $BASE_REF"

# --------------------------------------------------------------------------
# Run agent with experiment prompt
# --------------------------------------------------------------------------
echo ""
echo "🤖 Running agent with experiment prompt..."

EXP_OUTPUT="/tmp/shiploop-experiment-${SEGMENT_NAME}-${EXPERIMENT_NUM}.log"

if timeout "${AGENT_TIMEOUT}" $AGENT_COMMAND < "$EXPERIMENT_PROMPT" > "$EXP_OUTPUT" 2>&1; then
    echo "   ✅ Agent completed"
else
    EXIT_CODE=$?
    echo "   ❌ Agent failed (exit $EXIT_CODE)"
    tail -10 "$EXP_OUTPUT" 2>/dev/null | sed 's/^/   │ /' || true
    # Return to original branch
    git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
    exit 1
fi

# --------------------------------------------------------------------------
# Run preflight
# --------------------------------------------------------------------------
echo ""
echo "🛫 Running preflight on experiment..."

PREFLIGHT_LOG="/tmp/shiploop-experiment-preflight-${SEGMENT_NAME}-${EXPERIMENT_NUM}.log"

if bash "$SCRIPT_DIR/preflight.sh" "$SHIPLOOP_FILE" > "$PREFLIGHT_LOG" 2>&1; then
    echo "   ✅ Preflight PASSED"

    # Collect diff stats
    DIFF_STAT=$(git diff --stat "$BASE_REF" 2>/dev/null | tail -1 || echo "unknown")
    DIFF_LINES=$(git diff --stat "$BASE_REF" 2>/dev/null | wc -l || echo "0")

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ EXPERIMENT $EXPERIMENT_NUM PASSED"
    echo "   Diff: $DIFF_STAT"
    echo "META_EXPERIMENT_RESULT|status=pass|experiment=$EXPERIMENT_NUM|branch=$BRANCH_NAME|diff_lines=$DIFF_LINES"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Stay on experiment branch (caller will merge if this is the winner)
    exit 0
else
    echo "   ❌ Preflight FAILED"
    tail -15 "$PREFLIGHT_LOG" 2>/dev/null | sed 's/^/   │ /' || true

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ EXPERIMENT $EXPERIMENT_NUM FAILED"
    echo "META_EXPERIMENT_RESULT|status=fail|experiment=$EXPERIMENT_NUM|branch=$BRANCH_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Return to original branch
    git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
    exit 1
fi
