#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  create-telegram-agent.sh <agent_id> <telegram_token> [workspace]

Notes:
  - This script handles create + channel + bindings.
  - Pairing approval is a separate step after user sends /start.
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

AGENT_ID="$1"
TELEGRAM_TOKEN="$2"
WORKSPACE="${3:-$HOME/.openclaw/workspace-$AGENT_ID}"

openclaw agents add "$AGENT_ID" --workspace "$WORKSPACE"

mkdir -p "$HOME/.openclaw/agents/$AGENT_ID/agent/"
if [[ -f "$HOME/.openclaw/agents/main/agent/auth-profiles.json" ]]; then
  cp "$HOME/.openclaw/agents/main/agent/auth-profiles.json" "$HOME/.openclaw/agents/$AGENT_ID/agent/"
fi

openclaw channels add --channel telegram --account "$AGENT_ID" --token "$TELEGRAM_TOKEN"

BINDINGS_JSON="$(openclaw config get bindings --json 2>/dev/null || echo '[]')"

if jq -e --arg aid "$AGENT_ID" '
  any(.[]?; .agentId == $aid and .match.channel == "telegram" and .match.accountId == $aid)
' <<<"$BINDINGS_JSON" >/dev/null; then
  echo "Binding already exists for agent=$AGENT_ID"
else
  NEW_BINDINGS="$(jq -c --arg aid "$AGENT_ID" '
    . + [{agentId:$aid, match:{channel:"telegram", accountId:$aid}}]
  ' <<< "$BINDINGS_JSON")"
  openclaw config set bindings "$NEW_BINDINGS" --json
  echo "Binding appended for agent=$AGENT_ID"
fi

echo "Created and configured agent: $AGENT_ID"
echo "Next step: ask user to send /start to the Telegram bot, then run:"
echo "  openclaw pairing list --channel telegram --account $AGENT_ID --json"
echo "  openclaw pairing approve <PAIRING_CODE> --channel telegram --account $AGENT_ID"
