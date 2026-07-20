#!/usr/bin/env bash
# repair.sh — Loop 2: Attempt to fix a failed segment via the coding agent
# Usage: bash scripts/repair.sh <segment-name> <error-log-path> <attempt-number> [shiploop.yml]
#
# Constructs a repair prompt with full failure context and runs the agent.
# Exit 0 = agent completed (caller should re-run preflight/ship)
# Exit 1 = agent failed or error

set -euo pipefail

SEGMENT_NAME="${1:?Usage: repair.sh <segment-name> <error-log-path> <attempt-number> [shiploop.yml]}"
ERROR_LOG="${2:?Usage: repair.sh <segment-name> <error-log-path> <attempt-number>}"
ATTEMPT="${3:?Usage: repair.sh <segment-name> <error-log-path> <attempt-number>}"
SHIPLOOP_FILE="${4:-SHIPLOOP.yml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# --------------------------------------------------------------------------
# Parse agent config
# --------------------------------------------------------------------------
AGENT_COMMAND=$(grep "^agent_command:" "$SHIPLOOP_FILE" 2>/dev/null \
    | sed 's/^agent_command:[[:space:]]*//' \
    | sed 's/^["'"'"']//' | sed 's/["'"'"']$//' \
    | xargs 2>/dev/null || echo "")

if [[ -z "$AGENT_COMMAND" ]]; then
    echo "❌ No agent_command in $SHIPLOOP_FILE"
    exit 1
fi

AGENT_TIMEOUT=$(grep -A5 "^timeouts:" "$SHIPLOOP_FILE" 2>/dev/null \
    | grep "agent:" \
    | sed 's/.*agent:[[:space:]]*//' \
    | xargs 2>/dev/null || echo "900")
[[ -z "$AGENT_TIMEOUT" || "$AGENT_TIMEOUT" == "null" ]] && AGENT_TIMEOUT=900

# --------------------------------------------------------------------------
# Gather failure context
# --------------------------------------------------------------------------
ERROR_OUTPUT=""
if [[ -f "$ERROR_LOG" ]]; then
    ERROR_OUTPUT=$(tail -100 "$ERROR_LOG" 2>/dev/null || echo "(error log unreadable)")
fi

GIT_DIFF=$(git diff HEAD 2>/dev/null | head -500 || echo "(no diff)")
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | head -50 || echo "(none)")

# --------------------------------------------------------------------------
# Build repair prompt
# --------------------------------------------------------------------------
REPAIR_PROMPT_FILE=$(mktemp /tmp/shiploop-repair-XXXXXX.txt)

cat > "$REPAIR_PROMPT_FILE" << REPAIR_EOF
## REPAIR ATTEMPT ${ATTEMPT} for segment: ${SEGMENT_NAME}

The previous attempt to implement this segment failed. Your job is to FIX the issues
so the code builds, lints, and tests cleanly.

### Error Output
\`\`\`
${ERROR_OUTPUT}
\`\`\`

### Current Git Diff (changes so far)
\`\`\`diff
${GIT_DIFF}
\`\`\`

### Untracked Files
\`\`\`
${UNTRACKED}
\`\`\`

### Instructions
1. Read the error output carefully
2. Identify the root cause
3. Fix the code — do NOT start over from scratch unless the approach is fundamentally broken
4. Ensure the project builds, lints, and tests pass
5. Do NOT remove or disable tests to make them pass
REPAIR_EOF

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 REPAIR ATTEMPT $ATTEMPT: $SEGMENT_NAME"
echo "   Error log: $ERROR_LOG"
echo "   Agent: $AGENT_COMMAND"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --------------------------------------------------------------------------
# Run agent with repair prompt
# --------------------------------------------------------------------------
REPAIR_OUTPUT="/tmp/shiploop-repair-output-${SEGMENT_NAME}-${ATTEMPT}.log"

if timeout "${AGENT_TIMEOUT}" $AGENT_COMMAND < "$REPAIR_PROMPT_FILE" > "$REPAIR_OUTPUT" 2>&1; then
    echo "✅ Repair agent completed (attempt $ATTEMPT)"
    rm -f "$REPAIR_PROMPT_FILE"
    exit 0
else
    EXIT_CODE=$?
    echo "❌ Repair agent failed (attempt $ATTEMPT, exit $EXIT_CODE)"
    echo "   Last 15 lines:"
    tail -15 "$REPAIR_OUTPUT" 2>/dev/null | sed 's/^/   │ /' || true
    rm -f "$REPAIR_PROMPT_FILE"
    exit 1
fi
