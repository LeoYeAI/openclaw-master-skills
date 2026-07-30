#!/bin/bash
# init-agent-context.sh
# Wrapper for backwards compatibility with npx skills install.
# All logic lives in the main CLI at ../agent-context

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../agent-context" init "$@"
