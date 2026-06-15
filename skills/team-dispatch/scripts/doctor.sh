#!/bin/bash
# Team Dispatch 环境自检（模型/Agent）
# 用法: bash ~/skills/team-dispatch/scripts/doctor.sh

set -e

echo "🩺 Team Dispatch Doctor"

if ! command -v openclaw >/dev/null 2>&1; then
  echo "❌ openclaw 未安装"
  exit 1
fi

echo "✅ openclaw: $(openclaw --version 2>/dev/null || echo unknown)"

echo ""
echo "=== Agents & primary models ==="
node - <<'NODE'
const fs=require('fs');
const JSON5=require('/opt/homebrew/lib/node_modules/openclaw/node_modules/json5');
const c=JSON5.parse(fs.readFileSync(process.env.HOME+'/.openclaw/openclaw.json','utf8'));
const list=c.agents?.list||[];
for (const a of list) {
  const primary = typeof a.model === 'string' ? a.model : a.model?.primary;
  console.log(`${a.id}\t${a.name||''}\t${primary||''}`);
}
NODE

echo ""
echo "=== Suggested stable baseline (if you see 404/quota issues) ==="
echo "- coder primary = openai-codex/gpt-5.3-codex (OAuth, coding-optimized)"
echo "- others primary = openai-codex/gpt-5.4 (OAuth, general-purpose)"
echo "- fallbacks = bailian/qwen3.5-plus, bailian/kimi-k2.5, zai/glm-4.7"

echo ""
echo "If you want auto-patch to baseline, run:"
echo "  bash ~/skills/team-dispatch/scripts/setup.sh --baseline-models"
