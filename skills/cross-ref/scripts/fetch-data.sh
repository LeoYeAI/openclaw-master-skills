#!/usr/bin/env bash
# fetch-data.sh — Fetch PR and issue metadata from GitHub API
#
# Usage: ./fetch-data.sh <owner/repo> <workspace_dir> [pr_count] [issue_count] [pr_state] [issue_state]
#
# Fetches PR and issue metadata, builds compact indexes, and extracts
# existing cross-references. All output goes to workspace_dir.

set -euo pipefail

REPO="${1:?Usage: fetch-data.sh <owner/repo> <workspace_dir> [pr_count] [issue_count] [pr_state] [issue_state]}"
WORKSPACE="${2:?Usage: fetch-data.sh <owner/repo> <workspace_dir> [pr_count] [issue_count] [pr_state] [issue_state]}"
PR_COUNT="${3:-1000}"
ISSUE_COUNT="${4:-1000}"
PR_STATE="${5:-all}"
ISSUE_STATE="${6:-open}"

# ─── Input validation (B2: prevent API path traversal) ───────────────────
if ! [[ "$REPO" =~ ^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$ ]]; then
  echo "Error: Invalid repo format. Expected 'owner/repo', got: $REPO" >&2
  exit 1
fi

mkdir -p "$WORKSPACE/batches"

echo "=== Cross-Ref Data Fetch ==="
echo "Repo: $REPO"
echo "Workspace: $WORKSPACE"
echo "PRs: $PR_COUNT ($PR_STATE)"
echo "Issues: $ISSUE_COUNT ($ISSUE_STATE)"
echo ""

# ─── Fetch PRs ───────────────────────────────────────────────────────────
echo "Fetching PRs..."
PR_FILE="$WORKSPACE/prs.json"
echo "[" > "$PR_FILE"
FETCHED=0
PAGE=1
FIRST=true

while [ "$FETCHED" -lt "$PR_COUNT" ]; do
  REMAINING=$((PR_COUNT - FETCHED))
  PER_PAGE=100
  if [ "$REMAINING" -lt "$PER_PAGE" ]; then
    PER_PAGE=$REMAINING
  fi

  # B4: capture stderr instead of suppressing it
  if ! RESULT=$(gh api "repos/$REPO/pulls?state=$PR_STATE&per_page=$PER_PAGE&page=$PAGE&sort=created&direction=desc" \
    --jq '[.[] | {
      number,
      title,
      body: ((.body // "")[0:500]),
      labels: [.labels[].name],
      state,
      draft,
      created_at,
      head_ref: .head.ref,
      author: .user.login
    }]' 2>"$WORKSPACE/fetch-stderr.log"); then
    echo "Error: gh api failed fetching PRs (page $PAGE)." >&2
    cat "$WORKSPACE/fetch-stderr.log" >&2
    exit 1
  fi

  COUNT=$(echo "$RESULT" | jq 'length')
  # IMPORTANT: must break here, otherwise the paste below produces corrupt JSON
  if [ "$COUNT" -eq 0 ]; then
    break
  fi

  # Append items (strip outer brackets, add commas)
  if [ "$FIRST" = true ]; then
    FIRST=false
  else
    echo "," >> "$PR_FILE"
  fi
  echo "$RESULT" | jq -c '.[]' | paste -sd ',' >> "$PR_FILE"

  FETCHED=$((FETCHED + COUNT))
  PAGE=$((PAGE + 1))
  echo "  PRs fetched: $FETCHED / $PR_COUNT (API pages: $PAGE)"
done

echo "]" >> "$PR_FILE"

# B1+B3: Use env var to pass path safely; catch specific exceptions
CROSS_REF_TARGET_FILE="$PR_FILE" python3 << 'PYEOF'
import json
import os
import sys

target_file = os.environ["CROSS_REF_TARGET_FILE"]
with open(target_file) as f:
    content = f.read()
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    print(f"Warning: JSON parse error, attempting repair: {e}", file=sys.stderr)
    content = content.replace('}\n{', '},{').replace('}\r\n{', '},{')
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e2:
        print(f"Error: JSON repair failed: {e2}", file=sys.stderr)
        sys.exit(1)
# Deduplicate by PR number
seen = set()
unique = []
for item in data:
    if item['number'] not in seen:
        seen.add(item['number'])
        unique.append(item)
data = unique
with open(target_file, 'w') as f:
    json.dump(data, f, indent=2)
print(f'PRs saved: {len(data)}')
PYEOF

# ─── Fetch Issues (excluding PRs) ────────────────────────────────────────
echo ""
echo "Fetching issues..."
ISSUE_FILE="$WORKSPACE/issues.json"
echo "[" > "$ISSUE_FILE"
FETCHED=0
PAGE=1
FIRST=true

while [ "$FETCHED" -lt "$ISSUE_COUNT" ]; do
  # C2: always fetch max page size since PRs are filtered client-side
  PER_PAGE=100

  # W4: single API call — fetch raw, then filter client-side to detect page exhaustion
  if ! RAW_RESULT=$(gh api "repos/$REPO/issues?state=$ISSUE_STATE&per_page=$PER_PAGE&page=$PAGE&sort=created&direction=desc" \
    2>"$WORKSPACE/fetch-stderr.log"); then
    echo "Error: gh api failed fetching issues (page $PAGE)." >&2
    cat "$WORKSPACE/fetch-stderr.log" >&2
    exit 1
  fi

  RAW_COUNT=$(echo "$RAW_RESULT" | jq 'length')
  if [ "$RAW_COUNT" -eq 0 ]; then
    break
  fi

  RESULT=$(echo "$RAW_RESULT" | jq '[.[] | select(.pull_request == null) | {
    number,
    title,
    body: ((.body // "")[0:500]),
    labels: [.labels[].name],
    state,
    comments,
    reactions: .reactions.total_count,
    created_at,
    author: .user.login
  }]')
  COUNT=$(echo "$RESULT" | jq 'length')

  if [ "$COUNT" -gt 0 ]; then
    if [ "$FIRST" = true ]; then
      FIRST=false
    else
      echo "," >> "$ISSUE_FILE"
    fi
    echo "$RESULT" | jq -c '.[]' | paste -sd ',' >> "$ISSUE_FILE"
    FETCHED=$((FETCHED + COUNT))
  fi

  PAGE=$((PAGE + 1))
  # C7: show both counts for transparency
  echo "  Issues fetched: $FETCHED / $ISSUE_COUNT (API pages consumed: $PAGE)"
done

echo "]" >> "$ISSUE_FILE"

# B1+B3: safe env var + specific exception handling
# Also limit to requested count (C2: we fetch full pages, may overshoot)
CROSS_REF_TARGET_FILE="$ISSUE_FILE" CROSS_REF_MAX_COUNT="$ISSUE_COUNT" python3 << 'PYEOF'
import json
import os
import sys

target_file = os.environ["CROSS_REF_TARGET_FILE"]
max_count = int(os.environ.get("CROSS_REF_MAX_COUNT", "0"))
with open(target_file) as f:
    content = f.read()
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    print(f"Warning: JSON parse error, attempting repair: {e}", file=sys.stderr)
    content = content.replace('}\n{', '},{').replace('}\r\n{', '},{')
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e2:
        print(f"Error: JSON repair failed: {e2}", file=sys.stderr)
        sys.exit(1)
# Deduplicate by issue number (pagination can return duplicates)
seen = set()
unique = []
for item in data:
    if item['number'] not in seen:
        seen.add(item['number'])
        unique.append(item)
data = unique
# Limit to requested count (C2: full pages may overshoot)
if max_count > 0 and len(data) > max_count:
    data = data[:max_count]
with open(target_file, 'w') as f:
    json.dump(data, f, indent=2)
print(f'Issues saved: {len(data)}')
PYEOF

# ─── Build Compact Indexes ─────────────────────────────────────────────
echo ""
echo "Building compact indexes..."

CROSS_REF_WORKSPACE="$WORKSPACE" python3 << 'PYEOF'
import json
import re
import os

workspace = os.environ["CROSS_REF_WORKSPACE"]

with open(f"{workspace}/prs.json") as f:
    prs = json.load(f)
with open(f"{workspace}/issues.json") as f:
    issues = json.load(f)

# ── Extract existing references ──
ref_pattern = re.compile(r'#(\d+)')
fix_pattern = re.compile(r'(?:fix(?:es)?|close[sd]?|resolve[sd]?)\s+#(\d+)', re.IGNORECASE)

pr_to_issues = {}
issue_to_prs = {}
explicit_fixes = {}

issue_nums = {i["number"] for i in issues}

for pr in prs:
    num = pr["number"]
    body = pr.get("body", "") or ""
    title = pr.get("title", "") or ""
    text = f"{title} {body}"

    # Explicit fixes
    fixes = [int(m) for m in fix_pattern.findall(text)]
    if fixes:
        explicit_fixes[str(num)] = fixes
        pr_to_issues.setdefault(str(num), []).extend(fixes)
        for issue_num in fixes:
            issue_to_prs.setdefault(str(issue_num), []).append(num)

    # General references
    refs = [int(m) for m in ref_pattern.findall(text) if int(m) != num]
    issue_refs = [r for r in refs if r in issue_nums and r not in fixes]
    if issue_refs:
        pr_to_issues.setdefault(str(num), []).extend(issue_refs)
        for ir in issue_refs:
            issue_to_prs.setdefault(str(ir), []).append(num)

existing_refs = {
    "pr_to_issues": pr_to_issues,
    "issue_to_prs": issue_to_prs,
    "explicit_fixes": explicit_fixes
}

with open(f"{workspace}/existing-refs.json", "w") as f:
    json.dump(existing_refs, f, indent=2)

# ── Build compact issue index ──
with open(f"{workspace}/issue-index.txt", "w") as f:
    for issue in issues:
        labels = ",".join(issue.get("labels", []))
        label_str = f" [{labels}]" if labels else ""
        title = issue["title"].replace('"', "'")[:80]
        refs = issue_to_prs.get(str(issue["number"]), [])
        ref_str = ",".join(f"PR#{r}" for r in refs) if refs else "none"
        author = issue.get("author", "unknown")
        reactions = issue.get("reactions", 0) or 0
        comments = issue.get("comments", 0) or 0
        engagement = f" 💬{comments}👍{reactions}" if (comments or reactions) else ""
        f.write(f'#{issue["number"]} @{author}{label_str}{engagement} "{title}" linked:{ref_str}\n')

# ── Build compact PR index ──
with open(f"{workspace}/pr-index.txt", "w") as f:
    for pr in prs:
        labels = ",".join(pr.get("labels", []))
        label_str = f" [{labels}]" if labels else ""
        title = pr["title"].replace('"', "'")[:80]
        state = pr.get("state", "unknown").upper()
        draft = " DRAFT" if pr.get("draft") else ""
        fixes = explicit_fixes.get(str(pr["number"]), [])
        fix_str = ",".join(f"#{n}" for n in fixes) if fixes else "none"
        author = pr.get("author", "unknown")
        f.write(f'PR#{pr["number"]} @{author}{label_str} {state}{draft} "{title}" fixes:{fix_str}\n')

print(f"Indexes built: {len(issues)} issues, {len(prs)} PRs")
print(f"Existing refs: {len(explicit_fixes)} PRs with explicit fixes, "
      f"{len(issue_to_prs)} issues with PR references")

PYEOF

echo ""
echo "=== Fetch complete ==="
echo "Files:"
ls -lh "$WORKSPACE"/*.json "$WORKSPACE"/*.txt 2>/dev/null
