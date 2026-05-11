#!/bin/bash
# preset-manager.sh — Export, import, and manage named config presets
# Usage: bash preset-manager.sh <export|import|list> [args]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${HOME}/.openclaw/openclaw.json"
PRESETS_DIR="${HOME}/.openclaw/workspace/skills/cost-optimizer/presets"
ACTION="${1:-list}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "$PRESETS_DIR"

case "$ACTION" in
  export)
    NAME="${2:-}"
    DESC="${3:-Custom preset}"
    
    if [ -z "$NAME" ]; then
      echo "Usage: bash preset-manager.sh export <name> [description]"
      exit 1
    fi
    
    PRESET_FILE="$PRESETS_DIR/${NAME}.preset.json"
    
    node -e "
const fs = require('fs');
const raw = fs.readFileSync('$CONFIG', 'utf8');
const config = new Function('return (' + raw + ')')();
const d = config.agents?.defaults || {};
const m = d.model;

const preset = {
  name: '$NAME',
  description: '$DESC',
  author: require('os').hostname(),
  version: '5.0.0',
  created: new Date().toISOString(),
  config: {
    model: {
      primary: typeof m === 'string' ? m : m?.primary,
      fallbacks: typeof m === 'object' ? (m.fallbacks || []) : [],
    },
    heartbeat: {
      every: d.heartbeat?.every || null,
      model: d.heartbeat?.model || null,
      target: d.heartbeat?.target || null,
    },
    compaction: {
      memoryFlush: d.compaction?.memoryFlush || {},
    },
    maxConcurrent: d.maxConcurrent || null,
    subagentsMaxConcurrent: d.subagents?.maxConcurrent || null,
    aliases: d.models || {},
  },
};

fs.writeFileSync('$PRESET_FILE', JSON.stringify(preset, null, 2));
console.log('Preset exported: $PRESET_FILE');
console.log('');
console.log(JSON.stringify(preset, null, 2));
" 2>/dev/null
    
    echo -e "${GREEN}✅ Preset '${NAME}' exported to ${PRESET_FILE}${NC}"
    ;;
    
  import)
    PRESET_FILE="${2:-}"
    
    if [ -z "$PRESET_FILE" ] || [ ! -f "$PRESET_FILE" ]; then
      echo "Usage: bash preset-manager.sh import <preset-file.json>"
      echo ""
      echo "Available presets:"
      ls "$PRESETS_DIR"/*.preset.json 2>/dev/null | while read f; do
        NAME=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$f','utf8')).name)" 2>/dev/null)
        DESC=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$f','utf8')).description)" 2>/dev/null)
        echo "  $f"
        echo "    Name: $NAME — $DESC"
      done
      exit 0
    fi
    
    echo -e "${BOLD}Importing preset...${NC}"
    
    node -e "
const fs = require('fs');
const preset = JSON.parse(fs.readFileSync('$PRESET_FILE', 'utf8'));

console.log('Name:        ' + preset.name);
console.log('Description: ' + preset.description);
console.log('Author:      ' + (preset.author || '?'));
console.log('Created:     ' + (preset.created || '?'));
console.log('');
console.log('Changes:');
if (preset.config.model?.primary) console.log('  Primary model: ' + preset.config.model.primary);
if (preset.config.model?.fallbacks?.length) console.log('  Fallbacks: ' + preset.config.model.fallbacks.join(', '));
if (preset.config.heartbeat?.every) console.log('  Heartbeat: ' + preset.config.heartbeat.model + ' every ' + preset.config.heartbeat.every);
if (preset.config.maxConcurrent) console.log('  Concurrency: ' + preset.config.maxConcurrent);
console.log('');

// Generate config patch
const patch = { agents: { defaults: {} } };
if (preset.config.model) patch.agents.defaults.model = preset.config.model;
if (preset.config.heartbeat?.every) patch.agents.defaults.heartbeat = preset.config.heartbeat;
if (preset.config.compaction) patch.agents.defaults.compaction = preset.config.compaction;
if (preset.config.maxConcurrent) patch.agents.defaults.maxConcurrent = preset.config.maxConcurrent;
if (preset.config.subagentsMaxConcurrent) {
  patch.agents.defaults.subagents = { maxConcurrent: preset.config.subagentsMaxConcurrent };
}
if (preset.config.aliases && Object.keys(preset.config.aliases).length) {
  patch.agents.defaults.models = preset.config.aliases;
}

const patchFile = '/tmp/preset-import-patch.json';
fs.writeFileSync(patchFile, JSON.stringify(patch, null, 2));
console.log('Config patch generated: ' + patchFile);
console.log('');
console.log('To apply, tell your agent:');
console.log('  Apply the config patch from ' + patchFile);
" 2>/dev/null
    ;;
    
  list)
    echo -e "${BOLD}Available Presets:${NC}"
    echo ""
    
    # Built-in presets
    echo -e "${CYAN}Built-in (via apply-preset.sh):${NC}"
    echo "  free      — \$0-5/mo, free models only"
    echo "  budget    — \$5-30/mo, DeepSeek default"
    echo "  balanced  — \$30-100/mo, Sonnet default"
    echo "  quality   — \$100+/mo, Opus default, cheap heartbeats"
    echo ""
    
    # User presets
    PRESET_COUNT=$(ls "$PRESETS_DIR"/*.preset.json 2>/dev/null | wc -l)
    if [ "$PRESET_COUNT" -gt 0 ]; then
      echo -e "${CYAN}Custom presets:${NC}"
      ls "$PRESETS_DIR"/*.preset.json 2>/dev/null | while read f; do
        node -e "
const p = JSON.parse(require('fs').readFileSync('$f','utf8'));
console.log('  ' + p.name.padEnd(14) + '— ' + p.description + ' (by ' + (p.author||'?') + ', ' + (p.created||'?').substring(0,10) + ')');
" 2>/dev/null
      done
    else
      echo -e "${YELLOW}No custom presets yet.${NC}"
      echo "  Export current config: bash preset-manager.sh export my-setup 'My optimized config'"
    fi
    echo ""
    echo "Commands:"
    echo "  bash preset-manager.sh export <name> [description]"
    echo "  bash preset-manager.sh import <file.preset.json>"
    echo "  bash preset-manager.sh list"
    ;;
    
  *)
    echo "Usage: bash preset-manager.sh <export|import|list>"
    ;;
esac
