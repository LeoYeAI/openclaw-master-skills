#!/usr/bin/env bash
# =============================================================================
# Setup — Create worktree, branch, and initialize tracking state
# =============================================================================
# Usage: setup.sh <task_id> <branch> <worktree_dir> [task_desc] [backend]
#
# task_id:      Unique identifier (e.g., "add-pagination", "perf-analysis")
# branch:       Git branch name (e.g., "feat/add-pagination")
# worktree_dir: Path for git worktree
# task_desc:    Task description (any text: requirement, problem, issue body)
# backend:      "acpx" (default if available) or "tmux"
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
TASK_ID="${1:?Usage: setup.sh <task_id> <branch> <worktree_dir> [task_desc] [backend]}"
BRANCH="${2:?Usage: setup.sh <task_id> <branch> <worktree_dir> [task_desc] [backend]}"
WORKTREE_DIR="${3:?Usage: setup.sh <task_id> <branch> <worktree_dir> [task_desc] [backend]}"
TASK_DESC="${4:-No description provided}"
BACKEND="${5:-auto}"

# ---------------------------------------------------------------------------
# Auto-detect backend
# ---------------------------------------------------------------------------
if [ "$BACKEND" = "auto" ]; then
    if command -v acpx &>/dev/null; then
        BACKEND="acpx"
    elif command -v tmux &>/dev/null; then
        BACKEND="tmux"
    else
        echo "[setup] WARNING: Neither acpx nor tmux found. Backend set to 'none'."
        BACKEND="none"
    fi
fi

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT="$(git rev-parse --show-toplevel)"
ORCHESTRATOR_DIR="${REPO_ROOT}/.clawdbot"
ACTIVE_TASKS_FILE="${ORCHESTRATOR_DIR}/active-tasks.json"
MEMORY_FILE="${REPO_ROOT}/MEMORY.md"
DAILY_MEMORY_DIR="${REPO_ROOT}/memory"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DATE_TODAY="$(date -u +%Y-%m-%d)"
TIME_NOW="$(date -u +%H:%M)"

# ---------------------------------------------------------------------------
# Ensure directories
# ---------------------------------------------------------------------------
mkdir -p "$ORCHESTRATOR_DIR"
mkdir -p "$DAILY_MEMORY_DIR"

# ---------------------------------------------------------------------------
# 1. Create branch (skip if it already exists)
# ---------------------------------------------------------------------------
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
    echo "[setup] Branch '${BRANCH}' already exists — reusing."
else
    # Determine base branch
    BASE_BRANCH="main"
    if ! git show-ref --verify --quiet "refs/heads/main" && \
       ! git show-ref --verify --quiet "refs/remotes/origin/main"; then
        BASE_BRANCH="master"
    fi
    git branch "$BRANCH" "origin/${BASE_BRANCH}" 2>/dev/null || \
        git branch "$BRANCH" "${BASE_BRANCH}" 2>/dev/null || \
        git branch "$BRANCH"
    echo "[setup] Created branch '${BRANCH}'."
fi

# ---------------------------------------------------------------------------
# 2. Create worktree (skip if it already exists)
# ---------------------------------------------------------------------------
if [ -d "$WORKTREE_DIR" ]; then
    echo "[setup] Worktree '${WORKTREE_DIR}' already exists — reusing."
else
    git worktree add "$WORKTREE_DIR" "$BRANCH" 2>/dev/null || {
        echo "[setup] WARNING: Could not create worktree. Falling back to checkout."
        git checkout "$BRANCH"
        WORKTREE_DIR="$REPO_ROOT"
    }
    echo "[setup] Created worktree at '${WORKTREE_DIR}'."
fi

# ---------------------------------------------------------------------------
# 3. Initialize MEMORY.md
# ---------------------------------------------------------------------------
if ! [ -f "$MEMORY_FILE" ]; then
    cat > "$MEMORY_FILE" <<'HEADER'
# Project Memory

## In-Flight Tasks

HEADER
    echo "[setup] Created ${MEMORY_FILE}."
fi

# Ensure the "In-Flight Tasks" section exists
if ! grep -q "## In-Flight Tasks" "$MEMORY_FILE"; then
    printf '\n## In-Flight Tasks\n\n' >> "$MEMORY_FILE"
fi

# Truncate description for MEMORY.md entry (first 80 chars)
SHORT_DESC="${TASK_DESC:0:80}"
[ ${#TASK_DESC} -gt 80 ] && SHORT_DESC="${SHORT_DESC}..."

# Check if task entry already exists
if grep -q "### ${TASK_ID}:" "$MEMORY_FILE"; then
    echo "[setup] Task '${TASK_ID}' already in MEMORY.md — skipping."
else
    cat >> "$MEMORY_FILE" <<ENTRY

### ${TASK_ID}: ${SHORT_DESC}
- **Status**: pending
- **Branch**: ${BRANCH}
- **Session**: ${TASK_ID}
- **Backend**: ${BACKEND}
- **Agent**: TBD
- **Started**: ${TIMESTAMP}
- **Latest Milestone**: Initializing
- **Callback**: pending
ENTRY
    echo "[setup] Added task '${TASK_ID}' to MEMORY.md."
fi

# ---------------------------------------------------------------------------
# 4. Initialize / update active-tasks.json
# ---------------------------------------------------------------------------
if ! [ -f "$ACTIVE_TASKS_FILE" ]; then
    echo '{"tasks":[]}' > "$ACTIVE_TASKS_FILE"
    echo "[setup] Created ${ACTIVE_TASKS_FILE}."
fi

if command -v jq &>/dev/null; then
    EXISTING=$(jq -r --arg tid "$TASK_ID" '.tasks[] | select(.task_id == $tid) | .task_id' "$ACTIVE_TASKS_FILE")
    if [ -n "$EXISTING" ]; then
        echo "[setup] Task '${TASK_ID}' already in active-tasks.json — skipping."
    else
        TEMP_FILE=$(mktemp)
        jq --arg tid "$TASK_ID" \
           --arg sess "$TASK_ID" \
           --arg br "$BRANCH" \
           --arg wt "$WORKTREE_DIR" \
           --arg ts "$TIMESTAMP" \
           --arg be "$BACKEND" \
           --arg desc "$TASK_DESC" \
           '.tasks += [{
               "task_id": $tid,
               "session": $sess,
               "branch": $br,
               "worktree": $wt,
               "started_at": $ts,
               "status": "pending",
               "backend": $be,
               "description": $desc,
               "pid": null
           }]' "$ACTIVE_TASKS_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$ACTIVE_TASKS_FILE"
        echo "[setup] Registered task '${TASK_ID}' in active-tasks.json."
    fi
elif command -v python3 &>/dev/null; then
    python3 -c "
import json
with open('$ACTIVE_TASKS_FILE', 'r') as f:
    data = json.load(f)
if not any(t['task_id'] == '$TASK_ID' for t in data['tasks']):
    data['tasks'].append({
        'task_id': '$TASK_ID',
        'session': '$TASK_ID',
        'branch': '$BRANCH',
        'worktree': '$WORKTREE_DIR',
        'started_at': '$TIMESTAMP',
        'status': 'pending',
        'backend': '$BACKEND',
        'description': '''$TASK_DESC''',
        'pid': None
    })
    with open('$ACTIVE_TASKS_FILE', 'w') as f:
        json.dump(data, f, indent=2)
    print('[setup] Registered task in active-tasks.json (via python3).')
else:
    print('[setup] Task already in active-tasks.json — skipping.')
" 2>/dev/null || echo "[setup] WARNING: Could not update active-tasks.json."
fi

# ---------------------------------------------------------------------------
# 5. Save task description to file (for launch.sh to use as prompt)
# ---------------------------------------------------------------------------
TASK_DESC_FILE="${ORCHESTRATOR_DIR}/${TASK_ID}-desc.md"
echo "$TASK_DESC" > "$TASK_DESC_FILE"
echo "[setup] Saved task description to ${TASK_DESC_FILE}."

# ---------------------------------------------------------------------------
# 6. Write daily memory entry
# ---------------------------------------------------------------------------
DAILY_FILE="${DAILY_MEMORY_DIR}/${DATE_TODAY}.md"
if ! [ -f "$DAILY_FILE" ]; then
    echo "# ${DATE_TODAY}" > "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
fi
echo "- **${TIME_NOW}** [${TASK_ID}] Task initialized — branch: ${BRANCH}, backend: ${BACKEND}" >> "$DAILY_FILE"

# ---------------------------------------------------------------------------
# 7. Ensure .gitignore excludes runtime state
# ---------------------------------------------------------------------------
GITIGNORE="${REPO_ROOT}/.gitignore"
if ! [ -f "$GITIGNORE" ]; then
    touch "$GITIGNORE"
fi

for PATTERN in ".clawdbot/" "memory/" "*.pid"; do
    if ! grep -qF "$PATTERN" "$GITIGNORE"; then
        echo "$PATTERN" >> "$GITIGNORE"
    fi
done

# ---------------------------------------------------------------------------
echo "[setup] Done for task '${TASK_ID}'."
echo "[setup]   Branch:    ${BRANCH}"
echo "[setup]   Worktree:  ${WORKTREE_DIR}"
echo "[setup]   Backend:   ${BACKEND}"
echo "[setup]   MEMORY.md: updated"
