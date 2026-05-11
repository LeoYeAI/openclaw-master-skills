#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec node "${script_dir}/aqua-mirror-sync.mjs" "$@"
