#!/usr/bin/env bash
# yt-content-engine setup script
# Checks dependencies, creates config template, tests HeyGen API key

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   yt-content-engine setup check      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# ── Dependency Checks ──────────────────────────────────────────

MISSING=0

check_cmd() {
    local cmd="$1"
    local purpose="$2"
    local install="$3"

    if command -v "$cmd" &>/dev/null; then
        local version
        version=$("$cmd" --version 2>/dev/null | head -1 || echo "installed")
        echo -e "  ${GREEN}✅ $cmd${NC} — $purpose"
        echo -e "     $version"
    else
        echo -e "  ${RED}❌ $cmd${NC} — $purpose"
        echo -e "     ${YELLOW}Install: $install${NC}"
        MISSING=$((MISSING + 1))
    fi
}

echo "📋 Checking dependencies..."
echo ""
check_cmd "summarize" "YouTube transcript extraction" "brew install steipete/tap/summarize"
check_cmd "bird"      "X/Twitter posting"            "brew install steipete/tap/bird"
check_cmd "ffmpeg"    "Video post-processing"         "brew install ffmpeg"
check_cmd "curl"      "API calls to HeyGen"           "Usually pre-installed on macOS"
check_cmd "python3"   "Helper scripts"                "Usually pre-installed on macOS"
echo ""

if [ "$MISSING" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $MISSING missing dependencies. Install them before running the pipeline.${NC}"
else
    echo -e "${GREEN}✅ All dependencies installed!${NC}"
fi

# ── Config File ────────────────────────────────────────────────

echo ""
echo "📄 Checking config..."
echo ""

if [ -f "$CONFIG_FILE" ]; then
    echo -e "  ${GREEN}✅ config.json exists${NC}"

    # Validate required fields
    VALID=true
    for field in '.heygen.apiKey' '.heygen.avatarId' '.heygen.voiceId' '.substack.publication' '.twitter.handle'; do
        val=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); v=c$(echo $field | sed 's/\./"]["/g' | sed 's/^/["/' | sed 's/$/"]/'); print(v if v else '')" 2>/dev/null || echo "")
        key=$(echo "$field" | tr -d "'")
        if [ -z "$val" ] || [ "$val" = "YOUR_API_KEY" ] || [ "$val" = "YOUR_AVATAR_ID" ] || [ "$val" = "YOUR_VOICE_ID" ] || [ "$val" = "yourblog.substack.com" ] || [ "$val" = "@yourhandle" ]; then
            echo -e "  ${YELLOW}⚠️  $key needs to be configured${NC}"
            VALID=false
        else
            echo -e "  ${GREEN}✅ $key is set${NC}"
        fi
    done
else
    echo -e "  ${YELLOW}⚠️  config.json not found — creating template${NC}"
    cat > "$CONFIG_FILE" << 'TEMPLATE'
{
  "heygen": {
    "apiKey": "YOUR_API_KEY",
    "avatarId": "YOUR_AVATAR_ID",
    "voiceId": "YOUR_VOICE_ID"
  },
  "substack": {
    "publication": "yourblog.substack.com"
  },
  "twitter": {
    "handle": "@yourhandle"
  },
  "author": {
    "voice": "Description of your writing voice and style",
    "name": "Your Name"
  },
  "video": {
    "clipCount": 5,
    "maxClipSeconds": 60,
    "cropMode": "auto"
  }
}
TEMPLATE
    echo -e "  ${GREEN}✅ Template created at $CONFIG_FILE${NC}"
    echo -e "  ${YELLOW}   Edit it with your real values before running the pipeline.${NC}"
fi

# ── HeyGen API Test ────────────────────────────────────────────

echo ""
echo "🎥 Testing HeyGen API..."
echo ""

API_KEY=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c.get('heygen',{}).get('apiKey',''))" 2>/dev/null || echo "")

if [ -z "$API_KEY" ] || [ "$API_KEY" = "YOUR_API_KEY" ]; then
    echo -e "  ${YELLOW}⚠️  No API key configured — skipping HeyGen test${NC}"
    echo -e "  ${YELLOW}   Get your key at https://app.heygen.com/settings${NC}"
else
    # Test API key
    RESPONSE=$(curl -s -H "X-Api-Key: $API_KEY" "https://api.heygen.com/v2/avatars" 2>/dev/null || echo '{"error":"connection failed"}')
    HAS_DATA=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if 'data' in d else 'no')" 2>/dev/null || echo "no")

    if [ "$HAS_DATA" = "yes" ]; then
        echo -e "  ${GREEN}✅ HeyGen API key is valid!${NC}"
        echo ""

        # List avatars
        echo "  📸 Your avatars:"
        echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
avatars = data.get('data', {}).get('avatars', [])
if not avatars:
    print('     (none found)')
else:
    for a in avatars[:10]:
        name = a.get('avatar_name', 'unnamed')
        aid = a['avatar_id']
        print(f'     • {name} → {aid}')
    if len(avatars) > 10:
        print(f'     ... and {len(avatars)-10} more')
" 2>/dev/null || echo "     (could not parse avatars)"

        echo ""

        # List voices
        echo "  🎙️  Your voices:"
        VOICE_RESPONSE=$(curl -s -H "X-Api-Key: $API_KEY" "https://api.heygen.com/v2/voices" 2>/dev/null || echo '{}')
        echo "$VOICE_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
voices = data.get('data', {}).get('voices', [])
if not voices:
    print('     (none found)')
else:
    for v in voices[:10]:
        name = v.get('name', v.get('display_name', 'unnamed'))
        vid = v['voice_id']
        lang = v.get('language', '?')
        print(f'     • {name} ({lang}) → {vid}')
    if len(voices) > 10:
        print(f'     ... and {len(voices)-10} more')
" 2>/dev/null || echo "     (could not parse voices)"

    else
        echo -e "  ${RED}❌ HeyGen API key is invalid or request failed${NC}"
        echo -e "  ${YELLOW}   Check your key at https://app.heygen.com/settings${NC}"
    fi
fi

# ── Summary ────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}──────────────────────────────────────${NC}"
if [ "$MISSING" -eq 0 ]; then
    echo -e "${GREEN}🚀 Dependencies look good!${NC}"
else
    echo -e "${YELLOW}⚠️  Install missing dependencies, then re-run this script.${NC}"
fi
echo -e "${BLUE}   Config: $CONFIG_FILE${NC}"
echo ""
