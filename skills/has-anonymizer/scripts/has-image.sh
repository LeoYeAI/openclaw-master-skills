#!/usr/bin/env bash
# Wrapper script for HaS Image CLI — invoked as {baseDir}/scripts/has-image
# Delegates to has_image.py via uv run for automatic dependency management.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

exec uv run "$SCRIPT_DIR/has_image.py" "$@"
