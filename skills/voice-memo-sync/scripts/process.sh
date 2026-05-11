#!/bin/bash
# Voice Memo Sync - 统一处理脚本
# Usage: ./process.sh <input> [--type voice|url|text|file]
#
# 支持输入:
#   - Voice Memos路径 (.qta/.m4a)
#   - iCloud文件路径
#   - YouTube/Bilibili URL
#   - 音视频文件路径
#   - 文本文件路径 (.txt)

set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
DATA_DIR="$WORKSPACE/memory/voice-memos"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TODAY=$(date +%Y-%m-%d)

INPUT="$1"
TYPE="${2:---auto}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[VMS]${NC} $1"; }
warn() { echo -e "${YELLOW}[VMS]${NC} $1"; }
error() { echo -e "${RED}[VMS]${NC} $1"; exit 1; }

# 自动检测输入类型
detect_type() {
    local input="$1"
    
    if [[ "$input" =~ ^https?://(www\.)?(youtube\.com|youtu\.be) ]]; then
        echo "youtube"
    elif [[ "$input" =~ ^https?://(www\.)?bilibili\.com ]]; then
        echo "bilibili"
    elif [[ "$input" =~ \.(qta|m4a)$ ]]; then
        echo "voice_memo"
    elif [[ "$input" =~ \.(mp3|wav|aac|flac)$ ]]; then
        echo "audio"
    elif [[ "$input" =~ \.(mp4|mov|mkv|webm)$ ]]; then
        echo "video"
    elif [[ "$input" =~ \.(txt|md)$ ]]; then
        echo "text"
    elif [[ "$input" =~ \.(doc|docx)$ ]]; then
        echo "document"
    elif [[ "$input" =~ \.json$ ]]; then
        echo "json"
    elif [[ "$input" =~ \.csv$ ]]; then
        echo "csv"
    else
        echo "unknown"
    fi
}

# 提取Apple原生转录
extract_apple_transcript() {
    local file="$1"
    python3 "$SCRIPT_DIR/extract-apple-transcript.py" "$file" 2>/dev/null
}

# Whisper转录 (优先使用Metal加速的whisper-cpp)
whisper_transcribe() {
    local file="$1"
    local output_dir="$DATA_DIR/transcripts"
    local lang="${2:-auto}"
    local basename=$(basename "${file%.*}")
    
    # 优先使用whisper-cpp (Metal GPU加速, 15-20x faster)
    if command -v whisper-cpp &> /dev/null || command -v whisper-cli &> /dev/null; then
        local whisper_cmd=$(command -v whisper-cpp || command -v whisper-cli)
        local model_path="$HOME/.cache/whisper-cpp/ggml-small.bin"
        
        # 检查模型文件
        if [ ! -f "$model_path" ]; then
            log "下载whisper-cpp模型..."
            mkdir -p "$HOME/.cache/whisper-cpp"
            curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin" \
                -o "$model_path" 2>/dev/null
        fi
        
        # whisper-cpp需要wav格式
        local wav_file="/tmp/whisper_$$_${basename}.wav"
        log "转换为WAV格式 (Metal加速)..."
        ffmpeg -i "$file" -ar 16000 -ac 1 -c:a pcm_s16le "$wav_file" -y 2>/dev/null
        
        log "使用Metal GPU加速转录..."
        "$whisper_cmd" -m "$model_path" -l "$lang" -otxt -of "$output_dir/$basename" "$wav_file" 2>/dev/null
        
        rm -f "$wav_file"
        cat "$output_dir/${basename}.txt" 2>/dev/null
        
    # 回退到openai-whisper (CPU)
    elif command -v whisper &> /dev/null; then
        warn "使用CPU转录 (较慢)，建议安装whisper-cpp: brew install whisper-cpp"
        whisper "$file" --model small --language "$lang" \
            --output_dir "$output_dir" --output_format txt 2>/dev/null
        cat "$output_dir/${basename}.txt"
    else
        error "Whisper未安装，请运行: brew install whisper-cpp (推荐) 或 brew install openai-whisper"
    fi
}

# 处理YouTube
process_youtube() {
    local url="$1"
    local output_file="$DATA_DIR/transcripts/${TODAY}_youtube_$(echo "$url" | md5 -q | cut -c1-8).txt"
    
    if command -v summarize &> /dev/null; then
        log "使用summarize提取YouTube转录..."
        summarize "$url" --youtube auto --extract-only > "$output_file" 2>/dev/null
        cat "$output_file"
    else
        log "summarize未安装，使用yt-dlp下载音频..."
        local audio_file="/tmp/yt_audio_$$.mp3"
        yt-dlp -x --audio-format mp3 -o "$audio_file" "$url" --no-playlist
        whisper_transcribe "$audio_file"
        rm -f "$audio_file"
    fi
}

# 处理Bilibili
process_bilibili() {
    local url="$1"
    local audio_file="/tmp/bilibili_audio_$$.mp3"
    
    log "下载B站视频音频..."
    yt-dlp -x --audio-format mp3 -o "$audio_file" "$url" --no-playlist 2>&1
    
    if [ -f "$audio_file" ]; then
        log "音频下载完成，开始转录..."
        whisper_transcribe "$audio_file"
        rm -f "$audio_file"
    else
        error "B站音频下载失败"
    fi
}

# 处理语音备忘录
process_voice_memo() {
    local file="$1"
    local filename=$(basename "$file")
    local transcript_file="$DATA_DIR/transcripts/${TODAY}_voicememo_${filename%.*}.txt"
    
    # 尝试提取Apple原生转录
    log "尝试提取Apple原生转录..."
    local apple_transcript=$(extract_apple_transcript "$file")
    
    if [ -n "$apple_transcript" ] && [ "$apple_transcript" != "null" ]; then
        log "成功提取Apple原生转录"
        echo "$apple_transcript" > "$transcript_file"
        cat "$transcript_file"
    else
        log "无Apple转录，使用Whisper..."
        whisper_transcribe "$file" > "$transcript_file"
        cat "$transcript_file"
    fi
}

# 处理普通音频
process_audio() {
    local file="$1"
    whisper_transcribe "$file"
}

# 处理视频
process_video() {
    local file="$1"
    local audio_file="/tmp/video_audio_$$.mp3"
    
    log "提取视频音频..."
    ffmpeg -i "$file" -vn -acodec mp3 -ab 128k "$audio_file" -y 2>/dev/null
    whisper_transcribe "$audio_file"
    rm -f "$audio_file"
}

# 处理文本
process_text() {
    local file="$1"
    cat "$file"
}

# 处理Word文档 (.doc/.docx)
process_document() {
    local file="$1"
    local temp_txt="/tmp/doc_convert_$$.txt"
    
    log "转换Word文档..."
    # macOS自带textutil
    textutil -convert txt -output "$temp_txt" "$file" 2>/dev/null
    cat "$temp_txt"
    rm -f "$temp_txt"
}

# 处理JSON
process_json() {
    local file="$1"
    log "处理JSON文件..."
    # 提取文本内容，格式化输出
    python3 -c "
import json
import sys
with open('$file', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
def extract_text(obj, depth=0):
    if isinstance(obj, str):
        print(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) > 20:
                print(f'{k}: {v}')
            else:
                extract_text(v, depth+1)
    elif isinstance(obj, list):
        for item in obj:
            extract_text(item, depth+1)

extract_text(data)
"
}

# 处理CSV
process_csv() {
    local file="$1"
    log "处理CSV文件..."
    # 转为可读格式
    python3 -c "
import csv
with open('$file', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        for k, v in row.items():
            if v and len(str(v)) > 10:
                print(f'{k}: {v}')
        print('---')
"
}

# 主处理流程
main() {
    if [ -z "$INPUT" ]; then
        error "用法: $0 <input> [--type voice|url|text|file]"
    fi
    
    # 检测类型
    if [ "$TYPE" == "--auto" ]; then
        TYPE=$(detect_type "$INPUT")
    fi
    
    log "输入: $INPUT"
    log "类型: $TYPE"
    
    # 保存源信息
    local source_file="$DATA_DIR/sources/${TODAY}_$(echo "$INPUT" | md5 -q | cut -c1-8).json"
    mkdir -p "$DATA_DIR/sources"
    cat > "$source_file" << EOF
{
  "input": "$INPUT",
  "type": "$TYPE",
  "date": "$TODAY",
  "timestamp": "$(date -Iseconds)"
}
EOF
    
    # 根据类型处理
    case "$TYPE" in
        youtube)
            process_youtube "$INPUT"
            ;;
        bilibili)
            process_bilibili "$INPUT"
            ;;
        voice_memo)
            process_voice_memo "$INPUT"
            ;;
        audio)
            process_audio "$INPUT"
            ;;
        video)
            process_video "$INPUT"
            ;;
        text)
            process_text "$INPUT"
            ;;
        document)
            process_document "$INPUT"
            ;;
        json)
            process_json "$INPUT"
            ;;
        csv)
            process_csv "$INPUT"
            ;;
        *)
            error "无法识别输入类型: $INPUT"
            ;;
    esac
}

main "$@"
