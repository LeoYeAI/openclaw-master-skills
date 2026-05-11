#!/usr/bin/env bash
# Quick wrapper for text analysis.
# Usage: ./scripts/analyze.sh [file] [--json] [--verbose]

set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [[ $# -ge 1 && ! "$1" =~ ^-- ]]; then
  node "$DIR/src/cli.js" analyze -f "$@"
else
  node "$DIR/src/cli.js" analyze "$@"
fi
