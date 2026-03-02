#!/bin/bash
# collect.sh - Weekly OpenClaw Master Skills collection script
# Scans ClaWHub + GitHub for new skills, outputs candidates for review

SKILLS_DIR="$(dirname "$0")/../skills"
PENDING_DIR="$(dirname "$0")/../pending"
LOG_FILE="/tmp/openclaw-collect-$(date +%Y-%m-%d).log"

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "=== OpenClaw Master Skills Weekly Collector ==="
log "Date: $(date '+%Y-%m-%d')"

# ── 1. Scan ClaWHub for latest skills ────────────────────────────────────────
log "Scanning ClaWHub..."
if command -v clawhub &>/dev/null; then
    clawhub explore --limit 50 2>/dev/null | tee -a "$LOG_FILE" || log "ClaWHub explore failed"
else
    log "clawhub CLI not installed, skipping"
fi

# ── 2. Scan GitHub for repos tagged openclaw-skill ───────────────────────────
log "Scanning GitHub (openclaw-skill topic)..."
GH_TOKEN="${GITHUB_TOKEN:-}"
if [ -n "$GH_TOKEN" ]; then
    curl -s \
      -H "Authorization: token $GH_TOKEN" \
      "https://api.github.com/search/repositories?q=topic:openclaw-skill&sort=updated&per_page=20" \
      | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('items', []):
    print(f\"  {r['full_name']} — {r['description']} ({r['stargazers_count']} ⭐)\")
" 2>/dev/null | tee -a "$LOG_FILE"
else
    log "GITHUB_TOKEN not set, skipping GitHub scan"
fi

# ── 3. Validate existing skills ──────────────────────────────────────────────
log "Validating existing skills in collection..."
for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -f "$skill_dir/SKILL.md" ]; then
        log "  ✅ $skill_name — OK"
    else
        log "  ❌ $skill_name — missing SKILL.md!"
    fi
done

log "=== Done. Review $LOG_FILE for candidates ==="
log "Add approved skills to $SKILLS_DIR/ and update CHANGELOG.md"
