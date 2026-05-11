#!/bin/bash
# token-enforcer.sh — Set maxTokens per model to enforce output limits
# Usage: bash token-enforcer.sh <preset> [--dry-run]
# Presets: strict (1024), moderate (2048), normal (4096), unlimited (32000)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${1:-$HOME/.openclaw/openclaw.json}"
PRESET="${2:-}"
DRY_RUN="${3:-}"
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$PRESET" ] || [ "$PRESET" = "--help" ]; then
  echo -e "${BOLD}Token Budget Enforcer${NC}"
  echo ""
  echo "Usage: bash token-enforcer.sh <config-path> <preset> [--dry-run]"
  echo ""
  echo "Presets set maxTokens on all configured models:"
  echo ""
  echo "  strict    1024 tokens  Forces extreme conciseness. ~$0.08/response on Opus."
  echo "  moderate  2048 tokens  Good conciseness. ~$0.15/response on Opus."
  echo "  normal    4096 tokens  Balanced. ~$0.31/response on Opus."  
  echo "  generous  8192 tokens  Detailed when needed. ~$0.61/response on Opus."
  echo "  unlimited 32000 tokens Default. Full responses. ~$2.40/response on Opus."
  echo ""
  echo "Monthly savings at 50 req/day (output tokens only, Opus pricing):"
  echo "  strict vs unlimited:   ~$3,480/month saved"
  echo "  moderate vs unlimited: ~$3,375/month saved"
  echo "  normal vs unlimited:   ~$3,135/month saved"
  echo ""
  echo "Note: Agents can still request more via tool calls. This caps single responses."
  exit 0
fi

case "$PRESET" in
  strict)    MAX=1024; DESC="strict (1024 tokens)" ;;
  moderate)  MAX=2048; DESC="moderate (2048 tokens)" ;;
  normal)    MAX=4096; DESC="normal (4096 tokens)" ;;
  generous)  MAX=8192; DESC="generous (8192 tokens)" ;;
  unlimited) MAX=32000; DESC="unlimited (32000 tokens)" ;;
  *)
    echo -e "${RED}Unknown preset: $PRESET${NC}"
    echo "Options: strict, moderate, normal, generous, unlimited"
    exit 1
    ;;
esac

echo -e "${BOLD}Token Enforcer: ${CYAN}$DESC${NC}"
echo ""

# Generate the config patch
PATCH_FILE="/tmp/token-enforcer-${PRESET}.json"

node -e "
const fs = require('fs');
const raw = fs.readFileSync('$CONFIG', 'utf8');
const config = new Function('return (' + raw + ')')();
const providers = config.models?.providers || {};
const maxTokens = $MAX;

const patch = { models: { providers: {} } };
let count = 0;

for (const [provName, prov] of Object.entries(providers)) {
  if (prov.models && prov.models.length > 0) {
    patch.models.providers[provName] = {
      models: prov.models.map(m => ({
        ...m,
        maxTokens: maxTokens,
      }))
    };
    count += prov.models.length;
  }
}

console.log('  Setting maxTokens=' + maxTokens + ' on ' + count + ' models across ' + Object.keys(patch.models.providers).length + ' providers');
console.log('');

// Show impact
const tiers = [
  { name: 'Opus (output \$75/M)', rate: 75 },
  { name: 'Sonnet (output \$15/M)', rate: 15 },
  { name: 'DeepSeek (output \$1.10/M)', rate: 1.10 },
];

const unlimited = 32000;
console.log('  Monthly output cost savings vs unlimited (50 req/day):');
for (const t of tiers) {
  const currentCost = (unlimited / 1e6) * t.rate * 50 * 30;
  const newCost = (maxTokens / 1e6) * t.rate * 50 * 30;
  const savings = currentCost - newCost;
  console.log('    ' + t.name.padEnd(30) + '\$' + newCost.toFixed(0).padStart(5) + '/mo (was \$' + currentCost.toFixed(0) + ', save \$' + savings.toFixed(0) + ')');
}

fs.writeFileSync('$PATCH_FILE', JSON.stringify(patch, null, 2));
console.log('');
console.log('  Patch written to: $PATCH_FILE');
" 2>/dev/null

if [ "$DRY_RUN" = "--dry-run" ]; then
  echo ""
  echo -e "${YELLOW}DRY RUN — patch not applied.${NC}"
  echo "Review: cat $PATCH_FILE"
  echo "Apply via agent: 'Apply the token enforcer patch from $PATCH_FILE'"
else
  echo ""
  echo -e "${BOLD}Patch ready.${NC} Tell your agent:"
  echo "  'Apply the token enforcer ${PRESET} preset from $PATCH_FILE'"
fi
