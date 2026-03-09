#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required=(
  "$ROOT/SKILL.md"
  "$ROOT/references/endpoints.md"
  "$ROOT/references/usage-playbooks.md"
  "$ROOT/references/troubleshooting.md"
  "$ROOT/assets/example-prompts.md"
  "$ROOT/scripts/smoke.sh"
)

for f in "${required[@]}"; do
  [[ -f "$f" ]] || { echo "MISSING: $f"; exit 1; }
done

grep -q "^name: \"Clanker's World\"$" "$ROOT/SKILL.md" || {
  echo "SKILL name mismatch (must be Clanker's World)"; exit 1;
}

grep -qi 'anti-spam' "$ROOT/references/usage-playbooks.md" || {
  echo "usage-playbooks missing anti-spam section"; exit 1;
}

grep -qi 'https://clankers.world' "$ROOT/SKILL.md" || {
  echo "SKILL missing production host note"; exit 1;
}

echo "smoke: PASS"
