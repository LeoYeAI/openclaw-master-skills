#!/usr/bin/env bash
set -euo pipefail

# Discover AI coding session files from the last 30 days.
# Output: prints the path of a temp file containing one session path per line.
#
# Usage:
#   SESSION_LIST=$(bash discover-sessions.sh)
#
# Environment:
#   SESSION_LIST  – optional; reuse an existing temp file path instead of creating one
#   PF_DAYS       – optional; number of days to look back (default: 30)
#   PF_SOURCES    – optional; comma-separated list of sources to scan
#                   (e.g. "claude-code,cursor,codex"). If unset, scans all.

DAYS="${PF_DAYS:-30}"
SESSION_LIST="${SESSION_LIST:-$(mktemp /tmp/promptfolio-sessions.XXXXXX)}"
SOURCES="${PF_SOURCES:-all}"

should_scan() {
  [ "$SOURCES" = "all" ] && return 0
  echo ",$SOURCES," | grep -qi ",$1," && return 0
  return 1
}

# ── Find session files ────────────────────────────────────────────────

if should_scan "claude-code"; then
  find ~/.claude/projects/ -name "*.jsonl" -not -path "*/subagents/*" -type f 2>/dev/null >> "$SESSION_LIST" || true
fi

if should_scan "cursor"; then
  find ~/.cursor/projects/ -path "*/agent-transcripts/*" \( -name "*.txt" -o -name "*.jsonl" \) -type f 2>/dev/null >> "$SESSION_LIST" || true
fi

if should_scan "codex"; then
  find ~/.codex/sessions/ -name "*.jsonl" -type f 2>/dev/null >> "$SESSION_LIST" || true
  [ -f ~/.codex/history.jsonl ] && echo ~/.codex/history.jsonl >> "$SESSION_LIST"
fi

if should_scan "openclaw"; then
  find ~/.openclaw/sessions -name "*.jsonl" -type f 2>/dev/null >> "$SESSION_LIST" || true
  find ~/.openclaw/agents -name "*.jsonl" -type f 2>/dev/null >> "$SESSION_LIST" || true
fi

if should_scan "antigravity"; then
  find "$HOME/Library/Application Support/Antigravity" \
    \( -path "*/exthost/google.antigravity/*.log" -o -name "*.jsonl" -o -name "*.json" \) \
    -not -name "state.vscdb" -type f 2>/dev/null >> "$SESSION_LIST" || true
  find ~/.gemini/antigravity -type f \( -name "*.jsonl" -o -name "*.json" \) 2>/dev/null >> "$SESSION_LIST" || true
fi

if should_scan "windsurf"; then
  find ~/.codeium/windsurf ~/.windsurf \
    "$HOME/Library/Application Support/Windsurf" \
    "$HOME/Library/Application Support/Codeium/Windsurf" \
    -type f \( -name "*.jsonl" -o -name "*.json" -o -path "*/agent-transcripts/*" \) \
    -not -name "state.vscdb" 2>/dev/null >> "$SESSION_LIST" || true
fi

if should_scan "chatgpt"; then
  find ~/Desktop/chatgpt_history ~/Downloads -maxdepth 4 -type f \
    \( -name "conversations*.json" -o -name "chat.html" \) \
    2>/dev/null >> "$SESSION_LIST" || true
fi

if should_scan "gemini-cli"; then
  find ~/.gemini/tmp -path "*/chats/session-*.json" -type f 2>/dev/null >> "$SESSION_LIST" || true
fi

if should_scan "trae"; then
  # Trae CN / Trae stores AI chat in an encrypted SQLite DB (SQLCipher).
  # We cannot read it directly. Scan for user-exported chat files and
  # any accessible JSON/JSONL in known locations.
  TRAE_FOUND=0
  for TRAE_EXPORT in \
    "$HOME/.trae-cn/chat-export.json" \
    "$HOME/.trae/chat-export.json" \
    "$HOME/Desktop/trae-chat-export.json" \
    "$HOME/Downloads/trae-chat-export.json"; do
    [ -f "$TRAE_EXPORT" ] && echo "$TRAE_EXPORT" >> "$SESSION_LIST" && TRAE_FOUND=1
  done
  # Also scan for any exported conversation files
  while IFS= read -r _tf; do
    echo "$_tf" >> "$SESSION_LIST"
    TRAE_FOUND=1
  done < <(find "$HOME/.trae-cn" "$HOME/.trae" \
    -maxdepth 2 -name "*chat*export*.json" -type f 2>/dev/null || true)
  # Output detection marker if Trae is installed but no exports found
  if [ "$TRAE_FOUND" = "0" ]; then
    for TRAE_DIR in \
      "$HOME/.trae-cn" \
      "$HOME/.trae" \
      "$HOME/Library/Application Support/Trae CN" \
      "$HOME/Library/Application Support/Trae"; do
      [ -d "$TRAE_DIR" ] && echo "TRAE_DETECTED_NO_EXPORT" >&2 && break
    done
  fi
fi

if should_scan "opencode"; then
  OC_DB="$HOME/.local/share/opencode/opencode.db"
  if [ -f "$OC_DB" ]; then
    OC_DIR=$(mktemp -d /tmp/promptfolio-opencode.XXXXXX)
    PF_OC_DB="$OC_DB" PF_OC_DIR="$OC_DIR" python3 -c "
import sqlite3, json, os, sys, re
db = sqlite3.connect(os.environ['PF_OC_DB'])
out = os.environ['PF_OC_DIR']

def table_exists(name):
    return db.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name=?\", (name,)).fetchone() is not None

if not table_exists('session') or not table_exists('message'):
    sys.exit(0)

_safe_re = re.compile(r'[^a-zA-Z0-9_-]')
has_part = table_exists('part')

for sid, tc in db.execute('SELECT id, time_created FROM session'):
    safe_sid = _safe_re.sub('_', str(sid))[:200]
    if not safe_sid:
        continue
    msgs = []
    for mid, mdata, mtc in db.execute('SELECT id, data, time_created FROM message WHERE session_id=? ORDER BY time_created', (sid,)):
        try: md = json.loads(mdata)
        except: md = {}
        parts = []
        if has_part:
            for (pd,) in db.execute('SELECT data FROM part WHERE message_id=? ORDER BY time_created', (mid,)):
                try: parts.append(json.loads(pd))
                except: pass
        role = md.get('role', 'unknown')
        texts = []
        for p in parts:
            if isinstance(p, dict):
                t = p.get('text','') or p.get('content','')
                if isinstance(t, str) and t: texts.append(t)
        if not texts and 'content' in md:
             t = md['content']
             if isinstance(t, str): texts.append(t)
        if texts:
            msgs.append({'role': role, 'content': chr(10).join(texts), 'timestamp': mtc})
    if not msgs: continue
    fp = os.path.join(out, safe_sid + '.json')
    with open(fp, 'w') as f: json.dump({'messages': msgs}, f)
    print(fp)
db.close()
" >> "$SESSION_LIST" 2>/tmp/promptfolio-opencode-errors.log || {
      [ -s /tmp/promptfolio-opencode-errors.log ] && echo "opencode: extraction errors logged to /tmp/promptfolio-opencode-errors.log" >&2
      true
    }
  fi
fi

# ── Deduplicate ───────────────────────────────────────────────────────

sort -u -o "$SESSION_LIST" "$SESSION_LIST"

# ── Filter to last N days ────────────────────────────────────────────

CUTOFF=$(date -v-${DAYS}d +%s 2>/dev/null || date -d "${DAYS} days ago" +%s)
FILTERED=$(mktemp /tmp/promptfolio-filtered.XXXXXX)
while IFS= read -r f; do
  MTIME=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)
  if [ "$MTIME" -ge "$CUTOFF" ] 2>/dev/null; then
    echo "$f" >> "$FILTERED"
  fi
done < "$SESSION_LIST"
mv "$FILTERED" "$SESSION_LIST"

# ── Output ────────────────────────────────────────────────────────────

TOTAL=$(wc -l < "$SESSION_LIST" | tr -d ' ')
echo "$SESSION_LIST"
echo "Found $TOTAL session files (last ${DAYS} days)" >&2
