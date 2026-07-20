#!/bin/bash
# auto-video-maker.sh - 自动将素材 + 文案 + 音乐组装成完整视频
#
# 使用方式:
#   bash auto-video-maker.sh --project ./project-media --script "文案内容" --output final.mp4
#   bash auto-video-maker.sh --project ./project-media --script-file ./script.txt --style vlog
#   bash auto-video-maker.sh --project ./project-media --script "..." --music ./bgm.mp3 --output video.mp4
#
# 功能:
#   1. 读取文案，按段落拆分
#   2. 匹配视频素材到每个段落
#   3. 裁剪/缩放素材到统一分辨率
#   4. 叠加字幕（烧入文字）
#   5. 混入背景音乐
#   6. 输出成片
#
# 依赖: ffmpeg, ffprobe, jq

set -euo pipefail

# === 颜色 ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# === 默认参数 ===
PROJECT_DIR=""
SCRIPT_TEXT=""
SCRIPT_FILE=""
MUSIC_FILE=""
VOICEOVER_DIR=""
OUTPUT_FILE="output.mp4"
STYLE="default"          # default | vlog | cinematic | fast
RESOLUTION="1920x1080"
FPS=30
FONT_SIZE=42
FONT_COLOR="white"
SUBTITLE_BG="black@0.5"
SUBTITLE_POSITION="bottom"  # bottom | center | top
SECONDS_PER_CHAR=0.15       # 每个字符显示时长（用于计算字幕节奏）
MIN_CLIP_DURATION=3          # 每个片段最短时长
MAX_CLIP_DURATION=8          # 每个片段最长时长
TRANSITION="fade"            # fade | none | dissolve
TRANSITION_DURATION=0.5
PADDING_SECONDS=1            # 段落间额外间隔

usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "必需:"
    echo "  --project, -p       素材目录 (包含 videos/ music/ 子目录)"
    echo "  --script, -s        文案内容 (直接文本)"
    echo "  --script-file       文案文件路径"
    echo ""
    echo "可选:"
    echo "  --music, -m         背景音乐文件路径 (覆盖 project/music/ 中的)"
    echo "  --output, -o        输出文件 (默认: output.mp4)"
    echo "  --style             风格: default/vlog/cinematic/fast"
    echo "  --resolution        分辨率 (默认: 1920x1080)"
    echo "  --fps               帧率 (默认: 30)"
    echo "  --font-size         字幕大小 (默认: 42)"
    echo "  --subtitle-pos      字幕位置: bottom/center/top"
    echo "  --no-subtitle       不添加字幕"
    echo "  --transition        转场: fade/none (默认: fade)"
    echo "  --help              显示帮助"
    exit 0
}

NO_SUBTITLE=false
CLEANUP=false

# === 解析参数 ===
while [[ $# -gt 0 ]]; do
    case $1 in
        --project|-p) PROJECT_DIR="$2"; shift 2 ;;
        --script|-s) SCRIPT_TEXT="$2"; shift 2 ;;
        --script-file) SCRIPT_FILE="$2"; shift 2 ;;
        --music|-m) MUSIC_FILE="$2"; shift 2 ;;
        --voiceover) VOICEOVER_DIR="$2"; shift 2 ;;
        --output|-o) OUTPUT_FILE="$2"; shift 2 ;;
        --style) STYLE="$2"; shift 2 ;;
        --resolution) RESOLUTION="$2"; shift 2 ;;
        --fps) FPS="$2"; shift 2 ;;
        --font-size) FONT_SIZE="$2"; shift 2 ;;
        --subtitle-pos) SUBTITLE_POSITION="$2"; shift 2 ;;
        --no-subtitle) NO_SUBTITLE=true; shift ;;
        --transition) TRANSITION="$2"; shift 2 ;;
        --cleanup) CLEANUP=true; shift ;;
        --help) usage ;;
        *) echo "未知参数: $1"; usage ;;
    esac
done

# === 参数验证 ===
if [[ -z "$PROJECT_DIR" ]]; then
    echo -e "${RED}❌ 必须提供 --project 参数${NC}"
    usage
fi

if [[ -z "$SCRIPT_TEXT" ]] && [[ -z "$SCRIPT_FILE" ]]; then
    echo -e "${RED}❌ 必须提供 --script 或 --script-file${NC}"
    usage
fi

# 读取文案
if [[ -n "$SCRIPT_FILE" ]] && [[ -f "$SCRIPT_FILE" ]]; then
    SCRIPT_TEXT=$(cat "$SCRIPT_FILE")
fi

if [[ -z "$SCRIPT_TEXT" ]]; then
    echo -e "${RED}❌ 文案内容为空${NC}"
    exit 1
fi

# === 解析分辨率 ===
TARGET_W=$(echo "$RESOLUTION" | cut -dx -f1)
TARGET_H=$(echo "$RESOLUTION" | cut -dx -f2)

# === 应用风格预设 ===
case "$STYLE" in
    vlog)
        FONT_SIZE=38
        SECONDS_PER_CHAR=0.12
        MIN_CLIP_DURATION=2
        MAX_CLIP_DURATION=6
        TRANSITION_DURATION=0.3
        ;;
    cinematic)
        FONT_SIZE=48
        SECONDS_PER_CHAR=0.2
        MIN_CLIP_DURATION=4
        MAX_CLIP_DURATION=10
        TRANSITION_DURATION=1.0
        ;;
    fast)
        FONT_SIZE=36
        SECONDS_PER_CHAR=0.08
        MIN_CLIP_DURATION=1.5
        MAX_CLIP_DURATION=4
        TRANSITION_DURATION=0.2
        ;;
esac

# === 创建工作目录 ===
WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

echo -e "${BLUE}🎬 自动成片器${NC}"
echo -e "风格: ${GREEN}$STYLE${NC}"
echo -e "分辨率: ${GREEN}${TARGET_W}x${TARGET_H}${NC}"
echo -e "帧率: ${GREEN}${FPS}fps${NC}"
echo ""

# === Step 1: 拆分文案为段落 ===
echo -e "${CYAN}📝 Step 1: 解析文案...${NC}"

# 按换行分割，去空行，每段作为一个字幕
PARAGRAPHS=()
while IFS= read -r line; do
    # 去除首尾空白
    trimmed=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [[ -n "$trimmed" ]]; then
        PARAGRAPHS+=("$trimmed")
    fi
done <<< "$SCRIPT_TEXT"

NUM_PARAGRAPHS=${#PARAGRAPHS[@]}
echo -e "   文案段落数: ${GREEN}$NUM_PARAGRAPHS${NC}"

if [[ "$NUM_PARAGRAPHS" -eq 0 ]]; then
    echo -e "${RED}❌ 没有有效的文案段落${NC}"
    exit 1
fi

# 计算每段时长
DURATIONS=()
for idx in $(seq 0 $((NUM_PARAGRAPHS - 1))); do
    p="${PARAGRAPHS[$idx]}"
    
    # 如果有配音文件，用配音时长；否则按字符数估算
    VO_FILE=""
    if [[ -n "$VOICEOVER_DIR" ]] && [[ -f "$VOICEOVER_DIR/vo_$(printf '%03d' $idx).wav" ]]; then
        VO_FILE="$VOICEOVER_DIR/vo_$(printf '%03d' $idx).wav"
        DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VO_FILE" 2>/dev/null)
        # 加一点缓冲
        DURATION=$(echo "$DURATION + 0.5" | bc)
        echo -e "   段落 $((idx+1)): \"${p:0:30}...\" → ${DURATION}s (配音)"
    else
        CHAR_COUNT=${#p}
        DURATION=$(echo "$CHAR_COUNT * $SECONDS_PER_CHAR + $PADDING_SECONDS" | bc)
        
        # 限制范围
        if (( $(echo "$DURATION < $MIN_CLIP_DURATION" | bc -l) )); then
            DURATION="$MIN_CLIP_DURATION"
        fi
        if (( $(echo "$DURATION > $MAX_CLIP_DURATION" | bc -l) )); then
            DURATION="$MAX_CLIP_DURATION"
        fi
        echo -e "   段落 $((idx+1)): \"${p:0:30}...\" → ${DURATION}s (估算)"
    fi
    
    DURATIONS+=("$DURATION")
done

TOTAL_DURATION=0
for d in "${DURATIONS[@]}"; do
    TOTAL_DURATION=$(echo "$TOTAL_DURATION + $d" | bc)
done
echo -e "   总时长: ${GREEN}${TOTAL_DURATION}s${NC}"
echo ""

# === Step 2: 收集可用素材 ===
echo -e "${CYAN}📹 Step 2: 收集素材...${NC}"

VIDEOS_DIR="$PROJECT_DIR/videos"
if [[ ! -d "$VIDEOS_DIR" ]]; then
    echo -e "${RED}❌ 找不到视频目录: $VIDEOS_DIR${NC}"
    exit 1
fi

CLIPS=()
while IFS= read -r -d '' f; do
    CLIPS+=("$f")
done < <(find "$VIDEOS_DIR" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.mkv" -o -name "*.avi" \) -print0 | sort -z)

NUM_CLIPS=${#CLIPS[@]}
echo -e "   可用视频素材: ${GREEN}$NUM_CLIPS${NC}"

if [[ "$NUM_CLIPS" -eq 0 ]]; then
    echo -e "${RED}❌ 没有可用的视频素材${NC}"
    exit 1
fi

# 获取每个素材的时长
CLIP_DURATIONS=()
for clip in "${CLIPS[@]}"; do
    DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$clip" 2>/dev/null | cut -d. -f1)
    CLIP_DURATIONS+=("${DUR:-10}")
    echo -e "   $(basename "$clip"): ${DUR:-?}s"
done
echo ""

# === Step 3: 处理每个段落对应的视频片段 ===
echo -e "${CYAN}✂️  Step 3: 剪辑片段...${NC}"

SEGMENT_FILES=()
CLIP_INDEX=0

for i in $(seq 0 $((NUM_PARAGRAPHS - 1))); do
    PARAGRAPH="${PARAGRAPHS[$i]}"
    DURATION="${DURATIONS[$i]}"
    SEGMENT_FILE="$WORK_DIR/segment_$(printf '%03d' $i).mp4"
    
    # 循环选择素材
    CLIP="${CLIPS[$((CLIP_INDEX % NUM_CLIPS))]}"
    CLIP_DUR="${CLIP_DURATIONS[$((CLIP_INDEX % NUM_CLIPS))]}"
    CLIP_INDEX=$((CLIP_INDEX + 1))
    
    echo -e "   段落 $((i+1)): $(basename "$CLIP") → ${DURATION}s"
    
    # 计算起始时间（从素材中间截取，避免头尾）
    AVAIL_DUR=$CLIP_DUR
    if (( $(echo "$AVAIL_DUR > $DURATION + 2" | bc -l) )); then
        # 从中间开始
        START_TIME=$(echo "($AVAIL_DUR - $DURATION) / 2" | bc)
    else
        START_TIME=0
    fi
    
    # 字幕位置
    case "$SUBTITLE_POSITION" in
        top) SUB_Y="y=h*0.1" ;;
        center) SUB_Y="y=(h-text_h)/2" ;;
        bottom|*) SUB_Y="y=h*0.85-text_h" ;;
    esac
    
    # 构建 ffmpeg 滤镜
    # 1. 裁剪时长
    # 2. 缩放到目标分辨率（保持比例 + 黑边/裁切）
    # 3. 添加字幕
    
    SCALE_FILTER="scale=${TARGET_W}:${TARGET_H}:force_original_aspect_ratio=decrease,pad=${TARGET_W}:${TARGET_H}:(ow-iw)/2:(oh-ih)/2:black"
    
    if [[ "$NO_SUBTITLE" == "false" ]]; then
        # 写字幕文本到临时文件（避免 shell 转义问题）
        TEXTFILE="$WORK_DIR/subtitle_${i}.txt"
        echo "$PARAGRAPH" > "$TEXTFILE"
        
        # macOS 简体中文字体路径（优先 PingFang SC）
        CJK_FONT="/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc"
        if [[ ! -f "$CJK_FONT" ]]; then
            CJK_FONT="/System/Library/Fonts/STHeiti Medium.ttc"
        fi
        if [[ ! -f "$CJK_FONT" ]]; then
            CJK_FONT="/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        fi
        
        SUBTITLE_FILTER="drawtext=textfile='${TEXTFILE}':fontfile='${CJK_FONT}':fontsize=${FONT_SIZE}:fontcolor=${FONT_COLOR}:${SUB_Y}:x=(w-text_w)/2:borderw=2:bordercolor=black:box=1:boxcolor=${SUBTITLE_BG}:boxborderw=10"
        FILTER_COMPLEX="${SCALE_FILTER},${SUBTITLE_FILTER},fps=${FPS}"
    else
        FILTER_COMPLEX="${SCALE_FILTER},fps=${FPS}"
    fi
    
    # 检查是否有配音文件
    VO_FILE=""
    if [[ -n "$VOICEOVER_DIR" ]] && [[ -f "$VOICEOVER_DIR/vo_$(printf '%03d' $i).wav" ]]; then
        VO_FILE="$VOICEOVER_DIR/vo_$(printf '%03d' $i).wav"
    fi
    
    if [[ -n "$VO_FILE" ]]; then
        # 有配音：视频 + 配音混合
        ffmpeg -y -ss "$START_TIME" -i "$CLIP" -i "$VO_FILE" -t "$DURATION" \
            -vf "$FILTER_COMPLEX" \
            -c:v libx264 -preset fast -crf 23 \
            -c:a aac -b:a 192k \
            -map 0:v -map 1:a \
            -shortest \
            -pix_fmt yuv420p \
            "$SEGMENT_FILE" \
            -loglevel warning 2>/dev/null
    else
        # 无配音：静音视频
        ffmpeg -y -ss "$START_TIME" -i "$CLIP" -t "$DURATION" \
            -vf "$FILTER_COMPLEX" \
            -c:v libx264 -preset fast -crf 23 \
            -an \
            -pix_fmt yuv420p \
            "$SEGMENT_FILE" \
            -loglevel warning 2>/dev/null
    fi
    
    if [[ -f "$SEGMENT_FILE" ]]; then
        SEGMENT_FILES+=("$SEGMENT_FILE")
        echo -e "   ${GREEN}✅ segment_$(printf '%03d' $i).mp4${NC}"
    else
        echo -e "   ${RED}❌ 片段生成失败${NC}"
    fi
done

echo ""

# === Step 4: 拼接所有片段 ===
echo -e "${CYAN}🔗 Step 4: 拼接片段...${NC}"

CONCAT_FILE="$WORK_DIR/concat.txt"
for seg in "${SEGMENT_FILES[@]}"; do
    echo "file '$seg'" >> "$CONCAT_FILE"
done

CONCAT_VIDEO="$WORK_DIR/concat_raw.mp4"

if [[ "$TRANSITION" == "fade" ]] && [[ ${#SEGMENT_FILES[@]} -gt 1 ]]; then
    # 使用 xfade 做淡入淡出转场
    echo -e "   添加 fade 转场 (${TRANSITION_DURATION}s)..."
    
    # 对于多段视频，逐步拼接 xfade
    # 先简单 concat，然后对整体加 fade in/out
    ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" \
        -vf "fade=t=in:st=0:d=${TRANSITION_DURATION},fade=t=out:st=$(echo "$TOTAL_DURATION - $TRANSITION_DURATION" | bc):d=${TRANSITION_DURATION}" \
        -c:v libx264 -preset fast -crf 23 \
        -pix_fmt yuv420p \
        "$CONCAT_VIDEO" \
        -loglevel warning 2>/dev/null
else
    ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" \
        -c:v libx264 -preset fast -crf 23 \
        -pix_fmt yuv420p \
        "$CONCAT_VIDEO" \
        -loglevel warning 2>/dev/null
fi

echo -e "   ${GREEN}✅ 视频拼接完成${NC}"
echo ""

# === Step 5: 混入背景音乐 ===
echo -e "${CYAN}🎵 Step 5: 混入音频...${NC}"

# 检查视频是否已有音轨（配音）
HAS_AUDIO=$(ffprobe -v quiet -show_entries stream=codec_type -of csv=p=0 "$CONCAT_VIDEO" 2>/dev/null | grep -c "audio" || echo "0")

# 查找音乐文件
if [[ -z "$MUSIC_FILE" ]]; then
    MUSIC_DIR="$PROJECT_DIR/music"
    if [[ -d "$MUSIC_DIR" ]]; then
        MUSIC_FILE=$(find "$MUSIC_DIR" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" -o -name "*.aac" \) -not -name "calm_bgm.mp3" | head -1)
        # fallback 到任何音乐文件
        if [[ -z "$MUSIC_FILE" ]]; then
            MUSIC_FILE=$(find "$MUSIC_DIR" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" -o -name "*.aac" \) | head -1)
        fi
    fi
fi

if [[ -n "$MUSIC_FILE" ]] && [[ -f "$MUSIC_FILE" ]] && [[ "$HAS_AUDIO" -gt 0 ]]; then
    # 有配音 + 有 BGM → 三轨混合（视频 + 配音 + BGM）
    echo -e "   🎤 配音: 已嵌入"
    echo -e "   🎵 背景音乐: $(basename "$MUSIC_FILE")"
    echo -e "   📎 混合模式: 配音 + BGM"
    
    ffmpeg -y -i "$CONCAT_VIDEO" -i "$MUSIC_FILE" \
        -filter_complex "[0:a]volume=1.0[voice];[1:a]volume=0.15,afade=t=in:st=0:d=2,afade=t=out:st=$(echo "$TOTAL_DURATION - 3" | bc):d=3,atrim=0:${TOTAL_DURATION}[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]" \
        -map 0:v -map "[aout]" \
        -c:v copy -c:a aac -b:a 192k \
        -shortest \
        "$OUTPUT_FILE" \
        -loglevel warning 2>/dev/null
    
    echo -e "   ${GREEN}✅ 配音 + BGM 混合完成${NC}"

elif [[ -n "$MUSIC_FILE" ]] && [[ -f "$MUSIC_FILE" ]]; then
    # 无配音 + 有 BGM → 只混 BGM
    echo -e "   🎵 背景音乐: $(basename "$MUSIC_FILE")"
    
    ffmpeg -y -i "$CONCAT_VIDEO" -i "$MUSIC_FILE" \
        -filter_complex "[1:a]volume=0.3,afade=t=in:st=0:d=2,afade=t=out:st=$(echo "$TOTAL_DURATION - 3" | bc):d=3[music];[music]atrim=0:${TOTAL_DURATION}[trimmed]" \
        -map 0:v -map "[trimmed]" \
        -c:v copy -c:a aac -b:a 192k \
        -shortest \
        "$OUTPUT_FILE" \
        -loglevel warning 2>/dev/null
    
    echo -e "   ${GREEN}✅ 已混入背景音乐${NC}"

elif [[ "$HAS_AUDIO" -gt 0 ]]; then
    # 有配音 + 无 BGM → 直接用配音
    echo -e "   🎤 配音: 已嵌入"
    echo -e "   ${YELLOW}⚠️  无背景音乐${NC}"
    
    cp "$CONCAT_VIDEO" "$OUTPUT_FILE"
    echo -e "   ${GREEN}✅ 使用配音音轨${NC}"

else
    # 无配音 + 无 BGM → 静音
    echo -e "   ${YELLOW}⚠️  未找到背景音乐和配音，输出静音视频${NC}"
    ffmpeg -y -i "$CONCAT_VIDEO" \
        -f lavfi -i anullsrc=r=44100:cl=stereo \
        -c:v copy -c:a aac -b:a 128k \
        -shortest \
        "$OUTPUT_FILE" \
        -loglevel warning 2>/dev/null
fi

echo ""

# === 完成！ ===
if [[ -f "$OUTPUT_FILE" ]]; then
    FINAL_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
    FINAL_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT_FILE" 2>/dev/null | cut -d. -f1)
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 视频制作完成！${NC}"
    echo ""
    echo -e "   📁 文件: ${GREEN}$OUTPUT_FILE${NC}"
    echo -e "   ⏱️  时长: ${GREEN}${FINAL_DUR}s${NC}"
    echo -e "   📐 分辨率: ${GREEN}${TARGET_W}x${TARGET_H}${NC}"
    echo -e "   💾 大小: ${GREEN}$(echo "scale=1; $FINAL_SIZE / 1048576" | bc)MB${NC}"
    echo -e "   🎬 段落: ${GREEN}${NUM_PARAGRAPHS}${NC}"
    echo -e "   📹 使用素材: ${GREEN}${#SEGMENT_FILES[@]} 个片段${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # 保存制作信息
    cat > "$PROJECT_DIR/meta/video-info.json" 2>/dev/null << EOF || true
{
    "output": "$OUTPUT_FILE",
    "duration": "$FINAL_DUR",
    "resolution": "${TARGET_W}x${TARGET_H}",
    "fps": $FPS,
    "style": "$STYLE",
    "paragraphs": $NUM_PARAGRAPHS,
    "clips_used": ${#SEGMENT_FILES[@]},
    "file_size_bytes": $FINAL_SIZE,
    "music": "$(basename "${MUSIC_FILE:-none}")",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
else
    echo -e "${RED}❌ 视频制作失败${NC}"
    exit 1
fi

# === 清理临时文件 ===
if [[ "${CLEANUP:-false}" == true ]]; then
    echo ""
    echo -e "${BLUE}🗑️  清理临时文件...${NC}"
    
    # 清理片段文件
    if [[ -d "$TEMP_DIR" ]]; then
        SEG_COUNT=$(ls -1 "$TEMP_DIR"/segment_*.mp4 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$SEG_COUNT" -gt 0 ]]; then
            echo "   删除 $SEG_COUNT 个临时片段..."
            trash "$TEMP_DIR"/segment_*.mp4 2>/dev/null || rm -f "$TEMP_DIR"/segment_*.mp4
        fi
    fi
    
    # 清理拼接列表
    [[ -f "$CONCAT_LIST" ]] && trash "$CONCAT_LIST" 2>/dev/null || rm -f "$CONCAT_LIST"
    
    # 清理临时视频文件
    [[ -f "$TEMP_VIDEO" ]] && trash "$TEMP_VIDEO" 2>/dev/null || rm -f "$TEMP_VIDEO"
    
    # 清理字幕文件
    [[ -f "$SUBTITLE_SRT" ]] && trash "$SUBTITLE_SRT" 2>/dev/null || rm -f "$SUBTITLE_SRT"
    [[ -f "$SUBTITLE_ASS" ]] && trash "$SUBTITLE_ASS" 2>/dev/null || rm -f "$SUBTITLE_ASS"
    
    # 清理项目中的临时文件
    [[ -d "$PROJECT_DIR/meta" ]] && trash "$PROJECT_DIR/meta" 2>/dev/null || rm -rf "$PROJECT_DIR/meta"
    
    echo -e "${GREEN}✅ 清理完成${NC}"
fi

echo ""
echo -e "${GREEN}🎉 所有工作完成！${NC}"
