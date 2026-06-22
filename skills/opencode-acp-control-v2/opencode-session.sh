#!/bin/bash
# opencode-session.sh - Wrapper para OpenCode ACP con auto-retry, adaptive polling, y cleanup
# Parte de opencode-acp-control v2.2.0

set -e

# ============================================
# CONFIGURATION
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"

# Load config (use defaults if no config file)
if [[ -f "$CONFIG_FILE" ]]; then
    # Parse JSON config (simple parsing, works for flat structure)
    TIMEOUT_INIT=$(jq -r '.timeouts.initialize // 10000' "$CONFIG_FILE")
    TIMEOUT_SESSION=$(jq -r '.timeouts.sessionNew // 10000' "$CONFIG_FILE")
    TIMEOUT_PROMPT_SIMPLE=$(jq -r '.timeouts.prompt.simple // 60000' "$CONFIG_FILE")
    TIMEOUT_PROMPT_COMPLEX=$(jq -r '.timeouts.prompt.complex // 300000' "$CONFIG_FILE")
    RETRY_MAX=$(jq -r '.retry.maxAttempts // 3' "$CONFIG_FILE")
    RETRY_DELAY=$(jq -r '.retry.initialDelay // 2000' "$CONFIG_FILE")
    HEALTH_THRESHOLD=$(jq -r '.healthCheck.noOutputThreshold // 60000' "$CONFIG_FILE")
else
    TIMEOUT_INIT=10000
    TIMEOUT_SESSION=10000
    TIMEOUT_PROMPT_SIMPLE=60000
    TIMEOUT_PROMPT_COMPLEX=300000
    RETRY_MAX=3
    RETRY_DELAY=2000
    HEALTH_THRESHOLD=60000
fi

# ============================================
# GLOBAL STATE
# ============================================

PROCESS_SESSION_ID=""
OPENCODE_SESSION_ID=""
MESSAGE_ID=0
START_TIME=""
POLL_COUNT=0
RETRY_COUNT=0
LAST_OUTPUT_TIME=""

# ============================================
# UTILITY FUNCTIONS
# ============================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        ERROR) echo "[$timestamp] ERROR: $message" >&2 ;;
        WARN)  echo "[$timestamp] WARN: $message" ;;
        INFO)  echo "[$timestamp] INFO: $message" ;;
        DEBUG) [[ "${VERBOSE:-false}" == "true" ]] && echo "[$timestamp] DEBUG: $message" ;;
    esac
}

cleanup_stale_locks() {
    log INFO "Cleaning stale locks (>30min old)"
    find ~/.openclaw/agents -name '*.lock' -mmin +30 -delete 2>/dev/null || true
}

cleanup_session() {
    if [[ -n "$PROCESS_SESSION_ID" ]]; then
        log INFO "Cleaning up session"
        # Kill process would be done by caller via process.kill
        # Just clean locks here
        rm -f ~/.openclaw/agents/*/sessions/*.lock 2>/dev/null || true
    fi
}

calculate_backoff() {
    local attempt="$1"
    local delay=$((RETRY_DELAY * (2 ** (attempt - 1))))
    echo $((delay < 10000 ? delay : 10000))  # Max 10s
}

get_adaptive_interval() {
    local elapsed_ms="$1"
    
    if [[ $elapsed_ms -lt 10000 ]]; then
        echo 1000
    elif [[ $elapsed_ms -lt 60000 ]]; then
        echo 2000
    elif [[ $elapsed_ms -lt 120000 ]]; then
        echo 3000
    else
        echo 5000
    fi
}

# ============================================
# JSON-RPC FUNCTIONS
# ============================================

send_jsonrpc() {
    local method="$1"
    local params="$2"
    
    local json="{\"jsonrpc\":\"2.0\",\"id\":${MESSAGE_ID},\"method\":\"${method}\",\"params\":${params}}"
    MESSAGE_ID=$((MESSAGE_ID + 1))
    
    log DEBUG "Sending: $json"
    echo "$json"
}

initialize_opencode() {
    log INFO "Initializing OpenCode connection"
    
    local attempt=1
    while [[ $attempt -le $RETRY_MAX ]]; do
        local json=$(send_jsonrpc "initialize" '{"protocolVersion":1,"clientCapabilities":{"fs":{"readTextFile":true,"writeTextFile":true},"terminal":true},"clientInfo":{"name":"cypher","title":"CYPHER","version":"2.2.0"}}')
        
        # Note: Actual sending would be via process.write
        # This function just generates the JSON
        echo "$json"
        return 0
        
        attempt=$((attempt + 1))
        if [[ $attempt -le $RETRY_MAX ]]; then
            local backoff=$(calculate_backoff $attempt)
            log WARN "Initialize failed, retrying in ${backoff}ms (attempt $attempt/$RETRY_MAX)"
            sleep $((backoff / 1000))
        fi
    done
    
    log ERROR "Failed to initialize after $RETRY_MAX attempts"
    return 1
}

create_session() {
    local cwd="$1"
    local mcp_servers="$2"
    
    log INFO "Creating session in $cwd"
    
    local params="{\"cwd\":\"${cwd}\",\"mcpServers\":${mcp_servers:-[]}}"
    local json=$(send_jsonrpc "session/new" "$params")
    
    echo "$json"
}

send_prompt() {
    local session_id="$1"
    local prompt="$2"
    
    log INFO "Sending prompt (${#prompt} chars)"
    
    local params="{\"sessionId\":\"${session_id}\",\"prompt\":[{\"type\":\"text\",\"text\":\"${prompt}\"}]}"
    local json=$(send_jsonrpc "session/prompt" "$params")
    
    echo "$json"
}

cancel_session() {
    local session_id="$1"
    
    log INFO "Cancelling session $session_id"
    
    local json=$(send_jsonrpc "session/cancel" "{\"sessionId\":\"${session_id}\"}")
    echo "$json"
}

# ============================================
# TEMPLATE FUNCTIONS
# ============================================

get_template() {
    local template_name="$1"
    local template_file="${SCRIPT_DIR}/templates.md"
    
    if [[ ! -f "$template_file" ]]; then
        log WARN "Templates file not found: $template_file"
        return 1
    fi
    
    # Extract template section (simple grep between headers)
    # This is a basic implementation - could be enhanced
    grep -A 20 "### ${template_name}" "$template_file" | head -20
}

# ============================================
# WORKFLOW FUNCTIONS
# ============================================

preflight() {
    log INFO "Pre-flight checks"
    cleanup_stale_locks
    
    # Verify opencode is available
    if ! command -v opencode &> /dev/null; then
        log ERROR "opencode command not found in PATH"
        return 1
    fi
    
    log INFO "OpenCode version: $(opencode --version 2>&1 | head -1)"
}

# ============================================
# CLI INTERFACE
# ============================================

usage() {
    cat << EOF
Usage: opencode-session.sh [OPTIONS] --project PATH --prompt "PROMPT"

OpenCode ACP wrapper with auto-retry, adaptive polling, and cleanup.

Required:
  --project PATH        Project directory
  --prompt "TEXT"       Prompt to send

Options:
  --template NAME       Use template from templates.md
  --timeout TYPE        Prompt timeout: simple (60s) | medium (120s) | complex (300s)
  --mcp SERVERS         MCP servers as JSON array, e.g., '["supabase","github"]'
  --verbose             Enable debug logging
  --dry-run             Show JSON-RPC messages without executing
  --help                Show this help

Examples:
  # Simple prompt
  opencode-session.sh --project ~/myapp --prompt "Add error handling"

  # Using template
  opencode-session.sh --project ~/myapp --template "Add API endpoint" --prompt "POST /api/users"

  # With MCP servers
  opencode-session.sh --project ~/myapp --mcp '["supabase"]' --prompt "Create migration"

Output:
  The script outputs JSON-RPC messages that should be sent via process.write
  Actual execution requires integration with OpenClaw's process management.

EOF
}

# ============================================
# MAIN
# ============================================

main() {
    local project=""
    local prompt=""
    local template=""
    local timeout_type="simple"
    local mcp_servers="[]"
    local dry_run=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --project)
                project="$2"
                shift 2
                ;;
            --prompt)
                prompt="$2"
                shift 2
                ;;
            --template)
                template="$2"
                shift 2
                ;;
            --timeout)
                timeout_type="$2"
                shift 2
                ;;
            --mcp)
                mcp_servers="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                log ERROR "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Validate required args
    if [[ -z "$project" ]]; then
        log ERROR "--project is required"
        usage
        exit 1
    fi
    
    if [[ -z "$prompt" ]] && [[ -z "$template" ]]; then
        log ERROR "--prompt or --template is required"
        usage
        exit 1
    fi
    
    # Expand template if specified
    if [[ -n "$template" ]]; then
        local template_content=$(get_template "$template")
        if [[ -n "$template_content" ]]; then
            prompt="${template_content}\n\nSpecifics: ${prompt}"
        fi
    fi
    
    # Determine timeout
    local timeout_ms
    case "$timeout_type" in
        simple)   timeout_ms=$TIMEOUT_PROMPT_SIMPLE ;;
        medium)   timeout_ms=120000 ;;
        complex)  timeout_ms=$TIMEOUT_PROMPT_COMPLEX ;;
        *)        timeout_ms=$TIMEOUT_PROMPT_SIMPLE ;;
    esac
    
    # Pre-flight
    preflight || exit 1
    
    # Output workflow instructions
    cat << EOF
# OpenCode Session Workflow
# Generated by opencode-session.sh v2.2.0
#
# PROJECT: $project
# TIMEOUT: ${timeout_type} (${timeout_ms}ms)
# MCP: $mcp_servers
#
# Follow these steps:

## Step 1: Start OpenCode
exec(command: "opencode acp --cwd $project", background: true, workdir: "$project")
# → Save returned sessionId as PROCESS_SESSION_ID

## Step 2: Initialize
process.write(PROCESS_SESSION_ID, data: '$(initialize_opencode)' + "\\n")
process.poll(PROCESS_SESSION_ID, timeout: $TIMEOUT_INIT)
# → Expect: {"result":{"protocolVersion":1,...}}

## Step 3: Create Session
process.write(PROCESS_SESSION_ID, data: '$(create_session "$project" "$mcp_servers")' + "\\n")
process.poll(PROCESS_SESSION_ID, timeout: $TIMEOUT_SESSION)
# → Save result.sessionId as OPENCODE_SESSION_ID

## Step 4: Send Prompt
process.write(PROCESS_SESSION_ID, data: '$(send_prompt "OPENCODE_SESSION_ID" "$prompt")' + "\\n")

## Step 5: Adaptive Polling
# Poll with adaptive intervals until stopReason appears
# - 0-10s: every 1s
# - 10-60s: every 2s
# - 60-120s: every 3s
# - 120s+: every 5s
# - Max wait: ${timeout_ms}ms
# - Health check if no output > ${HEALTH_THRESHOLD}ms

## Step 6: Cleanup
process.kill(PROCESS_SESSION_ID)
exec(command: "rm -f ~/.openclaw/agents/*/sessions/*.lock")

# Metrics to log:
# - duration_ms
# - poll_count
# - retry_count
# - stop_reason

EOF
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
