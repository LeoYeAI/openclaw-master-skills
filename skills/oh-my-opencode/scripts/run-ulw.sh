#!/usr/bin/env bash
# Quick ultrawork launcher for oh-my-opencode
# Usage: ./scripts/run-ulw.sh [workdir] "your prompt here"
#
# Examples:
#   ./scripts/run-ulw.sh "add authentication to the API"
#   ./scripts/run-ulw.sh /path/to/project "refactor the database layer"
#   ./scripts/run-ulw.sh . "fix all lint errors"

set -euo pipefail

usage() {
    echo "Usage: $0 [workdir] \"prompt\""
    echo ""
    echo "Arguments:"
    echo "  workdir   Optional. Directory to run in (defaults to current directory)"
    echo "  prompt    Required. Your task description (ulw keyword is auto-prepended)"
    echo ""
    echo "Examples:"
    echo "  $0 \"add dark mode to the settings page\""
    echo "  $0 /path/to/project \"fix the broken tests\""
    echo "  $0 . \"refactor auth module\""
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

WORKDIR="."
PROMPT=""

if [ $# -eq 1 ]; then
    PROMPT="$1"
elif [ $# -ge 2 ]; then
    WORKDIR="$1"
    shift
    PROMPT="$*"
fi

if [ -z "$PROMPT" ]; then
    echo "Error: prompt is required"
    usage
fi

# Verify opencode is installed
if ! command -v opencode &>/dev/null; then
    echo "Error: opencode is not installed"
    echo "Install: curl -fsSL https://opencode.ai/install | bash"
    exit 1
fi

# Resolve workdir
WORKDIR=$(cd "$WORKDIR" && pwd)

echo "=== Ultrawork Mode ==="
echo "Directory: $WORKDIR"
echo "Prompt: ulw $PROMPT"
echo ""

# Run opencode in non-interactive mode with ulw prefix
cd "$WORKDIR"
exec opencode run "ulw $PROMPT"
