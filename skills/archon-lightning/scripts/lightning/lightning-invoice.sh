#!/usr/bin/env bash
set -euo pipefail

# lightning-invoice.sh - Create BOLT11 invoice to receive sats
# Usage: ./lightning-invoice.sh <amount> <memo> [id]

source ~/.archon.env

npx @didcid/keymaster lightning-invoice "$@"
