#!/usr/bin/env bash
# verify.sh — Verify local skill files against the AgentAudit
# Usage: ./scripts/verify.sh <package-name>
# Dependencies: curl, jq, sha256sum (or shasum on macOS)
set -euo pipefail

PACKAGE="${1:?Usage: verify.sh <package-name>}"
API_URL="https://www.agentaudit.dev/api/integrity"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load retry helper
source "$SCRIPT_DIR/_curl-retry.sh"

# Detect sha256 command
if command -v sha256sum &>/dev/null; then
  SHA_CMD="sha256sum"
elif command -v shasum &>/dev/null; then
  SHA_CMD="shasum -a 256"
else
  echo "❌ No sha256sum or shasum found"; exit 1
fi

# URL-encode the package name to prevent injection
ENCODED_PACKAGE=$(printf '%s' "$PACKAGE" | jq -sRr @uri)

echo "🔍 Fetching official hashes from registry..."
HTTP_RESPONSE=$(curl_retry -sL --max-time 15 -w "\n%{http_code}" "${API_URL}?package=${ENCODED_PACKAGE}")
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -lt 200 ] || [ "$HTTP_CODE" -ge 300 ]; then
  echo "❌ API request failed (HTTP ${HTTP_CODE})" >&2
  [ -n "$RESPONSE" ] && echo "   Response: $RESPONSE" >&2
  exit 1
fi

# Parse file list dynamically from API response (POSIX-compatible, no mapfile)
FILES=()
while IFS= read -r f; do
  FILES+=("$f")
done < <(echo "$RESPONSE" | jq -r '.files | keys[]')

if [ ${#FILES[@]} -eq 0 ]; then
  echo "❌ No files returned from registry for package '${PACKAGE}'" >&2
  exit 1
fi

MISMATCH=0
CHECKED=0

echo ""
echo "Package: ${PACKAGE}"
echo "Repo:    $(echo "$RESPONSE" | jq -r '.repo')"
echo "Commit:  $(echo "$RESPONSE" | jq -r '.commit' | head -c 12)"
echo "Verified: $(echo "$RESPONSE" | jq -r '.verified_at')"
echo ""

for file in "${FILES[@]}"; do
  # Sanitize: reject path traversal and absolute paths from API
  if [[ "$file" == /* ]] || [[ "$file" == *..* ]] || [[ "$file" == *$'\n'* ]] || [[ "$file" == *$'\0'* ]]; then
    echo "⚠️  ${file} — REJECTED (path traversal or absolute path)" >&2
    continue
  fi
  LOCAL_PATH="${ROOT_DIR}/${file}"
  # Resolve symlinks and verify path stays within ROOT_DIR
  REAL_PATH=$(realpath -m "$LOCAL_PATH" 2>/dev/null || echo "$LOCAL_PATH")
  if [[ "$REAL_PATH" != "${ROOT_DIR}"/* ]]; then
    echo "⚠️  ${file} — REJECTED (resolves outside project root)" >&2
    continue
  fi
  REMOTE_HASH=$(echo "$RESPONSE" | jq -r --arg f "$file" '.files[$f].sha256 // empty')

  if [ -z "$REMOTE_HASH" ] || [ "$REMOTE_HASH" = "null" ]; then
    echo "⚠️  ${file} — not tracked by registry"
    continue
  fi

  if [ ! -f "$LOCAL_PATH" ]; then
    echo "❌ ${file} — missing locally"
    MISMATCH=1
    continue
  fi

  LOCAL_HASH=$($SHA_CMD "$LOCAL_PATH" | awk '{print $1}')
  CHECKED=$((CHECKED + 1))

  if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    echo "✅ ${file}"
  else
    echo "❌ ${file} — HASH MISMATCH"
    echo "   local:  ${LOCAL_HASH}"
    echo "   remote: ${REMOTE_HASH}"
    MISMATCH=1
  fi
done

echo ""
echo "Checked: ${CHECKED} files"

# Check credentials.json permissions (both locations)
for cred_path in "${ROOT_DIR}/config/credentials.json" "${XDG_CONFIG_HOME:-$HOME/.config}/agentaudit/credentials.json"; do
  if [ -f "$cred_path" ]; then
    PERMS=$(stat -c '%a' "$cred_path" 2>/dev/null || stat -f '%Lp' "$cred_path" 2>/dev/null)
    if [ "$PERMS" != "600" ]; then
      echo "⚠️  $cred_path has permissions ${PERMS}, fixing to 600"
      chmod 600 "$cred_path"
    fi
  fi
done

if [ "$MISMATCH" -eq 0 ]; then
  echo "✅ All files verified — integrity OK"
  exit 0
else
  echo "❌ Integrity check FAILED — files differ from official repo"
  exit 1
fi
