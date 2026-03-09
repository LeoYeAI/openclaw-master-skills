#!/usr/bin/env bash

set -euo pipefail

skill_dir="${1:-}"
if [[ -z "$skill_dir" || ! -d "$skill_dir" ]]; then
  echo "usage: $0 /path/to/skill" >&2
  exit 1
fi

skill_md="${skill_dir}/SKILL.md"
if [[ ! -f "$skill_md" ]]; then
  echo "missing SKILL.md" >&2
  exit 1
fi

description="$(python3 - <<'PY' "$skill_md"
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
m = re.search(r"^description:\s*(.+)$", text, re.M)
print(m.group(1).strip() if m else "")
PY
)"

echo "description_length=${#description}"

if (( ${#description} > 140 )); then
  echo "warn: description is long and may truncate in listings"
fi

if find "$skill_dir" -maxdepth 3 -type f | rg -q 'README\.md|INSTALL|CHANGELOG|publish|watch|token|secret'; then
  echo "warn: package contains files or names that may look internal or noisy"
fi

if rg -n '\+?[0-9][0-9 ()-]{7,}|token|secret|password|api[_-]?key|private' "$skill_dir" >/dev/null; then
  echo "warn: possible private or sensitive strings found"
fi

echo "done"
