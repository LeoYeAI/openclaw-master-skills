#!/bin/bash
# _diagnose-claude.sh — Claude-powered diagnose with Solvr integration
# Internal implementation for: diagnose.sh claude
#
# Runs bash health checks (diagnose.sh health), then invokes Claude Code CLI
# with the Solvr skill to search for known solutions, try fixes,
# and post novel issues to the Solvr knowledge base.
#
# Usage (via diagnose.sh):
#   diagnose.sh claude [--json] [--no-solvr] [--bash-only]
#
# Requires:
#   - claude CLI (npm install -g @anthropic-ai/claude-code)
#   - anthropic.apiKey in ~/.amcp/config.json (agent's own key, NOT env)
#   - solvr.apiKey in ~/.amcp/config.json (optional)
#
# SECURITY: This script ONLY uses keys from config, never from environment.
#           This prevents the agent from accidentally using the human's API key.
#
# Exit codes:
#   0 = healthy or fixes applied
#   1 = issues found, some unfixed
#   2 = missing prerequisites (claude CLI, API key)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
SOLVR_SKILL_DIR="${SOLVR_SKILL_DIR:-$HOME/.claude/skills/solvr}"
AGENT_NAME="${AGENT_NAME:-$(hostname -s)}"

# ============================================================
# Helpers
# ============================================================

log_info()  { echo "[claude-diagnose] INFO:  $*" >&2; }
log_error() { echo "[claude-diagnose] ERROR: $*" >&2; }

# Read a key from proactive-amcp config (dot-path)
config_get() {
  local key="$1"
  if [[ -f "$CONFIG_FILE" ]]; then
    python3 -c "
import json, os
with open(os.path.expanduser('$CONFIG_FILE')) as f:
    data = json.load(f)
parts = '$key'.split('.')
obj = data
for part in parts:
    if isinstance(obj, dict) and part in obj:
        obj = obj[part]
    else:
        exit(0)
if isinstance(obj, (dict, list)):
    import json as j; print(j.dumps(obj))
elif obj is not None:
    print(obj)
" 2>/dev/null || true
  fi
}

# ============================================================
# Parse arguments
# ============================================================

FLAG_JSON=false
FLAG_NO_SOLVR=false
FLAG_BASH_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)       FLAG_JSON=true; shift ;;
    --no-solvr)   FLAG_NO_SOLVR=true; shift ;;
    --bash-only)  FLAG_BASH_ONLY=true; shift ;;
    -h|--help)
      cat <<EOF
proactive-amcp diagnose — Claude-powered health diagnostics with Solvr

Usage: proactive-amcp diagnose [OPTIONS]

Options:
  --json        Output raw JSON only (no human-readable text)
  --no-solvr    Skip Solvr search/post (bash checks + Claude analysis only)
  --bash-only   Run bash health checks only (no Claude, no Solvr)
  -h, --help    Show this help

Config (in ~/.amcp/config.json):
  anthropic.apiKey    Required for Claude analysis (agent's own key, NOT human's)
  solvr.apiKey        Optional for Solvr integration

NOTE: This script will NOT use inherited ANTHROPIC_API_KEY from environment.
      The agent must have its own configured API key.
EOF
      exit 0
      ;;
    *) shift ;;
  esac
done

# ============================================================
# Step 1: Run bash health checks (diagnose.sh health)
# ============================================================

log_info "Running bash health checks..."

FINDINGS=""
DIAGNOSE_EXIT=0
if [[ -x "$SCRIPT_DIR/diagnose.sh" ]]; then
  FINDINGS=$("$SCRIPT_DIR/diagnose.sh" health 2>/dev/null) || DIAGNOSE_EXIT=$?
else
  log_error "diagnose.sh not found at $SCRIPT_DIR/diagnose.sh"
  FINDINGS='{"status": "error", "findings": [], "checks_run": 0, "findings_count": 0}'
  DIAGNOSE_EXIT=1
fi

# If bash-only mode, just output findings and exit
if [[ "$FLAG_BASH_ONLY" == true ]]; then
  echo "$FINDINGS"
  exit "$DIAGNOSE_EXIT"
fi

# ============================================================
# Step 2: Resolve API keys (AGENT-ONLY — no env fallback)
# ============================================================

# SECURITY: Only use explicitly configured agent key, NEVER inherit from env.
# This prevents proactive-amcp from using the human's API key.
ANTHROPIC_API_KEY="$(config_get anthropic.apiKey)"
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  log_error "No agent Anthropic key configured in ~/.amcp/config.json"
  log_error "proactive-amcp requires its OWN API key (not the human's)."
  log_error ""
  log_error "Configure with:"
  log_error "  proactive-amcp config set anthropic.apiKey sk-ant-api03-YOUR-AGENT-KEY"
  log_error ""
  log_error "Or run with --bash-only to skip Claude analysis."
  # Fall back to bash-only output
  echo "$FINDINGS"
  exit 2
fi
export ANTHROPIC_API_KEY

SOLVR_API_KEY="${SOLVR_API_KEY:-$(config_get solvr.apiKey)}"
# Also check legacy flat key name
if [[ -z "${SOLVR_API_KEY:-}" ]]; then
  SOLVR_API_KEY="$(config_get solvr_api_key)"
fi
export SOLVR_API_KEY="${SOLVR_API_KEY:-}"

# Check claude CLI is available
if ! command -v claude &>/dev/null; then
  log_error "claude CLI not found. Install: npm install -g @anthropic-ai/claude-code"
  echo "$FINDINGS"
  exit 2
fi

# ============================================================
# Step 3: Locate Solvr skill
# ============================================================

# Solvr skill installed via solvr.dev/install.sh during proactive-amcp install

SOLVR_CLI="$SOLVR_SKILL_DIR/scripts/solvr.sh"
SOLVR_SKILL_MD="$SOLVR_SKILL_DIR/SKILL.md"

SOLVR_AVAILABLE=false
if [[ "$FLAG_NO_SOLVR" != true && -n "${SOLVR_API_KEY:-}" && -x "$SOLVR_CLI" ]]; then
  SOLVR_AVAILABLE=true
fi

# ============================================================
# Step 4: Build prompt for Claude
# ============================================================

build_prompt() {
  local findings="$1"

  cat <<PROMPT_EOF
You are a system health diagnostician for an OpenClaw gateway agent named "${AGENT_NAME}".

## Health Check Results

The following JSON contains findings from automated bash health checks:

\`\`\`json
${findings}
\`\`\`

## Your Task

Analyze each finding and determine the best course of action.
PROMPT_EOF

  # Add Solvr instructions if available
  if [[ "$SOLVR_AVAILABLE" == true ]]; then
    cat <<SOLVR_PROMPT_EOF

## Solvr Knowledge Base

You have access to the Solvr knowledge base. The SOLVR_API_KEY environment variable is already set.

For EACH finding with severity "critical" or "warning":

1. **Search Solvr** for existing solutions:
   \`\`\`bash
   bash ${SOLVR_CLI} search "<error type or message>" --json
   \`\`\`

2. **If a matching problem exists** with a succeeded approach:
   - Read the approach details: \`bash ${SOLVR_CLI} get <post_id> --include approaches --json\`
   - Try the fix described in the succeeded approach
   - If fix works: upvote the approach
   - If fix fails: note it in your output

3. **If NO match found**, post a new problem:
   \`\`\`bash
   bash ${SOLVR_CLI} post problem "<short title>" "<detailed description with error context>" --tags "openclaw,gateway,auto-diagnose,${AGENT_NAME}" --json
   \`\`\`
   Then add your approach:
   \`\`\`bash
   bash ${SOLVR_CLI} approach <problem_id> "<what you will try>" --json
   \`\`\`

4. **After attempting a fix**, update the approach if you posted one.
SOLVR_PROMPT_EOF
  fi

  # Output format instructions
  cat <<FORMAT_EOF

## Output Format

Respond with ONLY a JSON object (no markdown fences, no surrounding text):

{
  "agent": "${AGENT_NAME}",
  "timestamp": "<ISO 8601>",
  "bash_status": "<healthy|unhealthy from health checks>",
  "findings_count": <number>,
  "findings": [
    {
      "type": "<finding type from health check>",
      "severity": "<critical|warning>",
      "message": "<original message>",
      "solvr_match": <true|false|null if no solvr>,
      "solvr_post_id": "<id or null>",
      "fix_attempted": <true|false>,
      "fix_result": "<succeeded|failed|skipped>",
      "fix_details": "<what was tried or null>"
    }
  ],
  "solvr_searches": <number of solvr searches performed>,
  "solvr_posts": <number of new problems posted>,
  "fixes_attempted": <number>,
  "fixes_succeeded": <number>,
  "overall_status": "<healthy|degraded|critical>"
}
FORMAT_EOF
}

# ============================================================
# Step 5: Invoke Claude CLI
# ============================================================

log_info "Invoking Claude Code for analysis..."
if [[ "$SOLVR_AVAILABLE" == true ]]; then
  log_info "Solvr integration: enabled (skill at $SOLVR_SKILL_DIR)"
else
  log_info "Solvr integration: disabled"
fi

PROMPT=$(build_prompt "$FINDINGS")

CLAUDE_OUTPUT=""
CLAUDE_EXIT=0
CLAUDE_OUTPUT=$(ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" SOLVR_API_KEY="${SOLVR_API_KEY:-}" \
  claude --dangerously-skip-permissions --no-session-persistence \
    -p --output-format json \
    "$PROMPT" 2>/dev/null) || CLAUDE_EXIT=$?

# ============================================================
# Step 6: Extract and return JSON result
# ============================================================

if [[ -n "$CLAUDE_OUTPUT" ]]; then
  # Claude --output-format json wraps output; extract the result text
  RESULT_TEXT=$(echo "$CLAUDE_OUTPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # output-format json returns {result: '...', ...}
    if isinstance(data, dict) and 'result' in data:
        print(data['result'])
    else:
        print(json.dumps(data))
except:
    print(sys.stdin.read())
" 2>/dev/null || echo "$CLAUDE_OUTPUT")

  # Try to extract a JSON object from the result text
  JSON_RESULT=$(echo "$RESULT_TEXT" | python3 -c "
import sys, json
text = sys.stdin.read()

# Try direct parse first
try:
    obj = json.loads(text)
    print(json.dumps(obj, indent=2))
    sys.exit(0)
except:
    pass

# Find outermost JSON object in text
depth = 0
start = -1
for i, c in enumerate(text):
    if c == '{':
        if depth == 0:
            start = i
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0 and start >= 0:
            candidate = text[start:i+1]
            try:
                obj = json.loads(candidate)
                print(json.dumps(obj, indent=2))
                sys.exit(0)
            except:
                start = -1

# Fallback: return empty
print('')
" 2>/dev/null)

  if [[ -n "$JSON_RESULT" ]] && echo "$JSON_RESULT" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
    echo "$JSON_RESULT"

    # Determine exit code from overall_status
    OVERALL=$(echo "$JSON_RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('overall_status','unknown'))" 2>/dev/null || echo "unknown")
    case "$OVERALL" in
      healthy) exit 0 ;;
      *)       exit 1 ;;
    esac
  fi
fi

# Fallback: Claude output wasn't parseable JSON — return bash findings with error
log_error "Could not parse Claude output as JSON"
python3 -c "
import json, sys
findings = json.loads('''${FINDINGS}''')
result = {
    'agent': '${AGENT_NAME}',
    'bash_status': findings.get('status', 'unknown'),
    'findings_count': findings.get('findings_count', 0),
    'findings': findings.get('findings', []),
    'solvr_searches': 0,
    'solvr_posts': 0,
    'fixes_attempted': 0,
    'fixes_succeeded': 0,
    'overall_status': findings.get('status', 'unknown'),
    'error': 'Claude analysis failed — returning bash diagnostics only',
    'claude_exit_code': $CLAUDE_EXIT
}
print(json.dumps(result, indent=2))
"
exit "$DIAGNOSE_EXIT"
