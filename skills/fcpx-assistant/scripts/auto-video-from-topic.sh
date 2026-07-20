#!/bin/bash
# Auto Video From Topic - 从主题到发布一键完成
# Usage: bash scripts/auto-video-from-topic.sh --topic "主题" --publish bilibili --title "标题"

set -e

# 默认参数
TOPIC=""
STYLE="vlog"
DURATION=60
PLATFORM=""
PUBLISH_TITLE=""
PUBLISH_DESCRIPTION=""
PUBLISH_TAGS=""
OUTPUT_DIR="$HOME/Desktop/视频项目_$(date +%Y%m%d_%H%M%S)"
SKIP_PUBLISH=false

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_step() { echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${MAGENTA}📍 Step $1: $2${NC}"; echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 帮助信息
show_help() {
    cat << EOF
🎬 从主题到发布 - 全自动视频生产线

输入一个主题，自动生成文案、搜集素材、配音、成片、上传发布。

用法:
  bash $0 --topic "主题" [选项]

必需选项:
  --topic "主题"      视频主题（必需）

可选选项:
  --style <风格>      文案风格：vlog, 科普，教程，带货，故事 (默认：vlog)
  --duration <秒>     视频时长：30, 60, 90, 120, 180 (默认：60)
  --output <目录>     项目输出目录 (默认：~/Desktop/视频项目_时间戳)
  
  --publish <平台>    自动上传到：bilibili, youtube, tiktok, xiaohongshu
  --title "标题"      发布时的标题 (默认：从主题生成)
  --description "描述" 发布描述 (可选)
  --tags "标签"       发布标签，逗号分隔 (可选)
  
  --skip-publish      跳过发布，只生成视频
  --help              显示帮助信息

完整流程:
  1. AI 生成文案 → 2. 搜集素材 → 3. TTS 配音 → 4. 自动成片 → 5. 上传发布

示例:
  # 生成视频但不发布
  bash $0 --topic "如何制作一杯完美的咖啡" --style 教程 --duration 90
  
  # 生成并发布到 B 站
  bash $0 --topic "今天的旅行见闻" --publish bilibili --title "一个人的旅行" --tags "vlog，旅行"
  
  # 发布到 YouTube
  bash $0 --topic "My Daily Life" --style vlog --publish youtube --title "A Day in My Life"

EOF
    exit 0
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --topic)
            TOPIC="$2"
            shift 2
            ;;
        --style)
            STYLE="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --publish)
            PLATFORM="$2"
            shift 2
            ;;
        --title)
            PUBLISH_TITLE="$2"
            shift 2
            ;;
        --description)
            PUBLISH_DESCRIPTION="$2"
            shift 2
            ;;
        --tags)
            PUBLISH_TAGS="$2"
            shift 2
            ;;
        --skip-publish)
            SKIP_PUBLISH=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "未知参数：$1"
            show_help
            ;;
    esac
done

# 检查必需参数
if [[ -z "$TOPIC" ]]; then
    print_error "缺少必需参数：--topic"
    show_help
fi

# 如果没有指定发布平台，默认跳过发布
if [[ -z "$PLATFORM" ]]; then
    SKIP_PUBLISH=true
fi

# 设置默认发布标题
if [[ -z "$PUBLISH_TITLE" ]]; then
    PUBLISH_TITLE="$TOPIC"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
print_step "0" "准备工作"
echo ""

# 创建项目目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/videos"
mkdir -p "$OUTPUT_DIR/music"
mkdir -p "$OUTPUT_DIR/voiceover"
mkdir -p "$OUTPUT_DIR/output"

print_info "项目目录：$OUTPUT_DIR"
print_info "主题：$TOPIC"
print_info "风格：$STYLE"
print_info "时长：${DURATION}秒"
[[ -n "$PLATFORM" ]] && print_info "发布平台：$PLATFORM"

echo ""

# Step 1: AI 生成文案
print_step "1" "AI 生成文案 📝"
echo ""

SCRIPT_FILE="$OUTPUT_DIR/script.txt"
KEYWORDS_FILE="$OUTPUT_DIR/keywords.txt"

bash "$SCRIPT_DIR/ai-script-generator.sh" \
    --topic "$TOPIC" \
    --style "$STYLE" \
    --duration "$DURATION" \
    --output "$SCRIPT_FILE" \
    --keywords

print_success "文案生成完成"
echo ""

# Step 2: 搜集素材
print_step "2" "搜集视频素材 🔍"
echo ""

# 从文案中提取关键词（简化版，实际可以用 AI 提取）
KEYWORDS="$TOPIC background scene"

bash "$SCRIPT_DIR/media-collector.sh" \
    --keywords "$KEYWORDS" \
    --count 10 \
    --output "$OUTPUT_DIR"

print_success "素材搜集完成"
echo ""

# Step 3: TTS 配音
print_step "3" "生成 TTS 配音 🎤"
echo ""

bash "$SCRIPT_DIR/tts-voiceover.sh" \
    --script-file "$SCRIPT_FILE" \
    --output "$OUTPUT_DIR/voiceover/voiceover"

print_success "配音生成完成"
echo ""

# Step 4: 自动成片
print_step "4" "自动成片 🎞️"
echo ""

FINAL_VIDEO="$OUTPUT_DIR/output/final.mp4"

bash "$SCRIPT_DIR/auto-video-maker.sh" \
    --project "$OUTPUT_DIR" \
    --script-file "$SCRIPT_FILE" \
    --voiceover "$OUTPUT_DIR/voiceover" \
    --style "$STYLE" \
    --output "$FINAL_VIDEO"

print_success "视频生成完成"
print_info "输出文件：$FINAL_VIDEO"
echo ""

# Step 5: 上传发布
if [[ "$SKIP_PUBLISH" == false ]]; then
    print_step "5" "上传发布 🚀"
    echo ""
    
    bash "$SCRIPT_DIR/auto-publish.sh" \
        --video "$FINAL_VIDEO" \
        --platform "$PLATFORM" \
        --title "$PUBLISH_TITLE" \
        ${PUBLISH_DESCRIPTION:+--description "$PUBLISH_DESCRIPTION"} \
        ${PUBLISH_TAGS:+--tags "$PUBLISH_TAGS"}
    
    print_success "发布流程完成"
    echo ""
else
    echo ""
    print_info "跳过发布步骤"
    print_info "如需手动上传，运行："
    echo "  bash $SCRIPT_DIR/auto-publish.sh --video $FINAL_VIDEO --platform <平台> --title \"标题\""
    echo ""
fi

# 完成总结
echo ""
print_step "✓" "全部完成！🎉"
echo ""
print_success "视频已生成：$FINAL_VIDEO"
echo ""
print_info "项目文件位置:"
echo "  📁 项目目录：$OUTPUT_DIR"
echo "  📝 文案：$SCRIPT_FILE"
echo "  🎬 成品视频：$FINAL_VIDEO"
echo ""

if [[ -n "$PLATFORM" ]]; then
    print_info "发布状态:"
    echo "  📤 平台：$PLATFORM"
    echo "  📛 标题：$PUBLISH_TITLE"
    echo ""
    print_warning "请检查平台后台确认上传状态"
fi

echo ""
print_info "下次可以这样快速生成："
echo "  bash $0 --topic \"新主题\" --publish $PLATFORM"
echo ""
