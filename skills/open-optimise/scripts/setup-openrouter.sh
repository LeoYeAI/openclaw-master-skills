#!/bin/bash
# setup-openrouter.sh — Generate config patch to add OpenRouter provider with free models
# Usage: bash setup-openrouter.sh <your-openrouter-api-key>
# Outputs a JSON patch that adds OpenRouter as a provider with free + budget models

set -euo pipefail

API_KEY="${1:-}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$API_KEY" ]; then
  echo -e "${BOLD}Setup OpenRouter Provider${NC}"
  echo ""
  echo "Usage: bash setup-openrouter.sh <your-openrouter-api-key>"
  echo ""
  echo "Get your API key at: https://openrouter.ai/keys"
  echo ""
  echo "This generates a config patch that adds:"
  echo "  - OpenRouter as a model provider"
  echo "  - 5 free models (DeepSeek, Llama, Qwen, Gemma, Mistral)"
  echo "  - 6 budget models (MiniMax, DeepSeek paid, Kimi, GLM, Nano, Flash-Lite)"
  echo "  - Aliases for all models"
  exit 0
fi

PATCH_FILE="/tmp/openrouter-setup-patch.json"

cat > "$PATCH_FILE" << PATCH
{
  "models": {
    "providers": {
      "openrouter": {
        "baseUrl": "https://openrouter.ai/api/v1",
        "apiKey": "$API_KEY",
        "api": "openai-completions",
        "models": [
          {
            "id": "deepseek/deepseek-chat-v3-0324:free",
            "name": "DeepSeek V3 (Free)",
            "contextWindow": 164000,
            "maxTokens": 2048
          },
          {
            "id": "meta-llama/llama-4-scout-17b-16e-instruct:free",
            "name": "Llama 4 Scout (Free)",
            "contextWindow": 512000,
            "maxTokens": 2048
          },
          {
            "id": "qwen/qwen3-235b-a22b:free",
            "name": "Qwen 3 235B (Free)",
            "contextWindow": 40000,
            "maxTokens": 2048
          },
          {
            "id": "google/gemma-3-27b-it:free",
            "name": "Gemma 3 27B (Free)",
            "contextWindow": 96000,
            "maxTokens": 2048
          },
          {
            "id": "mistral/mistral-small-3.1-24b-instruct:free",
            "name": "Mistral Small 3.1 (Free)",
            "contextWindow": 96000,
            "maxTokens": 2048
          },
          {
            "id": "minimax/minimax-m2.5",
            "name": "MiniMax M2.5",
            "contextWindow": 1000000,
            "maxTokens": 16384
          },
          {
            "id": "deepseek/deepseek-v3.2",
            "name": "DeepSeek V3.2",
            "contextWindow": 164000,
            "maxTokens": 16384
          },
          {
            "id": "moonshotai/kimi-k2.5",
            "name": "Kimi K2.5",
            "contextWindow": 131072,
            "maxTokens": 16384
          },
          {
            "id": "z-ai/glm-5",
            "name": "GLM-5",
            "contextWindow": 128000,
            "maxTokens": 16384
          },
          {
            "id": "openai/gpt-5-nano",
            "name": "GPT-5 Nano",
            "contextWindow": 128000,
            "maxTokens": 16384
          },
          {
            "id": "google/gemini-2.5-flash-lite",
            "name": "Gemini Flash-Lite",
            "contextWindow": 1000000,
            "maxTokens": 16384
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "models": {
        "openrouter/deepseek/deepseek-chat-v3-0324:free": { "alias": "deepseek-free" },
        "openrouter/meta-llama/llama-4-scout-17b-16e-instruct:free": { "alias": "llama-free" },
        "openrouter/qwen/qwen3-235b-a22b:free": { "alias": "qwen-free" },
        "openrouter/google/gemma-3-27b-it:free": { "alias": "gemma-free" },
        "openrouter/mistral/mistral-small-3.1-24b-instruct:free": { "alias": "mistral-free" },
        "openrouter/minimax/minimax-m2.5": { "alias": "minimax" },
        "openrouter/deepseek/deepseek-v3.2": { "alias": "or-deepseek" },
        "openrouter/moonshotai/kimi-k2.5": { "alias": "kimi" },
        "openrouter/z-ai/glm-5": { "alias": "glm" },
        "openrouter/openai/gpt-5-nano": { "alias": "nano" },
        "openrouter/google/gemini-2.5-flash-lite": { "alias": "flashlite" }
      }
    }
  }
}
PATCH

echo -e "${GREEN}✅ Patch generated: $PATCH_FILE${NC}"
echo ""
echo "This adds:"
echo "  - OpenRouter provider with API key"
echo "  - 5 free models + 6 budget models"
echo "  - 11 aliases for quick model switching"
echo ""
echo "To apply, tell your agent:"
echo "  'Apply the OpenRouter config patch from $PATCH_FILE'"
echo ""
echo "Or use the gateway tool:"
echo "  gateway config.patch with contents of $PATCH_FILE"
echo ""
echo -e "${YELLOW}After applying, test with: /model deepseek-free${NC}"

# Validate API key format
if [[ ! "$API_KEY" =~ ^sk- ]]; then
  echo ""
  echo -e "${YELLOW}⚠ API key doesn't start with 'sk-' — verify it's correct${NC}"
fi
