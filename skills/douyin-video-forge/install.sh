#!/bin/bash
set -e

# douyin-video-forge v3.0 安装脚本
# 用法: bash install.sh

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

SKILL_NAME="douyin-video-forge"
SKILL_DIR="$HOME/.openclaw/skills/$SKILL_NAME"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

info()    { echo -e "${CYAN}[信息]${NC} $1"; }
success() { echo -e "${GREEN}[成功]${NC} $1"; }
warn()    { echo -e "${YELLOW}[警告]${NC} $1"; }
error()   { echo -e "${RED}[错误]${NC} $1"; exit 1; }

echo -e "\n${BOLD}${CYAN}=== douyin-video-forge v3.0 安装 ===${NC}\n"

# --- 1. 必需工具检查 ---
echo -e "${BOLD}[1/4] 检查必需工具${NC}"
command -v ffmpeg &>/dev/null && success "ffmpeg 已安装" || error "缺少 ffmpeg — brew install ffmpeg (macOS) / apt install ffmpeg (Linux)"
command -v yt-dlp &>/dev/null && success "yt-dlp 已安装" || error "缺少 yt-dlp — pip install yt-dlp"

# --- 2. 可选工具检查 ---
echo -e "\n${BOLD}[2/4] 检查可选工具${NC}"
if command -v python3 &>/dev/null; then
    success "python3 已安装 ($(python3 --version 2>&1))"
    # 检查 pyjwt + httpx（Kling API 需要）
    if python3 -c "import jwt, httpx" 2>/dev/null; then
        success "pyjwt + httpx 已安装"
    else
        warn "pyjwt/httpx 未安装 — Kling API 视频生成需要这两个包"
        info "安装: pip install pyjwt httpx"
    fi
    # 检查 faster-whisper（语音转写需要）
    if python3 -c "import faster_whisper" 2>/dev/null; then
        success "faster-whisper 已安装"
    else
        info "faster-whisper 未安装（可选，语音转写需要）— pip install faster-whisper"
    fi
else
    info "python3 未安装（可选 — 仅 Kling API 视频生成和语音转写需要）"
fi

# --- 3. 复制 Skill ---
echo -e "\n${BOLD}[3/4] 安装 Skill${NC}"
mkdir -p "$HOME/.openclaw/skills"
if [[ -d "$SKILL_DIR" ]]; then
    warn "已存在 $SKILL_DIR，正在覆盖更新..."
    rm -rf "$SKILL_DIR"
fi
cp -R "$SCRIPT_DIR" "$SKILL_DIR"
# 清理安装目录中不需要的文件
rm -rf "$SKILL_DIR/.git" "$SKILL_DIR/.env" "$SKILL_DIR/.DS_Store"
rm -rf "$SKILL_DIR/mcp_server"
success "已安装到 $SKILL_DIR"

# --- 4. 完成 ---
echo -e "\n${BOLD}[4/4] 安装完成${NC}"

KLING_STATUS="${YELLOW}未配置${NC}"
if [[ -n "${KLING_ACCESS_KEY:-}" && -n "${KLING_SECRET_KEY:-}" ]]; then
    KLING_STATUS="${GREEN}已配置${NC}"
fi

echo ""
echo -e "${BOLD}${GREEN}=== 安装成功！(v3.0) ===${NC}"
echo ""
echo -e "  安装路径:     $SKILL_DIR"
echo -e "  Kling API:    $KLING_STATUS"
echo -e "  数据采集:     ${GREEN}浏览器模式（无需 API Key）${NC}"
echo ""
echo -e "${BOLD}快速开始:${NC}"
echo -e "  在 OpenClaw 中输入 ${GREEN}'帮我制作抖音短视频'${NC} 即可开始"
echo ""
echo -e "${BOLD}可选配置:${NC}"
echo -e "  Kling API:    export KLING_ACCESS_KEY=xxx KLING_SECRET_KEY=xxx"
echo -e "  获取地址:     ${CYAN}https://klingai.com${NC}"
echo ""
