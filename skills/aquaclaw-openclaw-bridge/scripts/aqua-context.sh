#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(bash "${script_dir}/find-aquaclaw-repo.sh")"

cd "${repo}"
exec npm run aqua:context -- "$@"
