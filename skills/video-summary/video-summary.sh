#!/bin/bash

# Video Summary - AI-powered video summarization for multiple platforms
# Supports: YouTube, Bilibili, Xiaohongshu, Douyin, and local files
# 视频摘要 - AI 驱动的多平台视频摘要工具
# 支持：YouTube、B站、小红书、抖音及本地文件

set -e

# Colors for output | 输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values | 默认值
OUTPUT_FORMAT="text"
EXTRACT_SUBTITLE_ONLY=false
ENABLE_CHAPTERS=false
LANGUAGE="auto"
TRANSCRIBE=false
WHISPER_MODEL="${VIDEO_SUMMARY_WHISPER_MODEL:-base}"
OUTPUT_PATH=""
COOKIE_FILE="${VIDEO_SUMMARY_COOKIES:-}"

# API Configuration | API 配置
# User must set OPENAI_API_KEY and OPENAI_BASE_URL environment variables
# 用户必须设置 OPENAI_API_KEY 和 OPENAI_BASE_URL 环境变量
# This script does NOT auto-detect or collect any credentials
# 本脚本不会自动检测或收集任何凭证

# Temporary files cleanup | 临时文件清理
TEMP_FILES=()
cleanup() {
    if [[ ${#TEMP_FILES[@]} -gt 0 ]]; then
        rm -f "${TEMP_FILES[@]}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Help message | 帮助信息
show_help() {
    cat << EOF
video-summary - AI-powered video summarization | AI 视频摘要工具

Usage | 用法:
    video-summary <url> [options]
    video-summary <file> [options]

Options | 选项:
    --chapter         Generate chapter-by-chapter breakdown | 分章节详细解析
    --subtitle        Extract transcript only (no AI summary) | 仅提取字幕（不生成摘要）
    --json            Output in JSON format | JSON 格式输出
    --lang <code>     Specify subtitle language (default: auto) | 指定字幕语言（默认：自动）
    --transcribe      Force transcription with Whisper | 强制使用 Whisper 转写
    --output <path>   Save output to file | 保存输出到文件
    --cookies <file>  Use cookies file for restricted content | 使用 cookies 文件访问受限内容
    --help            Show this help message | 显示帮助信息

Examples | 示例:
    video-summary "https://www.bilibili.com/video/BV1xx411c7mu"
    video-summary "https://www.youtube.com/watch?v=xxxxx" --chapter
    video-summary "https://www.xiaohongshu.com/explore/xxxxx" --json
    video-summary "https://v.douyin.com/xxxxx" --transcribe
    video-summary ./video.mp4 --output summary.md

Supported Platforms | 支持平台:
    - YouTube (youtube.com, youtu.be)
    - Bilibili (bilibili.com)
    - Xiaohongshu (xiaohongshu.com, xhslink.com)
    - Douyin (douyin.com, v.douyin.com)
    - Local files (mp4, mkv, webm, mp3, etc.) | 本地文件

Environment Variables | 环境变量:
    VIDEO_SUMMARY_WHISPER_MODEL  Whisper model size (tiny/base/small/medium/large)
    VIDEO_SUMMARY_COOKIES        Path to cookies file for restricted content
    OPENAI_API_KEY               For OpenAI GPT summarization
    OPENAI_BASE_URL              Custom API endpoint (optional)

Performance Estimation | 性能预估:
    Video Duration | tiny | base | small
    5 min          | ~30s | ~1m  | ~2m
    30 min         | ~3m  | ~6m  | ~15m
    60 min         | ~6m  | ~12m | ~30m

EOF
}

# Check dependencies | 检查依赖
check_dependencies() {
    local missing=()
    
    if ! command -v yt-dlp &> /dev/null; then
        missing+=("yt-dlp")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing+=("jq")
    fi
    
    if ! command -v ffmpeg &> /dev/null; then
        missing+=("ffmpeg")
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "${RED}Error: Missing required dependencies: ${missing[*]}${NC}" >&2
        echo -e "${YELLOW}Install with:${NC}" >&2
        echo "  pip install yt-dlp" >&2
        echo "  apt install jq ffmpeg  # or brew install jq ffmpeg" >&2
        exit 1
    fi
}

# Estimate processing time | 估算处理时间
estimate_time() {
    local duration_seconds="$1"
    local duration_minutes=$((duration_seconds / 60))
    local model="$WHISPER_MODEL"
    
    local multiplier=1
    case "$model" in
        tiny) multiplier=0.1 ;;
        base) multiplier=0.2 ;;
        small) multiplier=0.5 ;;
        medium) multiplier=1 ;;
        large) multiplier=2 ;;
    esac
    
    local estimated_minutes=$(echo "$duration_minutes * $multiplier" | bc 2>/dev/null || echo "$duration_minutes")
    
    if [[ $(echo "$estimated_minutes < 1" | bc 2>/dev/null || echo 0) -eq 1 ]]; then
        echo "约 1 分钟"
    else
        echo "约 ${estimated_minutes%.*} 分钟"
    fi
}

# Parse arguments | 解析参数
parse_args() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 1
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --chapter)
                ENABLE_CHAPTERS=true
                shift
                ;;
            --subtitle)
                EXTRACT_SUBTITLE_ONLY=true
                shift
                ;;
            --json)
                OUTPUT_FORMAT="json"
                shift
                ;;
            --lang)
                LANGUAGE="$2"
                shift 2
                ;;
            --transcribe)
                TRANSCRIBE=true
                shift
                ;;
            --output)
                OUTPUT_PATH="$2"
                shift 2
                ;;
            --cookies)
                COOKIE_FILE="$2"
                shift 2
                ;;
            -*)
                echo -e "${RED}Error: Unknown option $1${NC}" >&2
                show_help
                exit 1
                ;;
            *)
                INPUT="$1"
                shift
                ;;
        esac
    done

    if [[ -z "$INPUT" ]]; then
        echo -e "${RED}Error: No input URL or file specified${NC}" >&2
        exit 1
    fi
}

# Detect platform from URL | 检测平台
detect_platform() {
    local url="$1"
    
    if [[ "$url" =~ youtube\.com|youtu\.be ]]; then
        echo "youtube"
    elif [[ "$url" =~ bilibili\.com ]]; then
        echo "bilibili"
    elif [[ "$url" =~ xiaohongshu\.com|xhslink\.com ]]; then
        echo "xiaohongshu"
    elif [[ "$url" =~ douyin\.com ]]; then
        echo "douyin"
    elif [[ -f "$url" ]]; then
        echo "local"
    else
        echo "unknown"
    fi
}

# Build yt-dlp cookie args | 构建 cookie 参数
build_cookie_args() {
    if [[ -n "$COOKIE_FILE" && -f "$COOKIE_FILE" ]]; then
        echo "--cookies $COOKIE_FILE"
    fi
    echo ""
}

# Get video info using yt-dlp | 获取视频信息
get_video_info() {
    local url="$1"
    local info
    
    echo -e "${BLUE}正在获取视频信息...${NC}" >&2
    
    local cookie_args=$(build_cookie_args)
    info=$(yt-dlp $cookie_args --dump-json --no-download "$url" 2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}Error: Failed to fetch video info${NC}" >&2
        echo -e "${YELLOW}Tip: Try using --cookies for restricted content | 提示：受限内容请使用 --cookies${NC}" >&2
        return 1
    fi
    
    echo "$info"
}

# Extract subtitles using yt-dlp | 提取字幕
extract_subtitles() {
    local url="$1"
    local lang="$2"
    local subtitle_file
    
    echo -e "${BLUE}正在提取字幕...${NC}" >&2
    
    local cookie_args=$(build_cookie_args)
    
    # Try manual subtitles first | 优先尝试手动字幕
    subtitle_file=$(yt-dlp $cookie_args --write-sub --sub-lang "$lang" --skip-download \
        --print subtitle_file "$url" 2>/dev/null || true)
    
    if [[ -n "$subtitle_file" && -f "$subtitle_file" ]]; then
        cat "$subtitle_file"
        rm -f "$subtitle_file"
        TEMP_FILES+=("$subtitle_file")
        return 0
    fi
    
    # Try auto-generated subtitles | 尝试自动生成字幕
    subtitle_file=$(yt-dlp $cookie_args --write-auto-sub --sub-lang "$lang" --skip-download \
        --convert-subs srt --print subtitle_file "$url" 2>/dev/null || true)
    
    if [[ -n "$subtitle_file" && -f "$subtitle_file" ]]; then
        cat "$subtitle_file"
        rm -f "$subtitle_file"
        TEMP_FILES+=("$subtitle_file")
        return 0
    fi
    
    echo -e "${YELLOW}Warning: No subtitles found | 警告：未找到字幕${NC}" >&2
    return 1
}

# Transcribe video using Whisper | 使用 Whisper 转写
transcribe_video() {
    local url="$1"
    local temp_audio="/tmp/video-summary-audio-$$"
    TEMP_FILES+=("${temp_audio}.*")
    
    local estimated=$(estimate_time "$2")
    echo -e "${BLUE}正在使用 Whisper 转写（${estimated}）...${NC}" >&2
    
    # Check if whisper is installed | 检查 whisper 是否安装
    if ! command -v whisper &> /dev/null; then
        echo -e "${RED}Error: Whisper not installed | 错误：Whisper 未安装${NC}" >&2
        echo -e "${YELLOW}Install with: pip install openai-whisper${NC}" >&2
        return 1
    fi
    
    # Download audio | 下载音频
    local cookie_args=$(build_cookie_args)
    yt-dlp $cookie_args -x --audio-format mp3 -o "${temp_audio}.%(ext)s" "$url" 2>/dev/null
    
    # Find the actual audio file | 查找实际音频文件
    local audio_file=$(ls ${temp_audio}.* 2>/dev/null | head -1)
    
    if [[ -z "$audio_file" ]]; then
        echo -e "${RED}Error: Failed to download audio${NC}" >&2
        return 1
    fi
    
    TEMP_FILES+=("$audio_file")
    
    # Transcribe | 转写
    local output_dir="/tmp/video-summary-$$"
    mkdir -p "$output_dir"
    TEMP_FILES+=("$output_dir")
    
    whisper "$audio_file" --model "$WHISPER_MODEL" --output_format txt \
        --output_dir "$output_dir" 2>/dev/null
    
    local transcript_file=$(ls ${output_dir}/*.txt 2>/dev/null | head -1)
    
    if [[ -f "$transcript_file" ]]; then
        cat "$transcript_file"
        return 0
    fi
    
    return 1
}

# Transcribe local file | 转写本地文件
transcribe_local() {
    local file="$1"
    
    # Get duration | 获取时长
    local duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$file" 2>/dev/null || echo "0")
    local estimated=$(estimate_time "${duration%.*}")
    
    echo -e "${BLUE}正在转写本地文件（${estimated}）...${NC}" >&2
    
    if ! command -v whisper &> /dev/null; then
        echo -e "${RED}Error: Whisper not installed${NC}" >&2
        return 1
    fi
    
    local output_dir="/tmp/video-summary-local-$$"
    mkdir -p "$output_dir"
    TEMP_FILES+=("$output_dir")
    
    whisper "$file" --model "$WHISPER_MODEL" --output_format txt \
        --output_dir "$output_dir" 2>/dev/null
    
    local transcript_file=$(ls ${output_dir}/*.txt 2>/dev/null | head -1)
    
    if [[ -f "$transcript_file" ]]; then
        cat "$transcript_file"
        return 0
    fi
    
    return 1
}

# Clean subtitle format | 清理字幕格式
clean_subtitle() {
    local subtitle="$1"
    
    # Remove WebVTT/SSA/SRT formatting | 移除字幕格式
    echo "$subtitle" | \
        sed 's/<[^>]*>//g' | \
        sed '/^[0-9]/d' | \
        sed '/^$/d' | \
        sed 's/&nbsp;/ /g' | \
        tr '\n' ' ' | \
        sed 's/  */ /g'
}

# Call LLM for summarization | 调用 LLM 生成摘要
# Note: This function outputs a request structure for external processing.
# Network calls are handled by the caller (agent or external tool).
# 注意：此函数输出请求结构供外部处理，网络调用由调用方（agent 或外部工具）处理。
call_llm() {
    local transcript="$1"
    local title="$2"
    local platform="$3"
    local mode="$4"  # "summary" or "chapter"
    
    # Save transcript to temp file | 保存字幕到临时文件
    local temp_file="/tmp/video-summary-transcript-$$"
    echo "$transcript" > "$temp_file"
    TEMP_FILES+=("$temp_file")
    
    # Output structured request for agent/external processing
    # 输出结构化请求供 agent/外部处理
    if [[ "$mode" == "chapter" ]]; then
        cat << EOF
# Chapter-Based Video Summary Request | 分章节视频摘要请求

**Title | 标题**: $title
**Platform | 平台**: $platform
**Transcript File | 字幕文件**: $temp_file
**API Endpoint**: ${OPENAI_BASE_URL:-https://api.openai.com}/v1/chat/completions
**Model**: ${OPENAI_MODEL:-gpt-4o-mini}

## Summary Format | 摘要格式
Create a chapter-by-chapter summary of the transcript.
请根据字幕文件生成分章节摘要。

For each chapter | 每个章节:
- Identify the main topic | 识别主题
- Summarize key points | 总结要点
- Note important timestamps | 记录时间戳
- Extract actionable insights | 提取可执行建议

EOF
    else
        cat << EOF
# Video Summary Request | 视频摘要请求

**Title | 标题**: $title
**Platform | 平台**: $platform
**Transcript File | 字幕文件**: $temp_file
**API Endpoint**: ${OPENAI_BASE_URL:-https://api.openai.com}/v1/chat/completions
**Model**: ${OPENAI_MODEL:-gpt-4o-mini}

## Summary Format | 摘要格式
Summarize the transcript file.
请根据字幕文件生成结构化摘要。

Generate | 生成:
- Core content overview | 核心内容概述
- Key points (3-5 items) | 关键观点 3-5 条
- Timestamp navigation | 时间戳导航
- Actionable takeaways | 可执行建议

EOF
    fi
}

# Output result | 输出结果
output_result() {
    local content="$1"
    
    if [[ -n "$OUTPUT_PATH" ]]; then
        echo "$content" > "$OUTPUT_PATH"
        echo -e "${GREEN}Output saved to: $OUTPUT_PATH${NC}" >&2
    else
        echo "$content"
    fi
}

# Main function | 主函数
main() {
    # Check dependencies | 检查依赖
    check_dependencies
    
    parse_args "$@"
    
    local platform=$(detect_platform "$INPUT")
    
    echo -e "${GREEN}Platform detected | 检测到平台: $platform${NC}" >&2
    
    # Get video info | 获取视频信息
    local video_info
    local title="Unknown"
    local duration=0
    local author="Unknown"
    
    if [[ "$platform" != "local" ]]; then
        video_info=$(get_video_info "$INPUT")
        if [[ $? -eq 0 ]]; then
            title=$(echo "$video_info" | jq -r '.title // "Unknown"')
            duration=$(echo "$video_info" | jq -r '.duration // 0')
            author=$(echo "$video_info" | jq -r '.uploader // .channel // "Unknown"')
        fi
    else
        title=$(basename "$INPUT")
        # Get local file duration | 获取本地文件时长
        duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$INPUT" 2>/dev/null || echo "0")
        author="Local File | 本地文件"
    fi
    
    # Extract or transcribe | 提取或转写
    local transcript=""
    
    if [[ "$TRANSCRIBE" == true || "$platform" == "xiaohongshu" || "$platform" == "douyin" || "$platform" == "local" ]]; then
        # Need transcription | 需要转写
        if [[ "$platform" == "local" ]]; then
            transcript=$(transcribe_local "$INPUT")
        else
            transcript=$(transcribe_video "$INPUT" "$duration")
        fi
    else
        # Try subtitles first | 优先尝试字幕
        transcript=$(extract_subtitles "$INPUT" "$LANGUAGE")
        
        if [[ -z "$transcript" ]]; then
            echo -e "${YELLOW}No subtitles available, falling back to transcription...${NC}" >&2
            echo -e "${YELLOW}无可用手幕，回退到转写模式...${NC}" >&2
            transcript=$(transcribe_video "$INPUT" "$duration")
        fi
    fi
    
    if [[ -z "$transcript" ]]; then
        echo -e "${RED}Error: Could not extract or transcribe video content${NC}" >&2
        echo -e "${RED}错误：无法提取或转写视频内容${NC}" >&2
        exit 1
    fi
    
    # Clean transcript | 清理字幕
    transcript=$(clean_subtitle "$transcript")
    
    # Output based on flags | 根据参数输出
    if [[ "$EXTRACT_SUBTITLE_ONLY" == true ]]; then
        output_result "$transcript"
    elif [[ "$ENABLE_CHAPTERS" == true ]]; then
        local result=$(call_llm "$transcript" "$title" "$platform" "chapter")
        output_result "$result"
    else
        local result=$(call_llm "$transcript" "$title" "$platform" "summary")
        output_result "$result"
    fi
    
    echo -e "${GREEN}Done! | 完成！${NC}" >&2
}

# Run main | 运行主函数
main "$@"
