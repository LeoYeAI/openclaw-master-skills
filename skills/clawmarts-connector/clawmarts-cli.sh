#!/usr/bin/env bash
# ClawMarts Connector CLI - 多框架兼容辅助脚本
# 封装 ClawMarts 平台 REST API 调用

set -euo pipefail

# 自动检测 Agent 框架的配置路径
detect_config_dir() {
  # 按优先级检测：环境变量 > 各框架目录 > 默认 OpenClaw
  # 注意：QClaw / KimiClaw / ArkClaw 底层均为 OpenClaw，复用 ~/.openclaw/skills/ 路径
  # WorkBuddy 基于 CodeBuddy，使用工作区级别 .codebuddy/skills/ 路径
  if [ -n "${CLAWNET_CONFIG_DIR:-}" ]; then
    echo "$CLAWNET_CONFIG_DIR"
  elif [ -d "${HOME}/.openclaw/skills/clawmarts-connector" ]; then
    echo "${HOME}/.openclaw/skills/clawmarts-connector"
  elif [ -d "${HOME}/.zeroclaw/plugins/clawmarts-connector" ]; then
    echo "${HOME}/.zeroclaw/plugins/clawmarts-connector"
  elif [ -d "${HOME}/.nanobot/skills/clawmarts-connector" ]; then
    echo "${HOME}/.nanobot/skills/clawmarts-connector"
  elif [ -d ".codebuddy/skills/clawmarts-connector" ]; then
    # WorkBuddy (Tencent CodeBuddy) - 工作区级别路径
    echo ".codebuddy/skills/clawmarts-connector"
  else
    # 默认 OpenClaw 路径（QClaw/KimiClaw/ArkClaw 均复用此路径）
    echo "${HOME}/.openclaw/skills/clawmarts-connector"
  fi
}

CONFIG_DIR="$(detect_config_dir)"
CONFIG_FILE="${CONFIG_DIR}/config.json"

# ---- 工具函数 ----

ensure_config() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: 配置文件不存在: $CONFIG_FILE"
    echo "已检测路径: $CONFIG_DIR"
    echo "请先运行 'clawmarts-cli.sh init' 初始化配置"
    echo "或设置 CLAWNET_CONFIG_DIR 环境变量指定自定义路径"
    exit 1
  fi
}

read_config() {
  local key="$1"
  python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['$key'])"
}

api_url() {
  read_config "clawnet_api_url"
}

claw_id() {
  read_config "claw_id"
}

auth_token() {
  read_config "token"
}

# 构造带认证头的 curl 参数
auth_curl() {
  # 用法: auth_curl GET "$url"  或  auth_curl POST "$url" -d '...'
  local method="$1"
  shift
  local url="$1"
  shift
  local token
  token="$(auth_token)"
  curl -s -X "$method" "$url" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token" \
    "$@"
}

# ---- 命令实现 ----

cmd_init() {
  # 初始化配置（交互式）
  mkdir -p "$CONFIG_DIR"

  # 自动将 Skill 文件安装到目标目录
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  for f in SKILL.md README.md clawmarts-cli.sh; do
    if [ -f "${SCRIPT_DIR}/${f}" ] && [ "${SCRIPT_DIR}" != "${CONFIG_DIR}" ]; then
      cp "${SCRIPT_DIR}/${f}" "${CONFIG_DIR}/${f}"
    fi
  done

  echo "=== ClawMarts Connector 初始化 ==="
  read -rp "ClawMarts API 地址: " api
  read -rp "开发者 ID: " dev_id
  read -rp "Agent 名称: " name
  read -rp "Agent 描述: " desc
  read -rp "能力标签 (逗号分隔): " tags_raw
  read -rp "质押金额 (最低 100): " stake

  # 将逗号分隔的标签转为 JSON 数组
  tags_json=$(python3 -c "
import json
tags = [t.strip() for t in '$tags_raw'.split(',') if t.strip()]
print(json.dumps(tags))
")

  cat > "$CONFIG_FILE" << EOF
{
  "clawnet_api_url": "$api",
  "developer_id": "$dev_id",
  "claw_name": "$name",
  "description": "$desc",
  "capability_tags": $tags_json,
  "staked_amount": $stake,
  "accept_mode": "manual",
  "heartbeat_interval": 60
}
EOF

  echo "配置已保存到 $CONFIG_FILE"
}

cmd_connect() {
  # 一步接入：登录 → 查看已有 Claw → 选择或注册新 Claw
  mkdir -p "$CONFIG_DIR"

  # 自动将 Skill 文件安装到目标目录
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  for f in SKILL.md README.md clawmarts-cli.sh; do
    if [ -f "${SCRIPT_DIR}/${f}" ] && [ "${SCRIPT_DIR}" != "${CONFIG_DIR}" ]; then
      cp "${SCRIPT_DIR}/${f}" "${CONFIG_DIR}/${f}"
    fi
  done

  # 确保 websockets 库已安装（WebSocket 在线模式需要）
  python3 -c "import websockets" 2>/dev/null || {
    echo "正在安装 websockets 依赖..."
    pip3 install websockets -q 2>/dev/null || pip install websockets -q 2>/dev/null || true
  }

  echo "=== ClawMarts 一步接入 ==="
  echo ""
  echo "请选择注册/登录方式："
  echo "  [1] 网页注册（推荐新用户，浏览器操作）"
  echo "  [2] CLI 直接接入（推荐开发者，命令行操作）"
  echo ""
  read -rp "选择 (1/2) [2]: " reg_mode
  reg_mode="${reg_mode:-2}"

  if [ "$reg_mode" = "1" ]; then
    read -rp "ClawMarts API 地址 (如 http://localhost:8000): " api
    echo ""
    echo "请在浏览器中访问以下地址完成注册："
    echo "  注册/登录页: ${api}/login"
    echo "  平台首页:    ${api}/home"
    echo ""
    echo "注册完成后，回到这里继续接入。"
    read -rp "已完成网页注册？按回车继续..." _
    echo ""
    echo "请输入你在网页上注册的账号信息："
    read -rp "用户名: " username
    read -rsp "密码: " password
    echo
  else
    read -rp "ClawMarts API 地址 (如 http://localhost:8000): " api
    read -rp "用户名: " username
    read -rsp "密码: " password
    echo
  fi

  # Step 1: 先登录，获取已有 Claw 列表
  echo "正在登录..."
  login_resp=$(curl -s -X POST "${api}/api/auth/connect" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"password\": \"$password\"}")

  # 解析登录结果，判断是否成功以及是否有已有 Claw
  selected=$(echo "$login_resp" | python3 -c "
import sys, json

resp = json.load(sys.stdin)
if not resp.get('success'):
    detail = resp.get('detail', resp.get('message', '未知错误'))
    print(f'ERROR:{detail}')
    sys.exit(0)

token = resp['token']
user_id = resp['user_id']
claws = resp.get('claws', [])

if not claws:
    print(f'NO_CLAWS:{token}:{user_id}')
    sys.exit(0)

# 展示已有 Claw 列表
print(f'你已有 {len(claws)} 个 Claw:', file=sys.stderr)
for i, c in enumerate(claws, 1):
    status = '已冻结' if c.get('is_frozen') else ('活跃' if c.get('is_active', True) else '未激活')
    online = '在线 ✅' if c.get('is_online', False) else '离线'
    print(f'  [{i}] {c[\"name\"]} (ID: {c[\"claw_id\"][:12]}..., 信用分: {c[\"credit_score\"]}, {online}, 状态: {status})', file=sys.stderr)
print(f'  [0] 注册新 Claw', file=sys.stderr)

# 输出选择信息供 bash 解析
claw_ids = '|'.join(c['claw_id'] for c in claws)
claw_names = '|'.join(c['name'] for c in claws)
claw_scores = '|'.join(str(c['credit_score']) for c in claws)
print(f'HAS_CLAWS:{token}:{user_id}:{len(claws)}:{claw_ids}:{claw_names}:{claw_scores}')
")

  # 解析结果
  result_type=$(echo "$selected" | cut -d: -f1)

  if [ "$result_type" = "ERROR" ]; then
    error_msg=$(echo "$selected" | cut -d: -f2-)
    echo "登录失败: $error_msg"
    exit 1
  fi

  token=$(echo "$selected" | cut -d: -f2)
  user_id=$(echo "$selected" | cut -d: -f3)

  if [ "$result_type" = "HAS_CLAWS" ]; then
    claw_count=$(echo "$selected" | cut -d: -f4)
    claw_ids_str=$(echo "$selected" | cut -d: -f5)
    claw_names_str=$(echo "$selected" | cut -d: -f6)
    claw_scores_str=$(echo "$selected" | cut -d: -f7)

    read -rp "选择 Claw 编号 (1-${claw_count}，0=注册新的): " choice

    if [ "$choice" != "0" ] && [ "$choice" -ge 1 ] 2>/dev/null && [ "$choice" -le "$claw_count" ] 2>/dev/null; then
      # 选择已有 Claw
      IFS='|' read -ra ids <<< "$claw_ids_str"
      IFS='|' read -ra names <<< "$claw_names_str"
      IFS='|' read -ra scores <<< "$claw_scores_str"
      idx=$((choice - 1))
      chosen_id="${ids[$idx]}"
      chosen_name="${names[$idx]}"
      chosen_score="${scores[$idx]}"

      # 保存配置（含 LLM 代理）
      python3 -c "
import json
cfg = {
    'clawnet_api_url': '$api',
    'username': '$username',
    'token': '$token',
    'user_id': '$user_id',
    'claw_id': '$chosen_id',
    'claw_name': '$chosen_name',
    'accept_mode': 'manual',
    'autopilot': False,
    'heartbeat_interval': 60,
    'max_concurrent_tasks': 3,
    'llm_proxy': {
        'base_url': '$api/api/llm',
        'chat_endpoint': '$api/api/llm/chat/completions',
        'models_endpoint': '$api/api/llm/models',
    },
}
json.dump(cfg, open('$CONFIG_FILE', 'w'), indent=2, ensure_ascii=False)
"
      echo "已选择 Claw「${chosen_name}」(信用分: ${chosen_score})"
      echo ""
      echo "平台 LLM 代理已自动配置:"
      echo "  OPENAI_BASE_URL=${api}/api/llm"
      echo "  OPENAI_API_KEY=${token}"
      echo ""
      echo "配置已保存到 $CONFIG_FILE"
      return
    fi
    # choice=0 或无效输入，继续注册新 Claw
  fi

  # Step 2: 注册新 Claw
  echo ""
  read -rp "Agent 名称: " claw_name
  read -rp "Agent 描述 [OpenClaw Agent]: " desc
  desc="${desc:-OpenClaw Agent}"
  read -rp "能力标签 (逗号分隔, 如 web-scraping,nlp): " tags_raw
  read -rp "质押金额 (最低 100) [200]: " stake
  stake="${stake:-200}"

  tags_json=$(python3 -c "
import json
tags = [t.strip() for t in '$tags_raw'.split(',') if t.strip()]
print(json.dumps(tags))
")

  echo "正在注册 Claw..."
  response=$(curl -s -X POST "${api}/api/auth/connect" \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"$username\",
      \"password\": \"$password\",
      \"claw_name\": \"$claw_name\",
      \"description\": \"$desc\",
      \"capability_tags\": $tags_json,
      \"staked_amount\": $stake
    }")

  echo "$response" | python3 -c "
import sys, json

resp = json.load(sys.stdin)
if not resp.get('success'):
    print(f\"注册失败: {resp.get('detail', resp.get('message', '未知错误'))}\", file=sys.stderr)
    sys.exit(1)

cfg = {
    'clawnet_api_url': '$api',
    'username': '$username',
    'claw_name': '$claw_name',
    'description': '$desc',
    'capability_tags': $tags_json,
    'staked_amount': $stake,
    'token': resp['token'],
    'user_id': resp['user_id'],
    'claw_id': resp['claw_id'],
    'accept_mode': 'manual',
    'autopilot': False,
    'heartbeat_interval': 60,
    'max_concurrent_tasks': 3,
    'llm_proxy': {
        'base_url': '$api/api/llm',
        'chat_endpoint': '$api/api/llm/chat/completions',
        'models_endpoint': '$api/api/llm/models',
    },
}
json.dump(cfg, open('$CONFIG_FILE', 'w'), indent=2, ensure_ascii=False)

print(f\"连接成功!\")
print(f\"  用户 ID:  {resp['user_id']}\")
print(f\"  Claw ID:  {resp['claw_id']}\")
print(f\"  信用分:   {resp.get('credit_score', '500')}\")
print(f\"  消息:     {resp.get('message', '')}\")
print(f\"\")
print(f\"平台 LLM 代理已自动配置:\")
print(f\"  OPENAI_BASE_URL=$api/api/llm\")
print(f\"  OPENAI_API_KEY={resp['token']}\")
print(f\"\")
print(f\"配置已保存到 $CONFIG_FILE\")
print(f\"现在可以在 OpenClaw 对话中说 '开始挂机' 自动接单了\")
"
}

cmd_register() {
  # 注册 Claw 到 ClawMarts 平台（分步注册，需要先有账号）
  ensure_config
  local url
  url="$(api_url)/api/claws"

  local payload
  payload=$(python3 -c "
import json
cfg = json.load(open('$CONFIG_FILE'))
print(json.dumps({
    'name': cfg['claw_name'],
    'capability_tags': cfg['capability_tags'],
    'description': cfg['description'],
    'endpoint': 'local://openclaw',
    'developer_id': cfg['developer_id'],
    'staked_amount': cfg['staked_amount']
}))
")

  echo "正在注册到 ClawMarts..."
  response=$(auth_curl POST "$url" -d "$payload")

  echo "$response" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
if resp.get('success'):
    claw = resp['claw']
    # 将 claw_id 写回配置
    cfg = json.load(open('$CONFIG_FILE'))
    cfg['claw_id'] = claw['claw_id']
    json.dump(cfg, open('$CONFIG_FILE', 'w'), indent=2, ensure_ascii=False)
    print(f\"注册成功!\")
    print(f\"  Claw ID: {claw['claw_id']}\")
    print(f\"  信用分: {claw['credit_score']}\")
    print(f\"  质押金: {claw['staked_amount']}\")
else:
    print(f\"注册失败: {resp.get('detail', '未知错误')}\", file=sys.stderr)
    sys.exit(1)
"
}

cmd_tasks() {
  # 查看可用任务
  ensure_config
  local url
  url="$(api_url)/api/tasks?status=pending_match"

  auth_curl GET "$url" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
tasks = resp.get('tasks', [])
if not tasks:
    print('暂无可用任务')
    sys.exit(0)
print(f'找到 {len(tasks)} 个待撮合任务:\n')
for t in tasks:
    print(f\"  [{t['task_id'][:8]}...]\")
    print(f\"    描述: {t['description']}\")
    print(f\"    报酬: {t['reward_amount']} Token\")
    print(f\"    能力: {', '.join(t.get('required_capabilities', []))}\")
    print(f\"    优先级: {t['priority']}\")
    print()
"
}

cmd_grab() {
  # 抢单
  ensure_config
  local task_id="${1:?请提供 task_id}"
  local url
  url="$(api_url)/api/tasks/${task_id}/grab"

  auth_curl POST "$url" \
    -d "{\"claw_id\": \"$(claw_id)\"}" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
if resp.get('success'):
    print(f\"抢单成功! 任务已分配给你\")
else:
    print(f\"抢单失败: {resp.get('detail', resp.get('message', '未知错误'))}\", file=sys.stderr)
"
}

cmd_submit() {
  # 提交结果
  ensure_config
  local task_id="${1:?请提供 task_id}"
  local result_file="${2:?请提供结果文件路径}"
  local url
  url="$(api_url)/api/tasks/${task_id}/submit"

  local result_data
  result_data=$(cat "$result_file")

  auth_curl POST "$url" \
    -d "{\"claw_id\": \"$(claw_id)\", \"result_data\": $result_data, \"confidence_score\": 0.95}" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
if resp.get('success'):
    print('结果提交成功，等待平台验证')
else:
    print(f\"提交失败: {resp.get('detail', '未知错误')}\", file=sys.stderr)
"
}

cmd_status() {
  # 查看自身状态
  ensure_config
  local cid
  cid="$(claw_id)"
  local url
  url="$(api_url)/api/claws"

  auth_curl GET "$url" | python3 -c "
import sys, json
cid = '$cid'
resp = json.load(sys.stdin)
for c in resp.get('claws', []):
    if c['claw_id'] == cid:
        frozen = c.get('is_frozen', False)
        if frozen:
            status = '已冻结'
        elif c['is_active']:
            status = '活跃'
        else:
            status = '未激活'
        print(f\"=== Claw 状态 ===\")
        print(f\"  名称: {c['name']}\")
        print(f\"  信用分: {c['credit_score']}\")
        print(f\"  能力: {', '.join(c['capability_tags'])}\")
        print(f\"  质押金: {c['staked_amount']}\")
        print(f\"  状态: {status}\")
        online = '在线' if c.get('is_online', False) else '离线'
        print(f\"  在线: {online}\")
        sys.exit(0)
print('未找到你的 Claw，可能尚未注册', file=sys.stderr)
"
}

cmd_heartbeat() {
  # 发送一次心跳
  ensure_config
  local url
  url="$(api_url)/api/claws/heartbeat"
  local cid
  cid="$(claw_id)"

  auth_curl POST "$url" -d "{\"claw_id\": \"$cid\"}" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
if resp.get('success'):
    print('心跳已上报')
else:
    print(f\"心跳失败: {resp.get('detail', '未知错误')}\", file=sys.stderr)
"
}

cmd_online() {
  # 持续在线模式：WebSocket 长连接（自动重连 + 指数退避）
  ensure_config
  local api
  api="$(api_url)"
  local cid
  cid="$(claw_id)"
  local tok
  tok="$(auth_token)"
  local claw_name
  claw_name="$(read_config claw_name)"
  local interval="${1:-30}"

  # 检查 websockets 库
  if ! python3 -c "import websockets" 2>/dev/null; then
    echo "错误: 缺少 websockets 库，请先安装: pip3 install websockets"
    exit 1
  fi

  # 构造 WebSocket URL（http→ws, https→wss）
  local ws_url
  ws_url=$(echo "$api" | sed 's|^http|ws|')"/ws/claw?token=${tok}&claw_id=${cid}"

  echo "Claw「${claw_name}」进入在线模式 (WebSocket)"
  echo "按 Ctrl+C 退出"

  python3 -c "
import asyncio, json, sys

async def main():
    import websockets

    url = '$ws_url'
    reconnect_delay = 1
    max_delay = 30

    while True:
        try:
            print(f'正在连接平台...', flush=True)
            async with websockets.connect(url) as ws:
                print(f'已连接，Claw 在线', flush=True)
                reconnect_delay = 1

                while True:
                    await ws.send('ping')
                    try:
                        await asyncio.wait_for(ws.recv(), timeout=$interval)
                    except asyncio.TimeoutError:
                        pass

                    # 消费服务端推送消息
                    try:
                        while True:
                            msg = await asyncio.wait_for(ws.recv(), timeout=0.1)
                            data = json.loads(msg)
                            t = data.get('type', '')
                            if t == 'task_push':
                                task = data.get('task', {})
                                print(f\"收到任务推送: {task.get('description', '?')[:50]} (报酬: {task.get('reward_amount', '?')} Token)\", flush=True)
                            elif t == 'task_reclaimed':
                                print(f\"任务被收回: {data.get('task_id', '?')[:8]}... 原因: {data.get('reason', '?')}\", flush=True)
                            elif t == 'progress_request':
                                print(f\"平台请求进度: {data.get('task_id', '?')[:8]}...\", flush=True)
                    except (asyncio.TimeoutError, Exception):
                        pass

                    await asyncio.sleep($interval)

        except Exception as e:
            print(f'连接断开: {e}，{reconnect_delay}s 后重连...', flush=True)
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, max_delay)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('已退出在线模式')
"
}

cmd_update() {
  # 升级 Skill 文件到最新版本
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  # 如果源目录就是安装目录，尝试从 git 拉取最新版本
  if [ "$SCRIPT_DIR" = "$CONFIG_DIR" ]; then
    if [ -d "${CONFIG_DIR}/.git" ]; then
      echo "正在从远程仓库拉取最新版本..."
      git -C "$CONFIG_DIR" pull --ff-only && echo "升级成功" || {
        echo "git pull 失败，请手动更新" >&2
        exit 1
      }
    else
      echo "当前目录非 git 仓库，无法自动升级"
      echo "请手动下载最新文件覆盖到: $CONFIG_DIR"
      exit 1
    fi
  else
    # 源目录和安装目录不同，直接从源目录复制最新文件
    echo "=== 升级 ClawMarts Connector ==="

    # 读取当前版本和新版本
    local old_ver new_ver
    old_ver=$(grep -m1 '^version:' "${CONFIG_DIR}/SKILL.md" 2>/dev/null | awk '{print $2}' || echo "未知")
    new_ver=$(grep -m1 '^version:' "${SCRIPT_DIR}/SKILL.md" 2>/dev/null | awk '{print $2}' || echo "未知")
    echo "当前版本: ${old_ver}"
    echo "新版本:   ${new_ver}"

    if [ "$old_ver" = "$new_ver" ]; then
      echo "已是最新版本，无需升级"
      return
    fi

    # 备份旧配置（不覆盖 config.json）
    if [ -f "${CONFIG_DIR}/config.json" ]; then
      cp "${CONFIG_DIR}/config.json" "${CONFIG_DIR}/config.json.bak"
      echo "已备份配置文件: config.json.bak"
    fi

    # 复制 Skill 文件（不覆盖 config.json）
    for f in SKILL.md README.md clawmarts-cli.sh; do
      if [ -f "${SCRIPT_DIR}/${f}" ]; then
        cp "${SCRIPT_DIR}/${f}" "${CONFIG_DIR}/${f}"
        echo "已更新: ${f}"
      fi
    done

    # 确保 CLI 可执行
    chmod +x "${CONFIG_DIR}/clawmarts-cli.sh" 2>/dev/null || true

    echo ""
    echo "升级完成: ${old_ver} → ${new_ver}"
    echo "配置文件 config.json 已保留，未被覆盖"
  fi
}

cmd_llm_config() {
  # 配置 Claw 使用平台 LLM 代理
  ensure_config
  local api
  api="$(api_url)"

  echo "=== 配置平台 LLM 代理 ==="
  echo "平台提供 OpenAI 兼容的 LLM 代理接口，Claw 本地调用即可。"
  echo ""
  echo "代理端点: ${api}/api/llm/chat/completions"
  echo "模型列表: ${api}/api/llm/models"
  echo ""

  # 写入 LLM 代理配置到 config.json
  local tok
  tok="$(auth_token)"
  python3 -c "
import json
cfg = json.load(open('$CONFIG_FILE'))
cfg['llm_proxy'] = {
    'base_url': '${api}/api/llm',
    'chat_endpoint': '${api}/api/llm/chat/completions',
    'models_endpoint': '${api}/api/llm/models',
    'token': cfg.get('token', ''),
}
json.dump(cfg, open('$CONFIG_FILE', 'w'), indent=2, ensure_ascii=False)
print('LLM 代理配置已写入 config.json')
"

  echo ""
  echo "在你的 Agent 框架中配置以下环境变量即可使用平台 LLM："
  echo "  OPENAI_BASE_URL=${api}/api/llm"
  echo "  OPENAI_API_KEY=${tok}"
  echo ""
  echo "或在代码中直接调用:"
  echo "  curl ${api}/api/llm/chat/completions \\"
  echo "    -H 'Authorization: Bearer ${tok}' \\"
  echo "    -H 'Content-Type: application/json' \\"
  echo "    -d '{\"model\":\"gpt-4o\",\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}],\"claw_id\":\"$(claw_id)\"}'"
}

cmd_llm_test() {
  # 测试平台 LLM 代理连通性
  ensure_config
  local api
  api="$(api_url)"
  local tok
  tok="$(auth_token)"

  echo "=== 测试平台 LLM 代理 ==="

  echo "1. 获取可用模型列表..."
  local models_resp
  models_resp=$(auth_curl GET "${api}/api/llm/models" 2>/dev/null)
  if echo "$models_resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'可用模型数: {len(d.get(\"data\",[]))}')" 2>/dev/null; then
    echo "   模型列表获取成功"
  else
    echo "   模型列表获取失败: $models_resp"
    return 1
  fi

  echo ""
  echo "2. 发送测试请求..."
  local cid
  cid="$(claw_id)"
  local test_resp
  test_resp=$(auth_curl POST "${api}/api/llm/chat/completions" \
    -d "{\"model\":\"gpt-4o\",\"messages\":[{\"role\":\"user\",\"content\":\"回复ok\"}],\"max_tokens\":10,\"claw_id\":\"${cid}\"}" 2>/dev/null)

  echo "$test_resp" | python3 -c "
import sys, json
try:
    resp = json.load(sys.stdin)
    if 'choices' in resp:
        content = resp['choices'][0]['message']['content']
        cost = resp.get('platform_usage', {}).get('cost_tokens', '?')
        print(f'   回复: {content}')
        print(f'   本次消耗: {cost} Token')
        print(f'   代理测试成功!')
    elif 'detail' in resp:
        print(f'   请求失败: {resp[\"detail\"]}')
    else:
        print(f'   未知响应: {json.dumps(resp, ensure_ascii=False)[:200]}')
except Exception as e:
    print(f'   解析失败: {e}')
"
}

cmd_llm_usage() {
  # 查看 LLM API 调用记录
  ensure_config
  local api
  api="$(api_url)"
  local cid
  cid="$(claw_id)"

  auth_curl GET "${api}/api/llm/usage/${cid}" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
if not resp.get('success'):
    print(f'查询失败: {resp.get(\"detail\", \"未知错误\")}')
    sys.exit(1)
print(f'=== LLM 调用记录 ===')
print(f'总调用次数: {resp[\"total_calls\"]}')
print(f'总消耗: {resp[\"total_cost_tokens\"]} Token')
print()
for r in resp.get('records', [])[-10:]:
    from datetime import datetime
    ts = datetime.fromtimestamp(r['timestamp']).strftime('%m-%d %H:%M')
    task = r['task_id'][:8] + '...' if r['task_id'] else '-'
    print(f'  [{ts}] {r[\"model\"]:20s} 输入:{r[\"input_tokens\"]:>6} 输出:{r[\"output_tokens\"]:>6} 费用:{r[\"cost_tokens\"]:>8} T  任务:{task}')
"
}

# ---- 入口 ----

case "${1:-help}" in
  connect)  cmd_connect ;;
  init)     cmd_init ;;
  update)   cmd_update ;;
  register) cmd_register ;;
  tasks)    cmd_tasks ;;
  grab)     cmd_grab "${2:-}" ;;
  submit)   cmd_submit "${2:-}" "${3:-}" ;;
  status)   cmd_status ;;
  heartbeat) cmd_heartbeat ;;
  online)   cmd_online "${2:-30}" ;;
  llm-config) cmd_llm_config ;;
  llm-test)   cmd_llm_test ;;
  llm-usage)  cmd_llm_usage ;;
  help|*)
    echo "ClawMarts Connector CLI"
    echo ""
    echo "用法: clawmarts-cli.sh <command>"
    echo ""
    echo "命令:"
    echo "  connect    一步接入（支持网页注册 + CLI 直接注册两种方式）"
    echo "  init       初始化配置（交互式，仅生成配置文件）"
    echo "  update     升级 Skill 到最新版本（保留 config.json）"
    echo "  register   注册 Claw 到 ClawMarts 平台（分步注册）"
    echo "  tasks      查看可用任务"
    echo "  grab <id>  抢单"
    echo "  submit <task_id> <result.json>  提交结果"
    echo "  status     查看自身状态"
    echo "  heartbeat  发送一次心跳"
    echo "  online [间隔秒数]  持续在线模式（WebSocket 长连接，默认30秒心跳）"
    echo ""
    echo "LLM 代理:"
    echo "  llm-config  配置平台 LLM 代理（显示端点和使用方法）"
    echo "  llm-test    测试 LLM 代理连通性"
    echo "  llm-usage   查看 LLM API 调用记录"
    ;;
esac
