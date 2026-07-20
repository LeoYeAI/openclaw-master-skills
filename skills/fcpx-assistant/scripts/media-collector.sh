#!/bin/bash
# media-collector.sh - 自动搜索和下载免费视频素材 + 背景音乐
# 
# 使用方式:
#   bash media-collector.sh --keywords "nature mountain" --count 5 --output ./project-media
#   bash media-collector.sh --keywords "城市 夜景" --count 3 --orientation portrait --output ./media
#   bash media-collector.sh --keywords "coding technology" --music-keywords "electronic chill" --output ./media
#
# 素材来源: Pexels (免费视频) + Pixabay (免费音乐)
# API Key: 设置环境变量 PEXELS_API_KEY（免费注册 https://www.pexels.com/api/）
#          如未设置，使用默认 key（可能有速率限制）

set -euo pipefail

# === 颜色 ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# === 默认参数 ===
KEYWORDS=""
MUSIC_KEYWORDS=""
COUNT=5
ORIENTATION="landscape"  # landscape | portrait | square
QUALITY="hd"             # hd | sd | 4k
OUTPUT_DIR="./project-media"
MIN_DURATION=3
MAX_DURATION=30
PEXELS_KEY="${PEXELS_API_KEY:-}"

usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --keywords, -k      视频搜索关键词 (必需)"
    echo "  --music-keywords    背景音乐搜索关键词"
    echo "  --count, -n         下载视频数量 (默认: 5)"
    echo "  --orientation, -o   方向: landscape/portrait/square (默认: landscape)"
    echo "  --quality, -q       质量: sd/hd/4k (默认: hd)"
    echo "  --output, -d        输出目录 (默认: ./project-media)"
    echo "  --min-duration      最短时长秒 (默认: 3)"
    echo "  --max-duration      最长时长秒 (默认: 30)"
    echo "  --pexels-key        Pexels API Key"
    echo "  --help              显示帮助"
    exit 0
}

# === 解析参数 ===
while [[ $# -gt 0 ]]; do
    case $1 in
        --keywords|-k) KEYWORDS="$2"; shift 2 ;;
        --music-keywords) MUSIC_KEYWORDS="$2"; shift 2 ;;
        --count|-n) COUNT="$2"; shift 2 ;;
        --orientation|-o) ORIENTATION="$2"; shift 2 ;;
        --quality|-q) QUALITY="$2"; shift 2 ;;
        --output|-d) OUTPUT_DIR="$2"; shift 2 ;;
        --min-duration) MIN_DURATION="$2"; shift 2 ;;
        --max-duration) MAX_DURATION="$2"; shift 2 ;;
        --pexels-key) PEXELS_KEY="$2"; shift 2 ;;
        --help) usage ;;
        *) echo "未知参数: $1"; usage ;;
    esac
done

if [[ -z "$KEYWORDS" ]]; then
    echo -e "${RED}❌ 必须提供 --keywords 参数${NC}"
    usage
fi

# === 创建目录 ===
VIDEOS_DIR="$OUTPUT_DIR/videos"
MUSIC_DIR="$OUTPUT_DIR/music"
META_DIR="$OUTPUT_DIR/meta"
mkdir -p "$VIDEOS_DIR" "$MUSIC_DIR" "$META_DIR"

echo -e "${BLUE}🎬 素材收集器${NC}"
echo -e "关键词: ${GREEN}$KEYWORDS${NC}"
echo -e "数量: ${GREEN}$COUNT${NC}"
echo -e "方向: ${GREEN}$ORIENTATION${NC}"
echo -e "质量: ${GREEN}$QUALITY${NC}"
echo -e "输出: ${GREEN}$OUTPUT_DIR${NC}"
echo ""

# === 确定目标分辨率 ===
case "$ORIENTATION" in
    landscape)
        case "$QUALITY" in
            sd) TARGET_W=854; TARGET_H=480 ;;
            hd) TARGET_W=1280; TARGET_H=720 ;;
            4k) TARGET_W=3840; TARGET_H=2160 ;;
            *) TARGET_W=1920; TARGET_H=1080 ;;
        esac
        ;;
    portrait)
        case "$QUALITY" in
            sd) TARGET_W=480; TARGET_H=854 ;;
            hd) TARGET_W=720; TARGET_H=1280 ;;
            4k) TARGET_W=2160; TARGET_H=3840 ;;
            *) TARGET_W=1080; TARGET_H=1920 ;;
        esac
        ;;
    square)
        case "$QUALITY" in
            sd) TARGET_W=480; TARGET_H=480 ;;
            hd) TARGET_W=720; TARGET_H=720 ;;
            4k) TARGET_W=2160; TARGET_H=2160 ;;
            *) TARGET_W=1080; TARGET_H=1080 ;;
        esac
        ;;
esac

# ============================
# 搜索和下载 Pexels 视频
# ============================

echo -e "${BLUE}📹 搜索 Pexels 视频素材...${NC}"

# 多关键词策略：逐词搜索再合并（免费 key 不支持多词查询）
KEYWORD_ARRAY=($KEYWORDS)
ALL_VIDEOS="[]"
VIDEOS_PER_KEYWORD=$(( (COUNT + ${#KEYWORD_ARRAY[@]} - 1) / ${#KEYWORD_ARRAY[@]} ))
[[ "$VIDEOS_PER_KEYWORD" -lt 2 ]] && VIDEOS_PER_KEYWORD=2

for kw in "${KEYWORD_ARRAY[@]}"; do
    echo -e "   搜索关键词: ${YELLOW}$kw${NC}"
    PEXELS_URL="https://api.pexels.com/videos/search?query=${kw}&per_page=${VIDEOS_PER_KEYWORD}"
    
    KW_RESP=$(curl -s "$PEXELS_URL" \
        -H "Authorization: ${PEXELS_KEY:-pexels}" \
        --connect-timeout 10 \
        --max-time 30 2>/dev/null || echo '{"videos":[]}')
    
    KW_VIDEOS=$(echo "$KW_RESP" | jq '.videos // []' 2>/dev/null || echo '[]')
    KW_COUNT=$(echo "$KW_VIDEOS" | jq 'length' 2>/dev/null || echo "0")
    echo -e "   → 找到 ${KW_COUNT} 个结果"
    
    # 合并到总列表
    ALL_VIDEOS=$(echo "$ALL_VIDEOS" "$KW_VIDEOS" | jq -s '.[0] + .[1] | unique_by(.id)' 2>/dev/null || echo "$ALL_VIDEOS")
    
    sleep 0.3
done

# 构造与原格式兼容的响应
PEXELS_RESP=$(echo "$ALL_VIDEOS" | jq '{videos: .}')

# 检查结果
VIDEO_COUNT=$(echo "$PEXELS_RESP" | jq '.videos | length' 2>/dev/null || echo "0")

if [[ "$VIDEO_COUNT" -eq 0 ]]; then
    echo -e "${RED}❌ 未找到视频素材，请尝试不同的关键词${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 找到 $VIDEO_COUNT 个视频${NC}"

# 保存搜索结果元数据
echo "$PEXELS_RESP" | jq '.' > "$META_DIR/pexels-search.json" 2>/dev/null

# 下载视频
DOWNLOADED=0
for i in $(seq 0 $((VIDEO_COUNT - 1))); do
    VIDEO_ID=$(echo "$PEXELS_RESP" | jq -r ".videos[$i].id")
    VIDEO_DURATION=$(echo "$PEXELS_RESP" | jq -r ".videos[$i].duration")
    VIDEO_USER=$(echo "$PEXELS_RESP" | jq -r ".videos[$i].user.name")
    VIDEO_URL_PAGE=$(echo "$PEXELS_RESP" | jq -r ".videos[$i].url")
    
    # 过滤时长
    if [[ "$VIDEO_DURATION" -lt "$MIN_DURATION" ]] || [[ "$VIDEO_DURATION" -gt "$MAX_DURATION" ]]; then
        echo -e "${YELLOW}⏭️  跳过 #$VIDEO_ID (${VIDEO_DURATION}s, 不在 ${MIN_DURATION}-${MAX_DURATION}s 范围)${NC}"
        continue
    fi
    
    # 选择最佳质量的视频文件
    # 根据目标宽度选最接近的
    DOWNLOAD_URL=$(echo "$PEXELS_RESP" | jq -r "
        .videos[$i].video_files 
        | sort_by((.width - $TARGET_W) | if . < 0 then -. else . end) 
        | .[0].link" 2>/dev/null)
    
    if [[ -z "$DOWNLOAD_URL" ]] || [[ "$DOWNLOAD_URL" == "null" ]]; then
        # fallback: 取第一个
        DOWNLOAD_URL=$(echo "$PEXELS_RESP" | jq -r ".videos[$i].video_files[0].link")
    fi
    
    FILENAME="clip_$(printf '%02d' $((DOWNLOADED + 1)))_${VIDEO_ID}.mp4"
    OUTPUT_FILE="$VIDEOS_DIR/$FILENAME"
    
    echo -e "${BLUE}⬇️  下载 clip $((DOWNLOADED + 1))/${COUNT}: #$VIDEO_ID (${VIDEO_DURATION}s, by $VIDEO_USER)${NC}"
    
    if curl -sL "$DOWNLOAD_URL" -o "$OUTPUT_FILE" --connect-timeout 15 --max-time 120 2>/dev/null; then
        # 验证文件
        FILE_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null || echo "0")
        if [[ "$FILE_SIZE" -gt 10000 ]]; then
            DOWNLOADED=$((DOWNLOADED + 1))
            
            # 保存元数据
            echo "{\"file\":\"$FILENAME\",\"id\":$VIDEO_ID,\"duration\":$VIDEO_DURATION,\"author\":\"$VIDEO_USER\",\"source\":\"$VIDEO_URL_PAGE\",\"license\":\"Pexels Free\"}" \
                | jq '.' >> "$META_DIR/clips-meta.jsonl"
            
            echo -e "${GREEN}   ✅ 已保存: $FILENAME ($(echo "scale=1; $FILE_SIZE / 1048576" | bc)MB)${NC}"
        else
            rm -f "$OUTPUT_FILE"
            echo -e "${RED}   ❌ 文件太小，跳过${NC}"
        fi
    else
        echo -e "${RED}   ❌ 下载失败${NC}"
    fi
    
    if [[ "$DOWNLOADED" -ge "$COUNT" ]]; then
        break
    fi
    
    # 请求间隔
    sleep 0.5
done

echo ""
echo -e "${GREEN}📹 视频素材: 下载了 $DOWNLOADED 个片段到 $VIDEOS_DIR/${NC}"

# ============================
# 搜索和下载免费音乐 (Pixabay)
# ============================

if [[ -n "$MUSIC_KEYWORDS" ]]; then
    echo ""
    echo -e "${BLUE}🎵 搜索免费背景音乐...${NC}"
    
    # 使用 Pixabay Music API (免费，无需 key)
    MUSIC_QUERY=$(echo "$MUSIC_KEYWORDS" | sed 's/ /+/g')
    
    # Pixabay 音乐页面搜索
    MUSIC_SEARCH_URL="https://pixabay.com/music/search/${MUSIC_QUERY}/"
    
    echo -e "${YELLOW}💡 自动音乐搜索需要 Pixabay API key${NC}"
    echo -e "   你可以手动从这些免费来源下载:"
    echo -e "   ${BLUE}🔗 Pixabay Music: ${MUSIC_SEARCH_URL}${NC}"
    echo -e "   ${BLUE}🔗 Free Music Archive: https://freemusicarchive.org/search?quicksearch=${MUSIC_QUERY}${NC}"
    echo -e "   ${BLUE}🔗 Incompetech: https://incompetech.com/music/royalty-free/music.html${NC}"
    echo ""
    echo -e "   下载后放到: ${GREEN}$MUSIC_DIR/${NC}"
fi

# ============================
# 生成汇总
# ============================

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📦 素材收集完成！${NC}"
echo ""

# 列出下载的文件
echo -e "${BLUE}📹 视频素材:${NC}"
if ls "$VIDEOS_DIR"/*.mp4 1>/dev/null 2>&1; then
    for f in "$VIDEOS_DIR"/*.mp4; do
        FNAME=$(basename "$f")
        FSIZE=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null || echo "0")
        FDURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null | cut -d. -f1 || echo "?")
        echo -e "   ${FNAME} (${FDURATION}s, $(echo "scale=1; $FSIZE / 1048576" | bc)MB)"
    done
else
    echo -e "   ${YELLOW}无视频文件${NC}"
fi

echo ""
echo -e "${BLUE}🎵 音乐素材:${NC}"
if ls "$MUSIC_DIR"/*.{mp3,wav,m4a,aac} 1>/dev/null 2>&1; then
    for f in "$MUSIC_DIR"/*.{mp3,wav,m4a,aac}; do
        [[ -f "$f" ]] || continue
        FNAME=$(basename "$f")
        echo -e "   $FNAME"
    done
else
    echo -e "   ${YELLOW}请手动添加音乐到 $MUSIC_DIR/${NC}"
fi

echo ""

# 保存项目信息
cat > "$META_DIR/project-info.json" << EOF
{
    "keywords": "$KEYWORDS",
    "music_keywords": "$MUSIC_KEYWORDS",
    "orientation": "$ORIENTATION",
    "quality": "$QUALITY",
    "target_resolution": "${TARGET_W}x${TARGET_H}",
    "clips_downloaded": $DOWNLOADED,
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "videos_dir": "$VIDEOS_DIR",
    "music_dir": "$MUSIC_DIR"
}
EOF

echo -e "${GREEN}✅ 项目信息已保存到 $META_DIR/project-info.json${NC}"
echo -e "${BLUE}下一步: 用 auto-video-maker.sh 组装成片！${NC}"
