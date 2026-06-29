#!/bin/bash
# pre-commit-check.sh — Scan staged files for secrets before commit
#
# Install as git hook:
#   cp scripts/pre-commit-check.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Or run manually: ./scripts/pre-commit-check.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

BLOCKED=0

# Patterns to detect
PATTERNS=(
    'ghp_[a-zA-Z0-9]{36}'                    # GitHub PAT (classic)
    'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}'  # GitHub PAT (fine-grained)
    'sk-[a-zA-Z0-9]{48}'                     # OpenAI API key
    'sk-proj-[a-zA-Z0-9_-]{80,}'             # OpenAI project key
    'solvr_[a-zA-Z0-9_-]{30,}'               # Solvr API key
    'am_[a-zA-Z0-9]{60,}'                    # AgentMail API key
    'moltbook_sk_[a-zA-Z0-9_-]{30,}'         # Moltbook API key
    'whsec_[a-zA-Z0-9]{30,}'                 # Webhook secret
    'AKIA[0-9A-Z]{16}'                       # AWS Access Key
    'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.' # JWT tokens
)

PATTERN_NAMES=(
    "GitHub PAT (classic)"
    "GitHub PAT (fine-grained)"
    "OpenAI API key"
    "OpenAI project key"
    "Solvr API key"
    "AgentMail API key"
    "Moltbook API key"
    "Webhook secret"
    "AWS Access Key"
    "JWT token"
)

# Get staged files
if git rev-parse --verify HEAD >/dev/null 2>&1; then
    STAGED=$(git diff --cached --name-only --diff-filter=ACM)
else
    STAGED=$(git diff --cached --name-only)
fi

if [[ -z "$STAGED" ]]; then
    echo -e "${GREEN}✓ No staged files to check${NC}"
    exit 0
fi

echo "Scanning staged files for secrets..."

for file in $STAGED; do
    if [[ ! -f "$file" ]]; then
        continue
    fi
    
    # Skip binary files (if 'file' command available)
    if command -v file >/dev/null 2>&1; then
        if file "$file" | grep -q "binary"; then
            continue
        fi
    fi
    
    for i in "${!PATTERNS[@]}"; do
        if grep -qE "${PATTERNS[$i]}" "$file" 2>/dev/null; then
            echo -e "${RED}🚨 BLOCKED: ${PATTERN_NAMES[$i]} found in $file${NC}"
            BLOCKED=1
        fi
    done
done

if [[ $BLOCKED -eq 1 ]]; then
    echo ""
    echo -e "${RED}❌ Commit blocked - secrets detected!${NC}"
    echo ""
    echo "To fix:"
    echo "  1. Remove the secret from the file"
    echo "  2. Store secrets in TOOLS.md (gitignored) or env vars"
    echo "  3. git add the fixed file"
    echo "  4. Try commit again"
    echo ""
    echo "If intentional (e.g., example patterns), use:"
    echo "  git commit --no-verify"
    exit 1
fi

echo -e "${GREEN}✓ No secrets detected in staged files${NC}"
exit 0
