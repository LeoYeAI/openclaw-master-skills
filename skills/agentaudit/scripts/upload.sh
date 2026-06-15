#!/usr/bin/env bash
# Upload a scan report to the AgentAudit
# Usage: bash scripts/upload.sh <report.json>
#   or:  cat report.json | bash scripts/upload.sh -
# Requires: AGENTAUDIT_API_KEY env var or config/credentials.json

set -euo pipefail

# Dependencies: curl, jq
for cmd in curl jq; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Required dependency '$cmd' not found. Install it first." >&2
    exit 1
  fi
done

REGISTRY_URL="https://www.agentaudit.dev"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load shared helpers
source "$SCRIPT_DIR/_load-key.sh"
source "$SCRIPT_DIR/_curl-retry.sh"
API_KEY="$(load_api_key)"

if [ -z "$API_KEY" ]; then
  echo "❌ No API key found. Set AGENTAUDIT_API_KEY or run: bash scripts/register.sh <agent-name>" >&2
  exit 1
fi

# Read report JSON
INPUT="${1:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: bash scripts/upload.sh <report.json>" >&2
  echo "   or: cat report.json | bash scripts/upload.sh -" >&2
  exit 1
fi

if [ "$INPUT" = "-" ]; then
  REPORT_JSON=$(head -c 512000)
  if [ ${#REPORT_JSON} -ge 512000 ]; then
    echo "❌ Stdin payload too large (max 512000 bytes). Aborting." >&2
    exit 1
  fi
elif [ -f "$INPUT" ]; then
  # Payload size check (max 500KB)
  FILE_SIZE=$(wc -c < "$INPUT")
  if [ "$FILE_SIZE" -gt 512000 ]; then
    echo "❌ Payload too large (${FILE_SIZE} bytes, max 512000). Aborting." >&2
    exit 1
  fi
  # JSON validation
  jq . "$INPUT" > /dev/null 2>&1 || { echo "❌ Invalid JSON in $INPUT" >&2; exit 1; }
  REPORT_JSON=$(cat "$INPUT")
else
  echo "❌ File not found: $INPUT" >&2
  exit 1
fi

# ══════════════════════════════════════════════════════════════════════════
# REQUIRED FIELDS VALIDATION
# ══════════════════════════════════════════════════════════════════════════

# Check for required source_url field
SOURCE_URL=$(echo "$REPORT_JSON" | jq -r '.source_url // empty')
if [ -z "$SOURCE_URL" ]; then
  cat >&2 <<EOF
❌ VALIDATION ERROR: Missing required field 'source_url'

The report must include a public source URL to the package repository.
Without a verifiable source, findings cannot be:
  • Peer-reviewed by other agents
  • Fixed via /fix endpoint
  • Verified for accuracy
  • Linked to specific files/lines

Add to your report JSON:
  "source_url": "https://github.com/owner/repo"

Examples of valid source URLs:
  • GitHub: https://github.com/owner/repo
  • GitLab: https://gitlab.com/owner/repo
  • npm: https://www.npmjs.com/package/name
  • PyPI: https://pypi.org/project/name/

For security reasons, the public registry only accepts reports with
public, verifiable sources.
EOF
  exit 1
fi

# Validate source_url format (basic check)
if [[ ! "$SOURCE_URL" =~ ^https?:// ]]; then
  echo "❌ VALIDATION ERROR: source_url must be a valid HTTP(S) URL" >&2
  echo "   Got: $SOURCE_URL" >&2
  exit 1
fi

echo "✓ source_url: $SOURCE_URL"

# Check remaining required fields: skill_slug/package_name, risk_score, result, findings_count
PKG_NAME=$(echo "$REPORT_JSON" | jq -r '.skill_slug // .package_name // empty')
if [ -z "$PKG_NAME" ]; then
  echo "❌ VALIDATION ERROR: Missing 'skill_slug' or 'package_name' field." >&2
  echo "   Add: \"package_name\": \"your-package-name\"" >&2
  exit 1
fi
echo "✓ package: $PKG_NAME"

RISK_SCORE=$(echo "$REPORT_JSON" | jq -r '.risk_score // empty')
if [ -z "$RISK_SCORE" ]; then
  echo "❌ VALIDATION ERROR: Missing 'risk_score' field (integer 0-100)." >&2
  exit 1
fi

RESULT=$(echo "$REPORT_JSON" | jq -r '.result // empty')
if [ -z "$RESULT" ]; then
  echo "❌ VALIDATION ERROR: Missing 'result' field (safe|caution|unsafe)." >&2
  exit 1
fi

# Auto-fix findings_count if missing (common agent mistake)
EXISTING_FC=$(echo "$REPORT_JSON" | jq -r '.findings_count // empty')
ACTUAL_FC=$(echo "$REPORT_JSON" | jq '.findings | length')
if [ -z "$EXISTING_FC" ]; then
  echo "⚠️  Missing 'findings_count' — auto-setting to $ACTUAL_FC"
  REPORT_JSON=$(echo "$REPORT_JSON" | jq --argjson fc "$ACTUAL_FC" '. + {findings_count: $fc}')
elif [ "$EXISTING_FC" != "$ACTUAL_FC" ]; then
  echo "⚠️  findings_count ($EXISTING_FC) doesn't match findings array ($ACTUAL_FC) — correcting"
  REPORT_JSON=$(echo "$REPORT_JSON" | jq --argjson fc "$ACTUAL_FC" '.findings_count = $fc')
fi

# Ensure skill_slug is set (API requires it; package_name is an alias)
HAS_SLUG=$(echo "$REPORT_JSON" | jq -r '.skill_slug // empty')
if [ -z "$HAS_SLUG" ]; then
  REPORT_JSON=$(echo "$REPORT_JSON" | jq --arg s "$PKG_NAME" '. + {skill_slug: $s}')
fi

# ══════════════════════════════════════════════════════════════════════════
# VERSION TRACKING: commit_sha and content_hash
# ══════════════════════════════════════════════════════════════════════════
# These fields are calculated by the BACKEND ENRICHMENT from the source_url.
# Do NOT auto-calculate locally — the agent's CWD is its workspace, not the
# audited package directory. Local calculation produces WRONG values:
#   - commit_sha would be the workspace repo HEAD (not the package's commit)
#   - content_hash would hash the workspace files (not the package files)
# If the agent explicitly provides these fields in the report JSON, we pass
# them through. Otherwise, backend enrichment handles it correctly.
# ══════════════════════════════════════════════════════════════════════════

EXISTING_COMMIT=$(echo "$REPORT_JSON" | jq -r '.commit_sha // empty')
EXISTING_CONTENT=$(echo "$REPORT_JSON" | jq -r '.content_hash // empty')

if [ -n "$EXISTING_COMMIT" ] || [ -n "$EXISTING_CONTENT" ]; then
  echo "ℹ️  Report contains version info (commit_sha/content_hash) — passing through"
else
  echo "ℹ️  Version info (commit_sha, content_hash) will be computed by backend enrichment"
fi

echo "Uploading report to $REGISTRY_URL/api/reports ..."

# Upload with retry for connection failures (POST is safe: backend deduplicates)
RESPONSE=$(echo "$REPORT_JSON" | curl_retry -s --max-time 60 -w "\n%{http_code}" -X POST "$REGISTRY_URL/api/reports" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d @-) || CURL_EXIT=$?

CURL_EXIT="${CURL_EXIT:-0}"
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$CURL_EXIT" -eq 28 ]; then
  echo "❌ Upload timed out (60s). The server may be processing a large repository." >&2
  echo "   The report may still have been accepted — check the registry or retry." >&2
  echo "   Tip: Provide a specific subdirectory URL (e.g., github.com/org/repo/tree/main/pkg/foo)" >&2
  exit 28
fi

# Handle rate limiting (429) — wait and retry once
if [ "$HTTP_CODE" = "429" ]; then
  echo "⚠️  Rate limited (429). Waiting 30s and retrying..." >&2
  sleep 30
  RESPONSE=$(echo "$REPORT_JSON" | curl_retry -s --max-time 60 -w "\n%{http_code}" -X POST "$REGISTRY_URL/api/reports" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d @-) || true
  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | sed '$d')
fi

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  REPORT_ID=$(echo "$BODY" | jq -r '.report_id // "unknown"')
  FINDINGS=$(echo "$BODY" | jq -r '.findings_created | length // 0')
  ENRICHMENT=$(echo "$BODY" | jq -r '.enrichment_status // "unknown"')
  echo "✅ Report uploaded successfully!"
  echo "Report ID: $REPORT_ID"
  echo "Findings created: $FINDINGS"
  if [ "$ENRICHMENT" = "pending" ]; then
    echo "ℹ️  Enrichment running in background (PURL, SWHID, version info computed async)"
  fi
  echo "$BODY" | jq .
elif [ "$HTTP_CODE" = "401" ]; then
  echo "❌ Authentication failed (HTTP 401). Your API key may be invalid or expired." >&2
  echo "   Re-register: bash scripts/register.sh <agent-name>" >&2
  echo "   Or rotate key: bash scripts/rotate-key.sh" >&2
  exit 1
else
  echo "❌ Upload failed (HTTP $HTTP_CODE):" >&2
  echo "$BODY" >&2
  exit 1
fi
