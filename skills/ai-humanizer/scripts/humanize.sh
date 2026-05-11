#!/usr/bin/env bash
# Quick wrapper for humanization suggestions.
# Usage: ./scripts/humanize.sh [file] [--autofix] [--json]

set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [[ $# -ge 1 && ! "$1" =~ ^-- ]]; then
  node "$DIR/src/cli.js" humanize -f "$@"
else
  node "$DIR/src/cli.js" humanize "$@"
fi
