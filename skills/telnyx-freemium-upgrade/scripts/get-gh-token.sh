#!/usr/bin/env bash
# get-gh-token.sh — Extract the current GitHub OAuth token via gh CLI.
# Validates the token is non-empty before outputting.
#
# Usage: bash get-gh-token.sh
# Output: Raw GitHub token on stdout (single line)

set -euo pipefail

# Check if gh is installed
if ! command -v gh &>/dev/null; then
    echo "ERROR: GitHub CLI (gh) is not installed. Install: https://cli.github.com" >&2
    exit 1
fi

# Check if gh is authenticated
if ! gh auth status &>/dev/null 2>&1; then
    echo "ERROR: GitHub CLI is not authenticated. Run: gh auth login --web" >&2
    exit 1
fi

# Get the token
TOKEN=$(gh auth token 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "ERROR: Failed to retrieve GitHub token. Run: gh auth login --web" >&2
    exit 1
fi

echo "$TOKEN"
