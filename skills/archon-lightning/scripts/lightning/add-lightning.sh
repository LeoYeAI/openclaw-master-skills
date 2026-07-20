#!/usr/bin/env bash
set -euo pipefail

# add-lightning.sh - Create Lightning wallet for a DID
# Usage: ./add-lightning.sh [id]

source ~/.archon.env

npx @didcid/keymaster add-lightning "$@"
