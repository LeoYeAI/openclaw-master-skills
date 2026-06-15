#!/bin/bash
# Initialize Team Dispatch user config (C option)
# Usage: bash ~/skills/team-dispatch/scripts/setup-config.sh

set -e

mkdir -p ~/.openclaw/configs

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# Single source of truth: skill root config.json
SRC="$SKILL_DIR/config.json"
DST=~/.openclaw/configs/team-dispatch.json

if [ -f "$DST" ]; then
  echo "⏭️  已存在: $DST"
  exit 0
fi

cp "$SRC" "$DST"
# marker file: safe for uninstall purge
mkdir -p ~/.openclaw/configs
[ -f ~/.openclaw/configs/.team-dispatch-managed ] || echo "managed-by=team-dispatch" > ~/.openclaw/configs/.team-dispatch-managed

echo "✅ 已生成用户可配置文件: $DST"
echo "你可以在这里为每个 agentId 配 displayName/username/telegram 通知(可选)"
