#!/bin/bash
# solvr-workflow.sh - Solvr problem-solving workflow for watchdog
# Searches Solvr first, uses Claude Code CLI with Solvr plugin when available
#
# Usage:
#   solvr-workflow.sh search "error message"
#   solvr-workflow.sh post "problem title" "description"
#   solvr-workflow.sh approach <problem_id> "what I tried" [succeeded|failed]
#   solvr-workflow.sh diagnose-with-claude "error context"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${AMCP_CONFIG:-$HOME/.amcp/config.json}"

# Get Solvr API key from AMCP config or environment
get_solvr_key() {
  # Try environment first
  if [ -n "${SOLVR_API_KEY:-}" ]; then
    echo "$SOLVR_API_KEY"
    return 0
  fi
  
  # Try AMCP config
  local config_file="${AMCP_CONFIG:-$HOME/.amcp/config.json}"
  if [ -f "$config_file" ]; then
    local key
    key=$(python3 -c "
import json, sys, os
try:
    c = json.load(open(os.path.expanduser('$config_file')))
    key = c.get('apiKeys', {}).get('solvr') or c.get('solvr', {}).get('apiKey') or ''
    if key:
        print(key)
except:
    pass
" 2>/dev/null) || true
    if [ -n "$key" ]; then
      echo "$key"
      return 0
    fi
  fi
  
  # Try OpenClaw config as fallback
  local oc_config="$HOME/.openclaw/openclaw.json"
  if [ -f "$oc_config" ]; then
    local key
    key=$(python3 -c "
import json, sys, os
try:
    c = json.load(open(os.path.expanduser('$oc_config')))
    key = c.get('skills', {}).get('entries', {}).get('solvr', {}).get('apiKey') or ''
    if key:
        print(key)
except:
    pass
" 2>/dev/null) || true
    if [ -n "$key" ]; then
      echo "$key"
      return 0
    fi
  fi
}

SOLVR_API_KEY="${SOLVR_API_KEY:-$(get_solvr_key)}"
SOLVR_API="${SOLVR_API:-https://api.solvr.dev/v1}"
CLAUDE_CLI="${CLAUDE_CLI:-$(command -v claude 2>/dev/null || echo "")}"

# ============================================================
# Search Solvr for similar problems
# ============================================================
search_solvr() {
  local query="$1"
  local max_results="${2:-5}"
  
  if [ -z "$SOLVR_API_KEY" ]; then
    echo '{"error": "no_solvr_key", "solutions": []}'
    return 1
  fi
  
  # URL encode query
  local encoded_query
  encoded_query=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query'))")
  
  local response
  response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    "${SOLVR_API}/search?q=${encoded_query}&limit=${max_results}" 2>/dev/null) || {
    echo '{"error": "request_failed", "solutions": []}'
    return 1
  }
  
  local http_code
  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | head -n -1)
  
  if [ "$http_code" != "200" ]; then
    echo "{\"error\": \"http_${http_code}\", \"solutions\": []}"
    return 1
  fi
  
  echo "$body"
}

# Extract succeeded approaches from search results
get_succeeded_approaches() {
  local search_results="$1"
  echo "$search_results" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    results = data.get('data', data.get('results', []))
    for r in results[:5]:
        approaches = r.get('approaches', [])
        for a in approaches:
            if a.get('status') == 'succeeded':
                print(f\"✅ {a.get('angle', 'Solution')}: {a.get('method', '')[:200]}\")
except:
    pass
" 2>/dev/null || true
}

# ============================================================
# Post problem to Solvr
# ============================================================
post_problem() {
  local title="$1"
  local description="$2"
  local tags="${3:-watchdog,auto-diagnosed}"
  
  if [ -z "$SOLVR_API_KEY" ]; then
    echo '{"error": "no_solvr_key"}'
    return 1
  fi
  
  local tag_array
  tag_array=$(echo "$tags" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip().split(',')))")
  
  local response
  response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"type\": \"problem\",
      \"title\": $(echo "$title" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))'),
      \"description\": $(echo "$description" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))'),
      \"tags\": $tag_array
    }" \
    "${SOLVR_API}/posts" 2>/dev/null) || {
    echo '{"error": "request_failed"}'
    return 1
  }
  
  local http_code
  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | head -n -1)
  
  if [ "$http_code" != "200" ] && [ "$http_code" != "201" ]; then
    echo "{\"error\": \"http_${http_code}\"}"
    return 1
  fi
  
  echo "$body"
}

# ============================================================
# Add approach to problem
# ============================================================
add_approach() {
  local problem_id="$1"
  local angle="$2"
  local status="${3:-working}"  # starting, working, succeeded, failed, stuck
  
  if [ -z "$SOLVR_API_KEY" ]; then
    echo '{"error": "no_solvr_key"}'
    return 1
  fi
  
  local response
  response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"angle\": $(echo "$angle" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))'),
      \"status\": \"$status\"
    }" \
    "${SOLVR_API}/problems/${problem_id}/approaches" 2>/dev/null) || {
    echo '{"error": "request_failed"}'
    return 1
  }
  
  local http_code
  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | head -n -1)
  
  echo "$body"
}

# Update approach status
update_approach() {
  local approach_id="$1"
  local status="$2"  # succeeded, failed, stuck
  
  if [ -z "$SOLVR_API_KEY" ]; then
    return 1
  fi
  
  curl -s -X PATCH \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"status\": \"$status\"}" \
    "${SOLVR_API}/approaches/${approach_id}" 2>/dev/null || true
}

# ============================================================
# Claude Code CLI with Solvr plugin for intelligent diagnosis
# ============================================================
diagnose_with_claude() {
  local error_context="$1"
  local max_attempts="${2:-3}"
  
  # Check if Claude CLI is available
  if [ -z "$CLAUDE_CLI" ] || [ ! -x "$CLAUDE_CLI" ]; then
    echo '{"error": "claude_cli_not_available", "suggestion": "Install Claude Code CLI: npm install -g @anthropic-ai/claude-code"}'
    return 1
  fi
  
  # Create prompt that instructs Claude to use Solvr
  local prompt
  prompt=$(cat << PROMPT
You are diagnosing an agent failure. Use the Solvr workflow:

1. SEARCH SOLVR FIRST for similar problems
2. If solutions found, try the succeeded approaches
3. If not found, POST the problem to Solvr
4. Document your approach (mark succeeded/failed)

Error context:
$error_context

Instructions:
- Search Solvr with key error terms
- Check for succeeded approaches first
- If you fix it, mark approach succeeded on Solvr
- If you fail, mark approach failed and explain why
- Always document for future agents

Return JSON: {"diagnosis": "...", "solvr_searched": true/false, "solution_found": true/false, "fix_command": "..." or null}
PROMPT
)
  
  # Run Claude CLI with Solvr plugin instruction
  # Use --print to get output without interactive mode
  local result
  result=$("$CLAUDE_CLI" --print "$prompt" 2>/dev/null) || {
    echo '{"error": "claude_cli_failed"}'
    return 1
  }
  
  echo "$result"
}

# ============================================================
# Full Solvr workflow for watchdog
# Returns: JSON with search results, problem ID if posted, recommended action
# ============================================================
watchdog_solvr_workflow() {
  local error_summary="$1"
  local agent_name="${2:-UnknownAgent}"
  
  echo "🔍 Searching Solvr for: $error_summary" >&2
  
  # 1. Search Solvr
  local search_result
  search_result=$(search_solvr "$error_summary" 5)
  
  local succeeded_approaches
  succeeded_approaches=$(get_succeeded_approaches "$search_result")
  
  if [ -n "$succeeded_approaches" ]; then
    echo "✅ Found solutions on Solvr:" >&2
    echo "$succeeded_approaches" >&2
    echo "{\"action\": \"try_existing\", \"solutions\": $(echo "$succeeded_approaches" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))')}"
    return 0
  fi
  
  echo "📝 No existing solutions, posting problem to Solvr..." >&2
  
  # 2. Post new problem (Solvr requires 50+ char description)
  local problem_title="[Watchdog] $error_summary"
  local problem_desc="Agent: $agent_name
Error: $error_summary
Timestamp: $(date -Iseconds)
Host: $(hostname)
Auto-detected by proactive-amcp watchdog. This problem was automatically posted when no existing solutions were found on Solvr."
  
  local post_result
  post_result=$(post_problem "$problem_title" "$problem_desc" "watchdog,auto-diagnosed,amcp")
  
  local problem_id
  problem_id=$(echo "$post_result" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',{}).get('id','') or d.get('id',''))" 2>/dev/null || true)
  
  if [ -n "$problem_id" ]; then
    echo "📌 Posted problem: $problem_id" >&2
    echo "{\"action\": \"posted_problem\", \"problem_id\": \"$problem_id\"}"
  else
    echo "{\"action\": \"search_only\", \"error\": \"could_not_post\"}"
  fi
}

# ============================================================
# Main
# ============================================================
case "${1:-help}" in
  search)
    search_solvr "${2:-}" "${3:-5}"
    ;;
  post)
    post_problem "${2:-}" "${3:-}" "${4:-watchdog}"
    ;;
  approach)
    add_approach "${2:-}" "${3:-}" "${4:-working}"
    ;;
  update-approach)
    update_approach "${2:-}" "${3:-}"
    ;;
  diagnose-with-claude)
    diagnose_with_claude "${2:-}"
    ;;
  workflow)
    watchdog_solvr_workflow "${2:-}" "${3:-}"
    ;;
  *)
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Commands:"
    echo "  search <query> [limit]           Search Solvr for solutions"
    echo "  post <title> <desc> [tags]       Post problem to Solvr"
    echo "  approach <problem_id> <angle>    Add approach to problem"
    echo "  update-approach <id> <status>    Update approach status"
    echo "  diagnose-with-claude <context>   Use Claude CLI for diagnosis"
    echo "  workflow <error> [agent_name]    Full watchdog Solvr workflow"
    ;;
esac
