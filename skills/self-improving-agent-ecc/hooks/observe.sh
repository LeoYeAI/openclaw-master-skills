#!/bin/bash
# v2 Instinct Observation Hook
# Captures session activity via PreToolUse/PostToolUse hooks
# Stores observations with project context for later analysis

set -e

# Configuration
HOMUNCULUS_DIR="${CLAUDE_HOMUNCULUS_DIR:-$HOME/.claude/homunculus}"
OBSERVATIONS_FILE="$HOMUNCULUS_DIR/observations.jsonl"

# Project detection
# Priority: CLAUDE_PROJECT_DIR > git remote URL hash > git repo path > global
detect_project() {
    if [[ -n "$CLAUDE_PROJECT_DIR" ]]; then
        echo "$CLAUDE_PROJECT_DIR"
        return
    fi

    # Try git remote URL (most portable - same repo on different machines gets same ID)
    if git remote get-url origin 2>/dev/null; then
        local remote_url
        remote_url=$(git remote get-url origin 2>/dev/null)
        if [[ -n "$remote_url" ]]; then
            # Create portable hash from remote URL
            echo "$(echo "$remote_url" | shasum | cut -c1-12)"
            return
        fi
    fi

    # Fallback to repo path (machine-specific)
    if git rev-parse --show-toplevel 2>/dev/null; then
        local repo_path
        repo_path=$(git rev-parse --show-toplevel 2>/dev/null)
        if [[ -n "$repo_path" ]]; then
            echo "$(echo "$repo_path" | shasum | cut -c1-12)"
            return
        fi
    fi

    # Global fallback
    echo "global"
}

# Get project name for registry
get_project_name() {
    if git rev-parse --show-toplevel 2>/dev/null; then
        basename "$(git rev-parse --show-toplevel)"
    else
        echo "global"
    fi
}

# Initialize directories
init_directories() {
    local project_id="$1"

    mkdir -p "$HOMUNCULUS_DIR/instincts/personal"
    mkdir -p "$HOMUNCULUS_DIR/instincts/inherited"
    mkdir -p "$HOMUNCULUS_DIR/evolved/agents"
    mkdir -p "$HOMUNCULUS_DIR/evolved/skills"
    mkdir -p "$HOMUNCULUS_DIR/evolved/commands"
    mkdir -p "$HOMUNCULUS_DIR/projects/$project_id/instincts/personal"
    mkdir -p "$HOMUNCULUS_DIR/projects/$project_id/instincts/inherited"
    mkdir -p "$HOMUNCULUS_DIR/projects/$project_id/evolved/skills"
    mkdir -p "$HOMUNCULUS_DIR/projects/$project_id/evolved/commands"
    mkdir -p "$HOMUNCULUS_DIR/projects/$project_id/evolved/agents"
    mkdir -p "$HOMUNCULUS_DIR/projects/$project_id/observations.archive"
}

# Update project registry
update_project_registry() {
    local project_id="$1"
    local project_name="$2"
    local project_path="${3:-$(pwd)}"

    local registry_file="$HOMUNCULUS_DIR/projects.json"

    if [[ ! -f "$registry_file" ]]; then
        echo "{}" > "$registry_file"
    fi

    # Update registry with project info
    # This is a simplified version - in production, use proper JSON manipulation
    local temp_file
    temp_file=$(mktemp)
    jq --arg id "$project_id" \
       --arg name "$project_name" \
       --arg path "$project_path" \
       '.[$id] = {name: $name, path: $path, last_seen: now}' \
       "$registry_file" > "$temp_file" && mv "$temp_file" "$registry_file"
}

# Log observation
log_observation() {
    local project_id="$1"
    local observation_type="$2"  # "pre_tool" or "post_tool"
    local tool_name="$3"
    local tool_input="$4"
    local tool_output="${5:-null}"

    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Determine observations file location
    local obs_file
    if [[ "$project_id" == "global" ]]; then
        obs_file="$OBSERVATIONS_FILE"
    else
        obs_file="$HOMUNCULUS_DIR/projects/$project_id/observations.jsonl"
    fi

    # Create JSON observation
    local observation
    observation=$(jq -n \
        --arg timestamp "$timestamp" \
        --arg type "$observation_type" \
        --arg tool "$tool_name" \
        --arg input "$tool_input" \
        --arg output "$tool_output" \
        --arg project "$project_id" \
        '{
            timestamp: $timestamp,
            type: $type,
            tool: $tool,
            input: $input,
            output: $output,
            project_id: $project
        }')

    # Append to observations file
    echo "$observation" >> "$obs_file"
}

# Archive old observations (if file gets too large)
archive_observations() {
    local project_id="$1"
    local max_lines=10000

    local obs_file
    if [[ "$project_id" == "global" ]]; then
        obs_file="$OBSERVATIONS_FILE"
    else
        obs_file="$HOMUNCULUS_DIR/projects/$project_id/observations.jsonl"
    fi

    if [[ -f "$obs_file" ]]; then
        local line_count
        line_count=$(wc -l < "$obs_file")
        if [[ $line_count -gt $max_lines ]]; then
            local archive_file
            archive_file="$HOMUNCULUS_DIR/projects/$project_id/observations.archive/$(date +%Y%m%d_%H%M%S).jsonl"
            mv "$obs_file" "$archive_file"
            gzip "$archive_file"
            touch "$obs_file"
        fi
    fi
}

# Main execution
main() {
    # Detect project
    local project_id
    project_id=$(detect_project)

    local project_name
    project_name=$(get_project_name)

    # Initialize directories
    init_directories "$project_id"

    # Update registry
    update_project_registry "$project_id" "$project_name"

    # Archive old observations if needed
    archive_observations "$project_id"

    # Log the observation
    # Arguments from hook: tool name and input are passed via environment or arguments
    # This is a simplified version - actual implementation depends on hook context
    if [[ $# -ge 2 ]]; then
        log_observation "$project_id" "$1" "$2" "$3" "$4"
    fi
}

# Run main function
main "$@"
