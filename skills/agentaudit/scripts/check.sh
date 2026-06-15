#!/usr/bin/env bash
# check.sh — Manual package check against AgentAudit registry
# Usage: bash check.sh <package-name>
#        bash check.sh --hash <sha256|git-sha|purl|swhid>
# Returns trust score and findings without installing anything.
set -euo pipefail

API_URL="https://www.agentaudit.dev"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for cmd in jq curl; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Required: ${cmd}" >&2; exit 1
  fi
done

if [[ $# -lt 1 ]]; then
  echo "Usage: check.sh <package-name>" >&2
  echo "       check.sh --hash|-H <sha256|git-sha|purl|swhid>" >&2
  exit 1
fi

# Load shared helpers
source "$SCRIPT_DIR/_load-key.sh"
source "$SCRIPT_DIR/_curl-retry.sh"
API_KEY="$(load_api_key)"

# ── Hash Lookup Mode ──
if [[ "$1" == "--hash" || "$1" == "-H" ]]; then
  if [[ $# -lt 2 ]]; then
    echo "Usage: check.sh --hash <hash-value>" >&2; exit 1
  fi
  HASH="$2"
  HASH_ENCODED="$(printf '%s' "$HASH" | python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read(), safe=''))" 2>/dev/null \
    || printf '%s' "$HASH" | jq -sRr @uri 2>/dev/null \
    || echo "$HASH")"

  echo "🔍 Looking up hash '${HASH}' against ${API_URL}..."
  echo ""

  LOOKUP_ARGS=(-sL -f --max-time 10 "${API_URL}/api/lookup?hash=${HASH_ENCODED}")
  [[ -n "$API_KEY" ]] && LOOKUP_ARGS+=(-H "Authorization: Bearer ${API_KEY}")

  LOOKUP_RESPONSE="$(curl_retry "${LOOKUP_ARGS[@]}")" || {
    echo "⚠️  Registry unreachable. Cannot look up hash."
    exit 2
  }

  DETECTED_TYPE=$(echo "$LOOKUP_RESPONSE" | jq -r '.detected_type // "unknown"')
  TOTAL=$(echo "$LOOKUP_RESPONSE" | jq '.total_matches // 0')
  REPORT_COUNT=$(echo "$LOOKUP_RESPONSE" | jq '.reports | length')
  FINDING_COUNT=$(echo "$LOOKUP_RESPONSE" | jq '.findings | length')

  echo "   Type: ${DETECTED_TYPE}"
  echo "   Matches: ${TOTAL} (${REPORT_COUNT} reports, ${FINDING_COUNT} findings)"
  echo ""

  if [[ "$REPORT_COUNT" -gt 0 ]]; then
    echo "   📋 Reports:"
    echo "$LOOKUP_RESPONSE" | jq -r '.reports[] | "   • \(.skill_slug) — score \(.risk_score), matched \(.matched_field)"'
    echo ""
  fi

  if [[ "$FINDING_COUNT" -gt 0 ]]; then
    echo "   🔎 Findings:"
    echo "$LOOKUP_RESPONSE" | jq -r '.findings[] | "   • [\(.severity | ascii_upcase)] \(.asf_id): \(.title) (matched \(.matched_field))"'
    echo ""
  fi

  if [[ "$TOTAL" -eq 0 ]]; then
    echo "📭 No audit data matches this hash."
  fi
  exit 0
fi

# ── Package Name Mode ──
PKG="$1"
PKG_ENCODED="$(printf '%s' "$PKG" | python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read(), safe=''))" 2>/dev/null \
  || printf '%s' "$PKG" | jq -sRr @uri 2>/dev/null \
  || echo "$PKG")"

echo "🔍 Checking '$PKG' against ${API_URL}..."
echo ""

# Fetch the trust score from /api/check (authoritative, accounts for by_design exclusions)
CHECK_ARGS=(-sL -f --max-time 10 "${API_URL}/api/check?package=${PKG_ENCODED}")
[[ -n "$API_KEY" ]] && CHECK_ARGS+=(-H "Authorization: Bearer ${API_KEY}")

CHECK_RESPONSE="$(curl_retry "${CHECK_ARGS[@]}")" || {
  echo "⚠️  Registry unreachable. Cannot verify package."
  echo "    Try again later or run a local LLM audit on the source."
  exit 2
}

# Check if the package has audit data
EXISTS=$(echo "$CHECK_RESPONSE" | jq -r '.exists // false')
if [[ "$EXISTS" != "true" ]]; then
  echo "📭 No audit data found for '$PKG'."
  echo "   This package has not been scanned yet."
  echo "   Consider submitting an audit: bash scripts/upload.sh <report.json>"
  exit 0
fi

# Use the authoritative trust_score from the API
API_SCORE=$(echo "$CHECK_RESPONSE" | jq '.trust_score // empty')

# Fetch detailed findings for severity breakdown and top findings display
FIND_ARGS=(-sL -f --max-time 10 "${API_URL}/api/findings?package=${PKG_ENCODED}")
[[ -n "$API_KEY" ]] && FIND_ARGS+=(-H "Authorization: Bearer ${API_KEY}")

RESPONSE="$(curl_retry "${FIND_ARGS[@]}")" || RESPONSE='{"findings":[],"total":0}'

# Use API trust_score (authoritative). Fallback to local calculation only if
# /api/check returned exists:true but no trust_score (unexpected edge case).
if [[ -n "$API_SCORE" ]]; then
  SCORE="$API_SCORE"
else
  echo "⚠️  API did not return trust_score — using local approximation" >&2
  SCORE=$(echo "$RESPONSE" | jq '
    [.findings // [] | .[] | select(.by_design != true and .by_design != "true") |
      .component_type as $ct |
      (if .severity == "critical" then -25
      elif .severity == "high" then -15
      elif .severity == "medium" then -8
      elif .severity == "low" then -3
      else 0 end) |
      if $ct == "hook" or $ct == "mcp" or $ct == "settings" or $ct == "plugin" then . * 12 / 10
      else . end
    ] | [100 + add, 0] | max | [., 100] | min | round
  ')
fi

# Severity counts (from /api/check response if available, else from findings)
CRIT=$(echo "$CHECK_RESPONSE" | jq '.critical // 0')
HIGH=$(echo "$CHECK_RESPONSE" | jq '.high // 0')
MED=$(echo "$CHECK_RESPONSE" | jq '.medium // 0')
LOW=$(echo "$CHECK_RESPONSE" | jq '.low // 0')
BYDESIGN=$(echo "$RESPONSE" | jq '[.findings[]|select(.by_design==true or .by_design=="true")]|length')

# Decision
if [[ "$SCORE" -ge 70 ]]; then
  ICON="✅"; VERDICT="PASS — Safe to install"
elif [[ "$SCORE" -ge 40 ]]; then
  ICON="⚠️"; VERDICT="CAUTION — Review findings before installing"
else
  ICON="🔴"; VERDICT="UNSAFE — Do not install without careful review"
fi

echo "${ICON} ${PKG} — Score: ${SCORE}/100"
echo "   ${VERDICT}"
echo ""
echo "   Findings: ${CRIT} critical | ${HIGH} high | ${MED} medium | ${LOW} low | ${BYDESIGN} by-design"
echo ""

# Show top findings
if [[ "$SCORE" -lt 70 ]]; then
  echo "   Top findings:"
  echo "$RESPONSE" | jq -r '.findings[] | select(.by_design != true and .by_design != "true") | "   • [\(.severity | ascii_upcase)] \(.title) (\(.file // "unknown"))"' | head -5
fi
