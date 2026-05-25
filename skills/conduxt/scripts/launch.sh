#!/usr/bin/env bash
# =============================================================================
# Launch — Start coding agent via ACPX (preferred) or tmux (fallback)
# =============================================================================
# Usage: launch.sh <task_id> <worktree_dir> <prompt_file> [backend] [agent]
#
# task_id:      Must match setup.sh's task_id
# worktree_dir: Working directory for the agent
# prompt_file:  File containing the task description
# backend:      "acpx" | "tmux" | "auto" (default: auto-detect)
# agent:        "claude" | "gemini" | "codex" | "aider" | "auto" (default: auto)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
TASK_ID="${1:?Usage: launch.sh <task_id> <worktree_dir> <prompt_file> [backend] [agent]}"
WORKTREE_DIR="${2:?Usage: launch.sh <task_id> <worktree_dir> <prompt_file> [backend] [agent]}"
PROMPT_FILE="${3:?Usage: launch.sh <task_id> <worktree_dir> <prompt_file> [backend] [agent]}"
BACKEND="${4:-auto}"
AGENT="${5:-auto}"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TMUX_SOCKET="/tmp/openclaw-tmux/openclaw.sock"
REPO_ROOT="$(git rev-parse --show-toplevel)"
ORCHESTRATOR_DIR="${REPO_ROOT}/.clawdbot"
ACTIVE_TASKS_FILE="${ORCHESTRATOR_DIR}/active-tasks.json"
MEMORY_FILE="${REPO_ROOT}/MEMORY.md"
DAILY_MEMORY_DIR="${REPO_ROOT}/memory"
DATE_TODAY="$(date -u +%Y-%m-%d)"
TIME_NOW="$(date -u +%H:%M)"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$ORCHESTRATOR_DIR"

# ---------------------------------------------------------------------------
# Auto-detect backend
# ---------------------------------------------------------------------------
if [ "$BACKEND" = "auto" ]; then
    if command -v acpx &>/dev/null; then
        BACKEND="acpx"
    elif command -v tmux &>/dev/null; then
        BACKEND="tmux"
    else
        echo "[launch] ERROR: Neither acpx nor tmux found."
        exit 1
    fi
fi
echo "[launch] Backend: ${BACKEND}"

# ---------------------------------------------------------------------------
# Auto-detect agent
# ---------------------------------------------------------------------------
if [ "$AGENT" = "auto" ]; then
    if command -v claude &>/dev/null; then
        AGENT="claude"
    elif command -v gemini &>/dev/null; then
        AGENT="gemini"
    elif command -v codex &>/dev/null; then
        AGENT="codex"
    elif command -v aider &>/dev/null; then
        AGENT="aider"
    else
        AGENT="none"
        echo "[launch] WARNING: No coding agent found."
    fi
fi
echo "[launch] Agent: ${AGENT}"

# ---------------------------------------------------------------------------
# Build full prompt with callback instruction
# ---------------------------------------------------------------------------
FULL_PROMPT_FILE=$(mktemp)
CURRENT_BRANCH="$(cd "$WORKTREE_DIR" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"

cat > "$FULL_PROMPT_FILE" <<PROMPT_HEADER
# Task Assignment

You are an autonomous coding agent. Complete the following task in this
repository. When finished, you MUST output a structured callback.

## Working Directory
$(realpath "$WORKTREE_DIR")

## Task Description
$(cat "$PROMPT_FILE")

## Structured Callback (MANDATORY)

When you complete this task, output the following JSON block on a line by
itself, wrapped in triple backticks with language tag "callback-json":

\`\`\`callback-json
{
  "task_id": "${TASK_ID}",
  "status": "completed",
  "branch": "${CURRENT_BRANCH}",
  "files_changed": ["list all files you modified"],
  "test_results": { "passed": 0, "failed": 0, "skipped": 0 },
  "duration_minutes": 0,
  "summary": "Brief description of what was done"
}
\`\`\`

### Status Values
- **completed**: Task is done (fill in test_results and files_changed)
- **failed**: Task could not be completed (explain in summary)
- **need_clarification**: Blocked, need user input (explain in summary)

### Rules
1. Always commit your changes before outputting the callback
2. Run tests and report accurate test_results
3. The callback JSON must be valid JSON
4. Do not skip the callback — it is how the orchestrator knows you are done
PROMPT_HEADER

echo "[launch] Built prompt ($(wc -l < "$FULL_PROMPT_FILE") lines)."

# Save prompt for debugging
cp "$FULL_PROMPT_FILE" "${ORCHESTRATOR_DIR}/${TASK_ID}-prompt.md"

# ---------------------------------------------------------------------------
# Launch via selected backend
# ---------------------------------------------------------------------------
LAUNCH_PID="unknown"

if [ "$BACKEND" = "acpx" ]; then
    # -----------------------------------------------------------------------
    # ACPX backend (preferred)
    # -----------------------------------------------------------------------
    echo "[launch] Starting via ACPX..."

    PROMPT_CONTENT="$(cat "$FULL_PROMPT_FILE")"

    # Use acpx with appropriate agent adapter
    case "$AGENT" in
        claude)
            ACPX_AGENT_FLAG="" ;;  # default agent
        gemini)
            ACPX_AGENT_FLAG="--agent gemini" ;;
        codex)
            ACPX_AGENT_FLAG="--agent codex" ;;
        *)
            ACPX_AGENT_FLAG="" ;;
    esac

    # Launch: --no-wait returns immediately, --approve-all prevents TTY blocks
    cd "$WORKTREE_DIR"
    # shellcheck disable=SC2086
    acpx prompt \
        -s "$TASK_ID" \
        --no-wait \
        --approve-all \
        $ACPX_AGENT_FLAG \
        "$PROMPT_CONTENT" 2>&1 || {
        echo "[launch] ACPX failed. Falling back to tmux..."
        BACKEND="tmux"
    }

    if [ "$BACKEND" = "acpx" ]; then
        LAUNCH_PID="acpx:${TASK_ID}"
        echo "[launch] ACPX session '${TASK_ID}' started."
    fi
fi

if [ "$BACKEND" = "tmux" ]; then
    # -----------------------------------------------------------------------
    # tmux backend (fallback)
    # -----------------------------------------------------------------------
    echo "[launch] Starting via tmux..."

    mkdir -p "$(dirname "$TMUX_SOCKET")"

    # Kill existing session (idempotent)
    if tmux -S "$TMUX_SOCKET" has-session -t "$TASK_ID" 2>/dev/null; then
        echo "[launch] Session '${TASK_ID}' exists. Killing and re-creating."
        tmux -S "$TMUX_SOCKET" kill-session -t "$TASK_ID"
    fi

    # Create session
    tmux -S "$TMUX_SOCKET" new-session -d -s "$TASK_ID" -c "$WORKTREE_DIR"

    # Detect agent command
    case "$AGENT" in
        claude)  AGENT_CMD="claude --print" ;;
        gemini)  AGENT_CMD="gemini" ;;
        codex)   AGENT_CMD="codex" ;;
        aider)   AGENT_CMD="aider" ;;
        *)       AGENT_CMD="" ;;
    esac

    if [ -n "$AGENT_CMD" ]; then
        tmux -S "$TMUX_SOCKET" send-keys -t "$TASK_ID" \
            "${AGENT_CMD} < '${FULL_PROMPT_FILE}'" Enter
    else
        tmux -S "$TMUX_SOCKET" send-keys -t "$TASK_ID" \
            "cat '${FULL_PROMPT_FILE}'" Enter
    fi

    LAUNCH_PID=$(tmux -S "$TMUX_SOCKET" display-message -t "$TASK_ID" -p '#{pane_pid}' 2>/dev/null || echo "unknown")
    echo "[launch] tmux session '${TASK_ID}' started (PID: ${LAUNCH_PID})."
fi

# ---------------------------------------------------------------------------
# Update active-tasks.json
# ---------------------------------------------------------------------------
if command -v jq &>/dev/null && [ -f "$ACTIVE_TASKS_FILE" ]; then
    TEMP_FILE=$(mktemp)
    jq --arg tid "$TASK_ID" \
       --arg ts "$TIMESTAMP" \
       --arg pid "$LAUNCH_PID" \
       --arg be "$BACKEND" \
       --arg ag "$AGENT" \
       '(.tasks[] | select(.task_id == $tid)) |= . + {
           "status": "running",
           "launched_at": $ts,
           "backend": $be,
           "agent": $ag,
           "pid": $pid
       }' "$ACTIVE_TASKS_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$ACTIVE_TASKS_FILE"
fi

# ---------------------------------------------------------------------------
# Update MEMORY.md
# ---------------------------------------------------------------------------
if [ -f "$MEMORY_FILE" ] && command -v sed &>/dev/null; then
    sed -i '' "/### ${TASK_ID}:/,/^### / {
        s/- \*\*Status\*\*: pending/- **Status**: in-progress/
        s/- \*\*Backend\*\*: .*/- **Backend**: ${BACKEND}/
        s/- \*\*Agent\*\*: .*/- **Agent**: ${AGENT}/
        s/- \*\*Latest Milestone\*\*: .*/- **Latest Milestone**: ${TIME_NOW} - Agent launched/
    }" "$MEMORY_FILE" 2>/dev/null || true
fi

# ---------------------------------------------------------------------------
# Write daily memory
# ---------------------------------------------------------------------------
DAILY_FILE="${DAILY_MEMORY_DIR}/${DATE_TODAY}.md"
if [ -f "$DAILY_FILE" ]; then
    echo "- **${TIME_NOW}** [${TASK_ID}] Agent launched (${BACKEND}/${AGENT})" >> "$DAILY_FILE"
fi

# ---------------------------------------------------------------------------
# Start watchdog for tmux backend (ACPX has built-in crash recovery)
# ---------------------------------------------------------------------------
if [ "$BACKEND" = "tmux" ]; then
    WATCHDOG_SCRIPT="$(dirname "$0")/watchdog.sh"
    if [ -f "$WATCHDOG_SCRIPT" ] && [ -x "$WATCHDOG_SCRIPT" ]; then
        echo "[launch] Starting watchdog for task '${TASK_ID}'."
        nohup "$WATCHDOG_SCRIPT" "$TASK_ID" > "${ORCHESTRATOR_DIR}/${TASK_ID}-watchdog.log" 2>&1 &
        WATCHDOG_PID=$!
        echo "$WATCHDOG_PID" > "${ORCHESTRATOR_DIR}/${TASK_ID}-watchdog.pid"
    fi
fi

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
rm -f "$FULL_PROMPT_FILE"

echo ""
echo "[launch] Done for task '${TASK_ID}'."
echo "[launch]   Backend:  ${BACKEND}"
echo "[launch]   Agent:    ${AGENT}"
echo "[launch]   PID:      ${LAUNCH_PID}"
if [ "$BACKEND" = "tmux" ]; then
    echo "[launch]   Attach:   tmux -S ${TMUX_SOCKET} attach -t ${TASK_ID}"
elif [ "$BACKEND" = "acpx" ]; then
    echo "[launch]   Status:   acpx sessions show -s ${TASK_ID}"
fi
