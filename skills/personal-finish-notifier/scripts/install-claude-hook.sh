#!/usr/bin/env bash

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK_PATH="${HOME}/.claude/hooks/mac-task-notify.sh"
SETTINGS_PATH="${HOME}/.claude/settings.json"
ENV_PATH="${HOME}/.claude/mac-notify.env"

mkdir -p "$(dirname "$HOOK_PATH")"
cp "${SKILL_DIR}/scripts/notify.sh" "$HOOK_PATH"
chmod +x "$HOOK_PATH"

python3 - <<'PY' "$SETTINGS_PATH" "$HOOK_PATH"
import json
import os
import sys

settings_path = sys.argv[1]
hook_path = sys.argv[2]

data = {}
if os.path.exists(settings_path):
    with open(settings_path, "r", encoding="utf-8") as f:
        data = json.load(f)

entry = [{
    "matcher": "*",
    "hooks": [{
        "type": "command",
        "command": f"bash {hook_path}",
        "timeout": 15
    }]
}]

data["Stop"] = entry
data["TaskCompleted"] = entry

with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY

if [[ ! -f "$ENV_PATH" ]]; then
  cat >"$ENV_PATH" <<'EOF'
MAC_NOTIFY_MODE=openclaw_whatsapp
MAC_NOTIFY_TITLE_PREFIX="Claude"
OPENCLAW_NOTIFY_CHANNEL=whatsapp
OPENCLAW_NOTIFY_TARGET=
OPENCLAW_NOTIFY_SELF_TARGET=
EOF
fi
