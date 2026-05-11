#!/bin/bash
# apply-preset.sh — Apply a cost optimization preset via openclaw config
# Usage: bash apply-preset.sh <preset> [--dry-run]
#
# Presets:
#   free      — Maximum savings. Free models only, zero cost target.
#   budget    — Low cost. DeepSeek/MiniMax default, free heartbeats.
#   balanced  — Quality + savings. Sonnet default, cheap heartbeats, session mgmt.
#   quality   — Minimal optimization. Opus default, cheap heartbeats only.
#
# Always generates a JSON patch — apply with: openclaw config patch <file>

set -euo pipefail

PRESET="${1:-}"
DRY_RUN="${2:-}"
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$PRESET" ]; then
  echo -e "${BOLD}Cost Optimization Presets${NC}"
  echo ""
  echo "Usage: bash apply-preset.sh <preset> [--dry-run]"
  echo ""
  echo "  free      \$0-5/mo    Free models only, zero-cost heartbeats"
  echo "  budget    \$5-30/mo   DeepSeek default, free heartbeats, session mgmt"
  echo "  balanced  \$30-100/mo Sonnet default, cheap heartbeats, memory flush"
  echo "  quality   \$100+/mo   Opus default, cheap heartbeats only"
  echo ""
  echo "Add --dry-run to preview without applying."
  exit 0
fi

PATCH_FILE="/tmp/cost-optimizer-patch-${PRESET}.json"

# Auto-backup before applying
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/backup-config.sh" ]; then
  echo -e "${CYAN}Creating config backup before applying preset...${NC}"
  bash "$SCRIPT_DIR/backup-config.sh" "$HOME/.openclaw/openclaw.json" "pre-${PRESET}" 2>/dev/null || true
  echo ""
fi

case "$PRESET" in
  free)
    echo -e "${CYAN}Preset: FREE — Target \$0-5/month${NC}"
    cat > "$PATCH_FILE" << 'PATCH'
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/deepseek/deepseek-chat-v3-0324:free",
        "fallbacks": [
          "openrouter/meta-llama/llama-4-scout-17b-16e-instruct:free",
          "openrouter/qwen/qwen3-235b-a22b:free"
        ]
      },
      "heartbeat": {
        "every": "55m",
        "model": "openrouter/deepseek/deepseek-chat-v3-0324:free",
        "target": "last",
        "lightContext": true
      },
      "compaction": {
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 3000
        }
      },
      "maxConcurrent": 1,
      "subagents": {
        "maxConcurrent": 1
      }
    }
  }
}
PATCH
    echo -e "  Primary: DeepSeek V3 Free (\$0.00/req)"
    echo -e "  Fallbacks: Llama 4 Scout Free, Qwen 3 Free"
    echo -e "  Heartbeat: Free model every 55m"
    echo -e "  Concurrency: 1/1 (minimal)"
    echo -e "  Memory flush: enabled"
    echo -e "${YELLOW}  ⚠️  Requires OpenRouter provider configured${NC}"
    ;;

  budget)
    echo -e "${CYAN}Preset: BUDGET — Target \$5-30/month${NC}"
    cat > "$PATCH_FILE" << 'PATCH'
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "deepseek/deepseek-v3.2",
        "fallbacks": [
          "anthropic/claude-haiku-4-5",
          "google-ai-studio/gemini-flash-latest"
        ]
      },
      "heartbeat": {
        "every": "55m",
        "model": "deepseek/deepseek-v3.2",
        "target": "last",
        "lightContext": true
      },
      "compaction": {
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 3000
        }
      },
      "maxConcurrent": 2,
      "subagents": {
        "maxConcurrent": 2
      }
    }
  }
}
PATCH
    echo -e "  Primary: DeepSeek V3.2 (~\$0.04/req)"
    echo -e "  Fallbacks: Haiku, Gemini Flash"
    echo -e "  Heartbeat: DeepSeek every 55m"
    echo -e "  Concurrency: 2/2"
    echo -e "  Memory flush: enabled"
    ;;

  balanced)
    echo -e "${CYAN}Preset: BALANCED — Target \$30-100/month${NC}"
    cat > "$PATCH_FILE" << 'PATCH'
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-6",
        "fallbacks": [
          "anthropic/claude-haiku-4-5",
          "deepseek/deepseek-v3.2"
        ]
      },
      "heartbeat": {
        "every": "55m",
        "model": "deepseek/deepseek-v3.2",
        "target": "last"
      },
      "compaction": {
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 3000
        }
      },
      "maxConcurrent": 3,
      "subagents": {
        "maxConcurrent": 3
      }
    }
  }
}
PATCH
    echo -e "  Primary: Claude Sonnet 4.6 (~\$0.53/req)"
    echo -e "  Fallbacks: Haiku, DeepSeek"
    echo -e "  Heartbeat: DeepSeek every 55m"
    echo -e "  Concurrency: 3/3"
    echo -e "  Memory flush: enabled"
    ;;

  quality)
    echo -e "${CYAN}Preset: QUALITY — Target \$100+/month${NC}"
    cat > "$PATCH_FILE" << 'PATCH'
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": [
          "anthropic/claude-sonnet-4-6",
          "anthropic/claude-haiku-4-5"
        ]
      },
      "heartbeat": {
        "every": "55m",
        "model": "deepseek/deepseek-v3.2",
        "target": "last"
      },
      "compaction": {
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 5000
        }
      },
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 4
      }
    }
  }
}
PATCH
    echo -e "  Primary: Claude Opus 4.6 (~\$0.71/req)"
    echo -e "  Fallbacks: Sonnet, Haiku"
    echo -e "  Heartbeat: DeepSeek every 55m (saves ~\$500/mo vs Opus heartbeats)"
    echo -e "  Concurrency: 4/4"
    echo -e "  Memory flush: enabled"
    ;;

  *)
    echo -e "${RED}Unknown preset: $PRESET${NC}"
    echo "Options: free, budget, balanced, quality"
    exit 1
    ;;
esac

echo ""
echo -e "${BOLD}Generated patch:${NC} $PATCH_FILE"
echo ""

if [ "$DRY_RUN" = "--dry-run" ]; then
  echo -e "${YELLOW}DRY RUN — showing patch content:${NC}"
  cat "$PATCH_FILE"
  echo ""
  echo "To apply: bash apply-preset.sh $PRESET"
else
  echo -e "${BOLD}Patch file ready.${NC}"
  echo ""
  echo "To apply via OpenClaw gateway, the agent can use:"
  echo "  gateway config.patch with the contents of $PATCH_FILE"
  echo ""
  echo "Or tell your agent: 'Apply the $PRESET cost preset'"
fi
