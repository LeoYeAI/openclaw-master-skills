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
# --publish-only ships an already-built local commit: skip archive/import/docs and
# go straight to push + Release + ClawHub. v0.22.0 was committed locally on
# 2026-07-30 and blocked at push by a dead PAT, and there was no way to resume
# the last three steps without re-importing and creating a second commit.
PUBLISH_ONLY="no"
if [ "$DRY_RUN" = "--publish-only" ]; then
  PUBLISH_ONLY="yes"
  DRY_RUN=""
fi
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
import hashlib

skills_dir = os.environ['SKILLS_DIR']
archive_dir = os.environ['ARCHIVE_DIR']

existing = set()
for name in os.listdir(skills_dir):
    path = os.path.join(skills_dir, name)
    if os.path.isdir(path):
        existing.add(name)


def normalize_desc(raw):
    """Frontmatter description, cleaned of YAML scalar artifacts.

    Block indicators (>, |) and wrapping quotes leak straight into RELEASES.md
    otherwise — every release up to v0.22.0 shipped lines like
    '- `slug` — > View, add, ...'.
    """
    desc = ' '.join(raw.strip().split())
    desc = re.sub(r'^[>|][+\-]?\s*', '', desc)
    if len(desc) >= 2 and desc[0] == desc[-1] and desc[0] in '"\'':
        desc = desc[1:-1].strip()
    else:
        desc = desc.lstrip('"\'').strip()
    return desc


def read_desc(skill_md):
    try:
        with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000)
    except OSError:
        return None
    if not content.lstrip().startswith('---'):
        return None
    match = re.search(r'^description:\s*(.+?)(?=\n[a-zA-Z_]+:|\n---|\Z)',
                      content, re.M | re.S)
    return normalize_desc(match.group(1)) if match else None


def body_hash(skill_md):
    """Fingerprint of the instructions, ignoring the frontmatter.

    Description keying alone is not enough: publishers reword the description
    while shipping a byte-identical body (ad-ready / product-to-ads,
    ding-skills / dingtalk-skills), so 56 redundant copies slipped past the
    desc-keyed dedup and into the collection.
    """
    try:
        with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except OSError:
        return None
    body = re.sub(r'^---\s*\n.*?\n---\s*\n', '',
                  content.replace('\r\n', '\n'), flags=re.S).strip()
    # Short bodies are stubs; hashing them would collapse unrelated skills.
    if len(body) < 200:
        return None
    return hashlib.sha1(' '.join(body.split()).encode()).hexdigest()


# Descriptions already in the collection. Candidate dedup has to compare against
# these, not just against other candidates: once a duplicate is removed by hand,
# its canonical sibling is installed and drops out of the candidate set, so the
# duplicate looks brand new and gets re-imported next run. That is exactly how
# the v0.22.0 cleanup regressed in end-to-end testing.
existing_descs = set()
existing_bodies = set()
for name in existing:
    for fn in ('SKILL.md', 'skill.md'):
        path = os.path.join(skills_dir, name, fn)
        if not os.path.isfile(path):
            continue
        desc = read_desc(path)
        if desc:
            existing_descs.add(desc)
        h = body_hash(path)
        if h:
            existing_bodies.add(h)
        break

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
            desc = normalize_desc(desc_match.group(1))
            if len(desc) < 50 or len(desc) > 1024:
                continue
            # Already in the collection under another slug.
            if desc in existing_descs:
                continue
            bh = body_hash(skill_md)
            if bh and bh in existing_bodies:
                continue
            prev = best_by_slug.get(slug)
            row = (size, publisher, slug, desc, bh)
            if prev is None or row[0] > prev[0]:
                best_by_slug[slug] = row
        except Exception:
            continue

# Reject throwaway uploads. v0.22.0 imported agent-autopilot-bak and
# qveris-test alongside their canonical siblings before this filter existed.
JUNK_SUFFIX = re.compile(r'-(bak|backup|old|copy|test|tmp|temp|deprecated)$')
best_by_slug = {s: r for s, r in best_by_slug.items() if not JUNK_SUFFIX.search(s)}

# Collapse re-uploads of the same skill. Publishers ship the same SKILL.md under
# several slugs (lovetago / lovetago-skill / lovetago-bot-tinder), which used to
# consume import budget and pad the release notes with repeats. Keep one per
# identical description, preferring the shortest slug as the canonical name.
# Two keys, because a re-upload can diverge in either field. Keying on
# (publisher, desc) alone missed both directions: the same body reworded under
# one publisher, and the same body republished verbatim by a different publisher
# (713 archive groups / 1335 redundant candidates). Body hash is deliberately
# publisher-independent.
key_winner = {}


def row_keys(row):
    _size, publisher, _slug, desc, bh = row
    keys = [('desc', publisher, desc)]
    if bh:
        keys.append(('body', bh))
    return keys


for row in best_by_slug.values():
    slug = row[2]
    for key in row_keys(row):
        cur = key_winner.get(key)
        if cur is None or (len(slug), slug) < (len(cur[2]), cur[2]):
            key_winner[key] = row
# A row can win on one key and lose on another, so keep only rows that win every
# key they participate in. No two survivors share a description or a body.
best_by_slug = {
    row[2]: row
    for row in best_by_slug.values()
    if all(key_winner[k][2] == row[2] for k in row_keys(row))
}

rows = sorted(best_by_slug.values(), key=lambda x: (-x[0], x[2]))
limit = int(os.environ.get('MAX_WEEKLY_IMPORTS', '100'))
for size, publisher, slug, desc, _bh in rows[:limit]:
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
import re, subprocess
from pathlib import Path

versions = []
# Source of truth: existing git tags (vX.Y.Z)
try:
    out = subprocess.check_output(['git', 'tag'], text=True)
    for line in out.splitlines():
        m = re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)', line.strip())
        if m:
            versions.append(tuple(map(int, m.groups())))
except Exception:
    pass
# Fallback/cross-check: all versions mentioned in CHANGELOG
try:
    content = Path('CHANGELOG.md').read_text(encoding='utf-8', errors='ignore')
    for m in re.finditer(r'v(\d+)\.(\d+)\.(\d+)', content):
        versions.append(tuple(map(int, m.groups())))
except Exception:
    pass
if versions:
    major, minor, patch = max(versions)
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
    total = os.environ['TOTAL_COUNT']
    # Badge URL count
    content = re.sub(r'Skills-[0-9]+%2B', f"Skills-{total}%2B", content)
    # Badge alt text (was never updated before, drifted to stale values).
    # The translated READMEs localize the noun ("2503+ Navyki", "2503+ スキル"),
    # so match any trailing label rather than a literal "Skills".
    content = re.sub(r'alt="[0-9]+\+ ([^"]*)"', lambda m: f'alt="{total}+ {m.group(1)}"', content)
    # Prose counts. Match "best skills" too, not just "best OpenClaw skills":
    # SKILL.md's body uses the shorter phrasing and silently went stale at
    # v0.13.0 (560 -> 11211), shipping a wrong number to ClawHub for months.
    content = re.sub(r'[0-9]+\+ best (OpenClaw )?skills', lambda m: f"{total}+ best {m.group(1) or ''}skills", content)
    path.write_text(content, encoding='utf-8')
PY

  # skill_index.md used to be hand-maintained and rotted badly (last written at
  # v0.7.0: 560 rows for 2400+ skills, 540 of them showing "name: <slug>").
  # Regenerate it every run so it cannot drift again.
  info "Rebuilding skill_index.md"
  python3 "$REPO_ROOT/scripts/build-index.py" | tee -a "$LOG_FILE"

  # The curated README tables are hand-maintained, so nothing caught 27 rows
  # whose description was a bare YAML block indicator, an empty clawsec cell, or
  # a row broken into 4 columns by unescaped pipes. Fail the run instead of
  # shipping that to GitHub and ClawHub.
  info "Validating README skill tables"
  python3 "$REPO_ROOT/scripts/check-readme-table.py" | tee -a "$LOG_FILE" || fail "README table validation failed"

  # The regex checks above only prove a description: line exists; they pass on
  # frontmatter no YAML loader can read. That is how 70 skills shipped with an
  # unquoted scalar containing ": ", 11 with structural damage and 2 wrapped in a
  # raw HTTP multipart envelope.
  info "Validating skill frontmatter"
  python3 "$REPO_ROOT/scripts/check-frontmatter.py" | tail -20 | tee -a "$LOG_FILE" || fail "frontmatter validation failed"

  # Nothing checked the version history, so eight consecutive weekly entries
  # shipped labelled v0.13.0 while the tag for each of those dates carried a
  # distinct version. Duplicates also make publish_release ambiguous: it takes
  # the first version match in CHANGELOG.md.
  info "Validating version history"
  python3 "$REPO_ROOT/scripts/check-changelog.py" | tee -a "$LOG_FILE" || fail "version history validation failed"

  # Report skills already installed under several directory names. collect.sh
  # only dedups incoming candidates, so 83 groups / 174 redundant directories
  # predate that filter. Reporting only: collapsing them deletes directories and
  # changes published slugs, which is Leo's call, not the weekly run's.
  #
  # grep the two headline lines rather than head -n: the report now ends with a
  # name-collision summary, and a positional filter would drop it.
  info "Checking for duplicate installed skills"
  python3 "$REPO_ROOT/scripts/find-duplicates.py" 2>&1 \
    | grep -E '^(scanned|duplicate groups|name collisions)' \
    | tee -a "$LOG_FILE" || true

  # Nothing ever looked at file contents for credentials, so cann-review shipped
  # a live GitCode token hardcoded in five scripts while its own README told
  # users to export GITCODE_API_TOKEN. Report-only for the same reason as the
  # duplicate check: rewriting an upstream author's code on a schedule is Leo's
  # call. New occurrences should get triaged before publish.
  info "Scanning for hardcoded credentials"
  python3 "$REPO_ROOT/scripts/check-secrets.py" 2>&1 \
    | grep -E '^(scanned|hardcoded credentials)' \
    | tee -a "$LOG_FILE" || true

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

  if [ "$PUBLISH_ONLY" = "yes" ]; then
    info "Publish-only: reusing existing local commit(s)"
    git -C "$REPO_ROOT" diff --quiet || fail "working tree is dirty; commit or stash before --publish-only"
  else
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
  fi

  [ -n "$GH_TOKEN" ] || fail "GITHUB_TOKEN is required for push"
  local remote_url="https://${GH_TOKEN}@github.com/LeoYeAI/openclaw-master-skills.git"
  git -C "$REPO_ROOT" push "$remote_url" main >> "$LOG_FILE" 2>&1 || fail "git push failed"
  ok "GitHub push succeeded"

  # Create and push the tag explicitly. The Releases API would create it
  # implicitly, but then no local tag exists and the --publish-only
  # "already tagged" guard can never trip, so a repeat run would try to
  # republish an already-shipped version.
  if [ -z "$(git -C "$REPO_ROOT" tag -l "v$NEW_VERSION")" ]; then
    git -C "$REPO_ROOT" tag -a "v$NEW_VERSION" -m "v${NEW_VERSION} — weekly update ${WEEK}" >> "$LOG_FILE" 2>&1 || fail "git tag failed"
  fi
  git -C "$REPO_ROOT" push "$remote_url" "refs/tags/v$NEW_VERSION" >> "$LOG_FILE" 2>&1 || fail "tag push failed"
  ok "Tag v$NEW_VERSION pushed"

  GH_TOKEN="$GH_TOKEN" NEW_VERSION="$NEW_VERSION" TMP_RELEASE_BODY="$TMP_RELEASE_BODY" python3 <<'PY' || fail "GitHub Release creation failed"
import json
import os
import sys
import urllib.error
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
        print(f'release created: HTTP {resp.status}')
except urllib.error.HTTPError as exc:
    detail = exc.read().decode('utf-8', 'replace')
    # A release for this tag already existing is not a failure: the tag and
    # commit are already public, so let the run continue to ClawHub.
    if exc.code == 422 and 'already_exists' in detail:
        print('release already exists; continuing')
    else:
        print(f'release creation failed: HTTP {exc.code} {detail}', file=sys.stderr)
        sys.exit(1)
except Exception as exc:
    print(f'release creation failed: {exc}', file=sys.stderr)
    sys.exit(1)
PY
  ok "GitHub Release ready"
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

# Recover version/count values from the already-built commit instead of the
# import lists, which are empty on a --publish-only run.
load_built_release() {
  info "Publish-only: reading release metadata from CHANGELOG.md"
  TOTAL_COUNT=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
  NEW_VERSION=$(python3 - "$CHANGELOG" <<'PY'
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='ignore')
m = re.search(r'v(\d+\.\d+\.\d+)', text)
print(m.group(1) if m else '')
PY
)
  [ -n "$NEW_VERSION" ] || fail "could not determine version from CHANGELOG.md"
  # Read the count from the release heading, not by counting bullet lines:
  # RELEASES.md only lists the top ~30 imports as highlights, so counting
  # bullets reported 28 instead of 94.
  NEW_COUNT=$(python3 - "$CHANGELOG" "$NEW_VERSION" <<'PY'
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='ignore')
version = re.escape(sys.argv[2])
m = re.search(r'##\s*\[?v' + version + r'\]?.*?新增\s*(\d+)\s*个 Skills', text, re.S)
print(m.group(1) if m else '')
PY
)
  [ -n "$NEW_COUNT" ] || fail "could not determine new-skill count for v$NEW_VERSION from CHANGELOG.md"

  # Date the tag from the release itself, not from today. A publish-only run
  # usually happens days after the commit was built (v0.22.0 was built
  # 2026-07-30 and published later), so $WEEK would stamp the wrong date.
  local release_date
  release_date=$(python3 - "$CHANGELOG" "$NEW_VERSION" <<'PY'
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='ignore')
m = re.search(r'##\s*\[?v' + re.escape(sys.argv[2]) + r'\]?\s*[—-]\s*(\d{4}-\d{2}-\d{2})', text)
print(m.group(1) if m else '')
PY
)
  [ -n "$release_date" ] && WEEK="$release_date"
  export NEW_COUNT TOTAL_COUNT NEW_VERSION

  # Idempotency is keyed on the published GitHub Release, not the local tag.
  # Keying it on the tag created a dead end: if the Release call fails after the
  # tag is pushed, every retry refuses as "already tagged" while nothing is
  # actually published. git_publish tolerates a pre-existing tag and an
  # already_exists Release, so resuming mid-flight is safe.
  local release_state
  release_state=$(GH_TOKEN="$GH_TOKEN" NEW_VERSION="$NEW_VERSION" python3 <<'PY'
import os
import urllib.error
import urllib.request

token = os.environ.get('GH_TOKEN', '')
version = os.environ['NEW_VERSION']
url = ('https://api.github.com/repos/LeoYeAI/openclaw-master-skills/'
       f'releases/tags/v{version}')


def probe(auth):
    headers = {'Accept': 'application/vnd.github+json'}
    if auth and token:
        headers['Authorization'] = f'token {token}'
    try:
        urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        return 'published'
    except urllib.error.HTTPError as exc:
        return 'absent' if exc.code == 404 else f'unknown:{exc.code}'
    except Exception:
        return 'unknown:network'


# The repo is public, so read the release list anonymously. Sending a dead PAT
# turns a definitive 200/404 into an inconclusive 401 and the guard would let a
# duplicate publish through. Retry with the token only if anonymous fails, in
# case the repo is ever made private.
state = probe(auth=False)
if state.startswith('unknown') and token:
    state = probe(auth=True)
print(state)
PY
)
  case "$release_state" in
    published) fail "v$NEW_VERSION is already released on GitHub; nothing to publish" ;;
    absent)    : ;;
    *)         warn "could not confirm release state ($release_state); proceeding" ;;
  esac
  if [ -n "$(git -C "$REPO_ROOT" tag -l "v$NEW_VERSION")" ]; then
    warn "tag v$NEW_VERSION exists locally but no release found; resuming publish"
  fi

  # update_docs normally writes this; it is skipped on a publish-only run.
  cat > "$TMP_RELEASE_BODY" <<EOF
## 🚀 周更：新增 ${NEW_COUNT} 个 Skills，总计 ${TOTAL_COUNT}

来源：openclaw/skills-archive 官方镜像，按质量规则筛选。

详见仓库内 RELEASES.md。
EOF

  ok "Publishing v$NEW_VERSION (+$NEW_COUNT => $TOTAL_COUNT total)"
}

main() {
  setup

  if [ "$PUBLISH_ONLY" = "yes" ]; then
    load_built_release
    git_publish
    publish_clawhub
    ok "Done. Log: $LOG_FILE"
    return
  fi

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
