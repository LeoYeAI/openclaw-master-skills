#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "${SCRIPT_DIR}/notify.sh" <<'EOF'
{"hook_event_name":"Stop","cwd":"/home/nova/.openclaw/workspace","reason":"end_turn","last_assistant_message":"I finished packaging the notifier skill and the live path is working."}
EOF
