#!/bin/bash
# solvr-integration.sh - Solvr API integration for restore-agent.sh
# Sourced by restore-agent.sh — provides search, solution matching,
# problem creation, and approach tracking functions.
#
# Requires: SOLVR_BASE, RECOVERY_LOG, AGENT_NAME,
#           CURRENT_DEATH_PROBLEM_FILE, CURRENT_APPROACH_FILE
#           and log() function from caller.
#
# SOLVR_API_KEY is auto-resolved from a fallback chain when sourced.

# Resolve SOLVR_API_KEY from multiple locations (fallback chain).
# Checks in order:
#   1. SOLVR_API_KEY env var (already set)
#   2. ~/.amcp/config.json → apiKeys.solvr
#   3. ~/.amcp/config.json → solvr.apiKey
#   4. ~/.amcp/config.json → pinning.solvr.apiKey
#   5. ~/.config/solvr/credentials.json → apiKey
_resolve_solvr_api_key() {
  # 1. Already set via env var
  if [ -n "${SOLVR_API_KEY:-}" ]; then
    log "Solvr: API key found from env var SOLVR_API_KEY"
    return 0
  fi

  local config_file="${CONFIG_FILE:-$HOME/.amcp/config.json}"

  # 2-4. Check config.json locations
  if [ -f "$config_file" ]; then
    SOLVR_API_KEY=$(python3 -c "
import json, sys
try:
    d = json.load(open('$config_file'))
    # Check locations in priority order, track which matched
    locations = [
        ('apiKeys.solvr', (d.get('apiKeys') or {}).get('solvr', '')),
        ('solvr.apiKey', (d.get('solvr') or {}).get('apiKey', '')),
        ('pinning.solvr.apiKey', (d.get('pinning') or {}).get('solvr', {}).get('apiKey', '')),
    ]
    for loc, val in locations:
        if val:
            print(loc + '|' + val)
            sys.exit(0)
except Exception:
    pass
" 2>/dev/null || echo "")

    if [ -n "$SOLVR_API_KEY" ]; then
      local found_location="${SOLVR_API_KEY%%|*}"
      SOLVR_API_KEY="${SOLVR_API_KEY#*|}"
      log "Solvr: API key found from $config_file → $found_location"
      return 0
    fi
  fi

  # 5. Check ~/.config/solvr/credentials.json
  local solvr_creds="$HOME/.config/solvr/credentials.json"
  if [ -f "$solvr_creds" ]; then
    SOLVR_API_KEY=$(python3 -c "
import json
try:
    d = json.load(open('$solvr_creds'))
    key = d.get('apiKey', '')
    if key: print(key)
except Exception:
    pass
" 2>/dev/null || echo "")

    if [ -n "$SOLVR_API_KEY" ]; then
      log "Solvr: API key found from $solvr_creds → apiKey"
      return 0
    fi
  fi

  # No key found anywhere
  log "Solvr: No API key found in any location (env, config.json, credentials.json) — Solvr features disabled"
  SOLVR_API_KEY=""
  return 0
}

# Auto-resolve key when sourced
_resolve_solvr_api_key

# Extract error signature from gateway logs for Solvr search
_extract_error_signature() {
  local sig=""
  local gateway_log="${GATEWAY_LOG:-/tmp/openclaw-gateway.log}"

  # Try gateway log first
  if [ -f "$gateway_log" ]; then
    sig=$(tail -50 "$gateway_log" 2>/dev/null | grep -iE 'ERROR|FATAL|panic|crash|ECONNREFUSED|ENOENT|SIGKILL' | tail -5 | head -c 500 || true)
  fi

  # Fall back to systemd journal
  if [ -z "$sig" ]; then
    sig=$(journalctl --user -u openclaw-gateway --since "1 hour ago" -n 50 --no-pager 2>/dev/null | grep -iE 'ERROR|FATAL|panic|crash' | tail -5 | head -c 500 || true)
  fi

  # Condense to searchable query (max 100 chars)
  if [ -n "$sig" ]; then
    # Extract key error phrases
    echo "$sig" | python3 -c "
import sys
lines = sys.stdin.read().strip().split('\n')
# Extract unique error keywords
words = set()
for line in lines:
    for w in line.split():
        w = w.strip('[]():,')
        if len(w) > 3 and w.upper() not in ('THE','AND','WITH','FOR','FROM','THAT'):
            words.add(w)
# Build condensed query
q = ' '.join(sorted(words)[:8])
print(q[:100])
" 2>/dev/null || echo "agent death gateway crash"
  else
    echo "agent death gateway crash openclaw"
  fi
}

# Search Solvr for matching problems (returns JSON with problems+approaches)
solvr_search_problem() {
  if [ -z "$SOLVR_API_KEY" ]; then
    log "Solvr: No API key, skipping search"
    echo '{"data":[]}'
    return 0
  fi

  local error_sig
  error_sig=$(_extract_error_signature)
  log "Solvr: Searching for: $error_sig"

  local result
  result=$(curl -s --max-time 10 "$SOLVR_BASE/search?q=$(echo "$error_sig" | sed 's/ /+/g')" \
    -H "Authorization: Bearer $SOLVR_API_KEY" 2>/dev/null || echo '{"data":[]}')

  local count
  count=$(echo "$result" | jq '.data | length' 2>/dev/null || echo "0")

  if [ "$count" != "0" ] && [ "$count" != "null" ]; then
    log "Solvr: Found $count similar problems"
    echo "$result" | jq -r '.data[:3][] | "  - [\(.id // "?")] \(.title // "untitled")"' 2>/dev/null | tee -a "$RECOVERY_LOG" || true
  else
    log "Solvr: No matches"
  fi

  echo "$result"
}

# Try Solvr solutions (succeeded approaches) before generic recovery
try_solvr_solutions() {
  local search_result="$1"

  if [ -z "$SOLVR_API_KEY" ]; then
    return 1
  fi

  # Extract problems with succeeded approaches
  local problems
  problems=$(echo "$search_result" | jq -c '.data // []' 2>/dev/null || echo '[]')
  local problem_count
  problem_count=$(echo "$problems" | jq 'length' 2>/dev/null || echo "0")

  if [ "$problem_count" = "0" ]; then
    return 1
  fi

  log "Solvr: Trying succeeded approaches from $problem_count problem(s)..."

  # Iterate through problems and their succeeded approaches
  echo "$problems" | jq -c '.[]' 2>/dev/null | while read -r problem; do
    local problem_id
    problem_id=$(echo "$problem" | jq -r '.id // ""' 2>/dev/null)

    # Get approaches for this problem
    local approaches
    approaches=$(curl -s --max-time 10 "$SOLVR_BASE/problems/$problem_id/approaches" \
      -H "Authorization: Bearer $SOLVR_API_KEY" 2>/dev/null || echo '{"data":[]}')

    echo "$approaches" | jq -c '.data // [] | .[] | select(.status == "succeeded")' 2>/dev/null | while read -r approach; do
      local method
      method=$(echo "$approach" | jq -r '.method // ""' 2>/dev/null)

      if [ -z "$method" ]; then
        continue
      fi

      log "Solvr: Trying known solution: $method"

      # Try the solution (simple heuristic matching)
      local success=false
      case "$method" in
        *restart*|*systemctl*)
          try_restart_gateway && success=true
          ;;
        *config*|*restore*|*backup*)
          try_fix_config && success=true
          ;;
        *rehydrate*|*checkpoint*)
          # Don't try rehydrate from Solvr suggestion — too heavy for first pass
          log "Solvr: Skipping rehydrate suggestion (will try in tier 3)"
          ;;
        *)
          log "Solvr: Cannot auto-apply method: $method"
          ;;
      esac

      if [ "$success" = "true" ]; then
        log "Solvr: Solution worked! (from problem $problem_id)"
        return 0
      else
        # Post failed approach to the existing problem
        solvr_post_failed_approach "$problem_id" "$method"
      fi
    done
  done

  return 1
}

# Create Solvr problem when no match found for this death
solvr_create_problem() {
  if [ -z "$SOLVR_API_KEY" ]; then
    return 0
  fi

  local error_sig
  error_sig=$(_extract_error_signature)

  # Condense to title (max 80 chars) and description (max 500 chars)
  local title="Agent death: ${AGENT_NAME} - ${error_sig:0:50}"
  title="${title:0:80}"
  local description="Agent ${AGENT_NAME} experienced death. Error context: ${error_sig:0:450}"

  log "Solvr: Creating problem: $title"

  local result
  result=$(curl -s --max-time 15 -X POST "$SOLVR_BASE/posts" \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg title "$title" --arg desc "$description" '{
      type: "problem",
      title: $title,
      description: $desc,
      tags: ["openclaw", "death", "auto-generated"]
    }')" 2>/dev/null || echo '{}')

  local problem_id
  problem_id=$(echo "$result" | jq -r '.id // .data.id // ""' 2>/dev/null)

  if [ -n "$problem_id" ] && [ "$problem_id" != "null" ]; then
    log "Solvr: Created problem $problem_id"
    mkdir -p "$(dirname "$CURRENT_DEATH_PROBLEM_FILE")"
    echo "{\"problem_id\":\"$problem_id\",\"title\":\"$title\",\"timestamp\":\"$(date -Iseconds)\"}" > "$CURRENT_DEATH_PROBLEM_FILE"
  else
    log "Solvr: Failed to create problem (API error)"
  fi
}

# Start approach tracking before a recovery attempt
solvr_start_approach() {
  local method="$1"
  local description="$2"

  if [ -z "$SOLVR_API_KEY" ]; then
    return 0
  fi

  local problem_id=""
  if [ -f "$CURRENT_DEATH_PROBLEM_FILE" ]; then
    problem_id=$(jq -r '.problem_id // ""' "$CURRENT_DEATH_PROBLEM_FILE" 2>/dev/null)
  fi

  if [ -z "$problem_id" ]; then
    return 0
  fi

  local result
  result=$(curl -s --max-time 10 -X POST "$SOLVR_BASE/problems/$problem_id/approaches" \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg angle "Will try: $method" --arg method "$description" '{
      angle: $angle,
      method: $method
    }')" 2>/dev/null || echo '{}')

  local approach_id
  approach_id=$(echo "$result" | jq -r '.id // .data.id // ""' 2>/dev/null)

  if [ -n "$approach_id" ] && [ "$approach_id" != "null" ]; then
    mkdir -p "$(dirname "$CURRENT_APPROACH_FILE")"
    echo "{\"approach_id\":\"$approach_id\",\"method\":\"$method\"}" > "$CURRENT_APPROACH_FILE"
  fi
}

# Update approach status after a recovery attempt
solvr_update_approach() {
  local status="$1"  # "succeeded" or "failed"

  if [ -z "$SOLVR_API_KEY" ]; then
    return 0
  fi

  local approach_id=""
  if [ -f "$CURRENT_APPROACH_FILE" ]; then
    approach_id=$(jq -r '.approach_id // ""' "$CURRENT_APPROACH_FILE" 2>/dev/null)
  fi

  if [ -z "$approach_id" ]; then
    return 0
  fi

  curl -s --max-time 10 -X PATCH "$SOLVR_BASE/approaches/$approach_id" \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg status "$status" '{status: $status}')" > /dev/null 2>&1 || true

  rm -f "$CURRENT_APPROACH_FILE"
}

# Post failed approach when a Solvr-suggested solution doesn't work
solvr_post_failed_approach() {
  local problem_id="$1"
  local method="$2"

  if [ -z "$SOLVR_API_KEY" ] || [ -z "$problem_id" ]; then
    return 0
  fi

  local error_snippet
  error_snippet=$(tail -20 "$RECOVERY_LOG" 2>/dev/null | head -c 300 || echo "no details")

  curl -s --max-time 10 -X POST "$SOLVR_BASE/problems/$problem_id/approaches" \
    -H "Authorization: Bearer $SOLVR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg angle "Tried existing solution" --arg method "$method" --arg notes "$error_snippet" '{
      angle: $angle,
      method: $method,
      status: "failed",
      notes: $notes
    }')" > /dev/null 2>&1 || true
}
