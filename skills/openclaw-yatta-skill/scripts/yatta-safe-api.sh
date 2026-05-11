#!/usr/bin/env bash
#
# yatta-safe-api.sh - Safe API wrapper functions for Yatta!
#
# Demonstrates proper input sanitization to prevent shell and JSON injection
# Use these patterns when constructing Yatta! API calls
#

set -euo pipefail

# Verify required tools
for cmd in jq curl; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: $cmd is required but not installed" >&2
    exit 1
  fi
done

# Verify environment
if [[ -z "${YATTA_API_URL:-}" ]]; then
  echo "Error: YATTA_API_URL environment variable not set" >&2
  exit 1
fi

if [[ -z "${YATTA_API_KEY:-}" ]]; then
  echo "Error: YATTA_API_KEY environment variable not set" >&2
  exit 1
fi

# ============================================================================
# SAFE PATTERN: URL Encoding for Path Parameters
# ============================================================================
# Always URL-encode IDs used in URL paths to prevent shell injection
#
# UNSAFE:   curl "$API_URL/tasks/$TASK_ID"
# SAFE:     curl "$API_URL/tasks/$(url_encode "$TASK_ID")"
# ============================================================================

url_encode() {
  printf %s "$1" | jq -sRr @uri
}

# ============================================================================
# SAFE PATTERN: JSON Construction with jq
# ============================================================================
# Always use jq to build JSON payloads, never string interpolation
#
# UNSAFE:   -d "{\"title\": \"$TITLE\"}"
# SAFE:     -d "$(build_json title "$TITLE")"
# ============================================================================

build_json() {
  local -a args=()
  while [[ $# -gt 0 ]]; do
    local key="$1"
    local value="$2"
    args+=(--arg "$key" "$value")
    shift 2
  done
  
  # Build object from arguments
  local fields=""
  for ((i=0; i<${#args[@]}; i+=2)); do
    local key="${args[i+1]}"
    [[ -n "$fields" ]] && fields+=", "
    fields+="$key: \$$key"
  done
  
  jq -n "${args[@]}" "{$fields}"
}

# ============================================================================
# Task Operations
# ============================================================================

# Create a task (safe)
yatta_create_task() {
  local title="$1"
  local priority="${2:-medium}"
  
  local payload
  payload=$(jq -n \
    --arg title "$title" \
    --arg priority "$priority" \
    '{title: $title, priority: $priority}')
  
  curl -s "$YATTA_API_URL/tasks" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Update a task (safe)
yatta_update_task() {
  local task_id="$1"
  local field="$2"
  local value="$3"
  
  # URL-encode the task ID for path parameter
  local task_id_encoded
  task_id_encoded=$(url_encode "$task_id")
  
  # Build JSON payload safely with jq
  local payload
  payload=$(jq -n \
    --arg id "$task_id" \
    --arg field_value "$value" \
    '{id: $id, ($field): $field_value}' \
    --arg field "$field")
  
  curl -s -X PUT "$YATTA_API_URL/tasks" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Complete a task (safe)
yatta_complete_task() {
  local task_id="$1"
  
  local payload
  payload=$(jq -n \
    --arg id "$task_id" \
    --arg status "done" \
    --arg completed_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    '{id: $id, status: $status, completed_at: $completed_at}')
  
  curl -s -X PUT "$YATTA_API_URL/tasks" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Archive a task (safe)
yatta_archive_task() {
  local task_id="$1"
  
  local payload
  payload=$(jq -n \
    --arg id "$task_id" \
    '{id: $id}')
  
  curl -s -X DELETE "$YATTA_API_URL/tasks" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Get task by ID (safe)
yatta_get_task() {
  local task_id="$1"
  local task_id_encoded
  task_id_encoded=$(url_encode "$task_id")
  
  curl -s "$YATTA_API_URL/tasks/$task_id_encoded" \
    -H "Authorization: Bearer $YATTA_API_KEY"
}

# ============================================================================
# Project Operations
# ============================================================================

# Create a project (safe)
yatta_create_project() {
  local name="$1"
  local description="${2:-}"
  local color="${3:-#3b82f6}"
  
  local payload
  payload=$(jq -n \
    --arg name "$name" \
    --arg description "$description" \
    --arg color "$color" \
    '{name: $name, description: $description, color: $color}')
  
  curl -s "$YATTA_API_URL/projects" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Update a project (safe)
yatta_update_project() {
  local project_id="$1"
  local name="$2"
  
  local payload
  payload=$(jq -n \
    --arg id "$project_id" \
    --arg name "$name" \
    '{id: $id, name: $name}')
  
  curl -s -X PUT "$YATTA_API_URL/projects" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Get project tasks (safe)
yatta_get_project_tasks() {
  local project_id="$1"
  local project_id_encoded
  project_id_encoded=$(url_encode "$project_id")
  
  curl -s "$YATTA_API_URL/projects/$project_id_encoded/tasks" \
    -H "Authorization: Bearer $YATTA_API_KEY"
}

# ============================================================================
# Comment Operations
# ============================================================================

# Add comment to task (safe)
yatta_add_comment() {
  local task_id="$1"
  local content="$2"
  local task_id_encoded
  task_id_encoded=$(url_encode "$task_id")
  
  local payload
  payload=$(jq -n \
    --arg content "$content" \
    '{content: $content}')
  
  curl -s -X POST "$YATTA_API_URL/tasks/$task_id_encoded/comments" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Update comment (safe)
yatta_update_comment() {
  local comment_id="$1"
  local content="$2"
  
  local payload
  payload=$(jq -n \
    --arg id "$comment_id" \
    --arg content "$content" \
    '{id: $id, content: $content}')
  
  curl -s -X PUT "$YATTA_API_URL/task-comments" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Delete comment (safe)
yatta_delete_comment() {
  local comment_id="$1"
  
  local payload
  payload=$(jq -n \
    --arg id "$comment_id" \
    '{id: $id}')
  
  curl -s -X DELETE "$YATTA_API_URL/task-comments" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# ============================================================================
# Context Operations
# ============================================================================

# Create context (safe)
yatta_create_context() {
  local name="$1"
  local color="${2:-#8b5cf6}"
  
  local payload
  payload=$(jq -n \
    --arg name "$name" \
    --arg color "$color" \
    '{name: $name, color: $color}')
  
  curl -s "$YATTA_API_URL/contexts" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# Assign context to task (safe)
yatta_assign_context() {
  local task_id="$1"
  local context_id="$2"
  
  local payload
  payload=$(jq -n \
    --arg task_id "$task_id" \
    --arg context_id "$context_id" \
    '{task_id: $task_id, context_ids: [$context_id]}')
  
  curl -s -X POST "$YATTA_API_URL/contexts/assign" \
    -H "Authorization: Bearer $YATTA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# ============================================================================
# Usage Examples
# ============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  cat <<'EOF'
Safe Yatta! API Wrapper Functions

Usage:
  source scripts/yatta-safe-api.sh

  # Create task
  yatta_create_task "Finish report" "high"

  # Update task
  yatta_update_task "$TASK_ID" "status" "done"

  # Complete task
  yatta_complete_task "$TASK_ID"

  # Archive task
  yatta_archive_task "$TASK_ID"

  # Add comment
  yatta_add_comment "$TASK_ID" "Waiting on client"

  # Create project
  yatta_create_project "Website Redesign" "Complete overhaul"

Why these patterns are safe:
  1. jq -n --arg properly escapes strings (no JSON injection)
  2. jq -sRr @uri URL-encodes path parameters (no shell injection)
  3. No direct string interpolation in JSON or URLs
  4. All user input sanitized before use

See SECURITY.md for vulnerability examples and testing guidance.
EOF
fi
