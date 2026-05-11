#!/usr/bin/env bash
# sync_md_to_notion_v4.sh - 修复版 v4.2
# 修复内容:
#   - 所有可能失败的命令添加 || true 兜底
#   - 修复 associative array 兼容性问题
#   - 修复哈希读取未命中时的退出问题

set -uo pipefail
# 移除 -e，改用显式错误检查

# ========== 1. 安全配置 ==========
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
WORKSPACE_ROOT="${SIGNALRADAR_WORKSPACE_ROOT:-${WORKSPACE_ROOT:-${DEFAULT_WORKSPACE_ROOT}}}"
API_KEY="${NOTION_API_KEY:-}"
PARENT_PAGE="${NOTION_PARENT_PAGE_ID:-}"
if [ -z "$PARENT_PAGE" ]; then
  echo "ERROR: NOTION_PARENT_PAGE_ID is required. Set it before running this script." >&2
  exit 1
fi
API_BASE="https://api.notion.com/v1"
API_VERSION="${NOTION_API_VERSION:-2022-06-28}"
DRY_RUN_THRESHOLD="${SYNC_DRY_RUN_THRESHOLD:-20}"
LOCK_TIMEOUT="${SYNC_LOCK_TIMEOUT:-300}"

if [[ -z "$API_KEY" ]]; then
    echo '{"ts":"'$(date -Iseconds)'","script":"sync_md_to_notion_v4","action":"init","result":"FAIL","exit_code":1,"error":"NOTION_API_KEY not set"}' >> /var/log/openclaw/sync.log
    echo "Error: NOTION_API_KEY environment variable not set" >&2
    echo "Please set it: export NOTION_API_KEY=your_key_here" >&2
    exit 1
fi

# ========== 2. 并发锁 ==========
LOCK_FILE="/var/lock/sync_md_to_notion.lock"
LOCK_FD=200

exec {LOCK_FD}>"$LOCK_FILE" 2>/dev/null || {
    echo '{"ts":"'$(date -Iseconds)'","script":"sync_md_to_notion_v4","action":"lock","result":"FAIL","exit_code":1,"error":"Cannot create lock file"}' >> /var/log/openclaw/sync.log
    exit 1
}

if ! flock -n $LOCK_FD 2>/dev/null; then
    echo '{"ts":"'$(date -Iseconds)'","script":"sync_md_to_notion_v4","action":"lock","result":"SKIP_LOCKED","exit_code":0}' >> /var/log/openclaw/sync.log
    echo "Another sync is running. Exiting."
    exit 0
fi

# ========== 3. 初始化 ==========
mkdir -p /var/log/openclaw 2>/dev/null || true
HASH_FILE="${SYNC_HASH_FILE:-${WORKSPACE_ROOT}/.notion_sync_hashes}"
touch "$HASH_FILE" 2>/dev/null || true

headers=(
  -H "Authorization: Bearer $API_KEY"
  -H "Notion-Version: $API_VERSION"
  -H "Content-Type: application/json"
)

START_TIME=$(date +%s%3N)

# 将 Markdown 转为 Notion blocks（保留标题/列表可读性）
build_children_payload() {
  local mode="$1"      # synced | created
  local hash="$2"
  local file_path="$3"
  local ts
  ts=$(date -Iseconds)

  python3 - "$mode" "$ts" "$hash" "$file_path" <<'PY'
import json, re, sys
from pathlib import Path

mode, ts, h, fp = sys.argv[1:5]
text = Path(fp).read_text(encoding='utf-8', errors='ignore')
lines = text.splitlines()[:220]  # 限制块数，避免超大 payload

meta = f"{'Created' if mode == 'created' else 'Last synced'}: {ts} | Hash: {h}"
emoji = "🆕" if mode == 'created' else "🕐"

children = [
  {"object":"block","type":"callout","callout":{"rich_text":[{"type":"text","text":{"content":meta}}],"icon":{"emoji":emoji}}},
  {"object":"block","type":"divider","divider":{}}
]

KNOWN_LANGS = {"python","bash","json","javascript","typescript","plain text","html","css","yaml","sql","markdown","shell","go","rust","java","c","c++"}
# Note: Notion API uses "c++" (not "cpp") for the C++ language enum.

def rich(txt):
  txt = txt.strip()
  if not txt:
    txt = " "
  # notion rich_text content <= 2000
  if len(txt) > 1900:
    txt = txt[:1900] + " …"
  return [{"type":"text","text":{"content":txt}}]

def code_blk(content, lang="plain text"):
  if len(content) > 1900:
    content = content[:1900] + " …"
  return {"object":"block","type":"code","code":{"language":lang,"rich_text":[{"type":"text","text":{"content":content}}]}}

in_code = False
code_lines = []
code_lang = "plain text"

for raw in lines:
  s = raw.rstrip("\n")
  # --- 围栏代码块处理 ---
  if s.strip().startswith("```") and not in_code:
    in_code = True
    lang = s.strip()[3:].strip().lower()
    code_lang = lang if lang in KNOWN_LANGS else "plain text"
    code_lines = []
    continue
  if in_code:
    if s.strip() == "```":
      children.append(code_blk("\n".join(code_lines), code_lang))
      in_code = False
      continue
    code_lines.append(s)
    continue
  # --- 原有逻辑 ---
  if not s.strip():
    continue
  if s.strip() == '---':
    children.append({"object":"block","type":"divider","divider":{}})
    continue
  if s.startswith('### '):
    children.append({"object":"block","type":"heading_3","heading_3":{"rich_text":rich(s[4:])}})
  elif s.startswith('## '):
    children.append({"object":"block","type":"heading_2","heading_2":{"rich_text":rich(s[3:])}})
  elif s.startswith('# '):
    children.append({"object":"block","type":"heading_1","heading_1":{"rich_text":rich(s[2:])}})
  elif s.startswith('> '):
    children.append({"object":"block","type":"quote","quote":{"rich_text":rich(s[2:])}})
  elif re.match(r'^\d+\.\s+', s):
    children.append({"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":rich(re.sub(r'^\d+\.\s+','',s))}})
  elif s.startswith('- '):
    children.append({"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":rich(s[2:])}})
  else:
    children.append({"object":"block","type":"paragraph","paragraph":{"rich_text":rich(s)}})

# 兜底：未闭合的代码块
if in_code and code_lines:
  children.append(code_blk("\n".join(code_lines), "plain text"))

if len(lines) >= 220:
  children.append({"object":"block","type":"quote","quote":{"rich_text":rich("⚠️ 文档较长，Notion 同步已截断显示前 220 行。完整内容请查看本地文件。")}})

print(json.dumps({"children": children}, ensure_ascii=False))
PY
}

# ========== 4. 获取Notion现有页面 ==========
page_data=$(curl -s --max-time 30 -X GET "${API_BASE}/blocks/${PARENT_PAGE}/children?page_size=100" \
  "${headers[@]}" 2>/dev/null) || {
    echo '{"ts":"'$(date -Iseconds)'","script":"sync_md_to_notion_v4","action":"fetch","result":"FAIL","exit_code":1,"error":"Notion API unreachable"}' >> /var/log/openclaw/sync.log
    exit 1
}

# 使用临时文件存储页面映射，避免associative array兼容性问题
TEMP_PAGES=$(mktemp)
echo "$page_data" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f\"{b.get('child_page',{}).get('title','')}|||{b['id']}\") for b in d.get('results',[]) if b['type']=='child_page']" 2>/dev/null > "$TEMP_PAGES" || true

TOTAL_EXISTING=$(wc -l < "$TEMP_PAGES" 2>/dev/null | tr -d ' ')

# ========== 5. 阈值保护 ==========
FILES_TO_PROCESS=0
for file in "${WORKSPACE_ROOT}"/*.md "${WORKSPACE_ROOT}"/memory/*.md; do
    [[ -f "$file" ]] || continue
    filename=$(basename "$file" .md)
    
    current_hash=$(md5sum "$file" 2>/dev/null | awk '{print $1}')
    # 关键修复：grep未命中时返回空字符串而非退出
    stored_hash=$(grep "^${filename}:" "$HASH_FILE" 2>/dev/null | cut -d: -f2 || echo "")
    
    if [[ "$current_hash" != "$stored_hash" ]]; then
        FILES_TO_PROCESS=$((FILES_TO_PROCESS + 1))
    fi
done

if [[ $FILES_TO_PROCESS -gt $DRY_RUN_THRESHOLD ]]; then
    echo '{"ts":"'$(date -Iseconds)'","script":"sync_md_to_notion_v4","action":"threshold_check","result":"DRY_RUN","exit_code":0,"pages_would_modify":'$FILES_TO_PROCESS',"threshold":'$DRY_RUN_THRESHOLD'}' >> /var/log/openclaw/sync.log
    echo "⚠️  DRY RUN MODE: Would modify $FILES_TO_PROCESS pages (threshold: $DRY_RUN_THRESHOLD)"
    rm -f "$TEMP_PAGES"
    exit 0
fi

# ========== 6. 执行同步 ==========
CREATED=0
UPDATED=0
SKIPPED=0
ERRORS=0

for file in "${WORKSPACE_ROOT}"/*.md "${WORKSPACE_ROOT}"/memory/*.md; do
  [[ -f "$file" ]] || continue
  
  filename=$(basename "$file" .md)

  # 排除列表过滤（由 run_signalradar_job.py 通过环境变量传入）
  if [[ -n "${SYNC_EXCLUDE_PATTERNS:-}" ]] && echo "$filename" | grep -qE "$SYNC_EXCLUDE_PATTERNS"; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  current_hash=$(md5sum "$file" 2>/dev/null | awk '{print $1}')
  # 关键修复：grep未命中时返回空字符串
  stored_hash=$(grep "^${filename}:" "$HASH_FILE" 2>/dev/null | cut -d: -f2 || echo "")

  # 幂等检查
  if [[ "$current_hash" == "$stored_hash" ]] && [[ -n "$stored_hash" ]]; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi
  
  payload_synced=$(build_children_payload "synced" "$current_hash" "$file")
  payload_created=$(build_children_payload "created" "$current_hash" "$file")
  
  # 检查页面是否存在（使用临时文件查询）
  page_id=$(grep "^${filename}|||" "$TEMP_PAGES" 2>/dev/null | cut -d'|' -f4 || echo "")
  
  if [[ -n "$page_id" ]]; then
    # UPDATE
    echo "🔄 Updating: $filename"
    
    block_ids=$(curl -s -X GET "${API_BASE}/blocks/${page_id}/children" \
      "${headers[@]}" 2>/dev/null | \
      python3 -c "import sys,json; d=json.load(sys.stdin); [print(b['id']) for b in d.get('results',[])]" 2>/dev/null) || true
    
    for block_id in $block_ids; do
      curl -s -X DELETE "${API_BASE}/blocks/${block_id}" "${headers[@]}" >/dev/null 2>&1 || true
    done
    
    curl -s -X PATCH "${API_BASE}/blocks/${page_id}/children" \
      "${headers[@]}" \
      -d "$payload_synced" > /dev/null || ERRORS=$((ERRORS + 1))
    
    UPDATED=$((UPDATED + 1))
  else
    # CREATE
    echo "➕ Creating: $filename"
    
    response=$(curl -s -X POST "${API_BASE}/pages" \
      "${headers[@]}" \
      -d "{
        \"parent\": {\"page_id\": \"${PARENT_PAGE}\"},
        \"properties\": {
          \"title\": {\"title\": [{\"text\": {\"content\": \"${filename}\"}}]}
        }
      }")
    
    page_id=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")
    
    if [[ -n "$page_id" ]]; then
      curl -s -X PATCH "${API_BASE}/blocks/${page_id}/children" \
        "${headers[@]}" \
        -d "$payload_created" > /dev/null || ERRORS=$((ERRORS + 1))
      
      CREATED=$((CREATED + 1))
    else
      ERRORS=$((ERRORS + 1))
      echo "   ✗ Failed to create page for $filename"
    fi
  fi
  
  # 更新哈希记录
  if grep -q "^${filename}:" "$HASH_FILE" 2>/dev/null; then
    sed -i "s/^${filename}:.*/${filename}:${current_hash}/" "$HASH_FILE" 2>/dev/null || true
  else
    echo "${filename}:${current_hash}" >> "$HASH_FILE" 2>/dev/null || true
  fi
  
  sleep 0.5
done

# 清理
rm -f "$TEMP_PAGES"

END_TIME=$(date +%s%3N)
DURATION=$((END_TIME - START_TIME))

# ========== 7. JSONL日志 ==========
LOG_ENTRY=$(cat <> EOF
{"ts":"$(date -Iseconds)","script":"sync_md_to_notion_v4","action":"sync","result":"COMPLETE","exit_code":$ERRORS,"duration_ms":$DURATION,"pages_created":$CREATED,"pages_updated":$UPDATED,"pages_skipped":$SKIPPED,"errors":$ERRORS}
EOF
)

echo "$LOG_ENTRY" >> /var/log/openclaw/sync.log 2>/dev/null || true

echo "=========================================="
echo "Sync Complete:"
echo "   Created: $CREATED"
echo "   Updated: $UPDATED"
echo "   Skipped: $SKIPPED"
echo "   Errors: $ERRORS"
echo "   Duration: ${DURATION}ms"
echo "=========================================="

exit $ERRORS
