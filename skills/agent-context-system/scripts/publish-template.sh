#!/bin/bash
# publish-template.sh
# Push to GitHub and mark as a template repo. Run once.

set -euo pipefail

REPO_NAME="agent-context-system"

echo "This will create a private GitHub repo and mark it as a template."
echo ""
read -rp "GitHub username: " GH_USER
if [[ -z "$GH_USER" ]]; then
    echo "Error: Username cannot be empty."
    exit 1
fi
if [[ ! "$GH_USER" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$ ]]; then
    echo "Error: Invalid GitHub username format."
    exit 1
fi
echo ""

[ ! -d ".git" ] && git init
sensitive_files=$(find . -maxdepth 2 \( -name ".env*" -o -name "*.pem" -o -name "*.key" -o -name "*.secret" -o -name "id_rsa*" \) 2>/dev/null || true)
if [ -n "$sensitive_files" ]; then
    echo "⚠️  Potentially sensitive files detected:"
    echo "$sensitive_files"
    echo ""
    read -rp "Continue anyway? (y/N) " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || exit 1
fi
git add -A
git commit -m "Initial commit: agent context system template" 2>/dev/null || true

gh repo create "$GH_USER/$REPO_NAME" \
    --private \
    --source=. \
    --remote=origin \
    --description "Template: persistent local-only memory for AI coding agents" \
    --push

gh api \
    --method PATCH \
    -H "Accept: application/vnd.github+json" \
    "/repos/$GH_USER/$REPO_NAME" \
    -f is_template=true

echo ""
echo "Done: https://github.com/$GH_USER/$REPO_NAME"
echo ""
echo "Create a new project from this template:"
echo "  gh repo create my-project --template $GH_USER/$REPO_NAME --private"
echo "  cd my-project && ./scripts/init-agent-context.sh"
