#!/bin/bash
# setup.sh - 初始化 thu-thesis 工作环境
#
# 功能：
#   1. 从 GitHub 拉取最新 thuthesis 源码
#   2. 编译生成 thuthesis.cls（如尚未生成）
#   3. 将 data/ 目录复制为 assets/databk/（格式参考基准）
#
# 用法：
#   bash setup.sh [skill目录]
#
# 环境变量（可选）：
#   THUTHESIS_DIR   - 指定已有的 thuthesis 目录（跳过拉取步骤）
#   XELATEX_PATH    - xelatex 完整路径（默认自动探测）

set -e

SKILL_DIR="${1:-$(dirname "$0")/..}"
SKILL_DIR="$(cd "$SKILL_DIR" && pwd)"
ASSETS_DIR="$SKILL_DIR/assets"
DATABK_DIR="$ASSETS_DIR/databk"
TMP_DIR="${THUTHESIS_DIR:-/tmp/thuthesis-latest}"

# ── 安全检查：禁止对敏感路径执行 rm -rf ──
_is_safe_tmpdir() {
  local p
  p="$(cd "$1" 2>/dev/null && pwd || echo "$1")"
  # 必须是 /tmp/ 下的目录，或明确是用户指定的 THUTHESIS_DIR（此时跳过删除）
  [[ "$p" == /tmp/* ]]
}


echo "=== thu-thesis 环境初始化 ==="
echo "Skill 目录: $SKILL_DIR"
echo "thuthesis 目录: $TMP_DIR"

# ── 探测 xelatex ──
if [ -n "$XELATEX_PATH" ]; then
  XELATEX="$XELATEX_PATH"
elif [ -f "/Library/TeX/texbin/xelatex" ]; then
  XELATEX="/Library/TeX/texbin/xelatex"
elif command -v xelatex &>/dev/null; then
  XELATEX="$(command -v xelatex)"
else
  echo "⚠️  未找到 xelatex，跳过 .cls 编译（可手动设置 XELATEX_PATH）"
  XELATEX=""
fi
[ -n "$XELATEX" ] && echo "xelatex: $XELATEX"

# ── 1. 拉取最新 thuthesis ──
echo ""
echo "[1/3] 拉取最新 thuthesis..."
if [ -d "$TMP_DIR/.git" ]; then
  echo "  已存在，执行 git pull..."
  git -C "$TMP_DIR" pull --quiet
else
  echo "  克隆 https://github.com/tuna/thuthesis ..."
  if _is_safe_tmpdir "$TMP_DIR"; then
    rm -rf "$TMP_DIR"
  else
    echo "  ⚠️  $TMP_DIR 不在 /tmp/ 下，跳过删除（保留现有内容直接 clone 到新目录不可行）"
    echo "  ❌ 请手动清理后重试，或不设置 THUTHESIS_DIR 使用默认路径 /tmp/thuthesis-latest"
    exit 1
  fi
  git clone --depth=1 --quiet https://github.com/tuna/thuthesis.git "$TMP_DIR"
fi
echo "  ✅ thuthesis 拉取完成"

# ── 2. 编译生成 thuthesis.cls ──
echo ""
echo "[2/3] 编译 thuthesis.cls ..."
if [ -f "$TMP_DIR/thuthesis.cls" ]; then
  echo "  ✅ thuthesis.cls 已存在，跳过编译"
elif [ -n "$XELATEX" ] && [ -f "$TMP_DIR/thuthesis.ins" ]; then
  (cd "$TMP_DIR" && "$XELATEX" -interaction=nonstopmode thuthesis.ins > /dev/null 2>&1)
  if [ -f "$TMP_DIR/thuthesis.cls" ]; then
    echo "  ✅ thuthesis.cls 编译成功"
  else
    echo "  ❌ 编译失败，请手动运行："
    echo "     cd $TMP_DIR && xelatex thuthesis.ins"
  fi
else
  echo "  ⚠️  跳过（无 xelatex 或无 .ins 文件）"
fi

# ── 3. 复制 data/ → assets/databk/ ──
echo ""
echo "[3/3] 更新 assets/databk/ ..."
if [ ! -d "$TMP_DIR/data" ]; then
  echo "  ⚠️  未找到 data/ 目录，跳过"
else
  rm -rf "$DATABK_DIR"
  cp -r "$TMP_DIR/data" "$DATABK_DIR"
  echo "  ✅ databk 已更新（$(ls "$DATABK_DIR" | wc -l | tr -d ' ') 个文件）"
fi

echo ""
echo "=== 初始化完成 ==="
echo "thuthesis 源码：$TMP_DIR"
echo "格式参考：$DATABK_DIR"
echo ""
echo "可选环境变量："
echo "  THUTHESIS_DIR=/path/to/thuthesis  # 使用本地已有版本"
echo "  XELATEX_PATH=/path/to/xelatex     # 指定 xelatex 路径"
