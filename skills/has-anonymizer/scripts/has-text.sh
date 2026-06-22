#!/usr/bin/env bash
# Wrapper script for HaS Text CLI — invoked as {baseDir}/scripts/has-text
# Delegates to has_text_entry.py via uv run for automatic dependency management.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

exec uv run "$SCRIPT_DIR/has_text_entry.py" "$@"
