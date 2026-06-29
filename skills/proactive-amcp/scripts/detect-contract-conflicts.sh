#!/bin/bash
# detect-contract-conflicts.sh — Cross-skill ontology conflict detection
# Part of proactive-amcp enforcer
#
# Finds incompatible postconditions across loaded skills. For example:
# - Skill A postcondition: "Task.status == done"
# - Skill B postcondition: "Task.status != done"
# These conflict because they cannot both be true simultaneously.
#
# Usage:
#   detect-contract-conflicts.sh [--skills-dir <path>] [--json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"

SKILLS_DIR="${SKILLS_DIR:-$HOME/.openclaw/skills}"
JSON_OUTPUT=false

usage() {
  cat <<EOF
detect-contract-conflicts.sh — Cross-skill ontology conflict detection

Usage:
  $(basename "$0") [options]

Options:
  --skills-dir <path>  Path to skills directory (default: ~/.openclaw/skills)
  --json               Output results as JSON
  -h, --help           Show this help
EOF
  exit 1
}

while [ $# -gt 0 ]; do
  case "$1" in
    --skills-dir) SKILLS_DIR="$2"; shift 2 ;;
    --json) JSON_OUTPUT=true; shift ;;
    -h|--help) usage ;;
    -*) echo "ERROR: Unknown option '$1'" >&2; usage ;;
    *) shift ;;
  esac
done

export _SKILLS_DIR="$SKILLS_DIR"
export _JSON_OUTPUT="$JSON_OUTPUT"

exec python3 "$SCRIPT_DIR/detect-contract-conflicts.py"
