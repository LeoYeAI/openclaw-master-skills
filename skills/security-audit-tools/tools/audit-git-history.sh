#!/bin/bash
# Git History Deep Analysis Script
# Usage: ./audit-git-history.sh /path/to/repo

set -e

REPO_DIR=$1

if [ -z "$REPO_DIR" ]; then
    echo "Usage: $0 <path-to-git-repo>"
    echo "Example: $0 ./github-repo"
    exit 1
fi

cd "$REPO_DIR"

echo "=== Git History Deep Analysis ==="
echo "Repository: $(pwd)"
echo ""

# 1. Contributors analysis
echo "[1/5] Analyzing contributors..."
echo "## All Contributors"
git log --format="%an <%ae>" | sort | uniq -c | sort -rn | head -20

echo ""
echo "## Suspicious Email Domains"
SUSPICIOUS_DOMAINS="temp|disposable|guerrilla|10minutemail|throwaway"
git log --format="%ae" | grep -iE "$SUSPICIOUS_DOMAINS" || echo "✅ No suspicious email domains found"

# 2. Timeline analysis
echo ""
echo "[2/5] Analyzing timeline..."
echo "## Recent Commits (Last 50)"
git log --oneline --graph --all -50 --date=short --format="%h %ad %an %s"

echo ""
echo "## Commit Frequency by Author"
git shortlog -sn --all

# 3. Large changes detection
echo ""
echo "[3/5] Detecting large changes..."
echo "## Commits with >100 files changed"
git log --all --oneline --stat | grep -B1 -E "files? changed.*[1-9][0-9]{2,}" | head -20 || echo "✅ No large-scale changes found"

echo ""
echo "## Commits with >1000 insertions"
git log --all --oneline --stat | grep -B1 -E "insertions.*[1-9][0-9]{3,}" | head -20 || echo "✅ No massive insertions found"

# 4. Suspicious patterns
echo ""
echo "[4/5] Detecting suspicious patterns..."
echo "## Dynamic Code Execution"
git log -p --all | grep -E "^\+.*\beval\b|^\+.*new Function\(" | head -10 || echo "✅ No eval/Function() found"

echo ""
echo "## Process Creation"
git log -p --all | grep -E "^\+.*child_process|^\+.*\.exec\(|^\+.*\.spawn\(" | head -10 || echo "✅ No process creation found"

echo ""
echo "## File System Access"
git log -p --all | grep -E "^\+.*fs\.read|^\+.*fs\.write|^\+.*readFile|^\+.*writeFile" | head -10 || echo "✅ No file system access found"

echo ""
echo "## Network Requests"
git log -p --all | grep -E "^\+.*https?://" | grep -v "^\+.*#" | grep -v "^\+.*polymarket\|github\|example\.com" | head -10 || echo "✅ No suspicious network requests found"

# 5. Recent changes analysis
echo ""
echo "[5/5] Analyzing recent changes..."
LATEST_COMMIT=$(git log -1 --format="%H")
echo "## Latest Commit: $LATEST_COMMIT"
git show $LATEST_COMMIT --stat

echo ""
echo "## Commits in Last 7 Days"
RECENT_COUNT=$(git log --oneline --since="7 days ago" | wc -l)
echo "Found $RECENT_COUNT commits in the last 7 days"

if [ $RECENT_COUNT -gt 20 ]; then
    echo "⚠️  High commit frequency detected"
    git log --oneline --since="7 days ago"
fi

# Summary
echo ""
echo "=== Analysis Summary ==="
TOTAL_COMMITS=$(git rev-list --all --count)
TOTAL_AUTHORS=$(git log --format="%an" | sort -u | wc -l)
TOTAL_EMAILS=$(git log --format="%ae" | sort -u | wc -l)

echo "Total commits: $TOTAL_COMMITS"
echo "Total authors: $TOTAL_AUTHORS"
echo "Total emails: $TOTAL_EMAILS"
echo ""
echo "Risk indicators:"
echo "- Multiple suspicious domains: Check for temp emails"
echo "- Large changes: Investigate mass refactors"
echo "- High frequency: Possible automation or rushed development"
echo ""
echo "✅ Analysis complete"
