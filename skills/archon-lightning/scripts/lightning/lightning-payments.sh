#!/usr/bin/env bash
set -euo pipefail

# lightning-payments.sh - Show payment history
# Usage: ./lightning-payments.sh [id]

source ~/.archon.env

npx @didcid/keymaster lightning-payments "$@"
