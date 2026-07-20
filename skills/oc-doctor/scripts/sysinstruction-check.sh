#!/bin/bash
# sysinstruction-check.sh — Collect system instruction health data for /oc-doctor
# Usage: bash sysinstruction-check.sh
# Outputs structured JSON to stdout
#
# Dependencies: jq
# Env vars:    OPENCLAW_HOME (optional, defaults to ~/.openclaw)
# Files read:  $OPENCLAW_HOME/workspace-*/*.md, openclaw.json, models.json
# Files write: none
# Network:     none
# Endpoints:   none

set -euo pipefail

# --- Dependency check ---
if ! command -v jq &>/dev/null; then
  echo '{"error": "jq is required but not installed. Install with: brew install jq (macOS) or apt install jq (Linux)"}' >&2
  exit 1
fi

# --- Paths (auto-detect, no hardcoding) ---
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OPENCLAW_CONFIG="$OPENCLAW_HOME/openclaw.json"
MODELS_JSON="$OPENCLAW_HOME/agents/main/agent/models.json"

# --- 1. Scan all workspace .md files ---
files_json="[]"
total_tokens=0
largest_file=""
largest_tokens=0
empty_templates_json="[]"

for f in "$OPENCLAW_HOME"/workspace-*/*.md; do
  [ -f "$f" ] || continue

  # Use relative path from OPENCLAW_HOME to preserve workspace context
  relpath="${f#$OPENCLAW_HOME/}"
  # wc -m counts characters (not bytes) — correct for CJK/UTF-8 content
  chars=$(wc -m < "$f" | tr -d ' ')
  lines=$(wc -l < "$f" | tr -d ' ')
  # Token estimation: CJK ~1.5 chars/token, English ~4 chars/token
  # Use 2.5 as blended average for mixed content
  tokens=$((chars * 10 / 25))
  total_tokens=$((total_tokens + tokens))

  # Track largest file (use relpath to disambiguate across workspaces)
  if [ "$tokens" -gt "$largest_tokens" ]; then
    largest_tokens=$tokens
    largest_file=$relpath
  fi

  # Detect empty templates (only headings, no real content)
  # A file is "empty template" if non-blank, non-heading lines are < 3
  content_lines=$(grep -cvE '^(#|$|[[:space:]]*$)' "$f" 2>/dev/null || true)
  content_lines=$(echo "$content_lines" | tr -d '[:space:]')
  content_lines=${content_lines:-0}
  is_empty="false"
  if [ "$content_lines" -lt 3 ]; then
    is_empty="true"
    # Use jq for safe JSON escaping (handles special chars in filenames)
    empty_templates_json=$(echo "$empty_templates_json" | jq --arg f "$relpath" '. + [$f]')
  fi

  # Use jq for safe JSON escaping (handles special chars in filenames)
  files_json=$(echo "$files_json" | jq \
    --arg file "$relpath" \
    --argjson chars "$chars" \
    --argjson lines "$lines" \
    --argjson est_tokens "$tokens" \
    --argjson is_empty_template "$is_empty" \
    '. + [{file: $file, chars: $chars, lines: $lines, est_tokens: $est_tokens, is_empty_template: $is_empty_template}]'
  )
done

# --- 2. Tool description bloat detection ---
tool_bloat_files="[]"
tool_bloat_tokens=0
while IFS= read -r match_file; do
  [ -n "$match_file" ] || continue
  relpath="${match_file#$OPENCLAW_HOME/}"
  fchars=$(wc -m < "$match_file" | tr -d ' ')
  ftokens=$((fchars * 10 / 25))
  tool_bloat_tokens=$((tool_bloat_tokens + ftokens))
  tool_bloat_files=$(echo "$tool_bloat_files" | jq --arg f "$relpath" --argjson t "$ftokens" '. + [{file: $f, est_tokens: $t}]')
done < <(grep -rlE 'feishu_bitable|bitable_app_table' "$OPENCLAW_HOME"/workspace-*/*.md 2>/dev/null || true)

# --- 3. BOOTSTRAP.md check (scan all workspaces, not just workspace-claude) ---
bootstrap="false"
for ws in "$OPENCLAW_HOME"/workspace-*/; do
  if [ -f "${ws}BOOTSTRAP.md" ] && [ -s "${ws}BOOTSTRAP.md" ]; then
    bootstrap="true"
    break
  fi
done

# --- 4. Context window from models.json ---
context_window_source="default_fallback"
context_window=200000

if [ -f "$OPENCLAW_CONFIG" ]; then
  primary_model=$(jq -r '.agents.defaults.model.primary // empty' "$OPENCLAW_CONFIG" 2>/dev/null || true)
  if [ -n "$primary_model" ] && [ -f "$MODELS_JSON" ]; then
    provider=$(echo "$primary_model" | cut -d/ -f1)
    model_id=$(echo "$primary_model" | cut -d/ -f2-)
    resolved=$(jq -r --arg p "$provider" --arg m "$model_id" \
      '.providers[$p].models[] | select(.id == $m) | .contextWindow' \
      "$MODELS_JSON" 2>/dev/null || true)
    if [ -n "$resolved" ] && [ "$resolved" != "null" ]; then
      context_window=$resolved
      context_window_source="models.json"
    fi
  fi
fi

# --- 5. Calculate percentage ---
if [ "$context_window" -gt 0 ]; then
  pct_x10=$((total_tokens * 1000 / context_window))
  pct_whole=$((pct_x10 / 10))
  pct_frac=$((pct_x10 % 10))
  pct="${pct_whole}.${pct_frac}"
else
  pct="0.0"
fi

# --- 6. Assemble JSON ---
jq -n \
  --argjson workspace_files "$files_json" \
  --argjson total_est_tokens "$total_tokens" \
  --arg largest_file "$largest_file" \
  --argjson empty_template_files "$empty_templates_json" \
  --argjson tool_bloat_files "$tool_bloat_files" \
  --argjson tool_bloat_est_tokens "$tool_bloat_tokens" \
  --argjson bootstrap_still_present "$bootstrap" \
  --argjson context_window "$context_window" \
  --arg context_window_source "$context_window_source" \
  --arg pct_of_context "$pct" \
  '{
    workspace_files: $workspace_files,
    total_est_tokens: $total_est_tokens,
    largest_file: $largest_file,
    empty_template_files: $empty_template_files,
    tool_bloat_files: $tool_bloat_files,
    tool_bloat_est_tokens: $tool_bloat_est_tokens,
    bootstrap_still_present: $bootstrap_still_present,
    context_window: $context_window,
    context_window_source: $context_window_source,
    pct_of_context: $pct_of_context
  }'
