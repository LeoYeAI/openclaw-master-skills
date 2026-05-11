#!/bin/bash
# Voice Memo Sync - Long Transcription Monitor
# 监控长音频转录任务，确保完成并处理结果
# Usage: ./monitor-transcription.sh <audio_file> [output_name]

set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
DATA_DIR="$WORKSPACE/memory/voice-memos"
LOG_DIR="$DATA_DIR/logs"
TODAY=$(date +%Y-%m-%d)

AUDIO_FILE="$1"
OUTPUT_NAME="${2:-$(basename "${AUDIO_FILE%.*}")}"
LOG_FILE="$LOG_DIR/transcribe_${OUTPUT_NAME}_$(date +%H%M%S).log"
PID_FILE="/tmp/whisper_${OUTPUT_NAME}.pid"
OUTPUT_FILE="$DATA_DIR/transcripts/${TODAY}_${OUTPUT_NAME}.txt"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date +%H:%M:%S)]${NC} $1"; }
error() { echo -e "${RED}[$(date +%H:%M:%S)]${NC} $1"; }

# 检查输入
if [ -z "$AUDIO_FILE" ] || [ ! -f "$AUDIO_FILE" ]; then
    error "Usage: $0 <audio_file> [output_name]"
    exit 1
fi

# 创建目录
mkdir -p "$LOG_DIR" "$DATA_DIR/transcripts"

# 获取音频信息
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO_FILE" 2>/dev/null)
DURATION_MIN=$(echo "scale=1; $DURATION/60" | bc)
FILE_SIZE=$(ls -lh "$AUDIO_FILE" | awk '{print $5}')

log "=========================================="
log "Long Transcription Monitor"
log "=========================================="
log "Input: $AUDIO_FILE"
log "Size: $FILE_SIZE | Duration: ${DURATION_MIN}min"
log "Output: $OUTPUT_FILE"
log "Log: $LOG_FILE"
log ""

# 选择模型（根据时长）
if (( $(echo "$DURATION_MIN > 60" | bc -l) )); then
    MODEL="small"
    warn "Audio > 60min, using 'small' model for speed"
elif (( $(echo "$DURATION_MIN > 30" | bc -l) )); then
    MODEL="small"
else
    MODEL="small"
fi

# 检测语言
log "Detecting language..."
LANG_HINT=$(whisper "$AUDIO_FILE" --model tiny --language auto --output_format txt 2>&1 | grep -o "Detected language: [a-z]*" | cut -d' ' -f3 || echo "en")
log "Detected: $LANG_HINT"

# 估算时间
EST_TIME=$(echo "scale=0; $DURATION_MIN * 2" | bc)  # 粗略估计：2x实时
log "Estimated time: ~${EST_TIME}min"
log ""

# 启动Whisper（后台）
log "Starting Whisper transcription..."
nohup whisper "$AUDIO_FILE" \
    --model "$MODEL" \
    --language "$LANG_HINT" \
    --output_dir "$DATA_DIR/transcripts" \
    --output_format txt \
    --verbose True \
    > "$LOG_FILE" 2>&1 &

WHISPER_PID=$!
echo "$WHISPER_PID" > "$PID_FILE"
log "Whisper PID: $WHISPER_PID"
log ""

# 监控进度
log "Monitoring progress (Ctrl+C to background)..."
LAST_SIZE=0
STALL_COUNT=0
MAX_STALL=10  # 10次无进展则告警

while kill -0 "$WHISPER_PID" 2>/dev/null; do
    # 检查日志大小
    if [ -f "$LOG_FILE" ]; then
        CURRENT_SIZE=$(wc -c < "$LOG_FILE")
        if [ "$CURRENT_SIZE" -eq "$LAST_SIZE" ]; then
            ((STALL_COUNT++))
            if [ "$STALL_COUNT" -ge "$MAX_STALL" ]; then
                warn "Progress stalled for ${STALL_COUNT}0 seconds"
            fi
        else
            STALL_COUNT=0
        fi
        LAST_SIZE=$CURRENT_SIZE
        
        # 显示最后一行进度
        PROGRESS=$(tail -1 "$LOG_FILE" 2>/dev/null | grep -o '\[.*\]' | tail -1 || echo "")
        if [ -n "$PROGRESS" ]; then
            echo -ne "\r  Progress: $PROGRESS          "
        fi
    fi
    sleep 10
done

echo ""

# 检查结果
wait "$WHISPER_PID"
EXIT_CODE=$?
rm -f "$PID_FILE"

if [ $EXIT_CODE -eq 0 ]; then
    # 查找输出文件
    OUTPUT_TXT=$(find "$DATA_DIR/transcripts" -name "$(basename "${AUDIO_FILE%.*}").txt" -newer "$LOG_FILE" 2>/dev/null | head -1)
    
    if [ -n "$OUTPUT_TXT" ] && [ -f "$OUTPUT_TXT" ]; then
        WORD_COUNT=$(wc -w < "$OUTPUT_TXT")
        log "=========================================="
        log "✅ Transcription complete!"
        log "Output: $OUTPUT_TXT"
        log "Words: $WORD_COUNT"
        log "=========================================="
        
        # 重命名为标准格式
        if [ "$OUTPUT_TXT" != "$OUTPUT_FILE" ]; then
            mv "$OUTPUT_TXT" "$OUTPUT_FILE"
            log "Renamed to: $OUTPUT_FILE"
        fi
        
        # 显示预览
        echo ""
        log "Preview (first 500 chars):"
        head -c 500 "$OUTPUT_FILE"
        echo ""
        echo "..."
    else
        error "Transcription completed but output file not found"
        exit 1
    fi
else
    error "Transcription failed with exit code: $EXIT_CODE"
    error "Check log: $LOG_FILE"
    tail -20 "$LOG_FILE"
    exit 1
fi
