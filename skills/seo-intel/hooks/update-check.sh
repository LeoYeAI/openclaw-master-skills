#!/bin/bash
# SEO Intel — Update check hook
# Called by OpenClaw's skill auto-update system
# Returns JSON with update info for the skill manager

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SEO_INTEL_DIR="$SKILL_DIR/seo-intel"
CACHE_FILE="$SEO_INTEL_DIR/.cache/update-check.json"

# Check cache freshness (24h TTL)
if [ -f "$CACHE_FILE" ]; then
  CACHE_AGE=$(( $(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0) ))
  if [ "$CACHE_AGE" -lt 86400 ]; then
    cat "$CACHE_FILE"
    exit 0
  fi
fi

# Get current version
CURRENT=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$SEO_INTEL_DIR/package.json','utf8')).version)" 2>/dev/null || echo "0.0.0")

# Check froggo.pro for latest version
FROGGO_RESPONSE=$(curl -s --max-time 5 "https://froggo.pro/api/seo-intel/version" 2>/dev/null || echo '{}')
LATEST=$(echo "$FROGGO_RESPONSE" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).version||'$CURRENT')}catch{console.log('$CURRENT')}})" 2>/dev/null || echo "$CURRENT")
SECURITY=$(echo "$FROGGO_RESPONSE" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).security||false)}catch{console.log('false')}})" 2>/dev/null || echo "false")

# Build result JSON
RESULT="{\"current\":\"$CURRENT\",\"latest\":\"$LATEST\",\"security\":$SECURITY,\"hasUpdate\":$([ "$CURRENT" != "$LATEST" ] && echo true || echo false),\"checkedAt\":$(date +%s)000}"

# Cache result
mkdir -p "$SEO_INTEL_DIR/.cache"
echo "$RESULT" > "$CACHE_FILE"

echo "$RESULT"
