#!/bin/bash
# validate-skill-contract.sh — Validate skill ontology contracts against graph.jsonl
# Part of proactive-amcp enforcer
#
# Checks preconditions declared in a skill's ontologyContract against the current
# ontology graph. Fails skill load if preconditions are not met.
#
# Usage:
#   validate-skill-contract.sh <skill-name> [--graph <path>] [--skills-dir <path>] [--json]
#   validate-skill-contract.sh --contract <contract.json> [--graph <path>] [--json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"

CONTENT_DIR="${CONTENT_DIR:-$HOME/.openclaw/workspace}"
GRAPH_PATH="${GRAPH_PATH:-$CONTENT_DIR/memory/ontology/graph.jsonl}"
SKILLS_DIR="${SKILLS_DIR:-$HOME/.openclaw/skills}"
JSON_OUTPUT=false
CONTRACT_FILE=""
SKILL_NAME=""

usage() {
  cat <<EOF
validate-skill-contract.sh — Validate skill ontology contracts

Usage:
  $(basename "$0") <skill-name> [options]
  $(basename "$0") --contract <contract.json> [options]

Options:
  --graph <path>       Path to graph.jsonl (default: \$CONTENT_DIR/memory/ontology/graph.jsonl)
  --skills-dir <path>  Path to skills directory (default: ~/.openclaw/skills)
  --contract <path>    Direct contract JSON file (bypasses skill lookup)
  --json               Output results as JSON
  -h, --help           Show this help
EOF
  exit 1
}

# Parse arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --graph) GRAPH_PATH="$2"; shift 2 ;;
    --skills-dir) SKILLS_DIR="$2"; shift 2 ;;
    --contract) CONTRACT_FILE="$2"; shift 2 ;;
    --json) JSON_OUTPUT=true; shift ;;
    -h|--help) usage ;;
    -*) echo "ERROR: Unknown option '$1'" >&2; usage ;;
    *)
      if [ -z "$SKILL_NAME" ]; then
        SKILL_NAME="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "$SKILL_NAME" ] && [ -z "$CONTRACT_FILE" ]; then
  echo "ERROR: Provide a skill name or --contract <file>" >&2
  usage
fi

# Resolve contract source
if [ -n "$CONTRACT_FILE" ]; then
  if [ ! -f "$CONTRACT_FILE" ]; then
    echo "ERROR: Contract file not found: $CONTRACT_FILE" >&2
    exit 1
  fi
  CONTRACT_SOURCE="$CONTRACT_FILE"
elif [ -f "$SKILLS_DIR/$SKILL_NAME/skill.json" ]; then
  CONTRACT_SOURCE="$SKILLS_DIR/$SKILL_NAME/skill.json"
else
  # No skill.json — backward compatible, skip
  if $JSON_OUTPUT; then
    echo '{"valid": true, "skipped": true, "reason": "no skill.json found"}'
  else
    echo "SKIP: ${SKILL_NAME} has no skill.json — validation skipped"
  fi
  exit 0
fi

# Run validation via python3 with env vars
export _CONTRACT_SOURCE="$CONTRACT_SOURCE"
export _GRAPH_PATH="$GRAPH_PATH"
export _JSON_OUTPUT="$JSON_OUTPUT"
export _SKILL_NAME="${SKILL_NAME:-}"
export _IS_DIRECT_CONTRACT="${CONTRACT_FILE:+true}"

exec python3 "$SCRIPT_DIR/validate-skill-contract.py"
