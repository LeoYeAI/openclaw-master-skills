#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
node "${script_dir}/aqua-sea-diary-context.mjs" "$@"
