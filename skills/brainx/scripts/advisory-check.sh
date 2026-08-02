#!/bin/bash
# BrainX Advisory Pre-Action Check
# Usage: brainx-advisory-check <tool> <args_json> [agent]
#
# Checks BrainX for relevant advisories before executing high-risk tools.
# Returns advisory text if relevant memories/patterns are found.
# Exit 0 always (advisory is informational, not blocking).

DIR="$(cd "$(dirname "$0")/.." && pwd)"
TOOL="$1"
ARGS="${2:-'{}'}"
AGENT="${3:-unknown}"

if [ -z "$TOOL" ]; then
  echo "Usage: $0 <tool> <args_json> [agent]"
  echo "Example: $0 exec '{\"command\":\"rm -rf /tmp/old\"}' coder"
  exit 0
fi

# Only check high-risk tools
case "$TOOL" in
  exec|deploy|railway|delete|rm|drop|git|migration|cron|message|email)
    result=$(node "$DIR/lib/cli.js" advisory --tool "$TOOL" --args "$ARGS" --agent "$AGENT" --json 2>/dev/null)
    if [ -n "$result" ] && echo "$result" | jq -e '.advisory_text != null' >/dev/null 2>&1; then
      echo "⚠️  BrainX Advisory:"
      echo "$result" | jq -r '.advisory_text' | sed 's/^/  /'
      echo ""
      confidence=$(echo "$result" | jq -r '.confidence // 0')
      echo "  Confidence: $confidence"
    fi
    ;;
  *)
    # Not a high-risk tool, skip silently
    ;;
esac
