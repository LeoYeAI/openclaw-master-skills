#!/usr/bin/env bash
# run-segment.sh — Orchestrate a single ship-loop segment with repair + meta loops
# Usage: bash scripts/run-segment.sh <segment-name> <prompt-file-path> [shiploop.yml]
#
# Three-loop architecture:
#   Loop 1: code → preflight → ship → verify (standard pipeline)
#   Loop 2: on failure → repair agent → re-run preflight → retry (up to N times)
#   Loop 3: on repair exhaustion → meta-analysis → experiment branches → pick winner
#
# Exit 0 = segment shipped and verified
# Exit 1 = failure (all loops exhausted)

set -euo pipefail

SEGMENT_NAME="${1:?Usage: run-segment.sh <segment-name> <prompt-file-path> [shiploop.yml]}"
PROMPT_FILE="${2:?Usage: run-segment.sh <segment-name> <prompt-file-path>}"
SHIPLOOP_FILE="${3:-SHIPLOOP.yml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_DIR"

# --------------------------------------------------------------------------
# Trap: clean up temp files on exit (normal or error)
# --------------------------------------------------------------------------
cleanup() {
    rm -f /tmp/shiploop-augmented-*.txt \
          /tmp/shiploop-agent-output-*.log \
          /tmp/shiploop-preflight-*.log \
          /tmp/shiploop-failure-history-*.txt \
          /tmp/shiploop-meta-*.txt \
          /tmp/shiploop-meta-output-*.log \
          /tmp/shiploop-exp-prompt-*.txt \
          /tmp/shiploop-experiment-*.log \
          /tmp/shiploop-experiment-preflight-*.log
}
trap cleanup EXIT

# --------------------------------------------------------------------------
# Validate inputs
# --------------------------------------------------------------------------
if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "❌ Prompt file not found: $PROMPT_FILE"
    exit 1
fi

if [[ ! -f "$SHIPLOOP_FILE" ]]; then
    echo "❌ SHIPLOOP.yml not found: $SHIPLOOP_FILE"
    exit 1
fi

PROMPT=$(cat "$PROMPT_FILE")
if [[ -z "$PROMPT" ]]; then
    echo "❌ Prompt file is empty: $PROMPT_FILE"
    exit 1
fi

# --------------------------------------------------------------------------
# Parse config from SHIPLOOP.yml
# --------------------------------------------------------------------------
AGENT_TIMEOUT=$(grep -A5 "^timeouts:" "$SHIPLOOP_FILE" 2>/dev/null \
    | grep "agent:" \
    | sed 's/.*agent:[[:space:]]*//' \
    | xargs 2>/dev/null || echo "900")
[[ -z "$AGENT_TIMEOUT" || "$AGENT_TIMEOUT" == "null" ]] && AGENT_TIMEOUT=900

AGENT_COMMAND=$(grep "^agent_command:" "$SHIPLOOP_FILE" 2>/dev/null \
    | sed 's/^agent_command:[[:space:]]*//' \
    | sed 's/^["'"'"']//' | sed 's/["'"'"']$//' \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || echo "")

if [[ -z "$AGENT_COMMAND" ]]; then
    echo "❌ No agent_command defined in $SHIPLOOP_FILE"
    exit 1
fi

# Repair config
MAX_REPAIR=$(grep -A3 "^repair:" "$SHIPLOOP_FILE" 2>/dev/null \
    | grep "max_attempts:" \
    | sed 's/.*max_attempts:[[:space:]]*//' \
    | xargs 2>/dev/null || echo "3")
[[ -z "$MAX_REPAIR" || "$MAX_REPAIR" == "null" ]] && MAX_REPAIR=3

# Meta config
META_ENABLED=$(grep -A3 "^meta:" "$SHIPLOOP_FILE" 2>/dev/null \
    | grep "enabled:" \
    | sed 's/.*enabled:[[:space:]]*//' \
    | xargs 2>/dev/null || echo "true")
[[ -z "$META_ENABLED" || "$META_ENABLED" == "null" ]] && META_ENABLED=true

META_EXPERIMENTS=$(grep -A3 "^meta:" "$SHIPLOOP_FILE" 2>/dev/null \
    | grep "experiments:" \
    | sed 's/.*experiments:[[:space:]]*//' \
    | xargs 2>/dev/null || echo "3")
[[ -z "$META_EXPERIMENTS" || "$META_EXPERIMENTS" == "null" ]] && META_EXPERIMENTS=3

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚢 SEGMENT: $SEGMENT_NAME"
echo "   Agent timeout: ${AGENT_TIMEOUT}s"
echo "   Repair attempts: $MAX_REPAIR"
echo "   Meta loop: $META_ENABLED (experiments: $META_EXPERIMENTS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --------------------------------------------------------------------------
# Load learnings into agent context (if learnings.yml exists)
# --------------------------------------------------------------------------
LEARNINGS_CONTEXT=""
if [[ -f "learnings.yml" ]]; then
    # Extract multi-word phrases (bigrams/trigrams) from prompt, skip stop words, max 10 keywords
    STOP_WORDS="a an the is are was were to from in on of for with by at and or but not this that it"
    # Get meaningful single words (4+ chars, not stop words)
    SINGLE_WORDS=$(echo "$PROMPT" | tr -cs '[:alnum:]' ' ' | tr ' ' '\n' | tr '[:upper:]' '[:lower:]' \
        | awk -v stops="$STOP_WORDS" 'BEGIN{split(stops,s," ");for(i in s)sw[s[i]]=1} length>=4 && !sw[$0]{print}' \
        | sort -u | head -10 | tr '\n' ' ')
    # Get bigrams from prompt (adjacent word pairs)
    BIGRAMS=$(echo "$PROMPT" | tr -cs '[:alnum:]' ' ' | tr '[:upper:]' '[:lower:]' \
        | awk '{for(i=1;i<NF;i++) print $i" "$(i+1)}' \
        | awk -v stops="$STOP_WORDS" 'BEGIN{split(stops,s," ");for(i in s)sw[s[i]]=1} {split($0,w," "); if(!sw[w[1]] && !sw[w[2]] && length(w[1])>=3 && length(w[2])>=3) print}' \
        | head -5 | tr '\n' '|')
    KEYWORDS="${SINGLE_WORDS}${BIGRAMS}"
    LEARNINGS_CONTEXT=$(bash "$SCRIPT_DIR/learnings.sh" load "$KEYWORDS" "learnings.yml" 2>/dev/null || true)
fi

# If we have learnings, prepend them to the prompt
if [[ -n "$LEARNINGS_CONTEXT" ]]; then
    AUGMENTED_PROMPT_FILE=$(mktemp /tmp/shiploop-augmented-XXXXXX.txt)
    {
        echo "$LEARNINGS_CONTEXT"
        echo ""
        echo "---"
        echo ""
        cat "$PROMPT_FILE"
    } > "$AUGMENTED_PROMPT_FILE"
    ACTIVE_PROMPT="$AUGMENTED_PROMPT_FILE"
    echo "   📚 Loaded relevant learnings into prompt"
else
    ACTIVE_PROMPT="$PROMPT_FILE"
fi

# --------------------------------------------------------------------------
# Step 1: Run coding agent (Loop 1)
# --------------------------------------------------------------------------
echo ""
echo "🤖 Running coding agent: $AGENT_COMMAND"

AGENT_LOG="/tmp/shiploop-agent-output-${SEGMENT_NAME}.log"
AGENT_START=$(date +%s)

if timeout "${AGENT_TIMEOUT}" $AGENT_COMMAND < "$ACTIVE_PROMPT" > "$AGENT_LOG" 2>&1; then
    AGENT_ELAPSED=$(( $(date +%s) - AGENT_START ))
    echo "✅ Agent completed in ${AGENT_ELAPSED}s"
else
    EXIT_CODE=$?
    AGENT_ELAPSED=$(( $(date +%s) - AGENT_START ))
    if [[ $EXIT_CODE -eq 124 ]]; then
        echo "❌ Agent timed out after ${AGENT_TIMEOUT}s"
    else
        echo "❌ Agent failed (exit $EXIT_CODE, ${AGENT_ELAPSED}s)"
    fi
    tail -20 "$AGENT_LOG" 2>/dev/null | sed 's/^/   │ /' || true
    exit 1
fi

# --------------------------------------------------------------------------
# Step 2: Run preflight checks
# --------------------------------------------------------------------------
echo ""
echo "🛫 Running preflight checks..."

PREFLIGHT_LOG="/tmp/shiploop-preflight-${SEGMENT_NAME}.log"

run_preflight() {
    bash "$SCRIPT_DIR/preflight.sh" "$SHIPLOOP_FILE" > "$PREFLIGHT_LOG" 2>&1
}

if run_preflight; then
    echo "✅ Preflight passed"
else
    echo "❌ Preflight FAILED — entering repair loop"
    cat "$PREFLIGHT_LOG" | tail -30 | sed 's/^/   │ /'

    # ------------------------------------------------------------------
    # Loop 2: Repair Loop
    # ------------------------------------------------------------------
    REPAIR_SUCCESS=false
    ERROR_SIGNATURES=()

    for attempt in $(seq 1 "$MAX_REPAIR"); do
        echo ""
        echo "🔧 Repair attempt $attempt/$MAX_REPAIR"

        # Capture error signature (first error line) for convergence detection
        ERROR_SIG=$(grep -m1 -iE "(error|fail|cannot|undefined|not found)" "$PREFLIGHT_LOG" 2>/dev/null || echo "unknown-error")
        ERROR_SIGNATURES+=("$ERROR_SIG")

        # Convergence check: if last 2 error signatures are identical, short-circuit to meta loop
        if [[ ${#ERROR_SIGNATURES[@]} -ge 2 ]]; then
            PREV_SIG="${ERROR_SIGNATURES[$(( ${#ERROR_SIGNATURES[@]} - 2 ))]}"
            if [[ "$ERROR_SIG" == "$PREV_SIG" ]]; then
                echo "   ⚠️  Convergence detected: same error twice in a row, skipping remaining repairs"
                break
            fi
        fi

        # Run repair agent
        if bash "$SCRIPT_DIR/repair.sh" "$SEGMENT_NAME" "$PREFLIGHT_LOG" "$attempt" "$SHIPLOOP_FILE"; then
            # Re-run preflight after repair
            echo "   🛫 Re-running preflight after repair..."
            if run_preflight; then
                echo "   ✅ Preflight passed after repair attempt $attempt"
                REPAIR_SUCCESS=true

                # Record the learning with detailed context
                FAILURE_DESC=$(echo "$ERROR_SIG" | head -c 200)
                REPAIR_DIFF_STAT=$(git diff --stat HEAD 2>/dev/null | tail -5 | tr '\n' '; ' || echo "unknown")
                bash "$SCRIPT_DIR/learnings.sh" record \
                    "$SEGMENT_NAME" \
                    "$FAILURE_DESC" \
                    "Fixed by repair loop attempt $attempt. Error sig: ${ERROR_SIG:0:100}" \
                    "Files changed: ${REPAIR_DIFF_STAT}" \
                    "learnings.yml" 2>/dev/null || true

                break
            else
                echo "   ❌ Preflight still failing after repair attempt $attempt"
                cat "$PREFLIGHT_LOG" | tail -15 | sed 's/^/   │ /'
            fi
        else
            echo "   ❌ Repair agent failed on attempt $attempt"
        fi
    done

    if ! $REPAIR_SUCCESS; then
        echo ""
        echo "❌ Repair loop exhausted ($MAX_REPAIR attempts)"

        # ------------------------------------------------------------------
        # Loop 3: Meta Loop
        # ------------------------------------------------------------------
        if [[ "$META_ENABLED" != "true" ]]; then
            echo "   Meta loop disabled — segment failed"
            exit 1
        fi

        echo ""
        echo "🧪 Entering meta loop..."

        # Discard uncommitted changes from failed attempts (they're worthless)
        git checkout -- . 2>/dev/null || true
        git clean -fd 2>/dev/null || true

        # Collect all failure context
        FAILURE_HISTORY=$(mktemp /tmp/shiploop-failure-history-XXXXXX.txt)
        {
            echo "# Failure History for: $SEGMENT_NAME"
            echo ""
            echo "## Original Prompt"
            cat "$PROMPT_FILE"
            echo ""
            echo "## Error Signatures from Repair Attempts"
            for i in "${!ERROR_SIGNATURES[@]}"; do
                echo "  Attempt $((i+1)): ${ERROR_SIGNATURES[$i]}"
            done
            echo ""
            echo "## Last Preflight Output"
            cat "$PREFLIGHT_LOG" 2>/dev/null || echo "(unavailable)"
            echo ""
            echo "## Git Diff at Failure"
            git diff HEAD 2>/dev/null | head -500 || echo "(no diff)"
        } > "$FAILURE_HISTORY"

        # Step 1: Meta-analysis — ask agent WHY everything fails
        echo "   🧠 Running meta-analysis..."
        META_PROMPT=$(mktemp /tmp/shiploop-meta-XXXXXX.txt)
        cat > "$META_PROMPT" << META_EOF
## META-ANALYSIS: Why does segment "$SEGMENT_NAME" keep failing?

All $MAX_REPAIR repair attempts failed. Analyze the failure history below and:

1. Identify the ROOT CAUSE — not the symptom, the underlying issue
2. Propose $META_EXPERIMENTS different approaches to solve this, each fundamentally different
3. For each approach, write a COMPLETE implementation prompt

Output format (exactly):
---APPROACH 1---
<complete prompt for approach 1>
---APPROACH 2---
<complete prompt for approach 2>
---APPROACH 3---
<complete prompt for approach 3>

$(cat "$FAILURE_HISTORY")
META_EOF

        META_OUTPUT="/tmp/shiploop-meta-output-${SEGMENT_NAME}.log"
        if timeout "${AGENT_TIMEOUT}" $AGENT_COMMAND < "$META_PROMPT" > "$META_OUTPUT" 2>&1; then
            echo "   ✅ Meta-analysis complete"
        else
            echo "   ❌ Meta-analysis agent failed — segment failed"
            rm -f "$META_PROMPT" "$FAILURE_HISTORY"
            exit 1
        fi

        # Step 2: Parse experiment prompts from meta output
        ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
        CANDIDATES=()
        CANDIDATE_DIFFS=()

        for exp_num in $(seq 1 "$META_EXPERIMENTS"); do
            echo ""
            echo "   🧪 Experiment $exp_num/$META_EXPERIMENTS"

            # Extract experiment prompt from meta output
            EXP_PROMPT_FILE=$(mktemp /tmp/shiploop-exp-prompt-XXXXXX.txt)

            # Parse between ---APPROACH N--- markers (lenient: allow whitespace, skip code fences)
            awk "
                /^\`\`\`/{next}
                /^[[:space:]]*---[[:space:]]*APPROACH[[:space:]]+${exp_num}[[:space:]]*---[[:space:]]*\$/{found=1; next}
                /^[[:space:]]*---[[:space:]]*APPROACH[[:space:]]+[0-9]+[[:space:]]*---/{found=0}
                found{print}
            " "$META_OUTPUT" > "$EXP_PROMPT_FILE" 2>/dev/null || true

            # If parsing failed, use a generic variant
            if [[ ! -s "$EXP_PROMPT_FILE" ]]; then
                echo "   ⚠️  Could not parse ---APPROACH ${exp_num}--- marker, using fallback prompt"
                cat > "$EXP_PROMPT_FILE" << FALLBACK_EOF
## Alternative approach $exp_num for: $SEGMENT_NAME

The standard approach failed $MAX_REPAIR times. Try a different strategy.

Original task:
$(cat "$PROMPT_FILE")

What failed previously:
$(cat "$FAILURE_HISTORY" | tail -50)

Use approach $exp_num: try a fundamentally different implementation strategy.
FALLBACK_EOF
            fi

            # Run experiment
            if bash "$SCRIPT_DIR/meta-experiment.sh" \
                "$SEGMENT_NAME" "$FAILURE_HISTORY" "$exp_num" "$EXP_PROMPT_FILE" "$SHIPLOOP_FILE"; then
                CANDIDATES+=("$exp_num")
                # Get diff lines for tiebreaker
                DIFF_LINES=$(git diff --stat "$(git merge-base HEAD "$ORIGINAL_BRANCH")" 2>/dev/null | wc -l || echo "999")
                CANDIDATE_DIFFS+=("$DIFF_LINES")
                echo "   ✅ Experiment $exp_num is a candidate (diff: $DIFF_LINES lines)"

                # Return to original branch before next experiment
                git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
            else
                echo "   ❌ Experiment $exp_num failed"
            fi

            rm -f "$EXP_PROMPT_FILE"
        done

        # Step 3: Pick winner
        if [[ ${#CANDIDATES[@]} -gt 0 ]]; then
            # Pick simplest diff as tiebreaker
            WINNER_IDX=0
            WINNER_DIFF=${CANDIDATE_DIFFS[0]}
            for i in "${!CANDIDATES[@]}"; do
                if [[ ${CANDIDATE_DIFFS[$i]} -lt $WINNER_DIFF ]]; then
                    WINNER_IDX=$i
                    WINNER_DIFF=${CANDIDATE_DIFFS[$i]}
                fi
            done

            WINNER_NUM=${CANDIDATES[$WINNER_IDX]}
            WINNER_BRANCH="experiment/${SEGMENT_NAME}-${WINNER_NUM}"

            echo ""
            echo "🏆 Winner: experiment $WINNER_NUM (branch: $WINNER_BRANCH, diff: $WINNER_DIFF lines)"
            echo "   Merging to $ORIGINAL_BRANCH..."

            git checkout "$ORIGINAL_BRANCH"
            git merge "$WINNER_BRANCH" -m "feat(shiploop): ${SEGMENT_NAME} via meta-experiment ${WINNER_NUM}" || {
                echo "   ❌ Merge conflicts detected — refusing to auto-resolve (could destroy production code)"
                echo "   Conflicting files:"
                git diff --name-only --diff-filter=U 2>/dev/null | sed 's/^/      /'
                git merge --abort 2>/dev/null || true
                echo "   Winner branch preserved: $WINNER_BRANCH"
                echo "   Resolve conflicts manually and merge $WINNER_BRANCH into $ORIGINAL_BRANCH"
                exit 1
            }

            # Record learning
            bash "$SCRIPT_DIR/learnings.sh" record \
                "$SEGMENT_NAME" \
                "Repair loop exhausted after $MAX_REPAIR attempts" \
                "Required meta-analysis and experiment branching" \
                "Experiment $WINNER_NUM succeeded with alternative approach" \
                "learnings.yml" 2>/dev/null || true

            # Clean up experiment branches
            for exp_num in $(seq 1 "$META_EXPERIMENTS"); do
                git branch -D "experiment/${SEGMENT_NAME}-${exp_num}" 2>/dev/null || true
            done

            echo "   ✅ Winner merged, experiment branches cleaned"
        else
            echo ""
            echo "❌ ALL $META_EXPERIMENTS experiments failed — segment failed"

            # Record learning about total failure
            bash "$SCRIPT_DIR/learnings.sh" record \
                "$SEGMENT_NAME" \
                "All repair and meta-experiment attempts failed" \
                "Task may need decomposition or human intervention" \
                "Review failure history at $FAILURE_HISTORY" \
                "learnings.yml" 2>/dev/null || true

            # Restore original branch
            git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true

            rm -f "$META_PROMPT" "$META_OUTPUT"
            exit 1
        fi

        rm -f "$META_PROMPT" "$META_OUTPUT" "$FAILURE_HISTORY"
    fi
fi

# --------------------------------------------------------------------------
# Step 3: Ship (stage, commit, push, verify)
# --------------------------------------------------------------------------
echo ""
echo "📦 Shipping..."

if bash "$SCRIPT_DIR/ship.sh" "$SEGMENT_NAME" "$SHIPLOOP_FILE"; then
    echo "✅ Shipped successfully"
else
    echo "❌ Ship FAILED"
    exit 1
fi

# --------------------------------------------------------------------------
# Step 4: Cleanup
# --------------------------------------------------------------------------
echo ""
echo "🧹 Cleanup..."

rm -f "$PROMPT_FILE" "${AUGMENTED_PROMPT_FILE:-}" "$AGENT_LOG" "$PREFLIGHT_LOG"
echo "   Removed temp files"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SEGMENT COMPLETE: $SEGMENT_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
exit 0
