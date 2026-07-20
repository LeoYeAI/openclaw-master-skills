#!/bin/bash
# Auto Thumbnail Generator
# Extracts best frames from video for thumbnails

VIDEO_FILE="$1"
OUTPUT_DIR="$2"

if [ -z "$VIDEO_FILE" ]; then
    echo "❌ 用法：auto-thumbnail.sh <视频文件> [输出目录]"
    exit 1
fi

if [ ! -f "$VIDEO_FILE" ]; then
    echo "❌ 文件不存在：$VIDEO_FILE"
    exit 1
fi

# Default output directory
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="$(dirname "$VIDEO_FILE")/thumbnails"
fi

mkdir -p "$OUTPUT_DIR"

echo "🖼️ 自动缩略图生成器"
echo "📁 视频：$VIDEO_FILE"
echo "📂 输出：$OUTPUT_DIR"
echo ""

# Get video duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null)

# Extract frames at different points
echo "📸 提取关键帧..."

# Frame at 10% of video
POS1=$(echo "$DURATION * 0.1" | bc)
ffmpeg -ss "$POS1" -i "$VIDEO_FILE" -vframes 1 -q:v 2 "$OUTPUT_DIR/thumb_10percent.jpg" -y 2>/dev/null

# Frame at 25% of video
POS2=$(echo "$DURATION * 0.25" | bc)
ffmpeg -ss "$POS2" -i "$VIDEO_FILE" -vframes 1 -q:v 2 "$OUTPUT_DIR/thumb_25percent.jpg" -y 2>/dev/null

# Frame at 50% of video
POS3=$(echo "$DURATION * 0.5" | bc)
ffmpeg -ss "$POS3" -i "$VIDEO_FILE" -vframes 1 -q:v 2 "$OUTPUT_DIR/thumb_50percent.jpg" -y 2>/dev/null

# Frame at 75% of video
POS4=$(echo "$DURATION * 0.75" | bc)
ffmpeg -ss "$POS4" -i "$VIDEO_FILE" -vframes 1 -q:v 2 "$OUTPUT_DIR/thumb_75percent.jpg" -y 2>/dev/null

# Extract scene change frames using scene detect
echo ""
echo "🎬 检测场景切换并提取..."
ffmpeg -i "$VIDEO_FILE" -vf "select='gt(scene,0.4)'" -vsync vfr -frames:v 5 "$OUTPUT_DIR/scene_%03d.jpg" -y 2>/dev/null

# Generate contact sheet
echo ""
echo "📋 生成联系表..."
ffmpeg -i "$VIDEO_FILE" -vf "tile=3x3" -q:v 2 "$OUTPUT_DIR/contact_sheet.jpg" -y 2>/dev/null

echo ""
echo "✅ 缩略图生成完成！"
echo ""
echo "📂 输出文件："
ls -lh "$OUTPUT_DIR"/*.jpg 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
echo ""
echo "💡 提示："
echo "- 选择最清晰、最有代表性的一帧作为封面"
echo "- 联系表适合快速预览整个视频内容"
echo "- 场景切换帧适合做章节封面"
