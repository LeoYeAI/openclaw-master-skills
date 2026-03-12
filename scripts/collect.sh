#!/bin/bash
# collect.sh - Weekly OpenClaw Master Skills collector
# Sources: skills.sh (top 200) + GitHub (openclaw-skill topic) + ClaWHub CLI
# Usage: ./collect.sh [--dry-run]
# Env: GITHUB_TOKEN (required for GitHub scan)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
PENDING_DIR="$REPO_ROOT/pending"
CHANGELOG="$REPO_ROOT/CHANGELOG.md"
README="$REPO_ROOT/README.md"
LOG_FILE="/tmp/openclaw-collect-$(date +%Y-%m-%d).log"
DRY_RUN="${1:-}"
GH_TOKEN="${GITHUB_TOKEN:-}"
WEEK=$(date +%Y-%m-%d)

mkdir -p "$PENDING_DIR"

log()  { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"; }
info() { log "ℹ️  $1"; }
ok()   { log "✅ $1"; }
warn() { log "⚠️  $1"; }

# ── helpers ──────────────────────────────────────────────────────────────────

fetch_json() {
    curl -s --max-time 15 \
        ${GH_TOKEN:+-H "Authorization: token $GH_TOKEN"} \
        "$@"
}

# Clone or update a GitHub repo skill folder into pending/
fetch_github_skill() {
    local repo="$1"   # e.g. vercel-labs/agent-skills
    local skill="$2"  # e.g. vercel-react-best-practices
    local dest="$PENDING_DIR/${skill}"

    if [ -d "$dest" ]; then
        info "Already fetched: $skill"
        return 0
    fi

    local url="https://api.github.com/repos/${repo}/contents/${skill}"
    local files
    files=$(fetch_json "$url" 2>/dev/null) || { warn "Cannot fetch $repo/$skill"; return 1; }

    local has_skill_md
    has_skill_md=$(echo "$files" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    names = [f['name'] for f in data if isinstance(data, list)]
    print('yes' if 'SKILL.md' in names else 'no')
except: print('no')
" 2>/dev/null)

    if [ "$has_skill_md" = "yes" ]; then
        mkdir -p "$dest"
        # Download each file
        echo "$files" | python3 -c "
import sys, json, urllib.request, os
data = json.load(sys.stdin)
dest = sys.argv[1]
for f in data:
    if f.get('type') == 'file' and f.get('download_url'):
        out = os.path.join(dest, f['name'])
        urllib.request.urlretrieve(f['download_url'], out)
        print(f'  → {f[\"name\"]}')
" "$dest" 2>/dev/null && ok "Fetched: $skill (from $repo)" || warn "Failed to download files for $skill"
    else
        warn "No SKILL.md in $repo/$skill, skipping"
    fi
}

# ── Source 1: skills.sh top 200 ──────────────────────────────────────────────
scan_skills_sh() {
    info "=== Scanning skills.sh top 200 ==="

    local html
    html=$(curl -s --max-time 30 "https://skills.sh/" 2>/dev/null) || { warn "skills.sh unreachable"; return; }

    # Extract repo/skill pairs from the leaderboard
    echo "$html" | python3 -c "
import re, sys
html = sys.stdin.read()
# Pattern: /owner/repo/skill-name in links
matches = re.findall(r'/([a-z0-9_-]+)/([a-z0-9_.-]+)/([a-z0-9_:-]+)', html)
seen = set()
for owner, repo, skill in matches:
    key = f'{owner}/{repo}/{skill}'
    if key not in seen and owner not in ('http', 'https', 'www'):
        seen.add(key)
        print(f'{owner}/{repo}\t{skill}')
" 2>/dev/null | head -60 | while IFS=$'\t' read -r repo skill; do
        fetch_github_skill "$repo" "$skill" || true
    done
}

# ── Source 2: GitHub topic:openclaw-skill ────────────────────────────────────
scan_github_topic() {
    info "=== Scanning GitHub topic: openclaw-skill ==="

    if [ -z "$GH_TOKEN" ]; then
        warn "GITHUB_TOKEN not set, skipping GitHub scan (rate limits apply)"
        return
    fi

    local results
    results=$(fetch_json \
        "https://api.github.com/search/repositories?q=topic:openclaw-skill&sort=stars&per_page=30" \
        2>/dev/null) || { warn "GitHub search failed"; return; }

    echo "$results" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('items', []):
    print(r['full_name'], r.get('description',''), r.get('stargazers_count',0))
" 2>/dev/null | while read -r full_name desc stars; do
        info "  Found: $full_name (⭐ $stars)"
        skill_name=$(echo "$full_name" | sed 's|.*/||')
        fetch_github_skill "$full_name" "$skill_name" || true
    done

    # Also search for repos containing SKILL.md with openclaw in description
    fetch_json \
        "https://api.github.com/search/repositories?q=openclaw+skill+in:description&sort=stars&per_page=20" \
        2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('items', []):
    print(r['full_name'])
" 2>/dev/null | while read -r full_name; do
        skill_name=$(echo "$full_name" | sed 's|.*/||')
        fetch_github_skill "$full_name" "$skill_name" || true
    done
}

# ── Source 3: ClaWHub CLI ─────────────────────────────────────────────────────
scan_clawhub() {
    info "=== Scanning ClaWHub ==="

    if ! command -v clawhub &>/dev/null; then
        warn "clawhub CLI not installed (npm i -g clawhub), skipping"
        return
    fi

    clawhub explore --limit 50 2>/dev/null | while read -r line; do
        info "  ClaWHub: $line"
        slug=$(echo "$line" | awk '{print $1}')
        [ -z "$slug" ] && continue
        dest="$PENDING_DIR/$slug"
        if [ ! -d "$dest" ]; then
            clawhub install "$slug" --workdir "$PENDING_DIR" --force 2>/dev/null && ok "Installed from ClaWHub: $slug" || true
        fi
    done
}

# ── Validate pending skills ───────────────────────────────────────────────────
validate_pending() {
    info "=== Validating pending skills ==="
    local approved=0
    local rejected=0

    for skill_dir in "$PENDING_DIR"/*/; do
        [ -d "$skill_dir" ] || continue
        skill_name=$(basename "$skill_dir")

        if [ -f "$skill_dir/SKILL.md" ]; then
            # Check frontmatter has name + description
            valid=$(python3 -c "
import sys
content = open('$skill_dir/SKILL.md').read()
has_name = 'name:' in content
has_desc = 'description:' in content
print('ok' if has_name and has_desc else 'fail')
" 2>/dev/null)
            if [ "$valid" = "ok" ]; then
                if [ "$DRY_RUN" = "--dry-run" ]; then
                    ok "[DRY RUN] Would approve: $skill_name"
                else
                    cp -r "$skill_dir" "$SKILLS_DIR/$skill_name" && ok "Approved: $skill_name"
                fi
                approved=$((approved+1))
            else
                warn "Invalid SKILL.md (missing name/description): $skill_name"
                rejected=$((rejected+1))
            fi
        else
            warn "No SKILL.md found: $skill_name"
            rejected=$((rejected+1))
        fi
    done

    info "Results: ✅ $approved approved, ❌ $rejected rejected"
    echo "$approved"
}

# ── Update CHANGELOG ─────────────────────────────────────────────────────────
update_changelog() {
    local count="$1"
    info "=== Updating CHANGELOG ==="

    local new_skills=""
    for skill_dir in "$SKILLS_DIR"/*/; do
        [ -d "$skill_dir" ] || continue
        skill_name=$(basename "$skill_dir")
        desc=$(python3 -c "
import re
try:
    content = open('$skill_dir/SKILL.md').read()
    m = re.search(r'description:\s*(.+)', content)
    print(m.group(1).strip()[:80] if m else '')
except: print('')
" 2>/dev/null)
        new_skills="$new_skills\n| \`$skill_name\` | $desc |"
    done

    local entry="## [Week of $WEEK]\n\n### Skills Added This Week: $count\n\n| Skill | Description |\n|---|---|\n$new_skills\n\n---\n"

    # Prepend to changelog after header
    python3 -c "
import re, sys
entry = sys.argv[1]
with open('$CHANGELOG', 'r') as f:
    content = f.read()
# Insert after first '---'
content = content.replace('---\n', '---\n\n' + entry, 1)
with open('$CHANGELOG', 'w') as f:
    f.write(content)
" "$entry" 2>/dev/null && ok "CHANGELOG updated"
}

# ── Update README skill index ─────────────────────────────────────────────────
update_readme() {
    info "=== Updating README skill index ==="
    local rows=""
    local count=0

    for skill_dir in "$SKILLS_DIR"/*/; do
        [ -d "$skill_dir" ] || continue
        skill_name=$(basename "$skill_dir")
        desc=$(python3 -c "
import re
try:
    content = open('$skill_dir/SKILL.md').read()
    m = re.search(r'description:\s*(.+)', content)
    print(m.group(1).strip()[:70] if m else '')
except: print('')
" 2>/dev/null)
        rows="$rows\n| [\`$skill_name\`](skills/$skill_name/) | $desc | — | — | — |"
        count=$((count+1))
    done

    if python3 -c "
import re, sys
rows = sys.argv[1]
count = sys.argv[2]
with open('$README', 'r') as f:
    content = f.read()
# Always refresh the visible total, even if the detailed table layout no longer
# matches the legacy flat-index template this script knows how to rewrite.
content = re.sub(
    r'## 📦 Skill Index \(\d+ skills\)',
    f'## 📦 Skill Index ({count} skills)',
    content,
    count=1,
)
# Replace table content between | Skill | header and next ---
table_header = '| Skill | Description | Category | Source | Added |'
table_sep = '|---|---|---|---|---|'
new_table = table_header + '\n' + table_sep + rows
content, replacements = re.subn(
    r'\| Skill \| Description \| Category \| Source \| Added \|.*?(?=\n---|\n##)',
    new_table,
    content, flags=re.DOTALL
)
with open('$README', 'w') as f:
    f.write(content)
sys.exit(0 if replacements > 0 else 2)
" "$rows" "$count" 2>/dev/null; then
        ok "README updated ($count skills)"
    else
        warn "README skill count refreshed, but the legacy flat-table layout was not found; index rows were left unchanged"
    fi
}

# ── Git commit & push ─────────────────────────────────────────────────────────
git_push() {
    local count="$1"
    info "=== Committing and pushing ==="

    cd "$REPO_ROOT"
    git add -A
    if git diff --cached --quiet; then
        info "No changes to commit"
        return
    fi

    git commit -m "chore: weekly update $WEEK — $count new skills collected"

    if [ -n "$GH_TOKEN" ]; then
        remote_url=$(git remote get-url origin 2>/dev/null | sed "s|https://|https://$GH_TOKEN@|")
        git push "$remote_url" main 2>/dev/null && ok "Pushed to GitHub" || warn "Push failed"
    else
        warn "GITHUB_TOKEN not set, skipping push"
    fi
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
    log "======================================"
    log "OpenClaw Master Skills Weekly Collector"
    log "Week: $WEEK | Dry-run: ${DRY_RUN:-no}"
    log "======================================"

    scan_skills_sh
    scan_github_topic
    scan_clawhub

    count=$(validate_pending)

    if [ "$DRY_RUN" != "--dry-run" ]; then
        update_changelog "$count"
        update_readme
        git_push "$count"
        # Clear pending after approval
        rm -rf "$PENDING_DIR"/*
    fi

    log "======================================"
    log "Done! Log: $LOG_FILE"
    log "======================================"
}

main
