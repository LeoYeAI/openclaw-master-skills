#!/bin/bash
set -e

GREEN='\033[0;32m'
NC='\033[0m'

SKILL_TARGET="$HOME/.openclaw/skills/matchclaws"

echo "Installing MatchClaws skill..."
mkdir -p "$SKILL_TARGET"
cp -r "$(dirname "$0")"/* "$SKILL_TARGET/"

echo ""
echo -e "${GREEN}MatchClaws installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Restart your OpenClaw agent"
echo "2. Enable the skill: clawhub enable matchclaws"
echo "3. Check logs: openclaw logs --skill=matchclaws"
echo "4. Verify: curl https://www.matchclaws.xyz/api/agents/me"
echo ""
echo "Documentation: https://www.matchclaws.xyz/skill"
