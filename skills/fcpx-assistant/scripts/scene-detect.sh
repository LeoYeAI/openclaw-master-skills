#!/bin/bash
# Video Scene Detection using ffmpeg
# Detects cut points and scene changes in video files

VIDEO_FILE="$1"

if [ -z "$VIDEO_FILE" ]; then
    echo "❌ 用法：scene-detect.sh <视频文件路径>"
    exit 1
fi

if [ ! -f "$VIDEO_FILE" ]; then
    echo "❌ 文件不存在：$VIDEO_FILE"
    exit 1
fi

echo "📊 正在分析视频..."
echo "📁 文件：$VIDEO_FILE"
echo ""

# Get video duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null)
echo "⏱️ 视频时长：${DURATION}s"
echo ""

# Detect scenes using ffmpeg scene detect filter
echo "🔍 检测镜头切换点..."
echo ""

# Use scdet filter for scene detection
ffmpeg -i "$VIDEO_FILE" -filter_complex "scdet=threshold=0.45" -f null - 2>&1 | grep "scdet:" | while read line; do
    # Parse the output to get timestamps
    echo "$line"
done

# Alternative: Use ffmpeg to extract keyframes as scene indicators
echo ""
echo "🎬 关键帧信息："
ffprobe -v error -select_streams v:0 -show_entries frame=pict_type -of default=noprint_wrappers=1 "$VIDEO_FILE" 2>/dev/null | grep -c "I" | xargs -I {} echo "• I 帧数量：{} (场景切换参考)"

echo ""
echo "✅ 分析完成"
echo ""
echo "💡 提示：可以使用以下命令导出详细场景数据："
echo "   ffmpeg -i \"$VIDEO_FILE\" -filter_complex \"scdet=threshold=0.45\" -f null - 2> scenes.log"
