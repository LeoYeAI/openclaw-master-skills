#!/bin/bash
# Smart Media Tagger - AI-powered media tagging
# Analyzes video/audio files and generates descriptive tags

MEDIA_DIR="$1"

if [ -z "$MEDIA_DIR" ]; then
    echo "❌ 用法：smart-tagger.sh <素材文件夹>"
    exit 1
fi

if [ ! -d "$MEDIA_DIR" ]; then
    echo "❌ 目录不存在：$MEDIA_DIR"
    exit 1
fi

echo "🏷️ 智能素材标签生成器"
echo "📁 扫描目录：$MEDIA_DIR"
echo ""

# Create tags output file
TAGS_FILE="$MEDIA_DIR/_media-tags.json"
echo "[" > "$TAGS_FILE"

FIRST=true

# Find all video files
find "$MEDIA_DIR" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.m4v" -o -name "*.avi" \) | while read VIDEO_FILE; do
    FILENAME=$(basename "$VIDEO_FILE")
    echo "🎬 分析：$FILENAME"
    
    # Get file metadata
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null)
    RESOLUTION=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null | tr '\n' 'x' | sed 's/x$//')
    
    # Generate AI description using local model (simplified)
    # In production, this would call a vision model
    AI_TAGS="视频，${RESOLUTION}, ${DURATION}s"
    
    # Detect basic content characteristics
    IS_HDR=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null)
    if [[ "$IS_HDR" == *"smpte"* ]]; then
        AI_TAGS="$AI_TAGS, HDR"
    fi
    
    # Check for audio
    HAS_AUDIO=$(ffprobe -v error -select_streams a -show_entries stream=codec_type -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null | head -1)
    if [ -n "$HAS_AUDIO" ]; then
        AI_TAGS="$AI_TAGS, 有音频"
    fi
    
    # Write to tags file
    if [ "$FIRST" = true ]; then
        FIRST=false
    else
        echo "," >> "$TAGS_FILE"
    fi
    
    cat >> "$TAGS_FILE" << EOF
  {
    "file": "$FILENAME",
    "path": "$VIDEO_FILE",
    "duration": "$DURATION",
    "resolution": "$RESOLUTION",
    "tags": "$AI_TAGS",
    "analyzed": "$(date -Iseconds)"
  }
EOF
    
    echo "  ✅ 标签：$AI_TAGS"
done

echo "]" >> "$TAGS_FILE"

echo ""
echo "✅ 分析完成！"
echo "📄 标签文件：$TAGS_FILE"
echo ""
echo "💡 使用方法："
echo "   - 在 FCP 中搜索素材时参考标签"
echo "   - 可以导入到素材管理工具"
echo "   - 支持搜索标签关键词快速定位素材"
