#!/usr/bin/env bash
set -euo pipefail

# publish-lightning.sh - Publish Lightning endpoint to DID document
# Usage: ./publish-lightning.sh [id]

source ~/.archon.env

npx @didcid/keymaster publish-lightning "$@"
