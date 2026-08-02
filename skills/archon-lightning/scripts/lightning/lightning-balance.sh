#!/usr/bin/env bash
set -euo pipefail

# lightning-balance.sh - Check Lightning wallet balance
# Usage: ./lightning-balance.sh [id]

source ~/.archon.env

npx @didcid/keymaster lightning-balance "$@"
