#!/usr/bin/env bash
set -euo pipefail

# vault-stats.sh — Generate Knowledge Vault statistics
# Reads data/vault-entries.json and outputs summary stats.

# --- Workspace Root Detection ---
# Prefer explicit WORKSPACE_ROOT. If unset, walk upward for workspace markers,
# but only accept roots that also look like a vault workspace.
is_vault_workspace_root() {
  local root="$1"
  [ -d "$root" ] || return 1
  if [ -f "$root/data/vault-entries.json" ] || [ -f "$root/config/vault-config.json" ]; then
    return 0
  fi
  return 1
}

find_workspace_root() {
  local dir="$PWD"
  while [ "$dir" != "/" ]; do
    if { [ -f "$dir/AGENTS.md" ] || [ -f "$dir/SOUL.md" ]; } && is_vault_workspace_root "$dir"; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  echo "ERROR: Could not find a valid vault workspace root." >&2
  echo "Set WORKSPACE_ROOT explicitly or run from a workspace containing AGENTS.md/SOUL.md and vault files." >&2
  exit 1
}

resolve_workspace_root() {
  if [ -n "${WORKSPACE_ROOT:-}" ]; then
    if [ ! -d "$WORKSPACE_ROOT" ]; then
      echo "ERROR: WORKSPACE_ROOT does not exist or is not a directory: $WORKSPACE_ROOT" >&2
      exit 1
    fi
    local resolved
    resolved="$(cd "$WORKSPACE_ROOT" && pwd)"
    if ! is_vault_workspace_root "$resolved"; then
      echo "ERROR: WORKSPACE_ROOT is not a valid vault workspace: $resolved" >&2
      echo "Expected data/vault-entries.json or config/vault-config.json." >&2
      exit 1
    fi
    echo "$resolved"
    return 0
  fi

  find_workspace_root
}

WORKSPACE_ROOT="$(resolve_workspace_root)"
VAULT_FILE="$WORKSPACE_ROOT/data/vault-entries.json"

# --- Validate vault file exists ---
if [ ! -f "$VAULT_FILE" ]; then
  echo "ERROR: Vault database not found at $VAULT_FILE" >&2
  echo "Have you run the Knowledge Vault setup? See SETUP-PROMPT.md." >&2
  exit 1
fi

# --- Check for jq ---
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required but not installed." >&2
  echo "Install it: brew install jq (macOS) or apt install jq (Linux)" >&2
  exit 1
fi

echo "=== 📊 Knowledge Vault Stats ==="
echo ""

# Total entries
TOTAL=$(jq 'length' "$VAULT_FILE")
echo "📚 Total entries: $TOTAL"

if [ "$TOTAL" -eq 0 ]; then
  echo ""
  echo "Your vault is empty. Send a URL to your agent to get started!"
  exit 0
fi

echo ""

# Count by content type
echo "By type:"
for TYPE in article video pdf tweet reddit podcast github; do
  COUNT=$(jq "[.[] | select(.content_type == \"$TYPE\")] | length" "$VAULT_FILE")
  if [ "$COUNT" -gt 0 ]; then
    case "$TYPE" in
      article)  EMOJI="📄" ;;
      video)    EMOJI="🎬" ;;
      pdf)      EMOJI="📑" ;;
      tweet)    EMOJI="🐦" ;;
      reddit)   EMOJI="💬" ;;
      podcast)  EMOJI="🎙️" ;;
      github)   EMOJI="💻" ;;
    esac
    echo "  $EMOJI $TYPE: $COUNT"
  fi
done

echo ""

# Count by status
DIGESTED=$(jq '[.[] | select(.status == "digested")] | length' "$VAULT_FILE")
QUEUED=$(jq '[.[] | select(.status == "queued")] | length' "$VAULT_FILE")
FAILED=$(jq '[.[] | select(.status == "failed")] | length' "$VAULT_FILE")

echo "By status:"
echo "  ✅ Digested: $DIGESTED"
[ "$QUEUED" -gt 0 ] && echo "  ⏳ Queued: $QUEUED"
[ "$FAILED" -gt 0 ] && echo "  ❌ Failed: $FAILED"

echo ""

# Top tags
echo "🏷️  Top tags:"
jq -r '[.[].tags[]?] | group_by(.) | map({tag: .[0], count: length}) | sort_by(-.count) | .[0:5] | .[] | "  #\(.tag) (\(.count))"' "$VAULT_FILE" 2>/dev/null || echo "  (no tags yet)"

echo ""

# Most recent entry
LATEST=$(jq -r 'sort_by(.ingested_date) | last | "\(.ingested_date) — \"\(.title)\""' "$VAULT_FILE" 2>/dev/null)
echo "📅 Most recent: $LATEST"

echo ""
echo "=== End Stats ==="
