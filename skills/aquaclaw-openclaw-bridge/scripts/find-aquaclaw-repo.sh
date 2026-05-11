#!/usr/bin/env bash
set -euo pipefail

is_gateway_hub_repo() {
  local dir="$1"
  [[ -f "$dir/package.json" ]] || return 1
  grep -Eq '"name"[[:space:]]*:[[:space:]]*"gateway-hub"' "$dir/package.json"
}

declare -a candidates=()

if [[ -n "${AQUACLAW_REPO:-}" ]]; then
  candidates+=("${AQUACLAW_REPO}")
fi

candidates+=(
  "${PWD}"
  "${HOME}/.openclaw/workspace/gateway-hub"
  "${HOME}/.openclaw/workspace/AquaClaw"
  "${HOME}/workspace/gateway-hub"
  "${HOME}/workspace/AquaClaw"
)

for candidate in "${candidates[@]}"; do
  [[ -n "$candidate" ]] || continue
  [[ -d "$candidate" ]] || continue
  if is_gateway_hub_repo "$candidate"; then
    (cd "$candidate" && pwd)
    exit 0
  fi
done

cat >&2 <<'EOF'
Could not find the AquaClaw repo.
Set AQUACLAW_REPO or place gateway-hub at $HOME/.openclaw/workspace/gateway-hub.
EOF
exit 1
