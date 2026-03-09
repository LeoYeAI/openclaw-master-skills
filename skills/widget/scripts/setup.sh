#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
CHECK_ONLY=0

if [ "${1:-}" = "--check" ] || [ "${1:-}" = "--doctor" ]; then
  CHECK_ONLY=1
fi

find_uebersicht_app() {
  local app
  for app in /Applications/*bersicht.app; do
    if [ -d "$app" ]; then
      echo "$app"
      return 0
    fi
  done
  return 1
}

require_brew() {
  if command -v brew >/dev/null 2>&1; then
    return 0
  fi
  echo -e "${RED}✗${NC} 未找到 Homebrew，请先安装：https://brew.sh"
  exit 1
}

get_release_metadata() {
  require_brew
  brew info --cask --json=v2 ubersicht | python3 -c '
import json, sys
data = json.load(sys.stdin)["casks"][0]
print(data["url"])
print(data["sha256"])
print(data["version"])
'
}

verify_sha256() {
  local file="$1"
  local expected="$2"
  local actual
  actual="$(shasum -a 256 "$file" | awk "{print \$1}")"
  [ "$actual" = "$expected" ]
}

install_uebersicht_app() {
  local metadata url sha256 version
  metadata="$(get_release_metadata)"
  url="$(printf '%s\n' "$metadata" | sed -n '1p')"
  sha256="$(printf '%s\n' "$metadata" | sed -n '2p')"
  version="$(printf '%s\n' "$metadata" | sed -n '3p')"
  local widgetdesk_cache="$HOME/Library/Caches/widgetdesk"
  local homebrew_cache="$HOME/Library/Caches/Homebrew/downloads"
  local zip_path="$widgetdesk_cache/Uebersicht-${version}.app.zip"
  local cached_homebrew_zip=""
  local tmpdir extracted_app dest_app

  mkdir -p "$widgetdesk_cache"

  cached_homebrew_zip="$(find "$homebrew_cache" -maxdepth 1 -type f -name "*--Uebersicht-${version}.app.zip" 2>/dev/null | head -1 || true)"
  if [ -n "$cached_homebrew_zip" ] && verify_sha256 "$cached_homebrew_zip" "$sha256"; then
    zip_path="$cached_homebrew_zip"
    echo -e "${GREEN}✓${NC} 复用已下载的 Übersicht 安装包"
  else
    if [ ! -f "$zip_path" ] || ! verify_sha256 "$zip_path" "$sha256"; then
      echo -e "${YELLOW}→${NC} 正在下载 Übersicht ${version}..."
      curl -fL "$url" -o "$zip_path"
    fi
    if ! verify_sha256 "$zip_path" "$sha256"; then
      echo -e "${RED}✗${NC} Übersicht 安装包校验失败"
      exit 1
    fi
  fi

  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' RETURN
  ditto -x -k "$zip_path" "$tmpdir"
  extracted_app="$(find "$tmpdir" -maxdepth 2 -type d -name '*bersicht.app' | head -1 || true)"

  if [ -z "$extracted_app" ]; then
    echo -e "${RED}✗${NC} 无法从安装包中找到 Übersicht.app"
    exit 1
  fi

  dest_app="/Applications/$(basename "$extracted_app")"
  echo -e "${YELLOW}→${NC} 正在安装 $(basename "$extracted_app") 到 /Applications..."
  ditto "$extracted_app" "$dest_app"
  xattr -dr com.apple.quarantine "$dest_app" 2>/dev/null || true
  echo -e "${GREEN}✓${NC} Übersicht 已安装 → $dest_app"
}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_SKILL_DIR="$HOME/.claude/skills/widget"
INSTALLED_SKILL_FILE="$TARGET_SKILL_DIR/SKILL.md"

echo ""
echo "WidgetDesk Skill Setup (Claude Code)"
echo "===================================="
echo ""

if [ "$CHECK_ONLY" -eq 1 ]; then
  echo "运行模式：只检查，不做安装"
else
  echo "运行模式：安装或修复依赖，并在结束时验证环境"
  echo ""
fi

APP_PATH="$(find_uebersicht_app || true)"
if [ -n "$APP_PATH" ]; then
  echo -e "${GREEN}✓${NC} Übersicht 已安装"
else
  if [ "$CHECK_ONLY" -eq 1 ]; then
    echo -e "${RED}✗${NC} 未检测到 Übersicht"
    echo "  运行：bash scripts/setup.sh"
    exit 1
  fi
  echo -e "${YELLOW}→${NC} 正在安装 Übersicht..."
  install_uebersicht_app
  APP_PATH="$(find_uebersicht_app || true)"
  if [ -z "$APP_PATH" ]; then
    echo -e "${RED}✗${NC} 未找到 Übersicht.app，请确认安装是否成功"
    exit 1
  fi
  open "$APP_PATH"
  echo -e "${GREEN}✓${NC} Übersicht 安装完成"
fi

WIDGET_DIR="$HOME/Library/Application Support/Übersicht/widgets"
if [ ! -d "$WIDGET_DIR" ]; then
  if [ "$CHECK_ONLY" -eq 1 ]; then
    echo -e "${RED}✗${NC} 未找到 Widget 目录：$WIDGET_DIR"
    echo "  请先手动打开 Übersicht 一次"
    exit 1
  fi
  echo -e "${YELLOW}→${NC} 正在启动 Übersicht 以创建 widget 目录..."
  open "$APP_PATH"
  for _ in 1 2 3 4 5; do
    if [ -d "$WIDGET_DIR" ]; then
      break
    fi
    sleep 1
  done
fi
if [ ! -d "$WIDGET_DIR" ]; then
  echo -e "${RED}✗${NC} 未找到 Widget 目录：$WIDGET_DIR"
  echo "  请先手动打开 Übersicht 一次，然后重新运行 scripts/setup.sh"
  exit 1
fi
echo -e "${GREEN}✓${NC} Widget 目录：$WIDGET_DIR"

if [ ! -f "$SOURCE_SKILL_DIR/SKILL.md" ]; then
  echo -e "${RED}✗${NC} 未找到 skill 文件：$SOURCE_SKILL_DIR/SKILL.md"
  exit 1
fi

if [ "$CHECK_ONLY" -eq 1 ]; then
  echo -e "${GREEN}✓${NC} 项目内 skill 文件完整"
  if [ -f "$INSTALLED_SKILL_FILE" ]; then
    echo -e "${GREEN}✓${NC} 已检测到已安装的 Claude Code skill"
  else
    echo -e "${YELLOW}→${NC} 尚未安装 Claude Code skill 到 ~/.claude/skills/widget/"
  fi
  echo ""
  echo "检查完成。"
  if [ ! -f "$INSTALLED_SKILL_FILE" ]; then
    echo "下一步：运行 bash scripts/setup.sh 完成安装"
  else
    echo "下一步：在 Claude Code 中尝试 /widget add a clock showing the current time"
  fi
  exit 0
fi

mkdir -p "$TARGET_SKILL_DIR/templates" "$TARGET_SKILL_DIR/scripts"

if [ "$SOURCE_SKILL_DIR" != "$TARGET_SKILL_DIR" ]; then
  cp "$SOURCE_SKILL_DIR/SKILL.md" "$TARGET_SKILL_DIR/SKILL.md"
  cp "$SOURCE_SKILL_DIR/patterns.md" "$TARGET_SKILL_DIR/patterns.md"
  cp "$SOURCE_SKILL_DIR/templates/"*.jsx "$TARGET_SKILL_DIR/templates/"
  cp "$SOURCE_SKILL_DIR/scripts/"*.sh "$TARGET_SKILL_DIR/scripts/"
  chmod +x "$TARGET_SKILL_DIR/scripts/"*.sh
  echo -e "${GREEN}✓${NC} Claude Code skill 已安装 → $TARGET_SKILL_DIR"
else
  chmod +x "$TARGET_SKILL_DIR/scripts/"*.sh
  echo -e "${GREEN}✓${NC} 正在使用已安装的 Claude Code skill：$TARGET_SKILL_DIR"
fi

echo ""
echo -e "${GREEN}安装与验证完成！${NC}"
echo ""
echo "诊断命令："
echo "  bash \"$TARGET_SKILL_DIR/scripts/doctor.sh\""
echo ""
echo "使用方式："
echo "  Claude Code：输入 /widget 然后描述你想要的组件"
echo "  例如：/widget 给我在右下角加一个显示天气的组件"
echo ""
echo "内置模板（可直接使用）："
ls "$TARGET_SKILL_DIR/templates/"*.jsx 2>/dev/null | while read -r f; do
  echo "  $(basename "$f")"
done
echo ""
