#!/usr/bin/env bash
# Muse Skill 一键部署
# 适用于所有支持 skills 的 AI CLI（Claude Code / OpenClaw / Kimi CLI / Qwen Code 等）
#
# 用法:
#   bash install.sh                      # 自动检测已安装的 CLI
#   bash install.sh --target claude      # 指定安装到 Claude Code
#   bash install.sh --target openclaw    # 指定安装到 OpenClaw
#   bash install.sh --target kimi        # 指定安装到 Kimi CLI
#   bash install.sh --target qwen        # 指定安装到 Qwen Code
#   bash install.sh --path /custom/dir   # 自定义安装路径
#   bash install.sh --uninstall          # 卸载（可搭配 --target 或 --path）

set -e

VERSION="1.0.6"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$HOME/.muse"

# ── CLI 目录映射 ──
get_skill_dir() {
  case "$1" in
    claude)   echo "$HOME/.claude/skills/muse" ;;
    openclaw) echo "$HOME/.openclaw/skills/muse" ;;
    kimi)     echo "$HOME/.config/agents/skills/muse" ;;
    qwen)     echo "$HOME/.qwen/skills/muse" ;;
    *)        echo "" ;;
  esac
}

get_cli_label() {
  case "$1" in
    claude)   echo "Claude Code" ;;
    openclaw) echo "OpenClaw" ;;
    kimi)     echo "Kimi CLI" ;;
    qwen)     echo "Qwen Code" ;;
  esac
}

# ── 自动检测已安装的 CLI ──
detect_clis() {
  DETECTED=""
  DETECTED_COUNT=0

  for cli in claude openclaw kimi qwen; do
    cli_found=false
    case "$cli" in
      claude)   [ -d "$HOME/.claude" ] && cli_found=true ;;
      openclaw) ([ -d "$HOME/.openclaw" ] || command -v openclaw >/dev/null 2>&1) && cli_found=true ;;
      kimi)     command -v kimi >/dev/null 2>&1 && cli_found=true ;;
      qwen)     ([ -d "$HOME/.qwen" ] || command -v qwen >/dev/null 2>&1) && cli_found=true ;;
    esac

    if [ "$cli_found" = true ]; then
      DETECTED="$DETECTED $cli"
      DETECTED_COUNT=$((DETECTED_COUNT + 1))
    fi
  done
}

# ── 解析参数 ──
TARGET=""
CUSTOM_PATH=""
UNINSTALL=false

while [ $# -gt 0 ]; do
  case "$1" in
    --uninstall)  UNINSTALL=true; shift ;;
    --target)
      if [ -z "$2" ] || [ "${2#--}" != "$2" ]; then
        echo "❌ --target 需要指定目标: claude / openclaw / kimi / qwen"
        exit 1
      fi
      TARGET="$2"; shift 2 ;;
    --path)
      if [ -z "$2" ] || [ "${2#--}" != "$2" ]; then
        echo "❌ --path 需要指定目录路径"
        exit 1
      fi
      CUSTOM_PATH="$2"; shift 2 ;;
    *)
      echo "❌ 未知参数: $1"
      echo "用法: bash install.sh [--target claude|openclaw|kimi|qwen] [--path /dir] [--uninstall]"
      exit 1 ;;
  esac
done

# ── 确定安装目录 ──
resolve_skill_dir() {
  if [ -n "$CUSTOM_PATH" ]; then
    SKILL_DIR="$CUSTOM_PATH"
    return
  fi

  if [ -n "$TARGET" ]; then
    SKILL_DIR=$(get_skill_dir "$TARGET")
    if [ -z "$SKILL_DIR" ]; then
      echo "❌ 未知目标: $TARGET"
      echo "   支持: claude / openclaw / kimi / qwen"
      exit 1
    fi
    return
  fi

  # 自动检测
  detect_clis

  if [ "$DETECTED_COUNT" -eq 0 ]; then
    echo "⚠️  未检测到已安装的 AI CLI，将安装到 Claude Code 默认目录"
    echo "   支持的 CLI: Claude Code / OpenClaw / Kimi CLI / Qwen Code"
    echo "   可用 --target 或 --path 手动指定"
    echo ""
    SKILL_DIR=$(get_skill_dir "claude")
  elif [ "$DETECTED_COUNT" -eq 1 ]; then
    cli=$(echo "$DETECTED" | tr -d ' ')
    label=$(get_cli_label "$cli")
    echo "✅ 检测到 $label"
    SKILL_DIR=$(get_skill_dir "$cli")
  else
    echo "检测到多个 AI CLI:"
    echo ""
    i=1
    for cli in $DETECTED; do
      label=$(get_cli_label "$cli")
      dir=$(get_skill_dir "$cli")
      echo "  $i) $label → $dir"
      i=$((i + 1))
    done
    echo ""
    printf "请选择安装目标 [1]: "
    read -r choice
    [ -z "$choice" ] && choice=1

    i=1
    SKILL_DIR=""
    for cli in $DETECTED; do
      if [ "$i" -eq "$choice" ] 2>/dev/null; then
        SKILL_DIR=$(get_skill_dir "$cli")
        break
      fi
      i=$((i + 1))
    done

    if [ -z "$SKILL_DIR" ]; then
      echo "❌ 无效选择"
      exit 1
    fi
  fi
}

resolve_skill_dir

# ── 卸载模式 ──
if [ "$UNINSTALL" = true ]; then
  echo "🗑  正在卸载 Muse Skill..."
  if [ -d "$SKILL_DIR" ]; then
    rm -rf "$SKILL_DIR"
    echo "✅ Muse Skill 已从 $SKILL_DIR 卸载"
  else
    echo "⚠️  未找到安装目录: $SKILL_DIR"
  fi
  echo "   Token 数据保留在 $DATA_DIR"
  echo "   如需彻底清除: rm -rf $DATA_DIR"
  exit 0
fi

# ── Python 检查 ──
# 优先 python3，兼容部分系统只有 python 的情况
PYTHON=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
fi

if [ -z "$PYTHON" ]; then
  echo "❌ 未检测到 Python，请先安装 Python 3.6+"
  echo "   Ubuntu/Debian: sudo apt install python3"
  echo "   macOS: brew install python3"
  exit 1
fi

PY_VER=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 6 ]); then
  echo "❌ Python $PY_VER 版本过低，需要 3.6+"
  echo "   Ubuntu/Debian: sudo apt install python3"
  echo "   macOS: brew install python3"
  exit 1
fi

# ── 部署 ──
echo "🎵 Muse Skill v$VERSION 安装中..."

mkdir -p "$DATA_DIR"

# 旧版数据迁移：~/.claude/.muse → ~/.muse
OLD_DATA_DIR="$HOME/.claude/.muse"
if [ -d "$OLD_DATA_DIR" ] && [ ! -f "$DATA_DIR/device_id" ]; then
  echo "   迁移旧版数据..."
  cp -r "$OLD_DATA_DIR"/* "$DATA_DIR/" 2>/dev/null || true
fi

# 升级安装：清理旧版本目录，确保无残留文件
if [ -d "$SKILL_DIR" ]; then
  echo "   检测到旧版本，正在升级..."
  rm -rf "$SKILL_DIR"
fi
mkdir -p "$SKILL_DIR"

# 排除非运行时文件
EXCLUDE_FILES="README.md LICENSE package.json install.sh install.bat .git"

for item in "$SCRIPT_DIR"/*; do
  name=$(basename "$item")
  skip=false
  for ex in $EXCLUDE_FILES; do
    [ "$name" = "$ex" ] && skip=true && break
  done
  [ "$skip" = true ] && continue
  cp -r "$item" "$SKILL_DIR/"
done

# ── 安装验证 ──
VERIFY_OK=true

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "❌ 安装异常：SKILL.md 缺失"
  VERIFY_OK=false
fi

if ! $PYTHON "$SKILL_DIR/scripts/muse_api.py" device-id >/dev/null 2>&1; then
  echo "❌ 安装异常：Python 脚本无法正常运行"
  VERIFY_OK=false
fi

if [ "$VERIFY_OK" = false ]; then
  echo "⚠️  安装可能不完整，请检查上述错误后重试"
  exit 1
fi

echo ""
echo "✅ Muse Skill v$VERSION 安装成功"
echo "   技能目录: $SKILL_DIR"
echo "   数据目录: $DATA_DIR"
echo "   Python:   $PY_VER ($PYTHON)"
echo ""
echo "在对话中发送「做首歌」即可开始创作 🎶"
