#!/usr/bin/env bash
# ═══════════════════════════════════════════════════
# iFinD API 调用脚本
# 计费验证 + iFinD Token 管理 + API 请求
# ═══════════════════════════════════════════════════

set -euo pipefail

# ─── 加载 .env ───
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="${SCRIPT_DIR}/.."
if [ -f "${SKILL_DIR}/.env" ]; then
  set -a; source "${SKILL_DIR}/.env"; set +a
fi

# ─── 配置 ───
IFIND_BASE_URL="https://quantapi.51ifind.com/api/v1"
IFIND_BILLING_URL="https://ifind.skillapp.vip"
IFIND_API_SECRET="ps_123c80aaf4c7134ee9faebd4d0cb0783a42be1ce9e440fbc"
DATA_DIR="${SCRIPT_DIR}/../.data"
mkdir -p "$DATA_DIR"
TOKEN_CACHE_FILE="${DATA_DIR}/access_token"
TOKEN_CACHE_TTL=86400  # 缓存有效期: 1天（token 实际7天有效）
USER_ID_FILE="${DATA_DIR}/user_id"

# ─── 参数检查 ───
if [ $# -lt 2 ]; then
  echo '{"error": "用法: ifind-api.sh <api_endpoint> <json_body>"}'
  exit 1
fi

API_ENDPOINT="$1"
JSON_BODY="$2"

# ─── 环境变量检查 ───
if [ -z "${IFIND_REFRESH_TOKEN:-}" ]; then
  echo '{"error": "缺少环境变量 IFIND_REFRESH_TOKEN，请设置后重试"}'
  exit 1
fi


# ═══════════════════════════════════════════════════
# 0. 自动生成 user_id（基于硬件指纹，持久化）
# ═══════════════════════════════════════════════════
get_user_id() {
  # 优先使用已持久化的 user_id
  if [ -f "$USER_ID_FILE" ]; then
    cat "$USER_ID_FILE"
    return 0
  fi

  # 采集硬件指纹：优先 MAC 地址，其次 CPU ID
  local hw_fingerprint=""

  # macOS: 取第一个以太网/Wi-Fi 的 MAC 地址
  if command -v ifconfig &>/dev/null; then
    hw_fingerprint=$(ifconfig 2>/dev/null | awk '/ether /{print $2; exit}')
  fi

  # Linux: 从 /sys 读 MAC
  if [ -z "$hw_fingerprint" ] && [ -d /sys/class/net ]; then
    for iface in /sys/class/net/*/address; do
      local addr
      addr=$(cat "$iface" 2>/dev/null)
      if [ -n "$addr" ] && [ "$addr" != "00:00:00:00:00:00" ]; then
        hw_fingerprint="$addr"
        break
      fi
    done
  fi

  # Linux 备选: CPU ID
  if [ -z "$hw_fingerprint" ] && [ -f /proc/cpuinfo ]; then
    hw_fingerprint=$(grep -m1 'Serial\|model name' /proc/cpuinfo | awk -F: '{print $2}' | xargs)
  fi

  # macOS 备选: 硬件 UUID
  if [ -z "$hw_fingerprint" ]; then
    hw_fingerprint=$(ioreg -rd1 -c IOPlatformExpertDevice 2>/dev/null | awk -F'"' '/IOPlatformUUID/{print $4}')
  fi

  # 最终兜底
  if [ -z "$hw_fingerprint" ]; then
    hw_fingerprint="$(hostname)-$(whoami)-fallback"
  fi

  # SHA256 哈希生成固定长度 user_id
  local user_id
  user_id=$(echo -n "ifind_${hw_fingerprint}" | shasum -a 256 | cut -c1-20)
  user_id="ifind_${user_id}"

  echo -n "$user_id" > "$USER_ID_FILE"
  echo "$user_id"
}

USER_ID=$(get_user_id)

# ═══════════════════════════════════════════════════
# 1. 计费验证（0.001 USDT/次）
# ═══════════════════════════════════════════════════
skillpay_charge() {
  local response
  response=$(curl -s -X POST "${IFIND_BILLING_URL}/charge" \
    -H "Content-Type: application/json" \
    -H "X-Api-Secret: ${IFIND_API_SECRET}" \
    -d "{\"user_id\": \"${USER_ID}\"}")

  local success
  success=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")

  if [ "$success" = "True" ] || [ "$success" = "true" ]; then
    # 输出试用期信息到 stderr，供 AI 读取
    local is_trial
    is_trial=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('trial', False))" 2>/dev/null || echo "False")
    if [ "$is_trial" = "True" ] || [ "$is_trial" = "true" ]; then
      echo "[TRIAL] $response" >&2
    fi
    return 0
  fi

  # 余额不足 → 返回充值链接给用户
  local payment_url balance
  payment_url=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('payment_url', ''))" 2>/dev/null || echo "")
  balance=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('balance', '0'))" 2>/dev/null || echo "0")

  echo "{\"error\": \"余额不足，请点击链接充值 USDT 后重试\", \"balance\": \"${balance} USDT\", \"payment_url\": \"${payment_url}\"}"
  exit 1
}

# ═══════════════════════════════════════════════════
# 2. iFinD Token 管理
# ═══════════════════════════════════════════════════
get_access_token() {
  # 检查缓存是否存在且未过期
  if [ -f "$TOKEN_CACHE_FILE" ]; then
    local cache_age
    cache_age=$(( $(date +%s) - $(stat -f %m "$TOKEN_CACHE_FILE" 2>/dev/null || stat -c %Y "$TOKEN_CACHE_FILE" 2>/dev/null || echo 0) ))
    if [ "$cache_age" -lt "$TOKEN_CACHE_TTL" ]; then
      cat "$TOKEN_CACHE_FILE"
      return 0
    fi
  fi

  # 请求新的 access_token
  local response token
  response=$(curl -s -X POST "${IFIND_BASE_URL}/get_access_token" \
    -H "Content-Type: application/json" \
    -H "refresh_token: ${IFIND_REFRESH_TOKEN}")

  token=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)

  if [ -z "$token" ] || [ "$token" = "None" ]; then
    echo '{"error": "获取 access_token 失败，请检查 IFIND_REFRESH_TOKEN 是否有效"}'
    exit 1
  fi

  # 缓存 token
  echo -n "$token" > "$TOKEN_CACHE_FILE"
  echo "$token"
}

# ═══════════════════════════════════════════════════
# 3. API 请求执行
# ═══════════════════════════════════════════════════
call_ifind_api() {
  local access_token="$1"
  local endpoint="$2"
  local body="$3"

  local url="${IFIND_BASE_URL}/${endpoint}"

  curl -s -X POST "$url" \
    -H "Content-Type: application/json" \
    -H "access_token: ${access_token}" \
    -H "Accept-Encoding: gzip,deflate" \
    --compressed \
    -d "$body"
}

# ═══════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════

# Step 1: 计费验证（0.001 USDT/次）
skillpay_charge

# Step 2: 获取 iFinD access_token
ACCESS_TOKEN=$(get_access_token)

# Step 3: 调用 iFinD API
RESULT=$(call_ifind_api "$ACCESS_TOKEN" "$API_ENDPOINT" "$JSON_BODY")

# 检查是否 token 过期（errorcode = -1302），自动重试
ERROR_CODE=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('errorcode', 0))" 2>/dev/null || echo "0")

if [ "$ERROR_CODE" = "-1302" ]; then
  rm -f "$TOKEN_CACHE_FILE"
  ACCESS_TOKEN=$(get_access_token)
  RESULT=$(call_ifind_api "$ACCESS_TOKEN" "$API_ENDPOINT" "$JSON_BODY")
fi

echo "$RESULT"
