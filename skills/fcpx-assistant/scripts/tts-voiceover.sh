#!/bin/bash
# tts-voiceover.sh - 用 Qwen TTS 为文案生成配音
#
# 使用方式:
#   bash tts-voiceover.sh --script "第一段\n第二段\n第三段" --output ./voiceover/
#   bash tts-voiceover.sh --script-file ./script.txt --output ./voiceover/ --merge
#   bash tts-voiceover.sh --script "文案" --instruct "温柔的女声" --output ./vo/
#
# 依赖：curl, jq, ffmpeg (用于修剪静音)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 默认参数
SCRIPT_TEXT=""
SCRIPT_FILE=""
OUTPUT_DIR="./voiceover"
TTS_HOST="http://127.0.0.1:7860"
INSTRUCT="活泼开朗的年轻男声，语调轻快有活力"
SPEAKER="default"
LANGUAGE="auto"
MODEL="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
TTS_OUTPUT_DIR="/Users/stevegao/qwen-tts-webui/outputs"
TRIM_SILENCE=true
SILENCE_THRESHOLD="-40dB"
POLL_INTERVAL=2
MAX_WAIT=120
MERGE_MODE=false  # 新增：合并模式，一次性生成

usage() {
    cat << EOF
用法：$0 [选项]

必需:
  --script, -s        文案内容 (每行一段)
  --script-file       文案文件路径

可选:
  --output, -o        输出目录 (默认：./voiceover)
  --instruct          声音特征描述 (默认：活泼开朗的年轻男声)
  --speaker           发言人 (默认：default)
  --language          语言 (默认：auto)
  --tts-host          TTS 服务地址 (默认：http://127.0.0.1:7860)
  --merge             合并文案一次性生成 (音色一致，强烈推荐！)
  --no-trim           不修剪静音
  --cleanup           生成后清理 TTS 输出目录的临时文件
  --help              显示帮助

示例:
  # 分段生成 (每段独立调用 TTS，音色可能有差异)
  bash $0 --script-file ./script.txt --output ./voiceover/
  
  # 合并生成 (一次性生成完整文案，音色一致)
  bash $0 --script-file ./script.txt --output ./voiceover/ --merge
  
  # 合并生成 + 清理临时文件
  bash $0 --script-file ./script.txt --output ./voiceover/ --merge --cleanup
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --script|-s) SCRIPT_TEXT="$2"; shift 2 ;;
        --script-file) SCRIPT_FILE="$2"; shift 2 ;;
        --output|-o) OUTPUT_DIR="$2"; shift 2 ;;
        --instruct) INSTRUCT="$2"; shift 2 ;;
        --speaker) SPEAKER="$2"; shift 2 ;;
        --language) LANGUAGE="$2"; shift 2 ;;
        --tts-host) TTS_HOST="$2"; shift 2 ;;
        --merge) MERGE_MODE=true; shift ;;
        --no-trim) TRIM_SILENCE=false; shift ;;
        --cleanup) CLEANUP_TTS=true; shift ;;
        --help) usage ;;
        *) echo "未知参数：$1"; usage ;;
    esac
done

if [[ -n "$SCRIPT_FILE" ]] && [[ -f "$SCRIPT_FILE" ]]; then
    SCRIPT_TEXT=$(cat "$SCRIPT_FILE")
fi

if [[ -z "$SCRIPT_TEXT" ]]; then
    echo -e "${RED}❌ 必须提供 --script 或 --script-file${NC}"
    usage
fi

mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}🎙️ TTS 配音生成器${NC}"
echo -e "声音：${GREEN}$INSTRUCT${NC}"
echo -e "输出：${GREEN}$OUTPUT_DIR${NC}"
echo -e "模式：${GREEN}${MERGE_MODE:+合并一次性生成}${MERGE_MODE:-分段生成}${NC}"
echo ""

# 检查 TTS 服务
if ! curl -s "${TTS_HOST}/gradio_api/info" >/dev/null 2>&1; then
    echo -e "${RED}❌ TTS 服务未运行 ($TTS_HOST)${NC}"
    echo -e "${YELLOW}请先启动 Qwen TTS WebUI${NC}"
    exit 1
fi
echo -e "${GREEN}✅ TTS 服务在线${NC}"
echo ""

# 拆分段落
PARAGRAPHS=()
while IFS= read -r line; do
    trimmed=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [[ -n "$trimmed" ]]; then
        PARAGRAPHS+=("$trimmed")
    fi
done <<< "$SCRIPT_TEXT"

NUM_PARAGRAPHS=${#PARAGRAPHS[@]}
echo -e "文案段落：${GREEN}$NUM_PARAGRAPHS${NC}"
echo ""

# === 合并模式：一次性生成完整配音 ===
if [[ "$MERGE_MODE" == true ]]; then
    echo -e "${BLUE}🎤 合并模式：将所有文案合并后一次性生成${NC}"
    
    # 合并所有段落为一个完整文本
    FULL_TEXT=$(printf '%s ' "${PARAGRAPHS[@]}")
    echo -e "   总字符数：${GREEN}${#FULL_TEXT}${NC}"
    
    # 记录生成前的文件列表
    BEFORE=$(ls -1t "$TTS_OUTPUT_DIR"/*.wav 2>/dev/null | head -1 || echo "")
    
    # 调用 TTS API 一次性生成
    echo -e "${BLUE}🚀 调用 TTS API...${NC}"
    RESP=$(curl -s "${TTS_HOST}/gradio_api/call/generate_voice_fn" \
        -H "Content-Type: application/json" \
        -d "$(jq -n --arg model "$MODEL" \
                     --arg text "$FULL_TEXT" \
                     --arg instruct "$INSTRUCT" \
                     --arg speaker "$SPEAKER" \
                     --arg lang "$LANGUAGE" \
                     '{data: [$model, $text, $instruct, $speaker, $lang, false]}')" 2>/dev/null)
    
    EVENT_ID=$(echo "$RESP" | jq -r '.event_id // empty' 2>/dev/null)
    
    if [[ -z "$EVENT_ID" ]]; then
        echo -e "${RED}❌ API 调用失败${NC}"
        exit 1
    fi
    
    # 等待生成完成
    echo -e "${BLUE}⏳ 等待生成完成...${NC}"
    WAITED=0
    NEW_FILE=""
    while [[ "$WAITED" -lt "$MAX_WAIT" ]]; do
        sleep "$POLL_INTERVAL"
        WAITED=$((WAITED + POLL_INTERVAL))
        
        AFTER=$(ls -1t "$TTS_OUTPUT_DIR"/*.wav 2>/dev/null | head -1 || echo "")
        if [[ "$AFTER" != "$BEFORE" ]] && [[ -n "$AFTER" ]]; then
            sleep 1  # 等文件写入完成
            NEW_FILE="$AFTER"
            break
        fi
    done
    
    if [[ -z "$NEW_FILE" ]]; then
        echo -e "${RED}❌ 生成超时 (${MAX_WAIT}s)${NC}"
        exit 1
    fi
    
    # 处理生成的音频
    OUTPUT_FILE="$OUTPUT_DIR/full_voiceover.wav"
    
    if [[ "$TRIM_SILENCE" == "true" ]]; then
        echo -e "${BLUE}✂️  修剪首尾静音...${NC}"
        ffmpeg -y -i "$NEW_FILE" \
            -af "silenceremove=start_periods=1:start_threshold=${SILENCE_THRESHOLD}:start_duration=0.05,areverse,silenceremove=start_periods=1:start_threshold=${SILENCE_THRESHOLD}:start_duration=0.05,areverse" \
            "$OUTPUT_FILE" \
            -loglevel warning 2>/dev/null
    else
        cp "$NEW_FILE" "$OUTPUT_FILE"
    fi
    
    if [[ -f "$OUTPUT_FILE" ]]; then
        DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT_FILE" 2>/dev/null)
        FSIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null | awk '{printf "%.1f", $1/1024/1024}')
        echo -e "${GREEN}✅ 完整配音生成成功！${NC}"
        echo -e "   时长：${DUR}s"
        echo -e "   大小：${FSIZE}MB"
        echo -e "   文件：${OUTPUT_FILE}"
        
        # 清理 TTS 输出目录的临时文件
        if [[ "${CLEANUP_TTS:-false}" == true ]]; then
            echo -e "${BLUE}🗑️  清理 TTS 临时文件...${NC}"
            trash "$NEW_FILE" 2>/dev/null || rm -f "$NEW_FILE"
            echo -e "${GREEN}✅ 清理完成${NC}"
        fi
    else
        echo -e "${RED}❌ 音频处理失败${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ 配音文件保存在：$OUTPUT_DIR${NC}"
    echo -e "${BLUE}下一步：用 auto-video-maker.sh --voiceover $OUTPUT_DIR/ 组装成片！${NC}"
    exit 0
fi

# === 分段模式：逐段生成（兼容旧版）===
echo -e "${YELLOW}⚠️  分段模式：每段独立生成，音色可能有差异${NC}"
echo -e "${BLUE}💡 提示：使用 --merge 参数可启用合并模式，音色更一致${NC}"
echo ""

# 记录 TTS 输出目录的当前文件（用于检测新文件）
BEFORE_FILES=$(ls -1 "$TTS_OUTPUT_DIR"/*.wav 2>/dev/null | sort)

GENERATED=0
AUDIO_FILES=()

for i in $(seq 0 $((NUM_PARAGRAPHS - 1))); do
    PARA="${PARAGRAPHS[$i]}"
    echo -e "${BLUE}🎤 段落 $((i+1))/$NUM_PARAGRAPHS: \"${PARA:0:40}...\"${NC}"
    
    # 记录生成前的文件列表
    BEFORE=$(ls -1t "$TTS_OUTPUT_DIR"/*.wav 2>/dev/null | head -1)
    
    # 调用 TTS API
    RESP=$(curl -s "${TTS_HOST}/gradio_api/call/generate_voice_fn" \
        -H "Content-Type: application/json" \
        -d "$(jq -n --arg model "$MODEL" \
                     --arg text "$PARA" \
                     --arg instruct "$INSTRUCT" \
                     --arg speaker "$SPEAKER" \
                     --arg lang "$LANGUAGE" \
                     '{data: [$model, $text, $instruct, $speaker, $lang, false]}')" 2>/dev/null)
    
    EVENT_ID=$(echo "$RESP" | jq -r '.event_id // empty' 2>/dev/null)
    
    if [[ -z "$EVENT_ID" ]]; then
        echo -e "   ${RED}❌ API 调用失败${NC}"
        continue
    fi
    
    # 等待生成完成（检测新文件出现）
    WAITED=0
    NEW_FILE=""
    while [[ "$WAITED" -lt "$MAX_WAIT" ]]; do
        sleep "$POLL_INTERVAL"
        WAITED=$((WAITED + POLL_INTERVAL))
        
        AFTER=$(ls -1t "$TTS_OUTPUT_DIR"/*.wav 2>/dev/null | head -1)
        if [[ "$AFTER" != "$BEFORE" ]] && [[ -n "$AFTER" ]]; then
            sleep 1
            NEW_FILE="$AFTER"
            break
        fi
    done
    
    if [[ -z "$NEW_FILE" ]]; then
        echo -e "   ${RED}❌ 生成超时 (${MAX_WAIT}s)${NC}"
        continue
    fi
    
    OUTPUT_FILE="$OUTPUT_DIR/vo_$(printf '%03d' $i).wav"
    
    if [[ "$TRIM_SILENCE" == "true" ]]; then
        ffmpeg -y -i "$NEW_FILE" \
            -af "silenceremove=start_periods=1:start_threshold=${SILENCE_THRESHOLD}:start_duration=0.05,areverse,silenceremove=start_periods=1:start_threshold=${SILENCE_THRESHOLD}:start_duration=0.05,areverse" \
            "$OUTPUT_FILE" \
            -loglevel warning 2>/dev/null
    else
        cp "$NEW_FILE" "$OUTPUT_FILE"
    fi
    
    if [[ -f "$OUTPUT_FILE" ]]; then
        DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT_FILE" 2>/dev/null | cut -d. -f1-2)
        echo -e "   ${GREEN}✅ vo_$(printf '%03d' $i).wav (${DUR}s)${NC}"
        AUDIO_FILES+=("$OUTPUT_FILE")
        GENERATED=$((GENERATED + 1))
        
        # 清理临时文件
        if [[ "${CLEANUP_TTS:-false}" == true ]]; then
            trash "$NEW_FILE" 2>/dev/null || rm -f "$NEW_FILE"
        fi
    else
        echo -e "   ${RED}❌ 音频处理失败${NC}"
    fi
    
    sleep 1
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎙️ 配音生成完成！${NC}"
echo -e "   生成：${GREEN}${GENERATED}/${NUM_PARAGRAPHS}${NC} 段"
echo ""

for f in "$OUTPUT_DIR"/vo_*.wav; do
    [[ -f "$f" ]] || continue
    DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null)
    echo -e "   $(basename "$f"): ${DUR}s"
done

echo ""

# 合并所有段落
if [[ "$GENERATED" -gt 0 ]]; then
    CONCAT_LIST="$OUTPUT_DIR/concat.txt"
    > "$CONCAT_LIST"
    for f in "$OUTPUT_DIR"/vo_*.wav; do
        [[ -f "$f" ]] || continue
        echo "file '$(realpath "$f")'" >> "$CONCAT_LIST"
    done
    
    FULL_VO="$OUTPUT_DIR/full_voiceover.wav"
    ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" -c copy "$FULL_VO" -loglevel warning 2>/dev/null
    
    if [[ -f "$FULL_VO" ]]; then
        FULL_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$FULL_VO" 2>/dev/null)
        echo -e "   📎 完整配音：full_voiceover.wav (${FULL_DUR}s)"
    fi
    
    rm -f "$CONCAT_LIST"
fi

echo ""
echo -e "${GREEN}✅ 配音文件保存在：$OUTPUT_DIR${NC}"
echo -e "${BLUE}下一步：用 auto-video-maker.sh --voiceover $OUTPUT_DIR/ 组装成片！${NC}"
