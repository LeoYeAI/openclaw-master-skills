#!/usr/bin/env bash
set -euo pipefail

# unpublish-lightning.sh - Remove Lightning endpoint from DID document
# Usage: ./unpublish-lightning.sh [id]

source ~/.archon.env

npx @didcid/keymaster unpublish-lightning "$@"
