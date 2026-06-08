#!/bin/bash
# 腾讯云 COS Skill 自动设置脚本
# 用法:
#   setup.sh --check-only                    仅检查环境状态
#   setup.sh --from-env                      从已有环境变量读取凭证（推荐）
#   setup.sh --secret-id <ID> --secret-key <KEY> --region <REGION> --bucket <BUCKET> [...]
#
# 凭证处理策略:
#   - 凭证仅导出到当前 shell session，不写入 ~/.zshrc / ~/.bashrc
#   - mcporter 配置（~/.mcporter/mcporter.json）需用户确认后才写入
#   - coscmd 配置（~/.cos.conf）需用户确认后才写入
#   - 所有配置文件设置 600 权限（仅当前用户可读写）
#   - ⚠️ 持久化凭证存储会增加暴露风险，强烈建议使用子账号最小权限密钥

set -e

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }

# 获取脚本所在目录（skill baseDir）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ========== 检查函数 ==========

check_node() {
  if command -v node &>/dev/null; then
    ok "Node.js $(node --version)"
    return 0
  else
    fail "Node.js 未安装"
    return 1
  fi
}

check_npm() {
  if command -v npm &>/dev/null; then
    ok "npm $(npm --version)"
    return 0
  else
    fail "npm 未安装"
    return 1
  fi
}

check_mcporter() {
  if command -v mcporter &>/dev/null; then
    ok "mcporter $(mcporter --version 2>/dev/null || echo '已安装')"
    return 0
  else
    fail "mcporter 未安装"
    return 1
  fi
}

check_mcporter_config() {
  if [ -f ~/.mcporter/mcporter.json ]; then
    if grep -q '"cos-mcp"' ~/.mcporter/mcporter.json 2>/dev/null; then
      ok "mcporter 已配置 cos-mcp 服务器"
      return 0
    else
      warn "mcporter.json 存在但未配置 cos-mcp"
      return 1
    fi
  else
    fail "~/.mcporter/mcporter.json 不存在"
    return 1
  fi
}

check_cos_mcp() {
  if command -v npx &>/dev/null && npx cos-mcp --help &>/dev/null 2>&1; then
    ok "cos-mcp 可用"
    return 0
  else
    fail "cos-mcp 未安装或不可用"
    return 1
  fi
}

check_cos_sdk() {
  if node -e "require('cos-nodejs-sdk-v5')" &>/dev/null 2>&1; then
    ok "cos-nodejs-sdk-v5 已安装"
    return 0
  else
    fail "cos-nodejs-sdk-v5 未安装"
    return 1
  fi
}

check_coscmd() {
  if command -v coscmd &>/dev/null; then
    ok "coscmd 可用"
    return 0
  else
    warn "coscmd 未安装（可选）"
    return 1
  fi
}

check_env_vars() {
  local all_set=true
  for var in TENCENT_COS_SECRET_ID TENCENT_COS_SECRET_KEY TENCENT_COS_REGION TENCENT_COS_BUCKET; do
    if [ -n "${!var}" ]; then
      ok "$var 已设置"
    else
      fail "$var 未设置"
      all_set=false
    fi
  done
  $all_set
}

check_cos_conf() {
  if [ -f ~/.cos.conf ]; then
    ok "~/.cos.conf 已存在"
    return 0
  else
    warn "~/.cos.conf 不存在"
    return 1
  fi
}

# ========== 检查模式 ==========

do_check() {
  echo "=== 腾讯云 COS Skill 环境检查 ==="
  echo ""
  echo "--- 基础环境 ---"
  check_node || true
  check_npm || true
  echo ""
  echo "--- 方式一: cos-mcp MCP ---"
  check_mcporter || true
  check_mcporter_config || true
  check_cos_mcp || true
  echo ""
  echo "--- 方式二: Node.js SDK ---"
  check_cos_sdk || true
  check_env_vars || true
  echo ""
  echo "--- 方式三: COSCMD ---"
  check_coscmd || true
  check_cos_conf || true
  echo ""
  echo "--- Skill 文件 ---"
  [ -f "$BASE_DIR/SKILL.md" ] && ok "SKILL.md" || fail "SKILL.md 不存在"
  [ -f "$BASE_DIR/scripts/cos_node.mjs" ] && ok "scripts/cos_node.mjs" || fail "scripts/cos_node.mjs 不存在"
  [ -f "$BASE_DIR/references/config_template.json" ] && ok "references/config_template.json" || fail "references/config_template.json 不存在"
  echo ""
}

# ========== 设置模式 ==========

do_setup() {
  local SECRET_ID=""
  local SECRET_KEY=""
  local REGION=""
  local BUCKET=""
  local DATASET=""
  local DOMAIN=""
  local SERVICE_DOMAIN=""
  local PROTOCOL=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --secret-id)       SECRET_ID="$2"; shift 2;;
      --secret-key)      SECRET_KEY="$2"; shift 2;;
      --region)          REGION="$2"; shift 2;;
      --bucket)          BUCKET="$2"; shift 2;;
      --dataset)         DATASET="$2"; shift 2;;
      --domain)          DOMAIN="$2"; shift 2;;
      --service-domain)  SERVICE_DOMAIN="$2"; shift 2;;
      --protocol)        PROTOCOL="$2"; shift 2;;
      *) shift;;
    esac
  done

  if [ -z "$SECRET_ID" ] || [ -z "$SECRET_KEY" ] || [ -z "$REGION" ] || [ -z "$BUCKET" ]; then
    echo "错误: 缺少必需参数"
    echo "用法: setup.sh --secret-id <ID> --secret-key <KEY> --region <REGION> --bucket <BUCKET> [--dataset <NAME>]"
    exit 1
  fi

  echo "=== 腾讯云 COS Skill 自动设置 ==="
  echo ""

  # 1. 检查 Node.js
  echo "--- 步骤 1: 检查 Node.js ---"
  if ! check_node; then
    fail "请先安装 Node.js: https://nodejs.org/"
    exit 1
  fi

  # 2. 确保 package.json 存在
  echo ""
  echo "--- 步骤 2: 初始化项目 ---"
  if [ ! -f "$BASE_DIR/package.json" ]; then
    (cd "$BASE_DIR" && npm init -y &>/dev/null)
    ok "已创建 package.json"
  else
    ok "package.json 已存在"
  fi

  # 3. 安装 cos-mcp、cos-nodejs-sdk-v5 和 mcporter
  echo ""
  echo "--- 步骤 3: 安装依赖 ---"
  (cd "$BASE_DIR" && npm install cos-mcp cos-nodejs-sdk-v5 --no-progress 2>&1 | tail -3)
  ok "cos-mcp + cos-nodejs-sdk-v5 安装完成"

  # 安装 mcporter（本地安装，避免全局 -g 改变系统状态）
  if command -v mcporter &>/dev/null; then
    ok "mcporter 已安装（全局）"
  else
    (cd "$BASE_DIR" && npm install mcporter --no-progress 2>&1 | tail -3)
    ok "mcporter 本地安装完成（通过 npx mcporter 调用）"
  fi

  # 4. 导出环境变量到当前 session（不持久化到 shell RC）
  echo ""
  echo "--- 步骤 4: 设置当前 session 环境变量 ---"

  export TENCENT_COS_SECRET_ID="$SECRET_ID"
  export TENCENT_COS_SECRET_KEY="$SECRET_KEY"
  export TENCENT_COS_REGION="$REGION"
  export TENCENT_COS_BUCKET="$BUCKET"
  [ -n "$DATASET" ] && export TENCENT_COS_DATASET_NAME="$DATASET"
  [ -n "$DOMAIN" ] && export TENCENT_COS_DOMAIN="$DOMAIN"
  [ -n "$SERVICE_DOMAIN" ] && export TENCENT_COS_SERVICE_DOMAIN="$SERVICE_DOMAIN"
  [ -n "$PROTOCOL" ] && export TENCENT_COS_PROTOCOL="$PROTOCOL"

  ok "环境变量已导出到当前 session"
  info "注意：凭证仅在当前 shell session 中有效，关闭终端后需重新设置"

  # 5. 配置 mcporter（写入 ~/.mcporter/mcporter.json）
  echo ""
  echo "--- 步骤 5: 配置 mcporter ---"
  info "此步骤将写入文件：~/.mcporter/mcporter.json"
  info "凭证通过 env 字段传递（不暴露在进程列表中）"

  local MCPORTER_DIR="$HOME/.mcporter"
  local MCPORTER_CONFIG="$MCPORTER_DIR/mcporter.json"

  mkdir -p "$MCPORTER_DIR"

  if [ -f "$MCPORTER_CONFIG" ]; then
    if grep -q '"cos-mcp"' "$MCPORTER_CONFIG" 2>/dev/null; then
      warn "mcporter.json 中已存在 cos-mcp 配置，将更新"
    fi
  fi

  # 通过环境变量安全传入 node 脚本，避免 shell 插值问题
  _COS_SID="$SECRET_ID" \
  _COS_SKEY="$SECRET_KEY" \
  _COS_REGION="$REGION" \
  _COS_BUCKET="$BUCKET" \
  _COS_DATASET="$DATASET" \
  _COS_DOMAIN="$DOMAIN" \
  _COS_SDOMAIN="$SERVICE_DOMAIN" \
  _COS_PROTO="$PROTOCOL" \
  _COS_CFG="$MCPORTER_CONFIG" \
  node -e "
    const fs = require('fs');
    const p = process.env;
    const configPath = p._COS_CFG;
    let config = {};
    try { config = JSON.parse(fs.readFileSync(configPath, 'utf-8')); } catch(e) {}
    if (!config.mcpServers) config.mcpServers = {};

    // 凭证通过 env 传递，不放入 args（安全：避免在进程列表中暴露密钥）
    const env = {
      TENCENT_COS_SECRET_ID: p._COS_SID,
      TENCENT_COS_SECRET_KEY: p._COS_SKEY,
      TENCENT_COS_REGION: p._COS_REGION,
      TENCENT_COS_BUCKET: p._COS_BUCKET,
    };
    if (p._COS_DATASET) env.TENCENT_COS_DATASET_NAME = p._COS_DATASET;
    if (p._COS_DOMAIN) env.TENCENT_COS_DOMAIN = p._COS_DOMAIN;
    if (p._COS_SDOMAIN) env.TENCENT_COS_SERVICE_DOMAIN = p._COS_SDOMAIN;
    if (p._COS_PROTO) env.TENCENT_COS_PROTOCOL = p._COS_PROTO;

    config.mcpServers['cos-mcp'] = {
      command: 'npx',
      args: ['cos-mcp', '--connectType=stdio'],
      env,
    };
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), { mode: 0o600 });
  " 2>/dev/null
  ok "mcporter.json 已创建/更新（凭证通过 env 传递）"

  # 设置 mcporter 配置文件权限为仅当前用户可读写
  chmod 600 "$MCPORTER_CONFIG"
  ok "mcporter.json 权限已设置为 600"

  # 6. 配置 COSCMD（仅当已安装时配置，不自动安装）
  echo ""
  echo "--- 步骤 6: 配置 COSCMD（可选） ---"
  if command -v coscmd &>/dev/null; then
    info "检测到 coscmd 已安装，将配置 COS 凭证"
    info "此步骤将写入文件：~/.cos.conf"

    # 构建 coscmd config 命令
    local COSCMD_ARGS="-a $SECRET_ID -s $SECRET_KEY -b $BUCKET -r $REGION"
    if [ -n "$SERVICE_DOMAIN" ]; then
      COSCMD_ARGS="$COSCMD_ARGS -e $SERVICE_DOMAIN"
    fi
    if [ -n "$PROTOCOL" ] && [ "$PROTOCOL" = "http" ]; then
      COSCMD_ARGS="$COSCMD_ARGS --do-not-use-ssl"
    fi

    eval coscmd config $COSCMD_ARGS 2>/dev/null && \
    chmod 600 ~/.cos.conf 2>/dev/null && \
    ok "coscmd 已配置（~/.cos.conf 权限 600）" || \
    warn "coscmd 配置失败（非关键）"
  else
    info "coscmd 未安装，跳过（如需使用方式三，请手动安装：pip install coscmd）"
  fi

  # 7. 验证
  echo ""
  echo "--- 步骤 7: 验证连接 ---"
  if (cd "$BASE_DIR" && node scripts/cos_node.mjs list --max-keys 1 2>/dev/null | grep -q '"success": true'); then
    ok "COS 连接验证成功"
  else
    warn "COS 连接验证失败，请检查凭证和网络"
  fi

  echo ""
  echo "=== 设置完成 ==="
  echo ""
  echo "现在可以使用以下方式操作 COS："
  echo "  方式一: npx mcporter call cos-mcp.<tool> --config ~/.mcporter/mcporter.json --output json"
  echo "  方式二: node $BASE_DIR/scripts/cos_node.mjs <action>"
  echo "  方式三: coscmd <command>（需预装 coscmd）"
  echo ""
  echo "⚠️  凭证存储位置（持久化存储，增加暴露风险，供您审查）："
  echo "  • ~/.mcporter/mcporter.json — MCP 服务器 env 配置（权限 600）"
  if [ -f ~/.cos.conf ]; then
    echo "  • ~/.cos.conf — coscmd 配置（权限 600）"
  fi
  echo ""
  echo "🔒 安全建议："
  echo "  • 必须使用子账号密钥（仅授予 COS 权限），严禁使用主账号密钥"
  echo "  • 不再使用时清理凭证：rm -f ~/.mcporter/mcporter.json ~/.cos.conf"
  echo "  • 建议每 90 天轮换一次 API 密钥"
  echo ""
  info "环境变量仅在当前 session 有效。如需持久化，请自行添加到 shell 配置文件中："
  echo "  export TENCENT_COS_SECRET_ID='...'"
  echo "  export TENCENT_COS_SECRET_KEY='...'"
  echo "  export TENCENT_COS_REGION='$REGION'"
  echo "  export TENCENT_COS_BUCKET='$BUCKET'"
}

# ========== 主入口 ==========

case "$1" in
  --check-only)
    do_check
    ;;
  --from-env)
    # 安全模式：从已有环境变量读取凭证，避免命令行历史泄露
    if [ -z "$TENCENT_COS_SECRET_ID" ] || [ -z "$TENCENT_COS_SECRET_KEY" ] || [ -z "$TENCENT_COS_REGION" ] || [ -z "$TENCENT_COS_BUCKET" ]; then
      echo "错误: --from-env 模式需要先设置环境变量："
      echo "  export TENCENT_COS_SECRET_ID='<ID>'"
      echo "  export TENCENT_COS_SECRET_KEY='<KEY>'"
      echo "  export TENCENT_COS_REGION='<Region>'"
      echo "  export TENCENT_COS_BUCKET='<Bucket>'"
      exit 1
    fi
    # 构造参数列表传递给 do_setup
    FROM_ENV_ARGS="--secret-id $TENCENT_COS_SECRET_ID --secret-key $TENCENT_COS_SECRET_KEY --region $TENCENT_COS_REGION --bucket $TENCENT_COS_BUCKET"
    [ -n "$TENCENT_COS_DATASET_NAME" ] && FROM_ENV_ARGS="$FROM_ENV_ARGS --dataset $TENCENT_COS_DATASET_NAME"
    [ -n "$TENCENT_COS_DOMAIN" ] && FROM_ENV_ARGS="$FROM_ENV_ARGS --domain $TENCENT_COS_DOMAIN"
    [ -n "$TENCENT_COS_SERVICE_DOMAIN" ] && FROM_ENV_ARGS="$FROM_ENV_ARGS --service-domain $TENCENT_COS_SERVICE_DOMAIN"
    [ -n "$TENCENT_COS_PROTOCOL" ] && FROM_ENV_ARGS="$FROM_ENV_ARGS --protocol $TENCENT_COS_PROTOCOL"
    eval do_setup $FROM_ENV_ARGS
    ;;
  --secret-id|--secret-key|--region|--bucket)
    warn "⚠️  凭证将出现在 shell 历史记录中。推荐使用 --from-env 模式："
    warn "    export TENCENT_COS_SECRET_ID='<ID>' TENCENT_COS_SECRET_KEY='<KEY>' ..."
    warn "    $0 --from-env"
    echo ""
    do_setup "$@"
    ;;
  *)
    echo "腾讯云 COS Skill 设置工具"
    echo ""
    echo "用法:"
    echo "  $0 --check-only"
    echo "    仅检查环境状态"
    echo ""
    echo "  $0 --from-env"
    echo "    从已有环境变量读取凭证（推荐，避免凭证出现在 shell 历史中）"
    echo "    需先设置: TENCENT_COS_SECRET_ID, TENCENT_COS_SECRET_KEY, TENCENT_COS_REGION, TENCENT_COS_BUCKET"
    echo ""
    echo "  $0 --secret-id <ID> --secret-key <KEY> --region <REGION> --bucket <BUCKET> [--dataset <NAME>] [--domain <DOMAIN>] [--service-domain <DOMAIN>] [--protocol <PROTOCOL>]"
    echo "    自动设置环境（⚠️ 凭证会出现在 shell 历史中）"
    echo ""
    echo "凭证处理策略："
    echo "  • 凭证仅导出到当前 shell session，不自动写入 ~/.zshrc 或 ~/.bashrc"
    echo "  • mcporter 配置写入 ~/.mcporter/mcporter.json（权限 600）"
    echo "  • coscmd 配置写入 ~/.cos.conf（权限 600，仅当 coscmd 已安装时）"
    ;;
esac
