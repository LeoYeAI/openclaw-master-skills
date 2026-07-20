#!/bin/bash
# AI Script Generator - 根据主题自动生成视频文案
# Usage: bash scripts/ai-script-generator.sh --topic "你的主题" --style vlog --duration 60

set -e

# 默认参数
TOPIC=""
STYLE="vlog"
DURATION=60  # 秒
OUTPUT=""
PLATFORM="general"  # general, tiktok, youtube, bilibili

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 帮助信息
show_help() {
    cat << EOF
📝 AI 文案自动生成器

根据主题自动生成视频脚本，支持不同平台和风格。

用法:
  bash $0 --topic "主题" [选项]

选项:
  --topic <文本>      视频主题（必需）
  --style <风格>      文案风格：vlog, 科普，教程，带货，故事 (默认：vlog)
  --duration <秒>     目标时长：30, 60, 90, 120, 180 (默认：60)
  --platform <平台>   目标平台：general, tiktok, youtube, bilibili (默认：general)
  --output <文件>     输出文件路径 (默认：~/Desktop/脚本_时间戳.txt)
  --keywords          同时输出素材搜索关键词
  --help              显示帮助信息

示例:
  bash $0 --topic "如何制作一杯完美的咖啡" --style 教程 --duration 90
  bash $0 --topic "今天的旅行见闻" --style vlog --platform tiktok --keywords

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
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --keywords)
            KEYWORDS=true
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

# 设置默认输出路径
if [[ -z "$OUTPUT" ]]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT="$HOME/Desktop/脚本_${TIMESTAMP}.txt"
fi

# 创建输出目录
mkdir -p "$(dirname "$OUTPUT")"

print_info "正在生成文案..."
print_info "主题：$TOPIC"
print_info "风格：$STYLE"
print_info "时长：${DURATION}秒"
print_info "平台：$PLATFORM"

# 根据不同平台和风格调整提示词
case $PLATFORM in
    tiktok)
        PLATFORM_HINT="短视频平台，节奏快，前 3 秒必须有钩子吸引注意力，适合竖屏"
        WORD_COUNT=$((DURATION * 3))  # 约 3 字/秒
        ;;
    youtube)
        PLATFORM_HINT="长视频平台，内容深度，适合横屏，可以有片头片尾"
        WORD_COUNT=$((DURATION * 5 / 2))
        ;;
    bilibili)
        PLATFORM_HINT="B 站用户喜欢干货和梗，可以适当玩梗，节奏中等"
        WORD_COUNT=$((DURATION * 14 / 5))
        ;;
    *)
        PLATFORM_HINT="通用格式，适合多平台分发"
        WORD_COUNT=$((DURATION * 5 / 2))
        ;;
esac

case $STYLE in
    vlog)
        STYLE_HINT="轻松自然的 Vlog 风格，第一人称叙述，像是和朋友聊天"
        ;;
    科普)
        STYLE_HINT="科普讲解风格，逻辑清晰，用简单语言解释复杂概念"
        ;;
    教程)
        STYLE_HINT="教程风格，步骤明确，每个步骤有详细说明"
        ;;
    带货)
        STYLE_HINT="带货风格，突出产品卖点，有号召力，引导购买"
        ;;
    故事)
        STYLE_HINT="故事叙述风格，有起承转合，情感丰富"
        ;;
    *)
        STYLE_HINT="通用风格"
        ;;
esac

# 调用 AI 生成文案（使用 OpenClaw 的 sessions_spawn 或外部 API）
# 这里使用一个模拟的 AI 调用，实际使用时可以替换成真实的 AI API

cat > "$OUTPUT" << EOF
# 视频脚本

**主题**: $TOPIC
**风格**: $STYLE
**目标时长**: ${DURATION}秒
**目标平台**: $PLATFORM
**预估字数**: ~${WORD_COUNT}字

---

## 【开场】(0-5 秒)
[吸引注意力的开场白，可以是问题、惊人事实、或视觉冲击]

## 【引入】(5-15 秒)
[介绍主题，说明视频内容，建立期待]

## 【主体内容】(15-${DURATION}秒)
[根据主题展开详细内容]

## 【结尾】(最后 10 秒)
[总结要点，号召行动（点赞/关注/评论）]

---

## 📝 完整文案

（以下是可直接用于 TTS 配音的纯文本，按段落分隔）

EOF

# 使用 AI 生成实际内容
# 这里调用 OpenClaw 的 AI 能力
AI_PROMPT="
请为以下视频生成完整文案：

主题：$TOPIC
风格要求：$STYLE_HINT
平台要求：$PLATFORM_HINT
目标时长：${DURATION}秒
预估字数：~${WORD_COUNT}字

输出格式：
1. 先输出分镜脚本（包含时间码和画面描述）
2. 再输出纯文案（用于 TTS 配音，按段落分隔）

注意：
- 开场要有吸引力
- 节奏符合平台特性
- 语言口语化，适合朗读
- 结尾有号召行动
"

# 如果有 OpenClaw AI，可以这样调用：
# AI_RESPONSE=$(openclaw ai "$AI_PROMPT")
# echo "$AI_RESPONSE" >> "$OUTPUT"

# 临时使用一个示例文案（实际使用时替换为真实 AI 调用）
cat >> "$OUTPUT" << EOFOUT

【示例文案 - 请根据实际 AI 生成替换】

嘿大家好！今天我们来聊聊$TOPIC。

你可能不知道，这里有一些有趣的事实。

让我来详细说说...

[主体内容根据主题展开]

好了，今天的分享就到这里！如果觉得有用，别忘了点赞关注哦！我们下期见！

EOFOUT

# 生成素材搜索关键词
if [[ "$KEYWORDS" == true ]]; then
    cat >> "$OUTPUT" << EOF

---

## 🔍 推荐素材关键词

（可用于 media-collector.sh 搜索素材）

EOF
    
    # 从主题提取关键词（简单实现，可以用 AI 优化）
    KEYWORDS_FILE="${OUTPUT%.txt}_keywords.txt"
    echo "# 素材搜索关键词" > "$KEYWORDS_FILE"
    echo "" >> "$KEYWORDS_FILE"
    echo "主要关键词：" >> "$KEYWORDS_FILE"
    echo "$TOPIC" >> "$KEYWORDS_FILE"
    echo "" >> "$KEYWORDS_FILE"
    echo "扩展关键词：" >> "$KEYWORDS_FILE"
    echo "background, scene, close-up, detail, action" >> "$KEYWORDS_FILE"
    
    print_info "关键词已保存到：$KEYWORDS_FILE"
fi

print_success "文案已生成：$OUTPUT"
print_info "下一步："
echo "  1. 查看并编辑文案（如需要）"
echo "  2. 使用 tts-voiceover.sh 生成配音"
echo "  3. 使用 media-collector.sh 搜集素材"
echo "  4. 使用 auto-video-maker.sh 自动成片"

# 返回输出文件路径
echo "$OUTPUT"
