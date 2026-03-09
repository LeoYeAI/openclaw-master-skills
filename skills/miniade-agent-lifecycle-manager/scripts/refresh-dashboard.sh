#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
STATE_DIR="$ROOT/state"
mkdir -p "$STATE_DIR"
TS_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

STATUS_JSON="$STATE_DIR/openclaw.status.json"
GATEWAY_JSON="$STATE_DIR/openclaw.gateway.status.json"
AGENTS_JSON="$STATE_DIR/openclaw.agents.list.json"
REGISTRY_JSON="$STATE_DIR/agent-registry.json"

openclaw status --json >"$STATUS_JSON"
openclaw gateway status --json >"$GATEWAY_JSON"
openclaw agents list --json >"$AGENTS_JSON"

jq -n \
  --arg updatedAt "$TS_UTC" \
  --slurpfile agents "$AGENTS_JSON" \
  --slurpfile status "$STATUS_JSON" \
  '(
    $status[0].heartbeat.agents as $hb
    | {
        updatedAt: $updatedAt,
        defaultAgentId: ($status[0].agents.defaultId // null),
        agents: (
          $agents[0]
          | map(
              . as $a
              | ($hb | map(select(.agentId == $a.id)) | .[0]) as $h
              | {
                  id: $a.id,
                  name: ($a.name // null),
                  identityName: ($a.identityName // null),
                  identityEmoji: ($a.identityEmoji // null),
                  workspace: ($a.workspace // null),
                  model: ($a.model // null),
                  bindings: ($a.bindings // null),
                  isDefault: ($a.isDefault // false),
                  heartbeat: {
                    enabled: ($h.enabled // false),
                    every: ($h.every // "disabled")
                  }
                }
            )
        )
      }
  )' >"$REGISTRY_JSON"

echo "# Agent 状态管理列表" > "$ROOT/AGENT_STATUS.md"
echo >> "$ROOT/AGENT_STATUS.md"
echo "更新时间(UTC): $TS_UTC" >> "$ROOT/AGENT_STATUS.md"
echo >> "$ROOT/AGENT_STATUS.md"
echo "| Agent ID | Name | Identity | Workspace | Model | Heartbeat | Default |" >> "$ROOT/AGENT_STATUS.md"
echo "|---|---|---|---|---|---|---|" >> "$ROOT/AGENT_STATUS.md"

jq -r '.agents[] | [
  .id,
  (.name // "-"),
  (((.identityEmoji // "") + " " + (.identityName // "-")) | gsub("^ ";"")),
  (.workspace // "-"),
  (.model // "-"),
  (if .heartbeat.enabled then .heartbeat.every else "disabled" end),
  (if .isDefault then "yes" else "no" end)
] | @tsv' "$REGISTRY_JSON" | while IFS=$'\t' read -r id name ident ws model hb def; do
  printf "| %s | %s | %s | %s | %s | %s | %s |\n" "$id" "$name" "$ident" "$ws" "$model" "$hb" "$def" >> "$ROOT/AGENT_STATUS.md"
done

echo "OK"
