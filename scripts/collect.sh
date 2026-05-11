#!/usr/bin/env bash
# collect.sh - Weekly OpenClaw Master Skills collector
# Source of truth: https://github.com/openclaw/skills-archive
# Strategy: clone/update archive -> diff by slug -> quality filter -> import

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
CHANGELOG="$REPO_ROOT/CHANGELOG.md"
RELEASES="$REPO_ROOT/RELEASES.md"
README="$REPO_ROOT/README.md"
LOG_FILE="/tmp/openclaw-master-skills-collect-$(date +%Y-%m-%d).log"
DRY_RUN="${1:-}"
WEEK="$(date -u +%Y-%m-%d)"
ARCHIVE_DIR="${OPENCLAW_SKILLS_ARCHIVE_DIR:-/tmp/openclaw-skills-archive}"
TMP_NEW_LIST="/tmp/openclaw-master-skills-new-slugs.txt"
TMP_IMPORT_LIST="/tmp/openclaw-master-skills-imported-slugs.txt"
TMP_RELEASE_BODY="/tmp/openclaw-master-skills-release-body.md"
GH_TOKEN="${GITHUB_TOKEN:-}"
CLAWHUB_TOKEN="${CLAWHUB_TOKEN:-}"
CLAWHUB_REGISTRY="${CLAWHUB_REGISTRY:-https://clawhub.ai}"
MAX_WEEKLY_IMPORTS="${MAX_WEEKLY_IMPORTS:-100}"
NEW_VERSION=""
NEW_COUNT="0"
TOTAL_COUNT="0"

log()  { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"; }
info() { log "INFO  $1"; }
ok()   { log "OK    $1"; }
warn() { log "WARN  $1"; }
fail() { log "FAIL  $1"; exit 1; }

require_bin() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required binary: $1"
}

setup() {
  require_bin git
  require_bin python3
  mkdir -p "$SKILLS_DIR"
  : > "$TMP_NEW_LIST"
  : > "$TMP_IMPORT_LIST"
  info "Repo root: $REPO_ROOT"
  info "Week: $WEEK | Dry-run: ${DRY_RUN:-no}"
}

refresh_archive() {
  info "Checking local archive mirror"
  [ -d "$ARCHIVE_DIR/skills" ] || fail "Local archive not found: $ARCHIVE_DIR"
  ok "Archive ready: $ARCHIVE_DIR"
}

find_new_candidates() {
  info "Finding new candidate skills"
  SKILLS_DIR="$SKILLS_DIR" ARCHIVE_DIR="$ARCHIVE_DIR" MAX_WEEKLY_IMPORTS="$MAX_WEEKLY_IMPORTS" python3 <<'PY' > "$TMP_NEW_LIST"
import os
import re

skills_dir = os.environ['SKILLS_DIR']
archive_dir = os.environ['ARCHIVE_DIR']

existing = set()
for name in os.listdir(skills_dir):
    path = os.path.join(skills_dir, name)
    if os.path.isdir(path):
        existing.add(name)

best_by_slug = {}
root = os.path.join(archive_dir, 'skills')
for publisher in sorted(os.listdir(root)):
    publisher_dir = os.path.join(root, publisher)
    if not os.path.isdir(publisher_dir):
        continue
    for slug in sorted(os.listdir(publisher_dir)):
        if slug in existing:
            continue
        skill_md = os.path.join(publisher_dir, slug, 'SKILL.md')
        if not os.path.isfile(skill_md):
            continue
        try:
            size = os.path.getsize(skill_md)
            if size < 800 or size > 30000:
                continue
            with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(5000)
            if not content.lstrip().startswith('---'):
                continue
            if not re.search(r'^name:\s*\S', content, re.M):
                continue
            desc_match = re.search(r'^description:\s*(.+?)(?=\n[a-zA-Z_]+:|\n---|\Z)', content, re.M | re.S)
            if not desc_match:
                continue
            desc = ' '.join(desc_match.group(1).strip().split())
            if len(desc) < 50 or len(desc) > 1024:
                continue
            prev = best_by_slug.get(slug)
            row = (size, publisher, slug, desc)
            if prev is None or row[0] > prev[0]:
                best_by_slug[slug] = row
        except Exception:
            continue

rows = sorted(best_by_slug.values(), key=lambda x: (-x[0], x[2]))
limit = int(os.environ.get('MAX_WEEKLY_IMPORTS', '100'))
for size, publisher, slug, desc in rows[:limit]:
    print(f"{slug}\t{publisher}\t{size}\t{desc}")
PY
  local total
  total=$(wc -l < "$TMP_NEW_LIST" | tr -d ' ')
  ok "Candidate skills found: $total"
}

import_candidates() {
  info "Importing candidates"
  REPO_ROOT="$REPO_ROOT" SKILLS_DIR="$SKILLS_DIR" ARCHIVE_DIR="$ARCHIVE_DIR" TMP_NEW_LIST="$TMP_NEW_LIST" TMP_IMPORT_LIST="$TMP_IMPORT_LIST" DRY_RUN="$DRY_RUN" python3 <<'PY'
import os
import shutil

skills_dir = os.environ['SKILLS_DIR']
archive_dir = os.environ['ARCHIVE_DIR']
tmp_new = os.environ['TMP_NEW_LIST']
tmp_import = os.environ['TMP_IMPORT_LIST']
dry_run = os.environ.get('DRY_RUN', '') == '--dry-run'

count = 0
with open(tmp_new, 'r', encoding='utf-8') as src, open(tmp_import, 'w', encoding='utf-8') as out:
    for line in src:
        slug, publisher, size, desc = line.rstrip('\n').split('\t', 3)
        source_dir = os.path.join(archive_dir, 'skills', publisher, slug)
        dest_dir = os.path.join(skills_dir, slug)
        if os.path.exists(dest_dir):
            continue
        if dry_run:
            out.write(f"{slug}\t{publisher}\t{desc}\n")
            count += 1
            continue
        shutil.copytree(source_dir, dest_dir)
        out.write(f"{slug}\t{publisher}\t{desc}\n")
        count += 1
print(count)
PY
}

update_docs() {
  NEW_COUNT=$(wc -l < "$TMP_IMPORT_LIST" | tr -d ' ')
  TOTAL_COUNT=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
  NEW_VERSION=$(python3 <<'PY'
import re
from pathlib import Path
content = Path('CHANGELOG.md').read_text(encoding='utf-8', errors='ignore')
match = re.search(r'v(\d+)\.(\d+)\.(\d+)', content)
if match:
    major, minor, patch = map(int, match.groups())
    print(f"{major}.{minor + 1}.0")
else:
    print('0.1.0')
PY
)
  export NEW_COUNT TOTAL_COUNT NEW_VERSION

  info "Updating docs for v$NEW_VERSION (+$NEW_COUNT => $TOTAL_COUNT total)"

  RELEASES="$RELEASES" WEEK="$WEEK" NEW_COUNT="$NEW_COUNT" TOTAL_COUNT="$TOTAL_COUNT" TMP_IMPORT_LIST="$TMP_IMPORT_LIST" NEW_VERSION="$NEW_VERSION" python3 <<'PY'
import os
from pathlib import Path

releases = Path(os.environ['RELEASES'])
week = os.environ['WEEK']
new_count = os.environ['NEW_COUNT']
total_count = os.environ['TOTAL_COUNT']
import_file = Path(os.environ['TMP_IMPORT_LIST'])
version = os.environ['NEW_VERSION']

items = []
if import_file.exists():
    with import_file.open('r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            slug, publisher, desc = line.rstrip('\n').split('\t', 2)
            if idx < 30:
                items.append(f"- `{slug}` — {desc[:120]}")

body = f"## v{version} — {week}\n\n### 🚀 周更：新增 {new_count} 个 Skills，总计 {total_count}\n\n来源：openclaw/skills-archive 官方镜像，按质量规则筛选（SKILL.md 800B-30KB、完整 YAML 元数据、有效 description）。\n\n#### 部分新增亮点（前 30 个）\n" + ("\n".join(items) if items else "- 本周无新增") + "\n\n---\n\n"
content = releases.read_text(encoding='utf-8', errors='ignore')
if content.startswith('# Release Notes'):
    parts = content.split('\n', 4)
    prefix = '\n'.join(parts[:4]) + '\n\n'
    rest = parts[4] if len(parts) > 4 else ''
    releases.write_text(prefix + body + rest, encoding='utf-8')
PY

  CHANGELOG="$CHANGELOG" WEEK="$WEEK" NEW_COUNT="$NEW_COUNT" TOTAL_COUNT="$TOTAL_COUNT" NEW_VERSION="$NEW_VERSION" python3 <<'PY'
import os
from pathlib import Path

changelog = Path(os.environ['CHANGELOG'])
week = os.environ['WEEK']
new_count = os.environ['NEW_COUNT']
total_count = os.environ['TOTAL_COUNT']
version = os.environ['NEW_VERSION']
entry = (
    f"## [v{version}] — {week}\n\n"
    f"### 🚀 周更：新增 {new_count} 个 Skills，总计 {total_count}\n\n"
    "来源：openclaw/skills-archive 官方镜像，按质量规则筛选。详见 RELEASES.md。\n\n"
    "---\n"
)
content = changelog.read_text(encoding='utf-8', errors='ignore')
marker = '---\n'
pos = content.find(marker)
if pos != -1:
    content = content[:pos + len(marker)] + '\n' + entry + content[pos + len(marker):]
else:
    content += '\n\n' + entry
changelog.write_text(content, encoding='utf-8')
PY

  TOTAL_COUNT="$TOTAL_COUNT" python3 <<'PY'
import os
import re
from pathlib import Path

for filename in ['README.md', 'SKILL.md', 'README.zh-CN.md', 'README.fr.md', 'README.de.md', 'README.ru.md', 'README.ja.md', 'README.it.md', 'README.es.md']:
    path = Path(filename)
    if not path.exists():
        continue
    content = path.read_text(encoding='utf-8', errors='ignore')
    content = re.sub(r'Skills-[0-9]+%2B', f"Skills-{os.environ['TOTAL_COUNT']}%2B", content)
    content = re.sub(r'collection of [0-9]+\+ best OpenClaw skills', f"collection of {os.environ['TOTAL_COUNT']}+ best OpenClaw skills", content)
    content = re.sub(r'[0-9]+\+ best OpenClaw skills', f"{os.environ['TOTAL_COUNT']}+ best OpenClaw skills", content)
    path.write_text(content, encoding='utf-8')
PY

  cat > "$TMP_RELEASE_BODY" <<EOF
## 🚀 周更：新增 ${NEW_COUNT} 个 Skills，总计 ${TOTAL_COUNT}

来源：openclaw/skills-archive 官方镜像，按质量规则筛选。

详见仓库内 RELEASES.md。
EOF
}

git_publish() {
  if [ "$DRY_RUN" = "--dry-run" ]; then
    warn "Dry-run: skipping git publish"
    return
  fi

  info "Committing changes"
  git -C "$REPO_ROOT" add -A
  if git -C "$REPO_ROOT" diff --cached --quiet; then
    warn "No changes to commit"
    return
  fi

  git -C "$REPO_ROOT" config user.name "The Doctor (MyClaw)"
  git -C "$REPO_ROOT" config user.email "doctor@myclaw.ai"
  git -C "$REPO_ROOT" commit -m "feat(v${NEW_VERSION}): weekly update ${WEEK} — ${NEW_COUNT} new skills (${TOTAL_COUNT} total)" >> "$LOG_FILE" 2>&1 || fail "git commit failed"
  ok "Commit created"

  [ -n "$GH_TOKEN" ] || fail "GITHUB_TOKEN is required for push"
  local remote_url="https://${GH_TOKEN}@github.com/LeoYeAI/openclaw-master-skills.git"
  git -C "$REPO_ROOT" push "$remote_url" main >> "$LOG_FILE" 2>&1 || fail "git push failed"
  ok "GitHub push succeeded"

  GH_TOKEN="$GH_TOKEN" NEW_VERSION="$NEW_VERSION" TMP_RELEASE_BODY="$TMP_RELEASE_BODY" python3 <<'PY'
import json
import os
import urllib.request

version = os.environ['NEW_VERSION']
body = open(os.environ['TMP_RELEASE_BODY'], 'r', encoding='utf-8').read()
payload = json.dumps({
    'tag_name': f'v{version}',
    'name': f'v{version} — Weekly Update',
    'body': body,
    'draft': False,
    'prerelease': False,
}).encode()
req = urllib.request.Request(
    'https://api.github.com/repos/LeoYeAI/openclaw-master-skills/releases',
    data=payload,
    headers={
        'Authorization': f"token {os.environ['GH_TOKEN']}",
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github+json',
    },
    method='POST',
)
try:
    with urllib.request.urlopen(req) as resp:
        print(resp.status)
except Exception as exc:
    print(f'WARN release creation failed: {exc}')
PY
}

publish_clawhub() {
  [ "$DRY_RUN" = "--dry-run" ] && { warn "Dry-run: skipping ClawHub publish"; return; }
  [ -n "$CLAWHUB_TOKEN" ] || { warn "CLAWHUB_TOKEN missing: skipping ClawHub publish"; return; }
  command -v clawhub >/dev/null 2>&1 || { warn "clawhub CLI missing: skipping ClawHub publish"; return; }

  info "Publishing lightweight package to ClawHub"
  local pkg_dir="/tmp/openclaw-master-skills-clawhub-pkg"
  rm -rf "$pkg_dir"
  mkdir -p "$pkg_dir/references"
  cp "$REPO_ROOT/SKILL.md" "$pkg_dir/"
  cp "$REPO_ROOT/README.md" "$pkg_dir/"
  [ -f "$REPO_ROOT/LICENSE" ] && cp "$REPO_ROOT/LICENSE" "$pkg_dir/"
  cat > "$pkg_dir/references/install-guide.md" <<EOF
# Install OpenClaw Master Skills

Full collection:
https://github.com/LeoYeAI/openclaw-master-skills
EOF

  clawhub logout >> "$LOG_FILE" 2>&1 || true
  clawhub login --token "$CLAWHUB_TOKEN" >> "$LOG_FILE" 2>&1 || fail "ClawHub login failed"
  clawhub publish "$pkg_dir" \
    --registry "$CLAWHUB_REGISTRY" \
    --slug openclaw-master-skills \
    --version "$NEW_VERSION" \
    --changelog "Weekly update: +${NEW_COUNT} skills, total ${TOTAL_COUNT}. Source: openclaw/skills-archive." \
    >> "$LOG_FILE" 2>&1 || fail "ClawHub publish failed"
  ok "ClawHub publish succeeded"
}

main() {
  setup
  refresh_archive
  find_new_candidates
  import_candidates >/tmp/openclaw-master-skills-import-count.txt
  local import_count
  import_count=$(tail -1 /tmp/openclaw-master-skills-import-count.txt)
  ok "Imported candidates: $import_count"

  if [ "$import_count" = "0" ]; then
    warn "No new skills found; exiting"
    exit 0
  fi

  if [ "$DRY_RUN" = "--dry-run" ]; then
    warn "Dry-run complete: skipping docs and publish steps"
    exit 0
  fi

  update_docs
  git_publish
  publish_clawhub
  ok "Done. Log: $LOG_FILE"
}

main
